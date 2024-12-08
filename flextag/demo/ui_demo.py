from tkinter import ttk
import tkinter as tk
import json

from flextag.managers.data import DataManager
from flextag.managers.query import QueryManager
from flextag.core.parser.provider import ParserProvider
from flextag.core.query.provider import QueryProvider


class FlexTagDemo:
    """Demo UI for FlexTag with complex metadata examples"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FlexTag Demo")
        self.root.geometry("1200x800")

        # Initialize managers
        self._setup_managers()
        self._setup_ui()
        self._load_sample()

    def _setup_managers(self):
        """Initialize and configure managers"""
        self.data_manager = DataManager()
        self.query_manager = QueryManager()

        parser_provider = ParserProvider()
        query_provider = QueryProvider()

        self.data_manager.register("parsers", "default", parser_provider)
        self.query_manager.register("query_parsers", "default", query_provider)

        self.data_manager.connect(self.query_manager)

    def _setup_ui(self):
        """Setup the UI components"""
        # Main container
        main = ttk.Frame(self.root, padding="5")
        main.pack(fill=tk.BOTH, expand=True)

        # Split pane: Input and Results
        paned = ttk.PanedWindow(main, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # Left side: Input with syntax help
        left_frame = ttk.Frame(paned)

        # Add syntax help
        help_frame = ttk.LabelFrame(left_frame, text="Query Syntax Help")
        help_text = """
Search Examples:
- Single tag: #action
- Multiple tags: #action AND #scifi
- Path search: .movies.scifi
- Multiple paths: .movies.scifi AND .favorites
- Parameters: rating = 5
- Combined: #action AND .movies.scifi AND rating = 5
"""
        help_label = ttk.Label(help_frame, text=help_text, justify=tk.LEFT)
        help_label.pack(fill=tk.X, padx=5, pady=5)
        help_frame.pack(fill=tk.X, padx=5, pady=5)

        # Input area
        input_frame = ttk.LabelFrame(left_frame, text="FlexTag Data")
        self.input_text = tk.Text(input_frame, wrap=tk.WORD)
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=5)

        # Right side: Results
        result_frame = ttk.LabelFrame(paned, text="Search Results")
        self.result_text = tk.Text(result_frame, wrap=tk.WORD, state="disabled")
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        paned.add(left_frame, weight=1)
        paned.add(result_frame, weight=1)

        # Controls
        controls = ttk.Frame(main)
        controls.pack(fill=tk.X, pady=5)

        # Search frame
        search_frame = ttk.LabelFrame(controls, text="Search")
        search_frame.pack(fill=tk.X, padx=5)

        ttk.Label(search_frame, text="Query:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.insert(0, "#scifi AND .movies.classics")

        ttk.Button(search_frame, text="Search",
                   command=self._search).pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status = tk.Text(main, height=2, wrap=tk.WORD)
        self.status.pack(fill=tk.X)
        self.status.config(state='disabled')

        # Bind events
        self.input_text.bind('<KeyRelease>', self._on_input_change)

    def _update_status(self, msg: str):
        """Update status text"""
        self.status.config(state='normal')
        self.status.delete('1.0', tk.END)
        self.status.insert('1.0', msg)
        self.status.config(state='disabled')

    def _display_result(self, data: dict):
        """Display formatted result"""
        self.result_text.config(state="normal")
        self.result_text.delete('1.0', tk.END)

        try:
            formatted = json.dumps(data, indent=2, default=str)
            self.result_text.insert('1.0', formatted)
        except Exception as e:
            self.result_text.insert('1.0', f"Error formatting result: {str(e)}")

        self.result_text.config(state="disabled")

    def _load_sample(self):
        """Load sample movie database example"""
        sample = """[[DATA:blade_runner #scifi #cyberpunk #classics .movies.scifi .movies.classics {"title": "Blade Runner", "year": 1982, "rating": 5}]]
A 1982 science fiction film directed by Ridley Scott, featuring Harrison Ford as Rick Deckard.
[[/DATA]]

[[DATA:matrix #scifi #action #cyberpunk .movies.scifi .movies.action .favorites {"title": "The Matrix", "year": 1999, "rating": 5}]]
A 1999 science fiction action film directed by the Wachowskis, starring Keanu Reeves.
[[/DATA]]

[[DATA:inception #scifi #action #mindbend .movies.scifi .movies.action {"title": "Inception", "year": 2010, "rating": 5}]]
A 2010 science fiction action film directed by Christopher Nolan, featuring Leonardo DiCaprio.
[[/DATA]]

[[DATA:alien #scifi #horror .movies.scifi .movies.horror .movies.classics {"title": "Alien", "year": 1979, "rating": 5}]]
A 1979 science fiction horror film directed by Ridley Scott, featuring Sigourney Weaver.
[[/DATA]]

[[DATA:terminator #scifi #action #classics .movies.scifi .movies.action .movies.classics {"title": "The Terminator", "year": 1984, "rating": 5}]]
A 1984 science fiction film directed by James Cameron, featuring Arnold Schwarzenegger.
[[/DATA]]

[[DATA:star_wars #scifi #adventure .movies.scifi .movies.classics .favorites {"title": "Star Wars: A New Hope", "year": 1977, "rating": 5}]]
The original Star Wars film that started the epic saga, directed by George Lucas.
[[/DATA]]"""

        self.input_text.delete('1.0', tk.END)
        self.input_text.insert('1.0', sample)
        self._on_input_change(None)

    def _on_input_change(self, event):
        """Handle input changes"""
        try:
            content = self.input_text.get('1.0', 'end-1c')
            self.data_manager.parse_string(content)
            self._update_status("Parsed successfully")
        except Exception as e:
            self._update_status(f"Error: {str(e)}")

    def _search(self):
        """Execute search with current query"""
        try:
            query = self.search_entry.get()
            results = self.query_manager.search(query)
            self._update_status(f"Found {len(results)} matches")
            self._display_result(results)
        except Exception as e:
            self._update_status(f"Search error: {str(e)}")

    def run(self):
        """Start the demo"""
        self.root.mainloop()


if __name__ == "__main__":
    demo = FlexTagDemo()
    demo.run()