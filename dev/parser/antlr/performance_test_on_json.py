import time

import json


def generate_json_data(blocks):
    # Create a sample JSON block
    sample_block = {
        "DATA": {
            "id": "id",
            "tag": "#tag",
            "path": ".path",
            "metadata": {"key": "value"},
            "content": "content here",
        }
    }
    # Duplicate the block to create a large JSON array
    data = [sample_block] * blocks
    return json.dumps(data)  # Serialize to JSON string


def parse_json(data):
    return json.loads(data)  # Deserialize JSON string to Python object


# Performance test for JSON
def performance_test_json(blocks):
    # Generate large JSON string
    json_data = generate_json_data(blocks)

    # Time JSON parsing
    start_time = time.time()
    parse_json(json_data)
    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"Parsing {blocks} JSON blocks took {elapsed_time:.4f} seconds.")
    return elapsed_time


if __name__ == "__main__":
    performance_test_json(1000000)  # Test with 100,000 JSON blocks
