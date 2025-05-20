"""Example usage of FlexTag with FTML integration."""

from flextag import FlexTag, FlexTagSyntaxError, SchemaValidationError
import json


def basic_example():
    """Basic FlexTag usage."""
    # Create a FlexTag document with various section types
    document = """
    [[config]]: ftml
    model_name = "GPT-4"
    max_tokens = 8192
    temperature = 0.7
    [[/config]]

    [[notes #draft @research]]
    This is a research note in raw format.
    [[/notes]]

    [[items]]: ftml
    items = [
        "apple",
        "banana",
        "orange"
    ]
    [[/items]]
    """

    # Load the document
    view = FlexTag.load(string=document, validate=False)

    # Access sections
    print("Sections:", len(view.sections))
    for i, section in enumerate(view.sections):
        print(f"- Section {i+1}: id={section.id}, type={section.type_name}")
        if section.tags:
            print(f"  Tags: {', '.join(section.tags)}")
        if section.paths:
            print(f"  Paths: {', '.join(section.paths)}")
        print(f"  Content type: {type(section.content).__name__}")

    # Access specific section content
    config = view.sections[0].content
    print(
        f"\nConfig: model={config['model_name']}, tokens={config['max_tokens']}, temp={config['temperature']}"
    )

    notes = view.sections[1].content
    print(f"Notes: {notes}")

    items = view.sections[2].content
    print(f"Items: {items['items']}")

    # Convert to dictionary
    data_dict = view.to_dict()
    print("\nAs dictionary:")
    print(json.dumps(data_dict, indent=2, default=str))


def schema_example():
    """Schema validation example."""
    # Document with schema validation
    document = """
    [[]]: schema
    [config]: ftml
    // FTML Schema
    model_name: str
    max_tokens: int
    [/]

    [notes #draft]+: raw
    [[/]]

    [[config]]: ftml
    model_name = "GPT-4"
    max_tokens = 8192
    [[/config]]

    [[notes #draft @research]]
    This is a valid note that matches the schema.
    [[/notes]]
    """

    try:
        # Load with validation enabled
        view = FlexTag.load(string=document, validate=True)
        print("Schema validation passed!")

        # Access validated content
        config = view.sections[0].content
        print(f"Config: model={config['model_name']}, tokens={config['max_tokens']}")

        notes = view.sections[1].content
        print(f"Notes: {notes}")
    except SchemaValidationError as e:
        print(f"Schema validation error: {e}")


def filtering_example():
    """Filtering example."""
    # Document with different tags and paths
    document = """
    [[note1 #draft @research]]
    Draft research note
    [[/note1]]

    [[note2 #draft @development]]
    Draft development note
    [[/note2]]

    [[note3 #final @research]]
    Final research note
    [[/note3]]

    [[note4 #final @development]]
    Final development note
    [[/note4]]
    """

    view = FlexTag.load(string=document, validate=False)

    # Filter by tag
    draft_notes = view.filter("#draft")
    print(f"Draft notes: {len(draft_notes.sections)}")
    for note in draft_notes.sections:
        print(f"- {note.id}: {note.content}")

    # Filter by path
    research_notes = view.filter("@research")
    print(f"\nResearch notes: {len(research_notes.sections)}")
    for note in research_notes.sections:
        print(f"- {note.id}: {note.content}")

    # Combined filters
    draft_research = view.filter("#draft @research")
    print(f"\nDraft research notes: {len(draft_research.sections)}")
    for note in draft_research.sections:
        print(f"- {note.id}: {note.content}")

    # OR filter
    final_or_dev = view.filter("#final OR @development")
    print(f"\nFinal OR development notes: {len(final_or_dev.sections)}")
    for note in final_or_dev.sections:
        print(f"- {note.id}: {note.content}")


def flexmap_example():
    """FlexMap example."""
    # Document with nested paths
    document = """
    [[config.api.keys]]: ftml
    openai = "sk-1234567890"
    anthropic = "sk-abcdef1234"
    [[/config.api.keys]]

    [[config.api.settings]]: ftml
    timeout = 30
    retries = 3
    [[/config.api.settings]]

    [[notes.research]]: raw
    Research notes here
    [[/notes.research]]

    [[notes.development]]: raw
    Development notes here
    [[/notes.development]]
    """

    view = FlexTag.load(string=document, validate=False)

    # Convert to FlexMap
    fm = view.to_flexmap()

    # Access by path
    print("Config API Keys:")
    api_keys = fm["config"].children["api"].children["keys"].sections[0].content
    print(f"- OpenAI: {api_keys['openai']}")
    print(f"- Anthropic: {api_keys['anthropic']}")

    print("\nConfig API Settings:")
    api_settings = fm["config"].children["api"].children["settings"].sections[0].content
    print(f"- Timeout: {api_settings['timeout']}")
    print(f"- Retries: {api_settings['retries']}")

    print("\nNotes:")
    print(f"- Research: {fm['notes'].children['research'].sections[0].content}")
    print(f"- Development: {fm['notes'].children['development'].sections[0].content}")


if __name__ == "__main__":
    print("=== Basic Example ===")
    basic_example()

    print("\n\n=== Schema Example ===")
    schema_example()

    print("\n\n=== Filtering Example ===")
    filtering_example()

    print("\n\n=== FlexMap Example ===")
    flexmap_example()
