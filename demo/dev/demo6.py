from openai import OpenAI
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from flextag.flextag import FlexTag, Tag


# First we need the Tag and ErrorHandling classes we created
class ErrorHandling(Enum):
    """Defines how to handle errors for individual tags"""
    RAISE = "raise"  # Raise exception on error
    IGNORE = "ignore"  # Skip invalid tags
    DEFAULT = "default"  # Use default value if provided




# Now your demo code using the new FlexTag class
client = OpenAI()


def get_keyword_info(keyword: str):
    flex = FlexTag()

    # Add custom system message
    flex.add_system_message("You are an expert Python developer explaining Python keywords.")
    flex.add_system_message("Provide clear, concise explanations with practical examples.")

    flex.add_tag(Tag(
        name="KEYWORD",
        required=True,
        llm_instructions="The keyword we are describing."
    ))

    flex.add_tag(Tag(
        name="EXPLANATION",
        required=True,
        llm_instructions="A short explanation of what the keyword does in under 10 words."
    ))

    flex.add_tag(Tag(
        name="CODE",
        required=False,
        llm_instructions="Simple code demonstration showing how to use the keyword."
    ))

    # Get complete system message
    system_message = flex.compose_system_message()

    print()
    print()
    print(system_message)

    # Create the chat completion
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Explain 5 random Python keywords"}
        ]
    )

    print(response)

    # Parse and validate FlexTag response
    try:
        records = flex.validate_response(response.choices[0].message.content)
        print("\nParsed FlexTag Result:")
        print(records[0])
        return records[0]
    except ValueError as e:
        print(f"Error parsing response: {e}")
        return None

if __name__ == "__main__":
    result = get_keyword_info('yield')
    