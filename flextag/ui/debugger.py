# flextag/ui/debugger.py
import tkinter as tk
from tkinter import ttk
import json
from typing import Optional, Dict, Any

from flextag import logger
from flextag.core.parser import Parser, ParserState
from flextag.settings import Const
from flextag.exceptions import FlexTagError


class FlexTagDebugger:
    def __init__(self):
        logger.info("Initializing FlexTag Debugger")
        self.root = tk.Tk()
        self.root.title("FlexTag Debugger")
        self.root.geometry("800x600")

        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Button frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.to_transport_btn = ttk.Button(
            self.button_frame, text="To Transport", command=self.convert_to_transport
        )
        self.to_transport_btn.pack(side=tk.LEFT, padx=5)

        self.from_transport_btn = ttk.Button(
            self.button_frame,
            text="From Transport",
            command=self.convert_from_transport,
        )
        self.from_transport_btn.pack(side=tk.LEFT, padx=5)

        # Create paned window for input/structure
        self.paned_main = ttk.PanedWindow(self.main_frame, orient=tk.VERTICAL)
        self.paned_main.pack(fill=tk.BOTH, expand=True)

        # Input area
        self.input_frame = ttk.LabelFrame(self.paned_main, text="Input")
        input_scroll = ttk.Scrollbar(self.input_frame)
        input_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.input_text = tk.Text(self.input_frame, yscrollcommand=input_scroll.set)
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        input_scroll.config(command=self.input_text.yview)

        # Structure area
        self.struct_frame = ttk.LabelFrame(self.paned_main, text="Structure")
        struct_scroll = ttk.Scrollbar(self.struct_frame)
        struct_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.struct_text = tk.Text(
            self.struct_frame,
            height=10,
            state="disabled",
            yscrollcommand=struct_scroll.set,
        )
        self.struct_text.pack(fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        struct_scroll.config(command=self.struct_text.yview)

        # Message area (fixed height)
        self.error_frame = ttk.LabelFrame(self.main_frame, text="Messages")
        self.error_frame.pack(fill=tk.BOTH, pady=(5, 0))

        error_scroll = ttk.Scrollbar(self.error_frame)
        error_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.error_text = tk.Text(
            self.error_frame, height=6, yscrollcommand=error_scroll.set
        )
        self.error_text.pack(fill=tk.BOTH, padx=(5, 0), pady=5)
        error_scroll.config(command=self.error_text.yview)

        # Add frames to paned window
        self.paned_main.add(self.input_frame, weight=3)
        self.paned_main.add(self.struct_frame, weight=2)

        # Set up syntax highlighting tags
        self._setup_tags()

        # Bind events
        self.input_text.bind("<KeyRelease>", self.on_text_change)

        # Add sample content and trigger initial update
        self.input_text.insert("1.0", self._get_sample_content())
        logger.debug("Added sample content")

        # Trigger initial parsing
        self.root.after(100, self.update_all)

    def _setup_tags(self):
        """Configure syntax highlighting tags using colors from Const"""
        logger.debug("Setting up syntax highlighting tags")
        for tag, color in Const.COLORS.items():
            self.input_text.tag_configure(tag, foreground=color)

    def update_all(self):
        """Update both syntax highlighting and structure"""
        logger.debug("Updating all UI elements")
        self.highlight_syntax()
        self.show_structure()

    def highlight_syntax(self):
        """Highlight syntax using the parser"""
        content = self.input_text.get("1.0", "end-1c")
        logger.debug("Starting syntax highlighting")

        # Clear existing tags
        for tag in Const.COLORS.keys():
            self.input_text.tag_remove(tag, "1.0", "end")

        try:
            current_pos = "1.0"
            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                logger.debug(f"Processing line {line_num}: {line[:20]}...")

                # Block markers
                if Const.BLOCK_START in line:
                    start_idx = line.find(Const.BLOCK_START)
                    end_idx = start_idx + len(Const.BLOCK_START)
                    logger.debug(f"Found block start at column {start_idx}")
                    self.input_text.tag_add(
                        "block_marker",
                        f"{line_num}.{start_idx}",
                        f"{line_num}.{end_idx}",
                    )

                if Const.BLOCK_END in line:
                    start_idx = line.find(Const.BLOCK_END)
                    end_idx = start_idx + len(Const.BLOCK_END)
                    logger.debug(f"Found block end at column {start_idx}")
                    self.input_text.tag_add(
                        "block_marker",
                        f"{line_num}.{start_idx}",
                        f"{line_num}.{end_idx}",
                    )

                # Item markers
                if Const.ITEM_START in line:
                    start_idx = line.find(Const.ITEM_START)
                    end_idx = start_idx + len(Const.ITEM_START)
                    logger.debug(f"Found item start at column {start_idx}")
                    self.input_text.tag_add(
                        "item_marker",
                        f"{line_num}.{start_idx}",
                        f"{line_num}.{end_idx}",
                    )

                if Const.ITEM_END in line:
                    start_idx = line.find(Const.ITEM_END)
                    end_idx = start_idx + len(Const.ITEM_END)
                    logger.debug(f"Found item end at column {start_idx}")
                    self.input_text.tag_add(
                        "item_marker",
                        f"{line_num}.{start_idx}",
                        f"{line_num}.{end_idx}",
                    )

                # Parameters
                param_start = line.find("[")
                while param_start != -1:
                    param_end = line.find("]", param_start)
                    if param_end != -1:
                        key_end = param_start
                        key_start = line.rfind(" ", 0, param_start)
                        if key_start == -1:
                            key_start = 0
                        else:
                            key_start += 1

                        logger.debug(f"Found parameter key at {key_start}-{key_end}")
                        logger.debug(
                            f"Found parameter value at {param_start+1}-{param_end}"
                        )

                        # Highlight key
                        self.input_text.tag_add(
                            "param_key",
                            f"{line_num}.{key_start}",
                            f"{line_num}.{key_end}",
                        )
                        # Highlight value
                        self.input_text.tag_add(
                            "param_value",
                            f"{line_num}.{param_start+1}",
                            f"{line_num}.{param_end}",
                        )

                    param_start = line.find("[", param_end + 1)

                # Comments
                if Const.COMMENT_START in line:
                    start_idx = line.find(Const.COMMENT_START)
                    end_idx = line.find(Const.COMMENT_END)
                    if end_idx != -1:
                        logger.debug(f"Found comment at {start_idx}-{end_idx}")
                        self.input_text.tag_add(
                            "comment",
                            f"{line_num}.{start_idx}",
                            f"{line_num}.{end_idx + len(Const.COMMENT_END)}",
                        )

            logger.debug("Syntax highlighting complete")

        except Exception as e:
            logger.error(f"Error during syntax highlighting: {str(e)}")
            self.show_error(f"Highlighting error: {str(e)}")

    def show_structure(self):
        """Show parsed structure"""
        content = self.input_text.get("1.0", "end-1c")

        try:
            parser = Parser(content)
            blocks = parser.parse()

            # More detailed and correctly formatted structure
            readable = []
            for block in blocks:
                block_info = {
                    "refs": block["refs"],
                    "params": {k: v for k, v in block["params"].items() if k != "refs"},
                    "items": [
                        {
                            "refs": item["refs"],
                            "params": {
                                k: v for k, v in item["params"].items() if k != "refs"
                            },
                            "content": (
                                item["content"]
                                if isinstance(item["content"], str)
                                else "".join(item["content"])
                            ),  # Join if it's a list of chars
                        }
                        for item in block["items"]
                    ],
                    "comments": block["comments"],
                }
                readable.append(block_info)

            self.struct_text.config(state="normal")
            self.struct_text.delete("1.0", "end")
            self.struct_text.insert("1.0", json.dumps(readable, indent=2))
            self.struct_text.config(state="disabled")

            logger.debug(f"Updated structure view with {len(blocks)} blocks")
            self.show_error("")

        except FlexTagError as e:
            logger.error(f"Parser error: {str(e)}")
            self.show_error(str(e))

    def show_error(self, message: str):
        """Show error message"""
        self.error_text.config(state="normal")
        self.error_text.delete("1.0", "end")
        self.error_text.insert("1.0", message)
        self.error_text.config(state="disabled")

    def on_text_change(self, event):
        """Handle text changes"""
        self.highlight_syntax()
        self.show_structure()

    def convert_to_transport(self):
        """Convert content to transport format"""
        # TODO: Implement conversion to transport format
        pass

    def convert_from_transport(self):
        """Convert content from transport format"""
        # TODO: Implement conversion from transport format
        pass

    def _get_sample_content(self) -> str:
        """Return sample FlexTag content"""
        return """<<--FT_BLOCK refs[config.dev]-->>
<<-- refs[database, sql]:
{
    "host": "localhost",
    "port": 5432
}
-->>

<<--# Configuration for development #-->>
<<-- refs[api.endpoint]:https://api.dev.example.com-->>
<<--FT_BLOCK-->>"""

    def run(self):
        """Start the debugger"""
        self.root.mainloop()


if __name__ == "__main__":
    debugger = FlexTagDebugger()
    debugger.run()
