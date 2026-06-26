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
    threshold = float(config["max_regression_percent"])

    baseline_value = baseline["stages"][stage][metric]
    candidate_value = candidate["stages"][stage][metric]
    change = percent_change(baseline_value, candidate_value)

    print("Inference Runtime Regression Check")
    print(f"Stage: {stage}")
    print(f"Metric: {metric}")
    print(f"Baseline: {baseline_value:.3f} ms")
    print(f"Candidate: {candidate_value:.3f} ms")
    print(f"Change: {change:.2f}%")
    print(f"Threshold: {threshold:.2f}%")

    if change > threshold:
        print("Status: FAIL")
        sys.exit(1)

    print("Status: PASS")


if __name__ == "__main__":
    main()