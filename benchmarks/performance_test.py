import time
import psutil
import logging
from pathlib import Path
from typing import List, Dict, Any
import json
import random
from flextag.managers.data import DataManager
from flextag.managers.query import QueryManager
from flextag.core.parser.provider import ParserProvider
from flextag.core.query.provider import QueryProvider
from flextag.managers.base import ManagerEvent

class PerformanceTester:
    def __init__(self):
        logging.getLogger('flextag').setLevel(logging.WARNING)

        self.data_manager = DataManager()
        self.query_manager = QueryManager()

        parser_provider = ParserProvider()
        query_provider = QueryProvider()

        self.data_manager.register("parsers", "default", parser_provider)
        self.query_manager.register("query_parsers", "default", query_provider)

        self.data_manager.connect(self.query_manager)

    def generate_test_data(self, num_blocks: int) -> str:
        """Generate test data with varied metadata"""
        # Use fewer unique tags and paths to avoid matrix size issues
        tags = [f"tag_{i}" for i in range(2)]  # Only 2 tags
        paths = [f"path.to.item{i}" for i in range(2)]  # Only 2 paths

        blocks = []
        for i in range(num_blocks):
            block_tags = random.sample(tags, 1)  # Just one tag per block
            block_paths = random.sample(paths, 1)  # Just one path per block
            block = f"""[[DATA:block_{i} {','.join(f'#{t}' for t in block_tags)} {','.join(f'.{p}' for p in block_paths)} {{"index": {i}}}]]
Content for block {i}
[[/DATA]]"""
            blocks.append(block)

        # Process in smaller chunks to avoid overwhelming the arrays
        return "\n".join(blocks)

    def benchmark_parsing(self, block_counts: List[int], iterations: int = 3):
        print("\nParsing Performance Test")
        print("=" * 50)

        for num_blocks in block_counts:
            print(f"\nBlocks: {num_blocks}")

            parse_times = []
            memory_usages = []

            for i in range(iterations):
                # Generate and parse in smaller chunks
                chunk_size = 100
                chunks = range(0, num_blocks, chunk_size)

                start_memory = psutil.Process().memory_info().rss / 1024 / 1024
                start_time = time.perf_counter()

                for chunk_start in chunks:
                    chunk_end = min(chunk_start + chunk_size, num_blocks)
                    data = self.generate_test_data(chunk_end - chunk_start)
                    self.data_manager.parse_string(data)

                elapsed = time.perf_counter() - start_time
                memory_used = psutil.Process().memory_info().rss / 1024 / 1024 - start_memory

                parse_times.append(elapsed)
                memory_usages.append(memory_used)

            avg_time = sum(parse_times) / len(parse_times)
            avg_memory = sum(memory_usages) / len(memory_usages)
            blocks_per_second = num_blocks / avg_time

            print(f"  Time: {avg_time:.4f}s ({blocks_per_second:.0f} blocks/s)")
            print(f"  Memory: {avg_memory:.1f}MB")

    def run_query_test(self, query: str, num_iterations: int = 100) -> Dict[str, float]:
        """Run a single query test"""
        times = []
        total_results = 0

        for _ in range(num_iterations):
            start_time = time.perf_counter()
            results = self.query_manager.search(query)
            elapsed = (time.perf_counter() - start_time) * 1000  # Convert to ms

            times.append(elapsed)
            total_results += len(results)

        return {
            "avg_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "avg_results": total_results / num_iterations
        }

    def benchmark_queries(self):
        print("\nQuery Performance Test")
        print("=" * 50)

        # Simplified queries using only the tags/paths we created
        queries = {
            "Single tag": "#tag_0",
            "Multiple tags": "#tag_0 AND #tag_1",
            "Path": ".path.to.item0",
            "Complex": "#tag_0 AND .path.to.item0 AND index = 5"
        }

        print("\nResults per query type:")
        print("-" * 30)

        for name, query in queries.items():
            results = self.run_query_test(query)
            print(f"\n{name}:")
            print(f"  Avg time: {results['avg_time']:.2f}ms")
            print(f"  Min time: {results['min_time']:.2f}ms")
            print(f"  Max time: {results['max_time']:.2f}ms")
            print(f"  Results:  {results['avg_results']:.1f}")

def main():
    tester = PerformanceTester()

    # Test with smaller numbers first
    # block_counts = [100, 500]
    block_counts = [1000000]
    tester.benchmark_parsing(block_counts)

    # Test queries
    tester.benchmark_queries()

if __name__ == "__main__":
    main()