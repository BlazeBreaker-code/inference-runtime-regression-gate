import argparse
import json
from pathlib import Path


REQUIRED_STAGES = [
    "preprocess_ms",
    "model_ms",
    "postprocess_ms",
    "serialization_ms",
    "end_to_end_ms",
]

REQUIRED_METRICS = [
    "samples",
    "mean_ms",
    "p50_ms",
    "p95_ms",
    "p99_ms",
    "min_ms",
    "max_ms",
]


def load_json(path: str) -> dict:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Missing benchmark result: {file_path}")

    return json.loads(file_path.read_text())


def validate_result(path: str) -> None:
    result = load_json(path)

    required_top_level = [
        "benchmark",
        "device",
        "batch_size",
        "iterations",
        "warmup",
        "throughput_requests_per_second",
        "stages",
    ]

    for key in required_top_level:
        if key not in result:
            raise ValueError(f"{path} is missing required field: {key}")

    if result["throughput_requests_per_second"] <= 0:
        raise ValueError(f"{path} has invalid throughput")

    stages = result["stages"]

    for stage in REQUIRED_STAGES:
        if stage not in stages:
            raise ValueError(f"{path} is missing stage: {stage}")

        for metric in REQUIRED_METRICS:
            if metric not in stages[stage]:
                raise ValueError(f"{path} is missing metric {stage}.{metric}")

    print(f"Validated benchmark result: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", default="results/baseline.json")
    parser.add_argument("--candidate", default="results/candidate.json")
    args = parser.parse_args()

    validate_result(args.baseline)
    validate_result(args.candidate)

    print("Smoke test passed.")


if __name__ == "__main__":
    main()