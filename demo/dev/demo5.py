import flextag

def print_flex_to_dict(flex_tag_string):
    print("######### Flex Tag to Dict #########")

    print(flex_tag_string)

    # Convert Flex Tag to dictionary
    result = flextag.flex_to_records(flex_tag_string)

    # Print the full list of dictionaries
    print("\n----------- Full Result -----------")
    print(result)

    # Print each group in the list
    for i, group in enumerate(result):
        print(f"\n----------- Group {i} -----------")
        print(f"Text: {group.get('TEXT', 'No text available')}")
        print(f"Code: {group.get('CODE', 'No code available')}")

def print_dict_to_flex(data):
    print("\n######### Dict to Flex Tag #########")

    # Convert dictionary back to Flex Tag
    flex_tag_string = flextag.records_to_flex(data)

    # Print the Flex Tag formatted string
    print("\n----------- Flex Tag String -----------")
    print(flex_tag_string)

# Example 1: Single group (index 0)
flex_tag_string = """
<<-- TEXT[0]:
This is a simple Python script that prints "Hello, World!" to the console.
-->>

<<-- CODE[0]:
print("Hello, World!")
-->>
"""

# Example 2: Multiple groups
flex_tag_string_multiple = """
<<-- TEXT[0]:
First example prints a greeting.
-->>

<<-- CODE[0]:
print("Hello, World!")
-->>

<<-- TEXT[1]:
Second example shows addition.
-->>

<<-- CODE[1]:
print(1 + 1)
-->>
"""

# Test single group
print("Testing single group:")
print_flex_to_dict(flex_tag_string)

# Test with sample dictionary (will be treated as group 0)
sample_dict = [{
    "TEXT": "This is a simple Python script that prints 'Hello, World!' to the console.",
    "CODE": "print('Hello, World!')"
}]

print_dict_to_flex(sample_dict)

# Test multiple groups
print("\nTesting multiple groups:")
print_flex_to_dict(flex_tag_string_multiple)

# Test with multiple dictionaries
multiple_dict = [
    {
        "TEXT": "First example prints a greeting.",
        "CODE": "print('Hello, World!')"
    },
    {
        "TEXT": "Second example shows addition.",
        "CODE": "print(1 + 1)"
    }
]

print_dict_to_flex(multiple_dict)
