from typing import Any, Dict, Type
import json
import yaml
from ..base.parser import BaseContentParser, BaseFlexTagParser
from .document import Document

try:
    import tomli_w as toml_write
    import tomli as toml_read
except ImportError:
    import tomlkit as toml_read

    toml_write = toml_read


class TOMLParser(BaseContentParser):
    def parse(self, content: str) -> Dict:
        return toml_read.loads(content)

    def dump(self, data: Any) -> str:
        return toml_write.dumps(data)


class JSONParser(BaseContentParser):
    def parse(self, content: str) -> Dict:
        return json.loads(content)

    def dump(self, data: Any) -> str:
        return json.dumps(data, indent=2)


class YAMLParser(BaseContentParser):
    def parse(self, content: str) -> Dict:
        return yaml.safe_load(content)

    def dump(self, data: Any) -> str:
        return yaml.safe_dump(data, sort_keys=False)


class FlexTagParser(BaseFlexTagParser):
    def __init__(self):
        super().__init__()
        # Register default parsers
        self.register_content_parser("toml", TOMLParser)
        self.register_content_parser("json", JSONParser)
        self.register_content_parser("yaml", YAMLParser)

    def parse(self, content: str) -> Document:
        doc = Document.from_string(content)

        # Parse section contents based on their format
        if doc.info and "fmt" in doc.info.params:
            parser = self.get_content_parser(doc.info.params["fmt"])
            doc.info.content = parser.parse(doc.info.content)

        for section in doc.sections:
            if "fmt" in section.params:
                parser = self.get_content_parser(section.params["fmt"])
                section.content = parser.parse(section.content)

        return doc

    def dump(self, document: Document) -> str:
        # Create a copy to avoid modifying the original
        doc = Document()
        doc.settings = document.settings.copy()

        # Handle INFO section
        if document.info:
            doc.info = document.info.__class__(**vars(document.info))
            if "fmt" in doc.info.params:
                parser = self.get_content_parser(doc.info.params["fmt"])
                doc.info.content = parser.dump(doc.info.content)

        # Handle regular sections
        for section in document.sections:
            new_section = section.__class__(**vars(section))
            if "fmt" in new_section.params:
                parser = self.get_content_parser(new_section.params["fmt"])
                new_section.content = parser.dump(new_section.content)
            doc.sections.append(new_section)

        return doc.to_string()
