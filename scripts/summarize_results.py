import argparse
import json
from pathlib import Path


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    args = parser.parse_args()

    result = load_json(args.input)
    end_to_end = result["stages"]["end_to_end_ms"]

    print("| Metric | Value |")
    print("| ------ | -----: |")
    print(f"| Device | {result['device']} |")
    print(f"| Batch size | {result['batch_size']} |")
    print(f"| Throughput | {result['throughput_requests_per_second']:.2f} req/s |")
    print(f"| p50 latency | {end_to_end['p50_ms']:.3f} ms |")
    print(f"| p95 latency | {end_to_end['p95_ms']:.3f} ms |")
    print(f"| p99 latency | {end_to_end['p99_ms']:.3f} ms |")


if __name__ == "__main__":
    main()