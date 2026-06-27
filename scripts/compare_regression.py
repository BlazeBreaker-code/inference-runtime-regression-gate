import argparse
import json
import sys
from pathlib import Path


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text())


def percent_change(baseline: float, candidate: float) -> float:
    if baseline == 0:
        return 0.0

    return ((candidate - baseline) / baseline) * 100.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--config", default="configs/regression_config.json")
    args = parser.parse_args()

    baseline = load_json(args.baseline)
    candidate = load_json(args.candidate)
    config = load_json(args.config)

    stage = config["stage"]
    metric = config["metric"]
    max_regression_percent = float(config["max_regression_percent"])
    min_regression_ms = float(config.get("min_regression_ms", 0.0))

    baseline_value = baseline["stages"][stage][metric]
    candidate_value = candidate["stages"][stage][metric]

    change_percent = percent_change(baseline_value, candidate_value)
    change_ms = candidate_value - baseline_value

    print("Inference Runtime Regression Check")
    print(f"Stage: {stage}")
    print(f"Metric: {metric}")
    print(f"Baseline: {baseline_value:.3f} ms")
    print(f"Candidate: {candidate_value:.3f} ms")
    print(f"Change: {change_percent:.2f}%")
    print(f"Absolute change: {change_ms:.3f} ms")
    print(f"Percent threshold: {max_regression_percent:.2f}%")
    print(f"Minimum regression floor: {min_regression_ms:.3f} ms")

    percent_failed = change_percent > max_regression_percent
    absolute_failed = change_ms > min_regression_ms

    if percent_failed and absolute_failed:
        print("Status: FAIL")
        sys.exit(1)

    print("Status: PASS")


if __name__ == "__main__":
    main()