import json
from typing import Generator, Dict
import time
import psutil


class StreamingFlexTagParser:
    def __init__(self):
        self.DATA_START = "[[DATA"
        self.DATA_END = "[[/DATA]]"

    def parse_metadata(self, metadata_str: str) -> Dict:
        """Parse a single metadata string into structured data"""
        result = {"id": None, "tags": [], "paths": [], "parameters": {}}

        # Find JSON by matching from the first { to the end
        json_start = metadata_str.find("{")
        if json_start != -1:
            json_str = metadata_str[json_start:]
            result["parameters"] = json.loads(json_str)
            metadata_str = metadata_str[:json_start].rstrip(" ,")

        # Process the rest as markers
        for part in metadata_str.split(","):
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

    def parse_stream(self, lines_iter) -> Generator[Dict, None, None]:
        """Parse stream following the simplified state machine"""
        current_block = None
        line_number = 0

        for line in lines_iter:
            line_number += 1
            line = line.strip()

            if not line:
                continue

            # Only process lines that start with [
            if line.startswith("["):
                if line.startswith(self.DATA_START):
                    # Extract metadata part
                    meta_end = line.find("]]")
                    if meta_end != -1:
                        metadata = line[6:meta_end]  # 6 is len('[[DATA')
                        current_block = self.parse_metadata(metadata)
                        current_block["content_start"] = line_number + 1

                elif line == self.DATA_END and current_block is not None:
                    current_block["content_end"] = line_number - 1
                    yield current_block
                    current_block = None


def generate_test_data(num_blocks: int) -> Generator[str, None, None]:
    """Generate test data one line at a time"""
    for i in range(num_blocks):
        yield f'[[DATA#tag_{i%5}, .path_{i%5}, {{"key": "value{i}", "flag": true}}]]'
        yield f"content{i}"
        yield "[[/DATA]]"
        yield ""


def benchmark_streaming_parser(num_blocks: int, iterations: int = 3):
    """Benchmark the streaming parser"""
    parser = StreamingFlexTagParser()
    total_time = 0

    print(f"\nTesting with {num_blocks} blocks:")

    # Warm up without collecting results
    for _ in parser.parse_stream(generate_test_data(1000)):
        pass

    for i in range(iterations):
        block_count = 0
        start_time = time.perf_counter()

        # Process without collecting results
        for _ in parser.parse_stream(generate_test_data(num_blocks)):
            block_count += 1

        elapsed = time.perf_counter() - start_time
        total_time += elapsed
        blocks_per_second = num_blocks / elapsed

        memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
        print(f"  Run {i+1}: {elapsed:.4f}s ({blocks_per_second:.0f} blocks/s)")
        print(f"  Memory usage: {memory_mb:.1f}MB")
        print(f"  Blocks processed: {block_count}")

    if iterations > 0:
        avg_time = total_time / iterations
        avg_blocks_per_second = num_blocks / avg_time
        print(f"  Average: {avg_time:.4f}s ({avg_blocks_per_second:.0f} blocks/s)")


if __name__ == "__main__":
    benchmark_streaming_parser(1000000)
