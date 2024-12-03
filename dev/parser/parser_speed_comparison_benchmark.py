import time
import json
import psutil
from typing import List, Dict, Generator

from dev.parser.line_by_line_speed_test import StreamingFlexTagParser
from flextag.core.parsers.parsers import ContainerParser

import time
import json
import psutil
from typing import List, Dict, Generator


def generate_stream_data(num_blocks: int) -> Generator[str, None, None]:
    """Generate test data for StreamingFlexTagParser"""
    for i in range(num_blocks):
        yield f'[[DATA#tag_{i%5}, .path_{i%5}, {{"key": "value{i}", "flag": true}}]]'
        yield f"content{i}"
        yield "[[/DATA]]"
        yield ""


def generate_traditional_data(num_blocks: int) -> Generator[str, None, None]:
    """Generate test data for Traditional Container Parser"""
    for i in range(num_blocks):
        yield f'[[SEC #tag_{i%5} .path_{i%5} key="value{i}" flag="true"]]'
        yield f"content{i}"
        yield "[[/SEC]]"
        yield ""


def benchmark_streaming_parser(num_blocks: int, iterations: int = 3):
    """Benchmark the streaming parser"""
    parser = StreamingFlexTagParser()
    total_time = 0
    memory_before = psutil.Process().memory_info().rss / 1024 / 1024

    print(f"\nTesting StreamingFlexTagParser with {num_blocks:,d} blocks:")

    # Generate complete test data
    test_data = list(generate_stream_data(num_blocks))

    # Warm up
    for _ in parser.parse_stream(test_data):
        pass

    for i in range(iterations):
        block_count = 0
        start_time = time.perf_counter()

        # Process all blocks
        for _ in parser.parse_stream(test_data):
            block_count += 1

        elapsed = time.perf_counter() - start_time
        total_time += elapsed
        blocks_per_second = num_blocks / elapsed

        memory_after = psutil.Process().memory_info().rss / 1024 / 1024
        memory_used = memory_after - memory_before

        print(f"  Run {i+1}: {elapsed:.4f}s ({blocks_per_second:,.0f} blocks/s)")
        print(f"  Memory usage: {memory_used:.1f}MB")
        print(f"  Blocks processed: {block_count:,d}")

    if iterations > 0:
        avg_time = total_time / iterations
        avg_blocks_per_second = num_blocks / avg_time
        print(f"  Average: {avg_time:.4f}s ({avg_blocks_per_second:,.0f} blocks/s)")


def benchmark_traditional_parser(num_blocks: int, iterations: int = 3):
    """Benchmark the traditional container parser"""
    parser = ContainerParser()
    total_time = 0
    memory_before = psutil.Process().memory_info().rss / 1024 / 1024

    print(f"\nTesting Traditional ContainerParser with {num_blocks:,d} blocks:")

    # Generate complete test data
    test_data = "\n".join(generate_traditional_data(num_blocks))

    # Warm up
    try:
        _ = parser.parse(test_data)
    except Exception as e:
        print(f"Warm-up failed: {str(e)}")
        return

    for i in range(iterations):
        try:
            start_time = time.perf_counter()

            container = parser.parse(test_data)
            section_count = len(container.sections)

            elapsed = time.perf_counter() - start_time
            total_time += elapsed
            blocks_per_second = num_blocks / elapsed

            memory_after = psutil.Process().memory_info().rss / 1024 / 1024
            memory_used = memory_after - memory_before

            print(f"  Run {i+1}: {elapsed:.4f}s ({blocks_per_second:,.0f} blocks/s)")
            print(f"  Memory usage: {memory_used:.1f}MB")
            print(f"  Sections processed: {section_count:,d}")

        except Exception as e:
            print(f"  Run {i+1} failed: {str(e)}")
            continue

    if iterations > 0:
        avg_time = total_time / iterations
        avg_blocks_per_second = num_blocks / avg_time
        print(f"  Average: {avg_time:.4f}s ({avg_blocks_per_second:,.0f} blocks/s)")


def main():
    block_sizes = [1000, 10000, 100000]

    for num_blocks in block_sizes:
        try:
            # Test streaming parser
            benchmark_streaming_parser(num_blocks)

            # Test traditional parser
            benchmark_traditional_parser(num_blocks)
        except Exception as e:
            print(f"Error testing with {num_blocks} blocks: {str(e)}")


if __name__ == "__main__":
    main()
