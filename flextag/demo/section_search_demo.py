import flextag


def demo_section_search():
    document = """[[SEC:movies #movies .content.movies]]
{
    "title": "The Matrix",
    "genre": ["action", "sci-fi"]
}
[[/SEC]]"""

    container = flextag.parse(document)
    section = container.sections[0]

    print("=== Section Search Demo ===")

    # Test direct section matching
    print("\nDirect section matches:")
    print(f"Matches #movies: {section.matches('#movies')}")
    print(f"Matches .content.movies: {section.matches('.content.movies')}")
    print(f"Matches :movies: {section.matches(':movies')}")


if __name__ == "__main__":
    demo_section_search()
    print("\n" + "=" * 50 + "\n")
