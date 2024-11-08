# FlexTag

[![PyPI version](https://badge.fury.io/py/flextag.svg)](https://badge.fury.io/py/flextag)
[![Python Versions](https://img.shields.io/pypi/pyversions/flextag.svg)](https://pypi.org/project/flextag/)
[![Build Status](https://github.com/darrenhaba/flextag/actions/workflows/ci.yml/badge.svg)](https://github.com/darrenhaba/flextag/actions)
[![codecov](https://codecov.io/gh/darrenhaba/flextag/branch/main/graph/badge.svg)](https://codecov.io/gh/darrenhaba/flextag)
[![License](https://img.shields.io/pypi/l/flextag.svg)](https://github.com/darrenhaba/flextag/blob/main/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Downloads](https://pepy.tech/badge/flextag)](https://pepy.tech/project/flextag)

A streamlined solution for structuring and parsing Large Language Model (LLM) responses.

---

## Why FlexTag?
FlexTag simplifies the integration of LLM responses into your applications by providing a flexible and easy-to-parse tagging system.

### With FlexTag, you can:
- 🚀 Simplify Parsing: Easily extract different types of content from LLM responses without dealing with complex nested structures.
- 🔧 Customize Tags: Define your own tags to suit your specific needs, giving you full control over the structure of LLM outputs.
- 📦 Handle Multiple Items Efficiently: Use numbered tags to manage multiple pieces of data without nesting, making parsing straightforward.
- 🧐 Enhance Reliability: Reduce parsing errors and inconsistencies, resulting in more robust and dependable LLM integrations.

---

<a id="installation"></a>

## Installation

Install FlexTag using pip:

```bash
pip install flextag
```

Or install the latest version from GitHub

```bash
pip install git+https://github.com/darrenhaba/flextag.git
```

## Understanding FlexTag

### The Basics

#### FlexTag uses a simple yet powerful tagging system:
```flextag
<<-- TAG_NAME: content -->>
```

That's it! This simple structure is what makes FlexTag powerful. Think of tags as containers for different parts of an LLM's response. When you use FlexTag:

1. You create tags with any names you want (e.g., `WORD`, `MEANING`)
2. The LLM understands these tags and uses them in its response
3. FlexTag converts the response into a list of Python dictionaries automatically

### Quick Example

Let's start with a simple "Hello World" example to demonstrate the basic concept:
```python
import flextag

# Example LLM response with a simple greeting
response = '''<<-- GREETING[0]: Hello, World!-->>'''

# Parse the response
results = flextag.flex_to_records(response)

# Print the greeting
print(results[0]['GREETING'])  # Output: Hello, World!
```



## Tutorial: Using FlexTag with OpenAI's API

### Using FlexTag with Large Language Models

This guide demonstrates how to integrate FlexTag with Large Language Models (LLMs) to structure and parse responses effectively.

#### Setting up the Environment

First, make sure you have the required packages installed:

```bash
pip install flextag openai
```

#### Basic LLM Integration

Here's a complete example that shows how to use FlexTag with OpenAI's GPT models:

```python
from openai import OpenAI
import os
import flextag

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Define the system message that establishes FlexTag formatting
system_message = """You are an AI assistant that ALWAYS responds using FlexTag format, following these strict rules:

1. All responses must be wrapped in ```flextag``` code blocks
2. All content must be inside FlexTag tags
3. Tag format rules:
   - Tags must be UPPERCASE
   - Only letters, numbers, and underscores allowed (e.g., USER_NAME, RESPONSE)
   - Each record uses sequential indices starting at [0]
   - Tags can be single-line: <<-- TAG_NAME[index]: content -->>
   - Or multi-line:
     <<-- TAG_NAME[index]:
     content
     can span
     multiple lines
     -->>
4. Multiple records share the same tag names:
   - First record uses tags with [0]
   - Second record uses same tags with [1]
   - And so on...
5. IMPORTANT: Place ALL content within tags - no explanations, comments, or text outside of tags. Only respond using the specific tags you are given
6. When generating code examples:
   - Use proper indentation
   - Format code across multiple lines for readability
   - Include all necessary code (no partial snippets)"""

def get_python_keyword_explanation(keyword: str) -> dict:
    """
    Get an explanation of a Python keyword using FlexTag formatting.
    """
    # Construct the prompt
    prompt = f"""Explain the Python keyword '{keyword}' using KEYWORD, EXPLANATION, and CODE tags."""

    # Make the API call
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    # Get the FlexTag formatted response and parse it
    llm_response = response.choices[0].message.content
    records = flextag.flex_to_records(llm_response)
    return records[0]

# Example usage
if __name__ == "__main__":
    # Get explanation for the 'yield' keyword
    result = get_python_keyword_explanation('yield')

    print(f"Keyword: {result['KEYWORD']}")
    print(f"\nExplanation: {result['EXPLANATION']}")
    print(f"\nExample Code:\n{result['CODE']}")
```

