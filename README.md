# Flex Tag

**A streamlined solution for structuring and parsing complex AI responses**

Flex Tag is a Python package (still in bata) that provides a simple, reliable way to structure and parse complex responses from Large Language Models (LLMs) and other AI systems. It offers a flexible tagging system that allows for the organization of multiple types of content within a single response, including:

- Plain text responses
- Code snippets in various languages
- File locations or references
- Structured data (like JSON or YAML)
- Descriptions or metadata
- And more

Key features:

1. **API-friendly**: Designed to work seamlessly with AI APIs, allowing for structured responses that are easy to parse programmatically.
2. **Human-readable**: The Flex Tag format is intuitive and easy to read, making it suitable for both machine and human consumption.
3. **Multi-response handling**: Capable of organizing multiple distinct pieces of information within a single response, solving the challenge of getting varied content from a single API call.
4. **Language-agnostic**: While implemented in Python, the Flex Tag format itself is language-independent, making it adaptable to various programming environments.
5. **Customizable**: Users can define their own tags to suit specific use cases, providing flexibility for diverse applications.

Flex Tag bridges the gap between unstructured AI outputs and the structured data often required in practical applications, making it easier to integrate AI responses into existing workflows and systems.

---

## Contents

- [Installation](#installation)
- [Quick Start Example ](#quick-start)
- [API Integration Example ](#chatgpt-example)
- [API Reference](#api-reference)
- [Converting to Other Formats](#converting)
- [Flex Tag System Standards](#standards)
- [Collaboration and Feedback](#feedback)


## Links

- [Project Repository](https://github.com/DarrenHaba/flextag)
- [Issue Tracker](https://github.com/DarrenHaba/flextag/issues)

---

<a id="installation"></a>
## Installation

``` bash
pip install flextag
```

This will download and install the latest version of Flex Tag and its dependencies.

For development purposes, you can install Flex Tag directly from the GitHub repository:

``` bash
pip install git+https://github.com/darrenhaba/flextag.git
```

After installation, you can import Flex Tag in your Python scripts as shown in the examples below.

---

<a id="quick-start"></a>
## Quick Start: LLM Chat Example

1. **Step 1: Instructing the LLM**

   You can start by pasting the following prompt into your LLM chat to instruct it to respond using Flex Tag format. The response will include a brief description and a simple Python code example.

   **Paste this prompt**:

   ```
   Please respond in Flex Tag format.
   
   Flex Tag is a system where different sections of content are separated using custom tags. The format is as follows:
   
   - Tags are written in lowercase, with spaces between words.
   - Opening tags start with `[[-- ` followed by the tag name.
   - Closing tags are `--]]`.
   - Opening and closing tags must be on separate lines, no inline tags allowed.
   
   Please use the following tags:
   - `text` for text responses.
   - `python code` for python code responses.
   
   Provide a brief text description (under 50 chars) and a Python code example that prints "Hello, World!" in one line.
   ```

2. **Step 2: Example LLM Response**

   After pasting the above instructions, you should receive a response similar to this:

   ```flextag
   [[-- text
   Here is a simple Python script.
   --]]

   [[-- python code
   print("Hello, World!")
   --]]
   ```

3. **Step 3: Parsing the Response**

   - Before we begin, ensure you have Flex Tag installed. If you haven't installed it yet, refer to the [Installation](#installation) section above.

   - Now, let's create a Python script that converts the example Flex Tag response from Step 2 into a dictionary. After converting, we'll print out both the `text` and `python code` sections.
   
   **Example Script**:

   ```python
   import flextag
   
   print("Welcome to the FlexTag Demo!")
   print("This demo will show you how to parse a FlexTag-formatted string into a dictionary.\n")
   
   print("Step 1: Here's our example FlexTag-formatted string:")
   # Example Flex Tag response
   flex_response = '''
   [[-- text
   Here is a simple Python script.
   --]]
   
   [[-- python code
   print("Hello, World!")
   --]]
   '''
   print(flex_response)
   
   print("\nStep 2: Now, let's convert this FlexTag string to a dictionary and see its contents:")
   # Convert Flex Tag to dictionary
   flex_dict = flextag.flex_to_dict(flex_response)
   
   # Print the text and python code sections from the dictionary
   print("Text content:", flex_dict.get('text', 'No text response available'))
   print("Python code content:", flex_dict.get('python code', 'No code response available'))
   
   print("\nThat's it! We've successfully parsed a FlexTag string into a dictionary.")
   print("You can now easily access different parts of the response using dictionary keys.")   
   ```

   In this script:
   - `flex_response` is the Flex Tag formatted response we received from the LLM in Step 2.
   - The `flex_to_dict` function converts the Flex Tag response into a Python dictionary.
   - Each section of the response is accessible by its tag (e.g., `text`, `python code`) as dictionary keys.

    This script demonstrates how to parse a Flex Tag formatted string into a dictionary and access its contents. It provides a step-by-step walkthrough of the process, making it easy for users to understand how Flex Tag works.

<a id="chatgpt-example"></a>
## API Integration: ChatGPT Example

1. **Step 1: Set Up the API Key**
   - Make sure you have your OpenAI API key. You can get one by signing up at [OpenAI](https://beta.openai.com/signup/).

2. **Step 2: Install Required Packages**
   - You'll need the `openai` Python package to interact with the ChatGPT API:
   - You'll need the `flextag` Python package to parse and organize multiple responses from the LLM, converting them into a structured dictionary format for easier handling.
   
  ```bash
  pip install openai flextag
  ```

3. **Step 3: Example API Script**
   - Use the following Python script to interact with the ChatGPT API. This script sends a request for a response in Flex Tag format and converts the response into a Python dictionary.

   ```python
   import os

   import openai
   import flextag
   
   # Set your API key
   os.environ['OPENAI_API_KEY'] = 'your-openai-api-key'

   # Initialize the OpenAI client
   client = openai.OpenAI()
   
   print("1. Preparing the request to the language model...")
   # Example request to GPT-4 with updated Flex Tag format
   response = client.chat.completions.create(
   model="gpt-4",
   messages=[
   {"role": "system", "content": "You are a helpful assistant that responds in Flex Tag format."},
   {"role": "user", "content": """
    Please respond in Flex Tag format.

    Flex Tag is a system where different sections of content are separated using custom tags. The format is as follows:

    - Tags are written in lowercase, with spaces between words.
       - Opening tags start on a new line `[[-- tag name here`.
       - The content goes is between the opening and closing tags.
       - closing tags start on a new line `--]]`.
   - Add an empty line between end tags and the next start tag.


    Please use the following tags:
    - `text` for text responses.
    - `python code` for python code responses.

    Provide a brief text description (under 50 chars) and a Python code example that prints "Hello, World!" in one line.
   """}
   ],
   max_tokens=300,
   temperature=0.7
   )
   
   print("\n2. Received response from the language model.")
   
   # Get the text part of the response
   flex_response = response.choices[0].message.content.strip()
   print("\n3. Raw Flex Tag response:")
   print(flex_response)
   
   print("\n4. Converting Flex Tag response to a dictionary...")
   # Convert the Flex Tag response to a dictionary
   flex_dict = flextag.flex_to_dict(flex_response)
   
   print("\n5. Flex Tag response converted to dictionary:")
   print(flex_dict)
   
   # Print the text and code sections
   print("\n6. Accessing specific sections from the response:")
   print("Text:", flex_dict.get('text', 'No text response available'))
   print("Python Code:", flex_dict.get('python code', 'No code response available'))
   
   print("\n7. Demo complete. Flextag successfully parsed the LLM response into separate sections.")
   
   ```

4. **Step 4: Running the Script**
   - After running the script, you should see the Flex Tag response from ChatGPT, parsed into a Python dictionary with the text and code sections printed.

<a id="api-reference"></a>
# API Reference

## Functions

### flex_to_dict

```python
def flex_to_dict(flex_tag_string: str) -> OrderedDict:
```

Converts a Flex Tag formatted string into an OrderedDict.

#### Parameters

- `flex_tag_string` (str): A string in Flex Tag format.

#### Returns

- `OrderedDict`: A dictionary representation of the Flex Tag content.

#### Example

```python
import flextag

flex_string = """
[[-- text
Hello, World!
--]]

[[-- python code
print("Hello, World!")
--]]
"""

result = flextag.flex_to_dict(flex_string)
print(result)
# Output: OrderedDict([('text', 'Hello, World!'), ('python code', 'print("Hello, World!")')])
```

### dict_to_flex

```python
def dict_to_flex(tag_dict: Union[OrderedDict, dict]) -> str:
```

Converts a nested OrderedDict or dict back into a Flex Tag formatted string.

#### Parameters

- `tag_dict` (Union[OrderedDict, dict]): A dictionary representation of Flex Tag content.

#### Returns

- `str`: A Flex Tag formatted string.

#### Example

```python
import flextag
from collections import OrderedDict

tag_dict = OrderedDict([
    ('text', 'Hello, World!'),
    ('python code', 'print("Hello, World!")')
])

flex_string = flextag.dict_to_flex(tag_dict)
print(flex_string)
# Output:
# [[-- text
# Hello, World!
# --]]
#
# [[-- python code
# print("Hello, World!")
# --]]
```

### flex_to_json

```python
def flex_to_json(flex_tag_string: str, indent: Optional[int] = None) -> str:
```

Converts a Flex Tag formatted string to a JSON string.

#### Parameters

- `flex_tag_string` (str): A string in Flex Tag format.
- `indent` (Optional[int]): Number of spaces for indentation in the resulting JSON string. If None, the JSON will be compact. Defaults to None.

#### Returns

- `str`: A JSON formatted string representing the input Flex Tag structure.

#### Example

```python
import flextag

flex_string = """
[[-- text
Hello, World!
--]]

[[-- python code
print("Hello, World!")
--]]
"""

json_string = flextag.flex_to_json(flex_string, indent=2)
print(json_string)
# Output:
# {
#   "text": "Hello, World!",
#   "python code": "print(\"Hello, World!\")"
# }
```

### json_to_flex

```python
def json_to_flex(json_string: str) -> str:
```

Converts a JSON string to a Flex Tag formatted string.

#### Parameters

- `json_string` (str): A JSON formatted string.

#### Returns

- `str`: A Flex Tag formatted string representing the input JSON structure.

#### Example

```python
import flextag

json_string = '{"text": "Hello, World!", "python code": "print(\\"Hello, World!\\")"}'

flex_string = flextag.json_to_flex(json_string)
print(flex_string)
# Output:
# [[-- text
# Hello, World!
# --]]
#
# [[-- python code
# print("Hello, World!")
# --]]
```

<a id="converting"></a>
## Converting to Other Formats

Flex Tag directly supports conversion to and from JSON format using the `flex_to_json` and `json_to_flex` functions. For other formats like YAML or TOML, you can easily convert the resulting dictionary using third-party packages.

### YAML Example (requires `pyyaml`):
```python
import yaml
import flextag

flex_string = "... your Flex Tag string ..."
flex_dict = flextag.flex_to_dict(flex_string)
yaml_string = yaml.dump(flex_dict)
```

### TOML Example (requires `toml`):
```python
import toml
import flextag

flex_string = "... your Flex Tag string ..."
flex_dict = flextag.flex_to_dict(flex_string)
toml_string = toml.dumps(flex_dict)
```

Note: For YAML and TOML conversions, you'll need to install the respective packages (`pyyaml` for YAML and `toml` for TOML) as they are not part of the Python standard library.

---

<a id="standards"></a>
## Flex Tag System Standards

**Flex Tag** is designed to be a flexible yet unique tagging system, using tags that are distinct from any other tags used in common scripting or programming languages. This ensures that Flex Tag's tags are never confused with language-specific syntax, preventing interference when AI generates code.

### Standards

#### 1. Tag Names
- Tags should be written in **lowercase**, with **spaces encouraged** for simplicity.
- The system is **case-insensitive**, but **lowercase preferred**.
- **Spaces**, **underscores**, and **dashes** are allowed, but **spaces are preferred**.

#### 2. Tag Structure
- **Opening tags**: `[[-- tag name` must appear on a new line.
- **Closing tags**: `--]]` must also appear on a new line.
- Opening and closing tags should be the only content on their respective lines.

#### 3. Multi-Language Support
- Flex Tag can be used across multiple programming languages, allowing it to work without conflicting with existing language syntax.

<a id="feedback"></a>
## Collaboration and Feedback

Flex Tag is currently in early beta, and we value your input to help shape its development. Whether you have suggestions for syntax improvements, feature requests, or unique use cases that could benefit from Flex Tag, we encourage you to participate in the project's evolution.

If you encounter any issues, have ideas for enhancements, or want to discuss potential applications, please open a GitHub Issue on our repository. Your feedback is crucial in refining Flex Tag to meet a wide range of needs in the AI and data processing communities.

We're committed to creating a tool that's both powerful and user-friendly, and your experiences and insights are invaluable in achieving this goal. Join us in developing Flex Tag into a robust solution for structured AI responses and data handling.