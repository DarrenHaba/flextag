from flextag import FlexTag, Tag
from openai import OpenAI
import argparse
import os
import sys

class JokeGenerator:
    def __init__(self, api_key: str = None):
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = OpenAI()

        self.flex = FlexTag()

        # Updated system message to be clearer about optional tags
        self.flex.add_system_message(
            "You are a professional comedian specializing in clever, contextual humor. "
            "You excel at wordplay and creating jokes that are both intelligent and entertaining. "
            "Generate jokes based on given topics while keeping content appropriate for general audiences. "
        )

        # Core tags remain required
        self.flex.add_tag(Tag(
            name="SETUP",
            required=True,
            llm_instructions="The setup/premise of the joke",
            example_value="Why did the AI go to the doctor?"
        ))

        self.flex.add_tag(Tag(
            name="PUNCHLINE",
            required=True,
            llm_instructions="The punchline that makes the joke funny",
            example_value="It had a case of deep learning flu!"
        ))

        self.flex.add_tag(Tag(
            name="TYPE",
            required=True,
            llm_instructions="The type/style of joke (pun, wordplay, observational, etc.)",
            example_value="AI Pun"
        ))

        self.flex.add_tag(Tag(
            name="EXPLANATION",
            required=False,
            llm_instructions=(
                "Explain the joke in 10 words or less. Be extremely concise."
            ),
            example_value="Wordplay between programming 'bugs' and actual insects."
        ))

    def generate(self, topic: str, count: int = 1, explain: bool = False) -> list[dict]:
        """Generate jokes based on a topic using OpenAI"""
        system_message = self.flex.compose_system_message()

        # Debug: Print system message
        if os.getenv('DEBUG'):
            print("\nSystem Message:", system_message, "\n", file=sys.stderr)

        explanation_request = (
            "\nIMPORTANT: Include the EXPLANATION tag for each joke, providing insight "
            "into the wordplay, references, or context that makes the joke clever."
            if explain else ""
        )

        prompt = (
            f"Generate {count} different {'joke' if count == 1 else 'jokes'} about or related to: {topic}\n"
            f"Make them clever and appropriate for a general audience. "
            f"Focus on wordplay and intelligent humor rather than simple or crude jokes."
            f"{explanation_request}"
        )

        # Debug: Print prompt
        if os.getenv('DEBUG'):
            print("\nPrompt:", prompt, "\n", file=sys.stderr)

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            llm_response = response.choices[0].message.content

            # Debug: Print raw LLM response
            if os.getenv('DEBUG'):
                print("\nRaw LLM Response:", llm_response, "\n", file=sys.stderr)

            records = self.flex.validate_response(llm_response)

            # Debug: Print parsed records
            if os.getenv('DEBUG'):
                print("\nParsed Records:", records, "\n", file=sys.stderr)

            if explain and any('EXPLANATION' not in record for record in records):
                print("Some explanations were missing, requesting them separately...",
                      file=sys.stderr)
                return self._add_missing_explanations(records)

            return records

        except Exception as e:
            print(f"Error generating jokes: {e}", file=sys.stderr)
            return []

    def _add_missing_explanations(self, jokes: list[dict]) -> list[dict]:
        """Request explanations for jokes that are missing them"""
        for i, joke in enumerate(jokes):
            if 'EXPLANATION' not in joke:
                prompt = (
                    f"Explain this joke:\nSetup: {joke['SETUP']}\n"
                    f"Punchline: {joke['PUNCHLINE']}\n"
                    f"Please provide insight into the wordplay, references, or context "
                    f"that makes this joke clever."
                )

                try:
                    response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": self.flex.compose_system_message()},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )

                    explanation_response = response.choices[0].message.content
                    records = self.flex.validate_response(explanation_response)
                    if records and 'EXPLANATION' in records[0]:
                        jokes[i]['EXPLANATION'] = records[0]['EXPLANATION']

                except Exception as e:
                    print(f"Error getting explanation for joke {i+1}: {e}", file=sys.stderr)

        return jokes


def main():
    parser = argparse.ArgumentParser(description="Generate clever contextual jokes using AI")
    parser.add_argument("topic", help="Topic or keyword for the joke")
    parser.add_argument("-n", "--number", type=int, default=1, help="Number of jokes to generate")
    parser.add_argument("--explain", action="store_true", help="Show joke explanations")
    parser.add_argument("--api-key", help="OpenAI API key (optional, can use OPENAI_API_KEY env var)")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()

    # Set debug environment variable if flag is used
    if args.debug:
        os.environ['DEBUG'] = '1'

    try:
        generator = JokeGenerator(api_key=args.api_key)
        jokes = generator.generate(args.topic, args.number, args.explain)

        if not jokes:
            print("No jokes were generated. Please try again.", file=sys.stderr)
            sys.exit(1)

        print(f"\nGenerated {len(jokes)} joke(s) about: {args.topic}\n")

        for i, joke in enumerate(jokes, 1):
            print(f"Joke #{i} ({joke['TYPE']})")
            print(f"Q: {joke['SETUP']}")
            print(f"A: {joke['PUNCHLINE']}")
            if args.explain:
                if 'EXPLANATION' in joke:
                    print(f"\nExplanation: {joke['EXPLANATION']}")
                else:
                    print("\nNo explanation available for this joke.")
            print("\n" + "-"*50 + "\n")

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()