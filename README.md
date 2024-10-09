
# Flex Tag System Standards

**Flex Tag** is designed to be a flexible yet unique tagging system, using opening and closing tags that are distinct from any other tags used in common scripting or programming languages. This ensures that Flex Tag's tags are never confused with language-specific syntax, preventing interference when AI generates code.

Flex Tag enables AI to code in any language and format while using this distinct tagging system to clearly separate content from code. One important note is that AI should generally avoid generating code using Flex Tag syntax itself, as it could create conflicts. In the future, the ` ```flextag ` format will be introduced to allow Flex Tag sections to be ignored within the AI's output, providing further flexibility.

---

## 1. Tag Names
- Tags should be written in **lowercase**, with **spaces encouraged** for simplicity (e.g., `ai text response`, `ai code response`).
- The system is **case-insensitive**, meaning tags like `[[---- ai text response --` and `[[---- AI text response --` are treated the same.
- **Spaces**, **underscores**, and **dashes** are allowed within tag names, but **spaces are preferred** for readability.

## 2. Tag Structure
- **Opening tags** follow the format `[[---- tag name --` and must appear on a new line.
- **Closing tags** follow the format `--]]` and must also appear on a new line.
- Both opening and closing tags must be **the only content on their respective lines** to ensure proper parsing.

## 3. Multi-Language Support
- Flex Tag is designed for use across multiple programming languages, allowing developers to write tags in a way that best fits their language and style.
- Flexibility ensures that Flex Tag can be used without conflicting with existing language syntax.

---

## Example of AI Response to a Python Class Request

In this example, a user asks the AI to write a Python class that prints "Hello, World!" The AI responds with both a brief textual explanation and the corresponding Python code.

### AI Response

```flextag
[[---- ai text response --
[[---- body --
Here’s a basic Python class that prints "Hello, World!"
--]]
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
```
