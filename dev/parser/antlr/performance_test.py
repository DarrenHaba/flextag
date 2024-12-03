import time
from antlr4 import CommonTokenStream, InputStream, ParseTreeWalker
from FlexTagLexer import FlexTagLexer
from FlexTagParser import FlexTagParser
from FlexTagListener import FlexTagListener


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
# [[DATA{"id":"id", "tags":"tag", "paths":"path", "key":"value"}]]
# content here
# [[/DATA]]
template = """
[[DATA:id, #tag, .path, {"key":"value"}]]
content here
[[/DATA]]
"""


# Generate the test string with repeated blocks
def generate_test_data(template, count):
    return "\n\n".join(template.strip() for _ in range(count))


# Performance test
def performance_test(template, repetitions):
    test_data = generate_test_data(template, repetitions)
    start_time = time.time()
    try:
        parse_flex_tag(test_data)
    except Exception as e:
        print(f"Error during parsing: {e}")
    end_time = time.time()
    print(f"Parsing {repetitions} blocks took {end_time - start_time:.4f} seconds.")


# Run the performance test
if __name__ == "__main__":
    performance_test(template, 100000)  # Adjust repetitions as needed
