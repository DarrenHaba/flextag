import time
import random
from typing import List


import re
import json
from typing import Dict, List, Optional, Tuple


class FlexTagParser:
    def __init__(self):
        self.data_start_pattern = re.compile(r"^\[\[DATA(.*?)\]\]", re.DOTALL)
        self.data_end_pattern = re.compile(r"^\[\[/DATA\]\]$")
        self.json_pattern = re.compile(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}")

    def extract_metadata_string(self, metadata: str) -> str:
        current_pos = 0
        result = ""

        for json_match in self.json_pattern.finditer(metadata):
            if current_pos < json_match.start():
                part = metadata[current_pos : json_match.start()]
                part = re.sub(r"\s+", "", part)
                result += part

            json_str = json_match.group(0)
            try:
                parsed_json = json.loads(json_str)
                result += json.dumps(parsed_json, separators=(",", ":"))
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON in metadata: {json_str}")

            current_pos = json_match.end()

        if current_pos < len(metadata):
            part = metadata[current_pos:]
            part = re.sub(r"\s+", "", part)
            result += part

        return result.strip()

    def parse_metadata(self, metadata_str: str) -> Dict:
        result = {"id": None, "tags": [], "paths": [], "parameters": {}}

        json_match = self.json_pattern.search(metadata_str)
        if json_match:
            result["parameters"] = json.loads(json_match.group(0))
            metadata_str = metadata_str[: json_match.start()].rstrip(",")

        parts = metadata_str.split(",")
        for part in parts:
            part = part.strip()
            if not part:
                continue

            if part.startswith(":"):
                result["id"] = part[1:]
            elif part.startswith("#"):
                result["tags"].append(part[1:])
            elif part.startswith("."):
                result["paths"].append(part[1:])

        return result

    def parse_file(self, content: str) -> List[Dict]:
        blocks = []
        lines = content.split("\n")
        current_line = 0

        while current_line < len(lines):
            line = lines[current_line].strip()
            # print(f"Processing line {current_line}: {line[:50]}...")  # Debug print

            if line.startswith("[[DATA"):
                # print(f"Found DATA start at line {current_line}")  # Debug print
                metadata_line = line

                # For multiline metadata, keep reading until we find ]]
                while "]]" not in metadata_line and current_line + 1 < len(lines):
                    current_line += 1
                    metadata_line += "\n" + lines[current_line].strip()

                start_match = self.data_start_pattern.match(metadata_line)
                if start_match:
                    # print(f"Matched metadata at line {current_line}")  # Debug print
                    metadata_str = self.extract_metadata_string(start_match.group(1))
                    block_data = self.parse_metadata(metadata_str)

                    content_start = current_line + 1
                    content_end = None

                    # Look for end of block
                    for end_line in range(content_start, len(lines)):
                        if self.data_end_pattern.match(lines[end_line].strip()):
                            content_end = end_line - 1
                            current_line = end_line
                            # print(f"Found end at line {end_line}")  # Debug print
                            break

                    if content_end is None:
                        raise ValueError(
                            f"No closing tag found for block starting at line {current_line + 1}"
                        )

                    block_data["content_start"] = content_start + 1
                    block_data["content_end"] = content_end + 1
                    blocks.append(block_data)

            current_line += 1

        return blocks


# Test it out
test_content = """Some random text
[[DATA:id1, #tag1, .path1, {"key": "value1"}]]
This is content line 1
This is content line 2
[[/DATA]]

[[DATA
    :example_id,
    #tag_1,
    .path.to.file,
    {
        "key": "value",
        "flag": true
    }
]]
More content here
And here
[[/DATA]]
"""

parser = FlexTagParser()
blocks = parser.parse_file(test_content)

# Print results
# for i, block in enumerate(blocks, 1):
#     print(f"\nBlock {i}:")
#     print(json.dumps(block, indent=2))


def generate_test_blocks(num_blocks: int) -> str:
    """Generate test content with specified number of blocks."""

    # Pre-generate some variation for random selection
    ids = [f"id_{i}" for i in range(10)]
    tags = [f"tag_{i}" for i in range(5)]
    paths = [f"path_{i}" for i in range(5)]

    blocks = []
    for i in range(num_blocks):
        # Randomly select 1-3 tags and paths
        block_tags = [random.choice(tags) for _ in range(random.randint(1, 3))]
        block_paths = [random.choice(paths) for _ in range(random.randint(1, 3))]

        # Create the block with consistent format
        block = f"""[[DATA:{random.choice(ids)}, {', '.join(f'#{t}' for t in block_tags)}, {', '.join(f'.{p}' for p in block_paths)}, {{"key": "value{i}", "flag": true}}]]
This is content line {i}
[[/DATA]]

"""
        blocks.append(block)

    return "".join(blocks)


def benchmark_parser(num_blocks: List[int], iterations: int = 3):
    """Run performance tests with different block counts."""
    parser = FlexTagParser()

    results = {}
    for n in num_blocks:
        print(f"\nTesting with {n} blocks:")
        test_content = generate_test_blocks(n)
        times = []

        # Warm up run
        parser.parse_file(test_content)

        # Timed runs
        for i in range(iterations):
            start_time = time.perf_counter()
            blocks = parser.parse_file(test_content)
            end_time = time.perf_counter()

            elapsed = end_time - start_time
            times.append(elapsed)
            blocks_per_second = n / elapsed

            print(f"  Run {i+1}: {elapsed:.4f}s ({blocks_per_second:.0f} blocks/s)")

        avg_time = sum(times) / len(times)
        avg_blocks_per_second = n / avg_time
        results[n] = {
            "avg_time": avg_time,
            "avg_blocks_per_second": avg_blocks_per_second,
        }

        print(f"  Average: {avg_time:.4f}s ({avg_blocks_per_second:.0f} blocks/s)")

        # Memory check for large tests
        if n >= 100000:
            import psutil

            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            print(f"  Memory usage: {memory_mb:.1f}MB")

    return results


# Run benchmarks with increasing block counts
block_counts = [100, 1000, 10000, 100000, 1000000]
results = benchmark_parser(block_counts)
