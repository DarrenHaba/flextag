import flextag


def demo_combined_search():
    document = """[[PARAMS fmt="yaml"]]
[[META title="Search Demo" #demo .config]]

[[SEC:movies #movies .content.movies]]
{
    "title": "The Matrix",
    "genre": ["action", "sci-fi"]
}
[[/SEC]]

[[SEC:shows #shows .content.shows]]
{
    "title": "Breaking Bad",
    "genre": ["drama"]
}
[[/SEC]]"""

    container = flextag.parse(document)

    print("=== Combined Search Demo ===")

    # Container level search
    print("\nContainer searches:")
    movies = container.search("#movies")
    shows = container.search("#shows")

    print(f"Found {len(movies)} movie sections")
    print(f"Found {len(shows)} show sections")

    # Section level search
    print("\nSection level matches:")
    for section in container.sections:
        print(f"\nSection {section.id}:")
        print(f"Matches #movies: {section.matches('#movies')}")
        print(f"Matches .content: {section.matches('.content')}")


if __name__ == "__main__":
    print("Running FlexTag Search Demos\n")
    print("\n" + "=" * 50 + "\n")
    demo_combined_search()
