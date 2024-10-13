import flextag


# Function to convert Flex Tag to dictionary and print details
def print_flex_to_dict(flex_tag_string):
    print("######### Flex Tag to Dict #########")

    # Convert Flex Tag to dictionary
    flex_tag_dict = flextag.flex_to_dict(flex_tag_string)

    # Print the full dictionary
    print("\n----------- Full Dictionary -----------")
    print(flex_tag_dict)

    # Print specific parts of the dictionary
    print("\n----------- Text Section -----------")
    print(f"Text: {flex_tag_dict.get('text', 'No text available')}")

    print("\n----------- Code Section -----------")
    print(f"Code: {flex_tag_dict.get('code', 'No code available')}")


# Function to convert Dictionary back to Flex Tag and print details
def print_dict_to_flex(flex_tag_dict):
    print("\n######### Dict to Flex Tag #########")

    # Convert dictionary back to Flex Tag
    flex_tag_string = flextag.dict_to_flex(flex_tag_dict)

    # Print the Flex Tag formatted string
    print("\n----------- Flex Tag String -----------")
    print(flex_tag_string)


# Example usage
flex_tag_string = """
[[---- text --
This is a simple Python script that prints "Hello, World!" to the console.
--]]

[[---- code --
print("Hello, World!")
--]]
"""

# Convert Flex Tag to dictionary and display results
print_flex_to_dict(flex_tag_string)

# Create a sample dictionary to convert back to Flex Tag
sample_dict = {
    "text": "This is a simple Python script that prints 'Hello, "
    "World!' to the console.",
    "code": "print('Hello, World!')",
}

# Convert dictionary back to Flex Tag and display results
print_dict_to_flex(sample_dict)
