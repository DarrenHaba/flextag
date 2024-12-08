from tkinter import ttk
import tkinter as tk
from typing import List, Set
import json

from flextag.managers.data import DataManager
from flextag.managers.query import QueryManager
from flextag.core.parser.provider import ParserProvider
from flextag.core.query.provider import QueryProvider

class FlexTagUI:
    """Enhanced FlexTag UI with interactive metadata filtering"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FlexTag")
        self.root.geometry("1200x800")

        # Initialize managers
        self._setup_managers()

        # Initialize state
        self.selected_tags: Set[str] = set()
        self.selected_paths: Set[str] = set()

        # Setup UI components
        self._setup_ui()
        self._setup_bindings()
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
        """Setup the main UI components"""
        # Main container
        main = ttk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True)

        # Create horizontal paned window for sidebar and content
        self.h_paned = ttk.PanedWindow(main, orient=tk.HORIZONTAL)
        self.h_paned.pack(fill=tk.BOTH, expand=True, pady=5)

        # Left sidebar for filters
        sidebar = ttk.Frame(self.h_paned)
        self._setup_sidebar(sidebar)

        # Main content area
        content = ttk.Frame(self.h_paned)
        self._setup_content(content)

        # Add to paned window with weights
        self.h_paned.add(sidebar, weight=1)
        self.h_paned.add(content, weight=3)

        # Status bar
        self.status = tk.Text(main, height=2, wrap=tk.WORD)
        self.status.pack(fill=tk.X, pady=(5,0))
        self.status.config(state='disabled')

    def _setup_sidebar(self, parent):
        """Setup the left sidebar with filtering sections"""
        # IDs Section
        id_frame = ttk.LabelFrame(parent, text="Block IDs", padding="5")
        id_frame.pack(fill=tk.X, padx=5, pady=(0,5))

        self.id_filter = ttk.Entry(id_frame)
        self.id_filter.pack(fill=tk.X, padx=5, pady=5)

        self.id_listbox = tk.Listbox(id_frame, height=10)
        self.id_listbox.pack(fill=tk.X, padx=5)

        # Tags Section
        tag_frame = ttk.LabelFrame(parent, text="Tags", padding="5")
        tag_frame.pack(fill=tk.X, padx=5, pady=5)

        self.tag_filter = ttk.Entry(tag_frame)
        self.tag_filter.pack(fill=tk.X, padx=5, pady=5)

        self.tag_listbox = tk.Listbox(tag_frame, height=10)
        self.tag_listbox.pack(fill=tk.X, padx=5)

        # Paths Section
        path_frame = ttk.LabelFrame(parent, text="Paths", padding="5")
        path_frame.pack(fill=tk.X, padx=5, pady=5)

        self.path_filter = ttk.Entry(path_frame)
        self.path_filter.pack(fill=tk.X, padx=5, pady=5)

        self.path_listbox = tk.Listbox(path_frame)
        self.path_listbox.pack(fill=tk.X, padx=5)

    def _setup_content(self, parent):
        """Setup the main content area"""
        # Search frame at top
        search_frame = ttk.Frame(parent, padding="5")
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="Query:").pack(side=tk.LEFT, padx=(0,5))

        self.query_var = tk.StringVar(value="*")  # Default to show all
        self.query_entry = ttk.Entry(search_frame, textvariable=self.query_var)
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))

        search_btn = ttk.Button(search_frame, text="Search", command=self._perform_search)
        search_btn.pack(side=tk.RIGHT)

        # FlexTag content
        content_frame = ttk.LabelFrame(parent, text="Results", padding="5")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.content_text = tk.Text(content_frame, wrap=tk.WORD)
        self.content_text.pack(fill=tk.BOTH, expand=True)

    def _setup_bindings(self):
        """Setup event bindings"""
        self.id_filter.bind('<KeyRelease>', lambda e: self._filter_items('id'))
        self.tag_filter.bind('<KeyRelease>', lambda e: self._filter_items('tag'))
        self.path_filter.bind('<KeyRelease>', lambda e: self._filter_items('path'))

        self.tag_listbox.bind('<Double-Button-1>', self._on_tag_select)
        self.path_listbox.bind('<Double-Button-1>', self._on_path_select)
        self.query_entry.bind('<Return>', lambda e: self._perform_search())

    def _update_status(self, msg: str):
        """Update status text"""
        self.status.config(state='normal')
        self.status.delete('1.0', tk.END)
        self.status.insert('1.0', msg)
        self.status.config(state='disabled')

    def _load_sample(self):
        """Load sample movie database"""
        sample = """[[DATA:blade_runner #scifi #cyberpunk #classics .movies.scifi .movies.classics {"title": "Blade Runner", "year": 1982, "rating": 5}]]
A 1982 science fiction film directed by Ridley Scott, featuring Harrison Ford as Rick Deckard.
[[/DATA]]

[[DATA:matrix #scifi #action #cyberpunk .movies.scifi .movies.action .favorites {"title": "The Matrix", "year": 1999, "rating": 5}]]
A 1999 science fiction action film directed by the Wachowskis, starring Keanu Reeves.
[[/DATA]]"""

        try:
            self.data_manager.parse_string(sample)
            self._update_status("Sample data loaded successfully")
            self._refresh_lists()
            self._perform_search()  # Show all results initially
        except Exception as e:
            self._update_status(f"Error loading sample: {str(e)}")

    def _refresh_lists(self):
        """Refresh all listboxes with current data"""
        self._filter_items('id')
        self._filter_items('tag')
        self._filter_items('path')

    def _filter_items(self, item_type: str):
        """Filter items in listboxes based on input"""
        filter_text = {
            'id': self.id_filter.get().lower(),
            'tag': self.tag_filter.get().lower(),
            'path': self.path_filter.get().lower()
        }[item_type]

        listbox = {
            'id': self.id_listbox,
            'tag': self.tag_listbox,
            'path': self.path_listbox
        }[item_type]

        # Clear and repopulate listbox
        listbox.delete(0, tk.END)

        # Get items from query manager's matrices
        items = []
        if item_type == 'id':
            items = list(set(self.query_manager.block_ids))[:10]  # Limit to 10 IDs
        elif item_type == 'tag':
            items = self.query_manager.unique_tags
        else:  # paths
            items = self.query_manager.unique_paths

        # Filter and add items
        for item in items:
            if item and filter_text in str(item).lower():
                listbox.insert(tk.END, item)

    def _on_tag_select(self, event):
        """Handle tag selection"""
        selection = self.tag_listbox.get(self.tag_listbox.curselection())
        if selection:
            self.selected_tags.add(selection)
            self._update_query()

    def _on_path_select(self, event):
        """Handle path selection"""
        selection = self.path_listbox.get(self.path_listbox.curselection())
        if selection:
            self.selected_paths.add(selection)
            self._update_query()

    def _update_query(self):
        """Update the query based on selections"""
        query_parts = []
        for tag in sorted(self.selected_tags):
            query_parts.append(f"#{tag}")
        for path in sorted(self.selected_paths):
            query_parts.append(f".{path}")

        if query_parts:
            self.query_var.set(' AND '.join(query_parts))
        else:
            self.query_var.set('*')  # Show all when no selections

        self._perform_search()

    def _perform_search(self):
        """Execute the search query"""
        query = self.query_var.get()
        try:
            results = self.query_manager.search(query)
            self.content_text.delete('1.0', tk.END)

            if results:
                formatted = json.dumps(results, indent=2)
                self.content_text.insert('1.0', formatted)
                self._update_status(f"Found {len(results)} matches")
            else:
                self.content_text.insert('1.0', "No results found")
                self._update_status("No matches found")

        except Exception as e:
            self._update_status(f"Search error: {str(e)}")

    def run(self):
        """Start the UI"""
        self.root.mainloop()

if __name__ == "__main__":
    demo = FlexTagUI()
    demo.run()