import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter import font as tkFont
from flextag import (
    FlexTagParser,
    TransportContainer,
    CompressionRegistry,
    factory
)
import json
import re

class FlexTagDemo:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FlexTag Technical Demo")
        self.root.geometry("1200x800")

        # Configure styles for dark mode
        self.style = ttk.Style()
        self.dark_mode = tk.BooleanVar(value=False)
        self.configure_colors()

        # Main container with notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self.setup_container_tab()
        self.setup_transport_tab()
        self.setup_query_tab()

        # Initial content
        self.load_sample_content()

    def setup_container_tab(self):
        """Setup the Data Container tab"""
        container_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(container_frame, text="Data Container")

        # Top controls
        controls = ttk.Frame(container_frame)
        controls.pack(fill=tk.X, pady=(0, 10))

        # Search frame
        search_frame = ttk.Frame(controls)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.search_var = tk.StringVar()
        ttk.Label(search_frame, text="Query:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(search_frame, text="Search", command=self.execute_query).pack(side=tk.LEFT)

        # Dark mode toggle
        ttk.Checkbutton(
            controls, text="Dark Mode",
            variable=self.dark_mode,
            command=self.toggle_theme
        ).pack(side=tk.RIGHT)

        # Content area
        content_frame = ttk.Frame(container_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Split view for container
        self.paned = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Left side - FlexTag content
        left_frame = ttk.Frame(self.paned)
        self.content_text = scrolledtext.ScrolledText(left_frame, wrap=tk.NONE)
        self.content_text.pack(fill=tk.BOTH, expand=True)
        self.paned.add(left_frame, weight=1)

        # Right side - Parsed view
        right_frame = ttk.Frame(self.paned)
        self.parsed_text = scrolledtext.ScrolledText(right_frame, wrap=tk.NONE)
        self.parsed_text.pack(fill=tk.BOTH, expand=True)
        self.paned.add(right_frame, weight=1)

        # Configure syntax highlighting
        self._setup_tags()

    def setup_transport_tab(self):
        """Setup the Transport Container tab"""
        transport_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(transport_frame, text="Transport Container")

        # Controls
        controls = ttk.Frame(transport_frame)
        controls.pack(fill=tk.X, pady=(0, 10))

        # Compression options
        ttk.Label(controls, text="Compression:").pack(side=tk.LEFT, padx=(0, 5))
        self.compression_var = tk.StringVar(value="none")
        comp_menu = ttk.OptionMenu(
            controls,
            self.compression_var,
            "none",
            "none", "gzip", "zip",
            command=self.update_transport
        )
        comp_menu.pack(side=tk.LEFT, padx=(0, 10))

        # Transport container view
        self.transport_text = scrolledtext.ScrolledText(transport_frame, height=10)
        self.transport_text.pack(fill=tk.BOTH, expand=True)

    def setup_query_tab(self):
        """Setup the Query Examples tab"""
        query_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(query_frame, text="Query Examples")

        # Example queries with descriptions
        examples = [
            ("Find by ID", ":config", "Find section with ID 'config'"),
            ("Find by tag", "#action", "Find sections with tag 'action'"),
            ("Find by path", ".movies", "Find sections under 'movies' path"),
            ("Combined search", "#action AND .movies", "Find action movies"),
            ("Rating filter", "rating>8.5", "Find high-rated content"),
            ("Complex query", "#scifi AND NOT .shows", "Find sci-fi movies (not shows)")
        ]

        for title, query, desc in examples:
            example_frame = ttk.LabelFrame(query_frame, text=title, padding="5")
            example_frame.pack(fill=tk.X, pady=5)

            ttk.Label(example_frame, text=desc).pack(anchor=tk.W)
            query_text = scrolledtext.ScrolledText(example_frame, height=2)
            query_text.insert("1.0", query)
            query_text.pack(fill=tk.X)
            ttk.Button(
                example_frame,
                text="Try Query",
                command=lambda q=query: self.try_query(q)
            ).pack(anchor=tk.E)

    def try_query(self, query):
        """Execute an example query"""
        self.search_var.set(query)
        self.notebook.select(0)  # Switch to container tab
        self.execute_query()

    def execute_query(self):
        """Execute the current query"""
        query = self.search_var.get().strip()
        parser = factory.create_parser()
        container = parser.parse(self.content_text.get("1.0", tk.END))

        try:
            if query:
                results = container.search(query)
                # Show results in parsed view
                self.parsed_text.delete("1.0", tk.END)
                for section in results:
                    self.parsed_text.insert(tk.END,
                                            f"Section ID: {section.id}\n"
                                            f"Tags: {section.tags}\n"
                                            f"Paths: {section.paths}\n"
                                            f"Content:\n{json.dumps(section.content, indent=2)}\n"
                                            f"{'='*40}\n\n"
                                            )
        except Exception as e:
            self.parsed_text.delete("1.0", tk.END)
            self.parsed_text.insert(tk.END, f"Error executing query: {str(e)}")

    def update_transport(self, *args):
        """Update transport container view"""
        try:
            parser = factory.create_parser()
            container = parser.parse(self.content_text.get("1.0", tk.END))

            transport = TransportContainer()
            if self.compression_var.get() != "none":
                transport.metadata["compression"] = self.compression_var.get()

            encoded = transport.encode(container)

            # Show transport container
            self.transport_text.delete("1.0", tk.END)
            self.transport_text.insert(tk.END,
                                       f"Metadata:\n{json.dumps(transport.metadata, indent=2)}\n\n"
                                       f"Encoded Data (truncated):\n{encoded[:100]}...\n\n"
                                       f"Total Size: {len(encoded)} bytes"
                                       )

        except Exception as e:
            self.transport_text.delete("1.0", tk.END)
            self.transport_text.insert(tk.END, f"Error creating transport container: {str(e)}")

    def configure_colors(self):
        """Configure color scheme based on theme"""
        if self.dark_mode.get():
            self.colors = {
                "bg": "#282828",
                "fg": "#ffffff",
                "section": "#bb86fc",    # Purple
                "tag": "#ff7597",        # Pink
                "path": "#78dce8",       # Light Blue
                "param": "#a9dc76",      # Light Green
                "content": "#cccccc",    # Light Gray
            }
        else:
            self.colors = {
                "bg": "#ffffff",
                "fg": "#000000",
                "section": "#4B0082",    # Indigo
                "tag": "#8B4513",        # Saddle Brown
                "path": "#2F4F4F",       # Dark Slate Gray
                "param": "#006400",      # Dark Green
                "content": "#000000",    # Black
            }

    def _setup_tags(self):
        """Configure syntax highlighting"""
        for tag, color in self.colors.items():
            if tag not in ["bg", "fg"]:
                self.content_text.tag_configure(tag, foreground=color)

    def highlight_syntax(self):
        """Apply syntax highlighting"""
        content = self.content_text.get("1.0", tk.END)

        # Clear existing tags
        for tag in ["section", "tag", "path", "param", "content"]:
            self.content_text.tag_remove(tag, "1.0", tk.END)

        # Highlight syntax
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            # Section markers
            if "[[" in line and "]]" in line:
                start = line.find("[[")
                end = line.find("]]") + 2
                self.content_text.tag_add("section", f"{i}.{start}", f"{i}.{end}")

                # Tags and paths within section
                if "[[SEC" in line:
                    for match in re.finditer(r"#\w+", line):
                        self.content_text.tag_add("tag",
                                                  f"{i}.{match.start()}", f"{i}.{match.end()}")
                    for match in re.finditer(r"\.\w+(?:\.\w+)*", line):
                        self.content_text.tag_add("path",
                                                  f"{i}.{match.start()}", f"{i}.{match.end()}")
                    # Parameters
                    for match in re.finditer(r"\w+=(?:\"[^\"]*\"|[^ \]]*)", line):
                        self.content_text.tag_add("param",
                                                  f"{i}.{match.start()}", f"{i}.{match.end()}")

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.configure_colors()
        self._setup_tags()

        bg = self.colors["bg"]
        fg = self.colors["fg"]

        for widget in [self.content_text, self.parsed_text, self.transport_text]:
            widget.configure(bg=bg, fg=fg, insertbackground=fg)

        self.highlight_syntax()

    def load_sample_content(self):
        """Load sample content"""
        sample = """[[PARAMS fmt="yaml" enc="utf-8"]]
[[META title="Entertainment Database" version="1.0" #database .entertainment]]

[[SEC:movies #movies .content.movies fmt="json"]]
{
    "items": [
        {
            "title": "The Matrix",
            "year": 1999,
            "genre": ["action", "sci-fi"],
            "rating": 9.0
        },
        {
            "title": "Inception",
            "year": 2010,
            "genre": ["action", "sci-fi"],
            "rating": 8.8
        }
    ]
}
[[/SEC]]

[[SEC:shows #shows .content.shows fmt="yaml"]]
series:
  - title: "Breaking Bad"
    years: "2008-2013"
    genre: ["drama", "crime"]
    rating: 9.5
  - title: "The Wire"
    years: "2002-2008"
    genre: ["drama", "crime"]
    rating: 9.3
[[/SEC]]
"""
        self.content_text.delete("1.0", tk.END)
        self.content_text.insert("1.0", sample)
        self.highlight_syntax()
        self.execute_query()
        self.update_transport()

    def run(self):
        """Start the demo application"""
        self.root.mainloop()

if __name__ == "__main__":
    demo = FlexTagDemo()
    demo.run()