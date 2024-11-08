from openai import OpenAI
import os
import flextag

# Initialize OpenAI client
client = OpenAI()

system_message = """Respond using FlexTag format. The request will show the exact tags and format to use.
If tags are shown like this:
<<-- TAG_NAME: expected content description -->>
Respond with single-line format.

If tags are shown like this:
<<-- TAG_NAME:
expected
content
description
-->>
Respond with multi-line format.

IMPORTANT: All tags MUST include an index, even for single records. Use [0], [1], etc:
<<-- ITEM_NAME[0]: First product. -->>
<<-- ITEM_PRICE[0]: 9.99 -->>
<<-- ITEM_NAME[1]: Second product. -->>
<<-- ITEM_PRICE[1]: 7.99 -->>"""


def get_random_keywords():
    """Get explanations for two random Python keywords."""

    # The prompt itself uses FlexTag to show exactly what we want back
    prompt = """Give me two random Python keywords, using these tags:

<<-- KEYWORD: name of the Python keyword -->>
<<-- EXPLANATION:
An explanation of what the key word
does in 3 short lines.
-->>
<<-- CODE:
example code showing
proper usage of
the keyword
-->>"""

    print("\nSending request for two keywords...")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
    )

    # Print raw response to see how it followed our format
    # print("\nRaw LLM Response:")

    print(response.choices[0].message.content)

    # Parse the response
    records = flextag.flex_to_records(response.choices[0].message.content)

    return records


if __name__ == "__main__":
    records = get_random_keywords()

    # Show parsed results
    for i, record in enumerate(records):
        print(f"\nKeyword {i + 1}:")
        print(f"- {record['KEYWORD']}")
        print(f"- {record['EXPLANATION']}")
        print(f"- Example:\n{record['CODE']}")
