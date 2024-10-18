"""Unit tests for the flextag module."""

import unittest
import json
from collections import OrderedDict

from flextag.flextag import flex_to_dict, dict_to_flex, flex_to_json, json_to_flex


class TestFlexTagParser(unittest.TestCase):
    """Test cases for the FlexTag parser functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.flex_tag_example = """[[-- ai text response
Here's a basic Python class that prints "Hello, World!"
--]]

[[-- ai code response
class HelloWorld:
    def __init__(self):
        self.message = "Hello, World!"

    def say_hello(self):
        print(self.message)

# Usage
hello = HelloWorld()
hello.say_hello()
--]]"""

        self.expected_dict = OrderedDict(
            [
                (
                    "ai text response",
                    'Here\'s a basic Python class that prints "Hello, World!"',
                ),
                (
                    "ai code response",
                    """class HelloWorld:
    def __init__(self):
        self.message = "Hello, World!"

    def say_hello(self):
        print(self.message)

# Usage
hello = HelloWorld()
hello.say_hello()""",
                ),
            ]
        )

    def test_parse_flex_tag_to_dict(self):
        """Test conversion from FlexTag to dictionary."""
        parsed_dict = flex_to_dict(self.flex_tag_example)
        self.assertEqual(parsed_dict, self.expected_dict)

    def test_parse_dict_to_flex_tag(self):
        """Test conversion from dictionary to FlexTag."""
        flex_tag_string = dict_to_flex(self.expected_dict)
        self.assertEqual(flex_tag_string.strip(), self.flex_tag_example.strip())

    def test_flex_to_json(self):
        """Test conversion from FlexTag to JSON."""
        json_string = flex_to_json(self.flex_tag_example)
        parsed_json = json.loads(json_string, object_pairs_hook=OrderedDict)
        self.assertEqual(parsed_json, self.expected_dict)

    def test_json_to_flex(self):
        """Test conversion from JSON to FlexTag."""
        json_string = json.dumps(self.expected_dict)
        flex_tag_string = json_to_flex(json_string)
        self.assertEqual(flex_tag_string.strip(), self.flex_tag_example.strip())


if __name__ == "__main__":
    unittest.main()
