from openai import OpenAI
import os
import flextag
from openai import OpenAI

# Set your API key
os.environ['OPENAI_API_KEY'] = 'Your dash API dash key dash here. '

# Initialize the OpenAI client
client = OpenAI()

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