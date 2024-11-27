from typing import Dict, Optional, List, Tuple, Any
from flextag.core.interfaces.parser import IContainerParser, ISectionParser, IContentParser
from flextag.core.types.container import Container
from flextag.core.types.section import Section
from flextag.core.parsers.metadata import MetadataParser
from flextag.logger import logger
from flextag.exceptions import FlexTagError
from flextag.settings import Const


class SectionParser(ISectionParser):
    """Parser for [[SEC]] sections"""

    def __init__(self):
        self.metadata_parser = MetadataParser()

    def parse(self, raw_section: str, content_parser: Optional[IContentParser] = None) -> Section:
        """Parse raw section text into Section object"""
        try:
            header, content = self._split_header_and_content(raw_section)
            metadata = self._parse_metadata(header)
            parsed_content = self._parse_content(content, content_parser)
            return Section(
                metadata=metadata,
                content=parsed_content,
                raw_content=content
            )
        except Exception as e:
            logger.error(f"Section parsing error: {str(e)}")
            raise FlexTagError(f"Failed to parse section: {str(e)}")

    def dump(self, section: Section, content_parser: Optional[IContentParser] = None) -> str:
        """Convert section back to string format"""
        try:
            header_line = self._build_header_line(section)
            content = self._dump_content(section.content, content_parser)
            end_marker = '[[/SEC]]'
            return "\n".join([header_line, content, end_marker])
        except Exception as e:
            logger.error(f"Section serialization error: {str(e)}")
            raise FlexTagError(f"Failed to serialize section: {str(e)}")

    def _split_header_and_content(self, raw_section: str) -> Tuple[str, str]:
        """Split raw section text into header and content"""
        lines = raw_section.strip().splitlines()
        header = lines[0]
        # Exclude the last line if it's '[[/SEC]]'
        if lines[-1].strip() == Const.SEC_END:
            content_lines = lines[1:-1]
        else:
            content_lines = lines[1:]
        content = "\n".join(content_lines)
        return header, content

    def _parse_metadata(self, header: str):
        """Parse metadata from the header line"""
        return self.metadata_parser.parse_section_meta(header)

    def _parse_content(self, content: str, content_parser: Optional[IContentParser]) -> str:
        """Parse content using the provided content parser"""
        if content_parser and content.strip():
            return content_parser.parse(content)
        return content

    def _build_header_line(self, section: Section) -> str:
        """Build the header line from section metadata"""
        header_parts = [f"[[SEC:{section.metadata.id}"]

        # Add tags
        for tag in section.metadata.tags:
            header_parts.append(f"#{tag}")

        # Add paths
        for path in section.metadata.paths:
            header_parts.append(f".{path}")

        # Add parameters
        for key, value in section.metadata.parameters.items():
            header_parts.append(f'{key}="{value}"')

        return " ".join(header_parts) + "]]"

    def _dump_content(self, content, content_parser: Optional[IContentParser]) -> str:
        """Dump content using the provided content parser"""
        if content_parser:
            return content_parser.dump(content)
        return content


