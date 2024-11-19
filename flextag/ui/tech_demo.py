import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
from flextag import FlexTagParser
import re


class FlexTagDemo:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FlexTag Demo")
        self.root.geometry("800x600")

        # Configure styles for dark mode
        self.style = ttk.Style()
        self.dark_mode = tk.BooleanVar(value=False)
        self.configure_colors()

        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Top frame for search and theme toggle
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        # Search frame
        self.search_frame = ttk.Frame(top_frame)
        self.search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.search_var = tk.StringVar()

        ttk.Label(self.search_frame, text="Filter:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry = ttk.Entry(
            self.search_frame, textvariable=self.search_var, width=40
        )
        self.search_entry.pack(side=tk.LEFT, padx=(0, 5))

        self.search_button = ttk.Button(
            self.search_frame, text="Search", command=self.update_content
        )
        self.search_button.pack(side=tk.LEFT)

        # Dark mode toggle
        ttk.Checkbutton(
            top_frame,
            text="Dark Mode",
            variable=self.dark_mode,
            command=self.toggle_theme,
        ).pack(side=tk.RIGHT)

        # Font size slider
        self.font_size = tk.IntVar(value=12)  # Default font size
        font_slider = ttk.Scale(
            self.main_frame,
            from_=8,
            to=24,
            variable=self.font_size,
            orient=tk.HORIZONTAL,
            command=lambda e: self.update_font_size(self.font_size.get()),
        )
        font_slider.pack(fill=tk.X, pady=(5, 10))

        # Content area
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(content_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Text widget for content
        self.content_text = tk.Text(
            content_frame, wrap=tk.NONE, yscrollcommand=scrollbar.set
        )
        self.content_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.content_text.yview)

        # Configure syntax highlighting tags
        self._setup_tags()

        # Load sample content
        self.all_content = self._get_sample_content()
        self.update_content()

        # Bind enter key to search
        self.search_entry.bind("<Return>", lambda e: self.update_content())

        # Initial font configuration
        self.update_font_size(self.font_size.get())

    def configure_colors(self):
        """Configure color scheme based on theme"""
        if self.dark_mode.get():
            self.colors = {
                "bg": "#282828",
                "fg": "#ffffff",
                "section_marker": "#bb86fc",  # Purple
                "tag": "#ff7597",  # Pink
                "path": "#78dce8",  # Light Blue
                "content": "#cccccc",  # Light Gray
            }
        else:
            self.colors = {
                "bg": "#ffffff",
                "fg": "#000000",
                "section_marker": "#4B0082",  # Indigo
                "tag": "#8B4513",  # Saddle Brown
                "path": "#2F4F4F",  # Dark Slate Gray
                "content": "#000000",  # Black
            }

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.configure_colors()
        self._setup_tags()

        bg = self.colors["bg"]
        fg = self.colors["fg"]

        self.content_text.configure(bg=bg, fg=fg, insertbackground=fg)
        self.highlight_syntax()

    def _setup_tags(self):
        """Configure syntax highlighting colors"""
        for tag, color in self.colors.items():
            if tag not in ["bg", "fg"]:
                self.content_text.tag_configure(tag, foreground=color)

    def highlight_syntax(self):
        """Apply syntax highlighting to visible content"""
        content = self.content_text.get("1.0", tk.END)

        # Clear existing tags
        for tag in ["section_marker", "tag", "path", "content"]:
            self.content_text.tag_remove(tag, "1.0", tk.END)

        # Highlight section markers
        for match in re.finditer(r"\[\[SEC(?:\s+[^\]]+)?\]\]|\[\[/SEC\]\]", content):
            start = match.start()
            end = match.end()
            self.content_text.tag_add("section_marker", f"1.0+{start}c", f"1.0+{end}c")

        # Highlight tags and paths
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            if "[[SEC" in line:
                # Highlight tags
                for match in re.finditer(r"#\w+", line):
                    start = match.start()
                    end = match.end()
                    self.content_text.tag_add("tag", f"{i}.{start}", f"{i}.{end}")

                # Highlight paths
                for match in re.finditer(r"\.\w+(?:\.\w+)*", line):
                    start = match.start()
                    end = match.end()
                    self.content_text.tag_add("path", f"{i}.{start}", f"{i}.{end}")

    def update_font_size(self, size):
        """Update the font size of the text widget"""
        custom_font = tkFont.Font(family="Helvetica", size=int(size))
        self.content_text.configure(font=custom_font)

    def update_content(self, *args):
        """Update displayed content based on search"""
        search_text = self.search_var.get().strip()

        # Enable text widget for editing
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete("1.0", tk.END)

        # Filter sections based on search
        if not search_text:
            filtered_content = self.all_content
        else:
            parser = FlexTagParser()
            doc = parser.parse(self.all_content)
            matches = doc.find(search_text)

            # Reconstruct matching sections
            filtered_content = ""
            for section in matches:
                filtered_content += (
                    f"[[SEC #{' #'.join(section.tags)} .{' .'.join(section.paths)}]]\n"
                )
                filtered_content += f"{section.content}\n"
                filtered_content += "[[/SEC]]\n\n"

        # Update content and highlighting
        self.content_text.insert("1.0", filtered_content)
        self.highlight_syntax()

    def _get_sample_content(self) -> str:
        """Return sample movie and TV show content"""
        return """[[SEC #action #scifi .movies.franchise]]
Title: The Matrix
Year: 1999
Rating: 9.0
Description: A computer programmer discovers a dystopian reality.
[[/SEC]]

[[SEC #drama #classic .shows.classics]]
Title: The Twilight Zone
Seasons: 5
Years: 1959-1964
Rating: 9.0
Description: Anthology series exploring the supernatural and unexpected.
[[/SEC]]

[[SEC #scifi #adventure .movies.franchise]]
Title: Star Wars: A New Hope
Year: 1977
Rating: 8.6
Description: A young farm boy joins a galactic rebellion.
[[/SEC]]

[[SEC #comedy #sitcom .shows.classics]]
Title: I Love Lucy
Seasons: 6
Years: 1951-1957
Rating: 8.5
Description: The misadventures of a wacky redhead and her bandleader husband.
[[/SEC]]

[[SEC #thriller #mystery .movies.award]]
Title: The Silence of the Lambs
Year: 1991
Rating: 8.6
Description: An FBI cadet must receive help from an incarcerated killer.
[[/SEC]]

[[SEC #drama #crime .shows.modern]]
Title: Breaking Bad
Seasons: 5
Years: 2008-2013
Rating: 9.5
Description: A high school chemistry teacher turns to a life of crime.
[[/SEC]]"""

    def run(self):
        """Start the demo application"""
        self.root.mainloop()


if __name__ == "__main__":
    demo = FlexTagDemo()
    demo.run()
