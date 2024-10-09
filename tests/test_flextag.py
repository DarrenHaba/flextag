import unittest

from flextag.flextag import flex_to_dict, dict_to_flex


class TestFlexTagParser(unittest.TestCase):
    def setUp(self):
        self.flex_tag_example = """
        [[---- ai text response --
        Here’s a basic Python class that prints "Hello, World!"
        --]]

        [[---- ai code response --
        class HelloWorld:
            def __init__(self):
                self.message = "Hello, World!"

            def say_hello(self):
                print(self.message)

        # Usage
        hello = HelloWorld()
        hello.say_hello()
        --]]
        """

        self.expected_dict = {
            "ai text response": "Here’s a basic Python class that prints"
            ' "Hello, World!"',
            "ai code response": "class HelloWorld:\ndef __init__(self):\n"
            'self.message = "Hello, World!"\n\n'
            "def say_hello(self):\nprint(self.message)"
            "\n\n# Usage\nhello = HelloWorld()\nhello."
            "say_hello()",
        }

        self.expected_flex_tag = """
[[---- ai text response --
Here’s a basic Python class that prints "Hello, World!"
--]]
[[---- ai code response --
class HelloWorld:
def __init__(self):
self.message = "Hello, World!"

def say_hello(self):
print(self.message)

# Usage
hello = HelloWorld()
hello.say_hello()
--]]
""".strip()

    def test_parse_flex_tag_to_dict(self):
        parsed_dict = flex_to_dict(self.flex_tag_example)
        self.assertEqual(parsed_dict, self.expected_dict)

    def test_parse_dict_to_flex_tag(self):
        flex_tag_string = dict_to_flex(self.expected_dict)
        self.assertEqual(flex_tag_string.strip(), self.expected_flex_tag)


# Run the unit tests
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestFlexTagParser)
)