class ContainerParser(IContainerParser):
    """Parser for complete FlexTag containers"""

    def __init__(self):
        self.metadata_parser = MetadataParser()
        self.section_parser = SectionParser()
        self._content_parsers: Dict[str, IContentParser] = {}

    def register_content_parser(self, fmt: str, parser: IContentParser) -> None:
        """Register content parser for format"""
        self._content_parsers[fmt] = parser
        logger.debug(f"Registered content parser for format: {fmt}")

    def parse(self, content: str) -> Container:
        """Parse raw content into Container object"""
        try:
            container = Container.create()
            lines = content.splitlines()
            idx = 0
            total_lines = len(lines)

            # Step 1: Look for PARAMS, META, SEC, or comment
            idx = self._skip_comments_and_empty_lines(lines, idx)
            if idx >= total_lines:
                raise FlexTagError("No valid content found")

            # Handle PARAMS if present
            if lines[idx].strip().startswith('[[PARAMS'):
                params_header_lines, idx = self._collect_header_lines(lines, idx)
                container.params = self._parse_params_lines(params_header_lines)
                # Move to next step
            elif lines[idx].strip().startswith('[[META') or lines[idx].strip().startswith('[[SEC'):
                # No PARAMS, proceed
                pass
            else:
                raise FlexTagError("Expected [[PARAMS]], [[META]], or [[SEC]] at the beginning")

            # Step 2: Look for META, SEC, or comment
            idx = self._skip_comments_and_empty_lines(lines, idx)
            if idx >= total_lines:
                raise FlexTagError("No valid content after PARAMS")

            # Handle META if present
            if lines[idx].strip().startswith('[[META'):
                meta_header_lines, idx = self._collect_header_lines(lines, idx)
                container.metadata = self._parse_meta_lines(meta_header_lines)
                # Move to next step
            elif lines[idx].strip().startswith('[[SEC'):
                # No META, proceed
                pass
            else:
                raise FlexTagError("Expected [[META]] or [[SEC]] after PARAMS")

            # Step 3: Look for SEC or comment
            idx = self._skip_comments_and_empty_lines(lines, idx)
            if idx >= total_lines or not lines[idx].strip().startswith('[[SEC'):
                raise FlexTagError("Expected [[SEC]] to start sections")

            # Parse sections
            container.sections = self._parse_sections(lines, idx)

            container.raw_content = content
            logger.debug(f"Parsed container with {len(container.sections)} sections")
            return container
        except Exception as e:
            logger.error(f"Container parsing error: {str(e)}")
            raise FlexTagError(f"Failed to parse container: {str(e)}")

    def _skip_comments_and_empty_lines(self, lines: List[str], idx: int) -> int:
        """Skip comments and empty lines, return next index"""
        total_lines = len(lines)
        while idx < total_lines:
            line = lines[idx].strip()
            if not line or line.startswith('[[#'):
                # Skip comments and empty lines
                idx = self._skip_comment_block(lines, idx)
                continue
            else:
                break
            idx += 1
        return idx

    def _skip_comment_block(self, lines: List[str], idx: int) -> int:
        """Skip over a comment block, return next index"""
        line = lines[idx].strip()
        if line.startswith('[[#]]'):
            # Single-line comment, skip line
            return idx + 1
        elif line.startswith('[[#'):
            # Multi-line comment
            idx += 1
            total_lines = len(lines)
            while idx < total_lines:
                line = lines[idx].strip()
                if line.endswith('#]]'):
                    return idx + 1
                idx += 1
            raise FlexTagError("Unterminated comment block")
        else:
            return idx + 1  # Should not reach here

    def _collect_header_lines(self, lines: List[str], start_idx: int) -> Tuple[List[str], int]:
        """Collect lines belonging to a header until closing ']]' is found"""
        header_lines = []
        idx = start_idx
        total_lines = len(lines)

        while idx < total_lines:
            line = lines[idx]
            header_lines.append(line)
            if ']]' in line:
                break
            if not line.strip():
                raise FlexTagError("Empty lines are not allowed within headers")
            idx += 1
        else:
            raise FlexTagError("Header not properly closed with ']]'")

        return header_lines, idx + 1  # Return next index after header

    def _parse_params_lines(self, header_lines: List[str]):
        """Parse PARAMS from collected header lines"""
        header = ' '.join(header_lines)
        return self.metadata_parser.parse_params(header)

    def _parse_meta_lines(self, header_lines: List[str]):
        """Parse META from collected header lines"""
        header = ' '.join(header_lines)
        return self.metadata_parser.parse_meta(header)

    def _parse_sections(self, lines: List[str], start_idx: int) -> List[Section]:
        """Parse sections starting from the given line number"""
        sections = []
        idx = start_idx
        total_lines = len(lines)

        while idx < total_lines:
            idx = self._skip_comments_and_empty_lines(lines, idx)
            if idx >= total_lines:
                break

            # Collect section header lines
            if not lines[idx].strip().startswith('[[SEC'):
                raise FlexTagError(f"Expected section start at line {idx + 1}")
            section_header_lines, idx = self._collect_header_lines(lines, idx)

            # Collect section content lines until '[[/SEC]]' is found
            section_content_lines = []
            in_section = True
            while idx < total_lines and in_section:
                line = lines[idx].strip()
                if line.startswith('[[#'):
                    idx = self._skip_comment_block(lines, idx)
                    continue
                if line == '[[/SEC]]':
                    in_section = False
                    idx += 1
                    break
                section_content_lines.append(lines[idx])
                idx += 1

            if in_section:
                raise FlexTagError("Unterminated section: missing '[[/SEC]]'")

            # Combine header and content lines
            section_lines = section_header_lines + section_content_lines + ['[[/SEC]]']
            section_text = '\n'.join(section_lines)

            # Parse the section
            section = self._create_section_from_text(section_text)
            sections.append(section)

        return sections

    def _create_section_from_text(self, section_text: str) -> Section:
        """Create a Section object from section text"""
        parsed_section = self._parse_section(section_text)
        return parsed_section

    def _parse_section(self, section_text: str) -> Section:
        """Parse a single section text"""
        # Parse section without content parser to get format
        parsed_section = self.section_parser.parse(section_text)
        fmt = parsed_section.metadata.parameters.get('fmt', 'text')

        # Get content parser for format
        content_parser = self._get_content_parser(fmt)
        if content_parser:
            # Re-parse with content parser
            parsed_section = self.section_parser.parse(section_text, content_parser)
        return parsed_section

    def _get_content_parser(self, fmt: str) -> Optional[IContentParser]:
        """Get parser for format"""
        return self._content_parsers.get(fmt)

    def dump(self, container: Container) -> str:
        """Convert container back to string format"""
        try:
            lines = []
            if container.params:
                params_line = self._build_params_line(container.params)
                lines.append(params_line)

            if container.metadata:
                meta_line = self._build_meta_line(container.metadata)
                lines.append(meta_line)

            for section in container.sections:
                content_parser = self._get_content_parser(section.metadata.fmt)
                section_text = self.section_parser.dump(section, content_parser)
                lines.append(section_text)

            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Container serialization error: {str(e)}")
            raise FlexTagError(f"Failed to serialize container: {str(e)}")

    def _find_marker_lines(self, lines: List[str]) -> Dict[str, int]:
        """Find line numbers of PARAMS, META, and sections"""
        marker_lines = {}
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            # Ignore escaped markers
            if stripped_line.startswith('\\'):
                continue
            if stripped_line.startswith(Const.PARAMS_START) and 'PARAMS' not in marker_lines:
                marker_lines['PARAMS'] = i
            elif stripped_line.startswith(Const.META_START) and 'META' not in marker_lines:
                marker_lines['META'] = i
            elif stripped_line.startswith(Const.SEC_START):
                marker_lines['SECTIONS'] = i
                break  # Sections must be after PARAMS and META
        return marker_lines

    def _parse_params_line(self, line: str):
        """Parse PARAMS line"""
        return self.metadata_parser.parse_params(line)

    def _parse_meta_line(self, line: str):
        """Parse META line"""
        return self.metadata_parser.parse_meta(line)

    def _build_params_line(self, params: Dict[str, Any]) -> str:
        """Build the PARAMS line, including parameters with empty values."""
        params_parts = ["[[PARAMS"]
        for key, value in params.items():
            value_str = str(value)
            params_parts.append(f'{key}="{value_str}"')
        params_parts.append("]]")
        return " ".join(params_parts)

    def _build_meta_line(self, metadata) -> str:
        """Build the META line"""
        meta_parts = ["[[META"]
        if metadata.id:
            meta_parts[0] += f":{metadata.id}"

        for tag in metadata.tags:
            meta_parts.append(f"#{tag}")

        for path in metadata.paths:
            meta_parts.append(f".{path}")

        for key, value in metadata.parameters.items():
            meta_parts.append(f'{key}="{value.to_string()}"')

        return " ".join(meta_parts) + "]]"
