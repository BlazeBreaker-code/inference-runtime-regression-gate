import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from src.synthetic_model import SyntheticInferenceModel


def sync_device(device: torch.device) -> None:
    if device.type == "cuda":
        torch.cuda.synchronize()


def percentile(values: list[float], p: float) -> float:
    return float(np.percentile(values, p))


def summarize(values: list[float]) -> dict:
    return {
        "samples": len(values),
        "mean_ms": float(np.mean(values)),
        "p50_ms": percentile(values, 50),
        "p95_ms": percentile(values, 95),
        "p99_ms": percentile(values, 99),
        "min_ms": float(np.min(values)),
        "max_ms": float(np.max(values)),
    }


def benchmark(args: argparse.Namespace) -> dict:
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    use_cuda = args.device == "cuda" and torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")

    model = SyntheticInferenceModel(
        input_size=args.input_size,
        hidden_size=args.hidden_size,
        output_size=args.output_size,
    ).to(device)

    model.eval()

    raw_input = np.random.randn(args.batch_size, args.input_size).astype(np.float32)

    timings = {
        "preprocess_ms": [],
        "model_ms": [],
        "controlled_delay_ms": [],
        "postprocess_ms": [],
        "serialization_ms": [],
        "end_to_end_ms": [],
    }

    with torch.no_grad():
        for _ in range(args.warmup):
            x = torch.from_numpy(raw_input).to(device)
            y = model(x)
            probabilities = torch.softmax(y, dim=-1)
            _ = torch.topk(probabilities, k=5, dim=-1).values.cpu().numpy()
            sync_device(device)

        total_start = time.perf_counter()

        for _ in range(args.iterations):
            request_start = time.perf_counter()

            start = time.perf_counter()
            x = torch.from_numpy(raw_input).to(device)
            sync_device(device)
            timings["preprocess_ms"].append((time.perf_counter() - start) * 1000.0)

            start = time.perf_counter()
            y = model(x)
            sync_device(device)
            timings["model_ms"].append((time.perf_counter() - start) * 1000.0)

            start = time.perf_counter()
            if args.controlled_delay_ms > 0:
                time.sleep(args.controlled_delay_ms / 1000.0)
            timings["controlled_delay_ms"].append((time.perf_counter() - start) * 1000.0)

            start = time.perf_counter()
            probabilities = torch.softmax(y, dim=-1)
            top_scores = torch.topk(probabilities, k=5, dim=-1).values.cpu().numpy()
            sync_device(device)
            timings["postprocess_ms"].append((time.perf_counter() - start) * 1000.0)

            start = time.perf_counter()
            _ = json.dumps({"top_scores": top_scores[0].tolist()})
            timings["serialization_ms"].append((time.perf_counter() - start) * 1000.0)

            timings["end_to_end_ms"].append((time.perf_counter() - request_start) * 1000.0)

        total_seconds = time.perf_counter() - total_start

    throughput = args.iterations / total_seconds

    return {
        "benchmark": "inference_runtime_regression_gate",
        "device": str(device),
        "batch_size": args.batch_size,
        "input_size": args.input_size,
        "hidden_size": args.hidden_size,
        "output_size": args.output_size,
        "iterations": args.iterations,
        "warmup": args.warmup,
        "controlled_delay_ms": args.controlled_delay_ms,
        "throughput_requests_per_second": throughput,
        "stages": {
            name: summarize(values)
            for name, values in timings.items()
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--iterations", type=int, default=300)
    parser.add_argument("--warmup", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--input-size", type=int, default=1024)
    parser.add_argument("--hidden-size", type=int, default=2048)
    parser.add_argument("--output-size", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output", default="results/current.json")
    parser.add_argument("--controlled-delay-ms", type=float, default=0.0)
    args = parser.parse_args()

    result = benchmark(args)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2))

    end_to_end = result["stages"]["end_to_end_ms"]

    print("Inference Runtime Benchmark")
    print(f"Device: {result['device']}")
    print(f"Batch size: {result['batch_size']}")
    print(f"Throughput: {result['throughput_requests_per_second']:.2f} req/s")
    print(f"p50: {end_to_end['p50_ms']:.3f} ms")
    print(f"p95: {end_to_end['p95_ms']:.3f} ms")
    print(f"p99: {end_to_end['p99_ms']:.3f} ms")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()