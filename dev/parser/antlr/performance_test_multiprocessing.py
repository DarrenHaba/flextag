import time
from concurrent.futures import ProcessPoolExecutor

from antlr4 import CommonTokenStream, InputStream, ParseTreeWalker
from FlexTagLexer import FlexTagLexer
from FlexTagParser import FlexTagParser
from FlexTagListener import FlexTagListener
from flextag.core.parsers.antlr.performance_test import generate_test_data


# Define a listener without print statements
class PerformanceFlexTagListener(FlexTagListener):
    def enterContent(self, ctx):
        # Handle content (no prints)
        for line in ctx.contentLine():
            line.TEXT()  # Process content if needed

    def enterFullTag(self, ctx):
        # Handle full tags (no prints)
        pass

    def enterSelfClosingTag(self, ctx):
        # Handle self-closing tags (no prints)
        pass


# Parsing function using the performance listener
def parse_flex_tag(input_text):
    input_stream = InputStream(input_text)
    lexer = FlexTagLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = FlexTagParser(stream)
    tree = parser.document()
    listener = PerformanceFlexTagListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)


# Template for FlexTag blocks
template = """
[[DATA:id, #tag, .path, {"key":"value"}]]
content here
[[/DATA]]
"""

# Generate the test string with repeated blocks
from concurrent.futures import ProcessPoolExecutor
import time


# Generate multiple test strings
def generate_test_files(template, count, num_files):
    files = []
    blocks_per_file = count // num_files
    for _ in range(num_files):
        files.append(generate_test_data(template, blocks_per_file))
    return files


# Function to parse a single file (or string)
def parse_file(file_data):
    parse_flex_tag(file_data)


# Performance test with multiple files
def performance_test_multiple_files(template, repetitions, num_files, num_workers):
    test_files = generate_test_files(template, repetitions, num_files)

    start_time = time.time()
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        executor.map(parse_file, test_files)
    end_time = time.time()

    elapsed_time = end_time - start_time
    print(
        f"Parsing {repetitions} blocks across {num_files} files with {num_workers} workers took {elapsed_time:.4f} seconds."
    )
    return elapsed_time


if __name__ == "__main__":
    # Adjust repetitions, number of files, and workers as needed
    performance_test_multiple_files(template, 1000000, 36, 36)  # 4 files, 4 workers
