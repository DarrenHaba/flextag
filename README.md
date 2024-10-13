# Flex Tag

**A streamlined solution for handling complex AI responses**

When working with Large Language Models (LLMs), developers often face a challenge: how to receive multiple pieces of information in a structured way. LLMs typically respond best to single prompts, but real-world applications often require more context, such as handling code, file locations, and descriptions all in one response. Flex Tag solves this problem by offering a consistent tagging system that lets you receive structured responses containing multiple sections—like text, code, or file references—all parsed into a clean, usable format.

---

### Why Use Flex Tag?

Flex Tag gives you a simple, reliable way to interact with LLMs across different use cases. Whether you need multiple responses in one request or want to ensure the response is split into distinct sections, Flex Tag makes it easy. It converts AI responses into structured Python dictionaries, so you can quickly access and utilize each part of the response—whether it's code, instructions, or references. The tags give you control, making AI interactions more predictable and structured, eliminating the hassle of handling mixed-content responses manually.



### Quick Start

#### 1. **Installation**

To install Flex Tag, use the following command:

```bash
pip install flextag
```

#### 2. **How to Use Flex Tag with an LLM**

When working with LLMs, you can instruct the AI to respond with specific tags that you define. These tags can be customized for your needs. For instance, in this case, we use:
- `text` to describe the code or explain the response.
- `code` to contain the actual code.

This prompt can be sent as the first message in an API request or it can be used directly in a ChatGPT-like interface **for demo purposes**. The primary purpose of Flex Tag is to facilitate interactions when using an API to communicate with LLMs.

Simply paste the prompt below, and you should receive a response formatted in Flex Tag, as shown in the example below.

**Here is the sample prompt to send to the LLM**:

```
Please respond in Flex Tag format.

Flex Tag is a system where different sections of content are separated using custom tags. The format is as follows:

- Tags are written in lowercase.
- Opening tags start with `[[---- `followed by the tag name and end with` --`.
- Closing tags start with `--]]`.

Please respond in Flex Tag format and ensure you use ```flextag``` to enclose the response.

Please use the following tags:
- `text` for text responses.
- `code` for code responses.

Provide a brief text description and a Python code example that prints "Hello, World!" in one line.
```

You can use this prompt in any ChatGPT window **for demo purposes**, or in an API request where interacting with an LLM, and it will generate a response similar to the one shown below.

#### 3. **Example Response**

After sending the above request, the LLM should respond with something similar, wrapped in Flex Tag format:

```flextag
[[---- text --
This is a simple Python script that prints "Hello, World!" to the console.
--]]

[[---- code --
print("Hello, World!")
--]]
```

#### 4. **Converting Flex Tag to a Dictionary**

Now let's convert the Flex Tag response into a Python dictionary:

```python
import flextag

flex_tag_string = '''
[[---- description --
This is a simple Python script that prints "Hello, World!" to the console.
--]]

[[---- python code --
print("Hello, World!")
--]]
'''

flex_tag_dict = flextag.flex_to_dict(flex_tag_string)
print(flex_tag_dict)
```

This will output a dictionary like this:

```python
{
    "description": "This is a simple Python script that prints 'Hello, World!' to the console.",
    "python code": "print('Hello, World!')"
}
```

#### 5. **Converting the Dictionary Back to Flex Tag**

You can also convert the dictionary back to Flex Tag format:

```python
flex_tag_dict = {
    "description": "This is a simple Python script that prints 'Hello, World!' to the console.",
    "python code": "print('Hello, World!')"
}

flex_tag_string = flextag.dict_to_flex(flex_tag_dict)
print(flex_tag_string)
```

The output will return the original Flex Tag format:

```flextag
[[---- description --
This is a simple Python script that prints 'Hello, World!' to the console.
--]]

[[---- python code --
print('Hello, World!')
--]]
```

---

### Flex Tag System Standards

**Flex Tag** is designed to be a flexible yet unique tagging system, using opening and closing tags that are distinct from any other tags used in common scripting or programming languages. This ensures that Flex Tag's tags are never confused with language-specific syntax, preventing interference when AI generates code.

---

### Standards

#### 1. Tag Names
- Tags should be written in **lowercase**, with **spaces encouraged** for simplicity.
- The system is **case-insensitive**.
- **Spaces**, **underscores**, and **dashes** are allowed, but **spaces are preferred**.

#### 2. Tag Structure
- **Opening tags**: `[[---- tag name --` must appear on a new line.
- **Closing tags**: `--]]` must also appear on a new line.
- Opening and closing tags should be the only content on their respective lines.

#### 3. Multi-Language Support
- Flex Tag can be used across multiple programming languages, allowing it to work without conflicting with existing language syntax.