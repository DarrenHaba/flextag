from tkinter import ttk
import tkinter as tk
import json
from flextag.core.managers.parser import ParserManager
from flextag.core.managers.search import SearchManager
from flextag.core.managers.transport import TransportManager
from flextag.core.parsers.parsers import ContainerParser, SectionParser
from flextag.core.parsers.content import JSONParser, YAMLParser, TextParser
from flextag.core.search.algorithms.exact import ExactMatchAlgorithm
from flextag.core.search.algorithms.wildcard import WildcardMatchAlgorithm
from flextag.core.search.query import SearchQuery
from flextag.core.transport.container import TransportContainer
from flextag.logger import logger


class FlexTagDemo:
    """Simple demo UI for FlexTag functionality"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FlexTag Demo")
        self.root.geometry("1000x600")  # Reduced height

        # Initialize managers
        self._setup_managers()
        self._setup_ui()
        self._load_sample()

    def _setup_managers(self):
        """Initialize and configure all managers"""
        # Parser Manager setup
        self.parser_manager = ParserManager()

        # Create parsers
        container_parser = ContainerParser()
        section_parser = SectionParser()
        json_parser = JSONParser()
        yaml_parser = YAMLParser()
        text_parser = TextParser()

        # Register container and section parsers
        self.parser_manager.register_container_parser(container_parser)
        self.parser_manager.register_section_parser(section_parser)

        # Register content parsers
        content_parsers = {
            "json": json_parser,
            "yaml": yaml_parser,
            "text": text_parser
        }

        for fmt, parser in content_parsers.items():
            self.parser_manager.register_content_parser(fmt, parser)
            container_parser.register_content_parser(fmt, parser)

        # Search Manager setup with query parser
        self.search_manager = SearchManager()
        self.search_manager.register_algorithm("exact", ExactMatchAlgorithm)
        self.search_manager.register_algorithm("wildcard", WildcardMatchAlgorithm)
        self.search_manager.register_query_parser(SearchQuery)  # Added registration

        # Transport Manager setup
        self.transport_manager = TransportManager()
        self.transport_manager.register_transport_container(TransportContainer)

        logger.info("All managers initialized and configured")

    def _setup_ui(self):
        """Setup the UI components"""
        # Main container with padding
        main = ttk.Frame(self.root, padding="5")
        main.pack(fill=tk.BOTH, expand=True)

        # Top pane: Input and Results split
        paned = ttk.PanedWindow(main, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # Left side: Input
        input_frame = ttk.LabelFrame(paned, text="FlexTag Input")
        self.input_text = tk.Text(input_frame, wrap=tk.WORD)
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Right side: Parsed Result
        result_frame = ttk.LabelFrame(paned, text="Parsed Structure")
        self.result_text = tk.Text(result_frame, wrap=tk.WORD, state="disabled")
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        paned.add(input_frame, weight=1)
        paned.add(result_frame, weight=1)

        # Bottom frame: Controls
        controls = ttk.Frame(main)
        controls.pack(fill=tk.X, pady=(0, 5))

        # Search frame
        search_frame = ttk.LabelFrame(controls, text="Search")
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        # Search input
        ttk.Label(search_frame, text="Query:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.insert(0, "#system")

        # Search buttons
        ttk.Button(
            search_frame,
            text="Find First",
            command=self._find_first
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            search_frame,
            text="Find All",
            command=self._find_all
        ).pack(side=tk.LEFT, padx=5)

        # Transport frame
        transport_frame = ttk.LabelFrame(controls, text="Transport")
        transport_frame.pack(fill=tk.X, padx=5, pady=5)

        # Transport buttons
        ttk.Button(
            transport_frame,
            text="To Transport",
            command=self._to_transport
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            transport_frame,
            text="From Transport",
            command=self._from_transport
        ).pack(side=tk.LEFT, padx=5)

        # Status bar (now using Text widget)
        self.status = tk.Text(main, height=2, wrap=tk.WORD)
        self.status.pack(fill=tk.X)
        self.status.config(state='disabled')

        # Bind events
        self.input_text.bind('<KeyRelease>', self._on_input_change)

    def _update_status(self, msg):
        """Update status text widget"""
        self.status.config(state='normal')
        self.status.delete('1.0', tk.END)
        self.status.insert('1.0', msg)
        self.status.config(state='disabled')

    def _display_result(self, data):
        """Display formatted result based on data type"""
        self.result_text.config(state="normal")
        self.result_text.delete('1.0', tk.END)

        if isinstance(data, (dict, list)):
            # For structured data, use appropriate formatter
            try:
                formatted = json.dumps(data, indent=2, default=str)
                self.result_text.insert('1.0', formatted)
            except Exception as e:
                self.result_text.insert('1.0', f"Error formatting result: {str(e)}\n\nRaw data:\n{str(data)}")
        else:
            # For other types, use string representation
            self.result_text.insert('1.0', str(data))

        self.result_text.config(state="disabled")

    def _load_sample(self):
        """Load sample FlexTag content"""
        sample = '''[[PARAMS fmt="text" enc="utf-8"]]
[[META:config #prod .sys.config version="1.0"]]

[[SEC:database #system #db .sys.database fmt="json"]]
{
    "host": "localhost",
    "port": 5432,
    "user": "admin"
}
[[/SEC]]

[[SEC:api #service #web .sys.api fmt="yaml"]]
host: api.example.com
port: 8080
endpoints:
  - /users
  - /products
[[/SEC]]'''

        self.input_text.delete('1.0', tk.END)
        self.input_text.insert('1.0', sample)
        self._on_input_change(None)

    def _on_input_change(self, event):
        """Handle input changes"""
        try:
            content = self.input_text.get('1.0', 'end-1c')
            container = self.parser_manager.parse_container(content)

            # Display parsed sections with their content
            result = []
            for section in container.sections:
                section_data = {
                    "id": section.metadata.id,
                    "tags": list(section.metadata.tags),
                    "paths": list(section.metadata.paths),
                    "format": section.metadata.fmt,
                    "content": section.content
                }
                result.append(section_data)

            self._display_result(result)
            self._update_status("Parsed successfully")

        except Exception as e:
            self._update_status(f"Error: {str(e)}")

    def _find_first(self):
        """Execute find_first with current query"""
        try:
            query = self.search_entry.get()
            content = self.input_text.get('1.0', 'end-1c')
            container = self.parser_manager.parse_container(content)

            result = self.search_manager.find_first(container, query)
            if result:
                self._update_status(f"Found section: {result.metadata.id}")

                # Display section data
                section_data = {
                    "id": result.metadata.id,
                    "tags": list(result.metadata.tags),
                    "paths": list(result.metadata.paths),
                    "format": result.metadata.fmt,
                    "content": result.content
                }
                self._display_result(section_data)
            else:
                self._update_status("No matches found")

        except Exception as e:
            self._update_status(f"Search error: {str(e)}")

    def _find_all(self):
        """Execute find with current query"""
        try:
            query = self.search_entry.get()
            content = self.input_text.get('1.0', 'end-1c')
            container = self.parser_manager.parse_container(content)

            results = self.search_manager.find(container, query)
            self._update_status(f"Found {len(results)} matches")

            # Display all matching sections
            result_data = []
            for result in results:
                section_data = {
                    "id": result.metadata.id,
                    "tags": list(result.metadata.tags),
                    "paths": list(result.metadata.paths),
                    "format": result.metadata.fmt,
                    "content": result.content
                }
                result_data.append(section_data)

            self._display_result(result_data)

        except Exception as e:
            self._update_status(f"Search error: {str(e)}")

    def _to_transport(self):
        """Convert current content to transport format"""
        try:
            content = self.input_text.get('1.0', 'end-1c')
            container = self.parser_manager.parse_container(content)
            transport = self.transport_manager.to_transport(container)

            self._display_result(transport)
            self._update_status("Converted to transport format")

        except Exception as e:
            self._update_status(f"Transport error: {str(e)}")

    def _from_transport(self):
        """Convert transport format back to container"""
        try:
            transport = self.result_text.get('1.0', 'end-1c')
            container = self.transport_manager.from_transport(transport)

            # Show original format
            self.input_text.delete('1.0', tk.END)
            self.input_text.insert('1.0', self.parser_manager.dump_container(container))
            self._update_status("Converted from transport format")

        except Exception as e:
            self._update_status(f"Transport error: {str(e)}")

    def run(self):
        """Start the demo"""
        self.root.mainloop()


if __name__ == "__main__":
    demo = FlexTagDemo()
    demo.run()
