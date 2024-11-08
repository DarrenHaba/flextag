from openai import OpenAI
import os
import flextag

# Initialize OpenAI client
client = OpenAI()

# Simple system message explaining FlexTag format
system_message = """You must respond using FlexTag format:
1. Wrap response in ```flextag``` blocks
2. Use UPPERCASE tags
3. Tag format: <<-- TAG_NAME[0]: content -->>
4. ALL content must be inside tags"""

def get_keyword_info(keyword: str):
    """Get info about a Python keyword using FlexTag."""
    # Print what we're sending to the LLM
    print(f"\nAsking LLM about: {keyword}")

    prompt = f"Explain Python keyword '{keyword}' using KEYWORD, EXPLANATION, and CODE tags."

    # Get response from LLM
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
    )

    # Print raw LLM response
    print("\nRaw LLM Response:")
    print(response.choices[0].message.content)

    # Parse FlexTag response
    records = flextag.flex_to_records(response.choices[0].message.content)
    print("\nParsed FlexTag Result:")
    print(records[0])

    return records[0]

# Example usage
if __name__ == "__main__":
    result = get_keyword_info('yield')
    