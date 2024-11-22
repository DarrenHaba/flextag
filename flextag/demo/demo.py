from flextag import factory, FlexTagParser, TransportContainer

# Example FlexTag document with different sections and formats
document = """[[PARAMS fmt="yaml"]]
[[META title="Example Document" version="1.0" #demo .config]]

[[SEC:config #settings .sys.config fmt="json"]]
{
    "port": 8080,
    "host": "localhost",
    "debug": true
}
[[/SEC]]

[[SEC:users #data .sys.users fmt="yaml"]]
users:
  - name: John Doe
    role: admin
  - name: Jane Smith
    role: user
[[/SEC]]
"""

def demo_data_container():
    print("=== Data Container Demo ===")

    # Create parser and parse document
    parser = factory.create_parser()
    container = parser.parse(document)

    # Access container metadata
    print("\nContainer Metadata:")
    print(f"Title: {container.metadata.get('title')}")
    print(f"Version: {container.metadata.get('version')}")

    # Find sections using new query syntax
    print("\nConfig Section:")
    config = container.find_first(":config")
    print(config.content)

    print("\nUsers Section:")
    users = container.find_first("#data")
    print(users.content)

    # Modify content
    users.content['users'].append({
        "name": "New User",
        "role": "guest"
    })

    # Export modified container
    print("\nModified Container:")
    print(parser.dump(container))


def demo_transport_container():
    print("\n=== Transport Container Demo ===")

    # Create and parse original container
    parser = factory.create_parser()
    container = parser.parse(document)

    # Create transport container with compression
    transport = TransportContainer()
    transport.metadata["compression"] = "gzip"  # or "zip"

    # Encode container for transport
    encoded = transport.encode(container)
    print("\nEncoded Transport Container:")
    print(encoded[:100] + "..." + encoded[-50:])  # Show truncated version

    # Decode transport container
    decoded = TransportContainer.decode(encoded)
    print("\nDecoded Container Validation:")
    print(f"Metadata matches: {decoded.metadata == container.metadata}")
    print(f"Section count matches: {len(decoded.sections) == len(container.sections)}")

    # Verify content survived roundtrip
    config = decoded.find_first(":config")
    print("\nDecoded Config Section:")
    print(config.content)

def demo_search():
    print("\n=== Search Demo ===")

    parser = factory.create_parser()
    container = parser.parse(document)

    print("\nFind by section ID:")
    config = container.find_first(":config")
    print(f"Found: {config.id}")

    print("\nFind by tag:")
    settings = container.find_first("#settings")
    print(f"Found: {settings.id}")

    print("\nFind by path:")
    sys_config = container.find_first(".sys.config")
    print(f"Found: {sys_config.id}")

    print("\nComplex query:")
    result = container.find_first("#settings AND .sys.config")
    print(f"Found: {result.id if result else 'None'}")


if __name__ == "__main__":
    demo_data_container()
    demo_transport_container()
    demo_search()
