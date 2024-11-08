from openai import OpenAI
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from flextag.flextag import FlexTag, Tag


# Now your demo code using the new FlexTag class
client = OpenAI()


def get_keyword_info(keyword: str):
    flex = FlexTag()

    # Add system context
    flex.add_system_message(
        "You are an expert Python developer explaining Python keywords."
    )

    # Level 1: Simple usage
    flex.add_tag(
        Tag(
            name="KEYWORD",
            required=True,
            llm_instructions="The keyword we are describing.",
        )
    )

    # Level 2: Custom example
    flex.add_tag(
        Tag(
            name="EXPLANATION",
            required=False,
            llm_instructions="A short explanation of what the keyword does in under 10 words.",
            example_value="Defines a new function in Python code",
        )
    )

    # Level 3: Advanced usage
    flex.add_advanced_tag(
        """
    CODE (Optional)
    - Must be valid Python code
    - Should demonstrate the keyword usage
    - Must be properly indented
    - Example:
    <<-- CODE[0]:
    def example():
        pass
    -->>
    """
    )

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
            {
                "role": "user",
                "content": f"Generate and explain 2 random Python keywords",
            },
        ],
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
    result = get_keyword_info("yield")
