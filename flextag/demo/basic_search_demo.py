import flextag


def demo_basic_search():
    """Basic container search demo"""
    document = """[[PARAMS fmt="text"]]
[[META title="Basic Search Demo" version="1.0"]]

[[SEC:config #settings .sys.config fmt="json"]]
{
    "port": 8080,
    "host": "localhost"
}
[[/SEC]]"""

    # try:
    print("=== Basic Search Demo ===")

    # Parse container
    container = flextag.parse(document)
    print(f"\nParsed container with {len(container.sections)} sections")

    # Print parsed sections for verification
    for section in container.sections:
        print(f"\nFound section:")
        print(f"  ID: {section.id}")
        print(f"  Tags: {section.tags}")
        print(f"  Paths: {section.paths}")

    # Search by ID
    config = container.find_first(":config")
    print(f"\nFind by ID ':config':")
    print(f"Found: {config.id if config else 'None'}")

    # Search by tag
    settings = container.find_first("#settings")
    print(f"\nFind by tag '#settings':")
    print(f"Found: {settings.id if settings else 'None'}")

    # Search by path
    sys_config = container.find_first(".sys.config")
    print(f"\nFind by path '.sys.config':")
    print(f"Found: {sys_config.id if sys_config else 'None'}")

    # except Exception as e:
    #     print(f"Error in demo: {str(e)}")


if __name__ == "__main__":
    print("Running FlexTag Search Demo\n")
    demo_basic_search()
    print("\n" + "=" * 50 + "\n")
