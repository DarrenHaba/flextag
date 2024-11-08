# JokeGen Demo

A simple command-line joke generator that demonstrates FlexTag's structured output capabilities. This demo shows how to:
- Structure creative content using tags
- Handle optional content (explanations)
- Process multiple items in a single response

## Setup & Installation

1. Navigate to the joke generator directory:
```bash
# From the FlexTag root directory:
cd demos/01_jokegen
```

2. Ensure you have the required packages:
- FlexTag
- OpenAI API key (set as environment variable or passed via --api-key)

## Usage

Make sure you're in the correct directory (`demos/01_jokegen`) before running these commands:

```bash
# Basic usage - generate one joke
python joke_generator.py "computers"

# Generate multiple jokes
python joke_generator.py "programming" -n 3

# Include explanations
python joke_generator.py "artificial intelligence" --explain

# Debug mode for troubleshooting
python joke_generator.py "python" --debug

# Use custom API key
python joke_generator.py "databases" --api-key "your-api-key"
```

## Example Output
```
Generated 1 joke(s) about: programming

Joke #1 (Programming Pun)
Q: Why do programmers hate nature?
A: Too many bugs!

Explanation: Plays on dual meaning of 'bugs' in code and nature.

--------------------------------------------------
```

## Common Issues

1. "Command not found" or similar error:
    - Make sure you're in the correct directory (`demos/01_jokegen`)
    - Run `pwd` to check your current directory
    - Use `cd` to navigate to the correct location

2. Module not found error:
    - Ensure you're running the command from the `01_jokegen` directory
    - Check that FlexTag is installed in your Python environment

## How It Works
This demo uses FlexTag to structure the LLM's response into distinct tags:
- `SETUP`: The joke's opening line
- `PUNCHLINE`: The joke's conclusion
- `TYPE`: The style of joke
- `EXPLANATION`: Brief insight into the wordplay (optional)

The system prompts the LLM to generate contextual humor while maintaining consistent structure in the response.