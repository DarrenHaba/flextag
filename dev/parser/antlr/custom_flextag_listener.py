from antlr4 import CommonTokenStream, InputStream, ParseTreeWalker
from FlexTagLexer import FlexTagLexer
from FlexTagParser import FlexTagParser
from FlexTagListener import FlexTagListener


class CustomFlexTagListener(FlexTagListener):
    def enterContent(self, ctx):
        # Handle content - now properly handling multiple lines
        for line in ctx.contentLine():
            print(f"Content: {line.TEXT()}")

    def enterFullTag(self, ctx):
        # Handle full tags
        print(f"Full tag found")

    def enterSelfClosingTag(self, ctx):
        # Handle self-closing tags
        print(f"Self-closing tag found")


def parse_flex_tag(input_text):
    # Create an input stream
    input_stream = InputStream(input_text)

    # Create a lexer
    lexer = FlexTagLexer(input_stream)

    # Create a token stream
    stream = CommonTokenStream(lexer)

    # Create a parser
    parser = FlexTagParser(stream)

    # Get the parse tree
    tree = parser.document()

    # Create and attach our listener
    listener = CustomFlexTagListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)


# Test the parser
if __name__ == "__main__":
    test_input = """[[DATA:id, #tag, {"key": "value"}/]]

[[DATA:id]]
content here, OMG!!
and HERE???
[[/DATA]]"""

    try:
        parse_flex_tag(test_input)
    except Exception as e:
        print(f"Error parsing: {e}")
