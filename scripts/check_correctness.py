import argparse
import importlib.util
from pathlib import Path

import torch


def load_model_class(repo_root: Path, module_name: str):
    model_path = repo_root.resolve() / "src" / "synthetic_model.py"
    spec = importlib.util.spec_from_file_location(module_name, model_path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load model from {model_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.SyntheticInferenceModel


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-root", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    args = parser.parse_args()

    baseline_class = load_model_class(
        args.baseline_root, "baseline_model"
    )
    candidate_class = load_model_class(
        args.candidate_root, "candidate_model"
    )

    dimensions = {
        "input_size": 1024,
        "hidden_size": 2048,
        "output_size": 1000,
    }

    torch.manual_seed(7)

    baseline = baseline_class(**dimensions).cpu().float().eval()
    candidate = candidate_class(**dimensions).cpu().float().eval()

    # Copy the actual parameters, rather than relying on matching seeds.
    candidate.load_state_dict(baseline.state_dict(), strict=True)

    generator = torch.Generator().manual_seed(123)
    cases_checked = 0

    with torch.no_grad():
        for batch_size in (1, 16, 32):
            shape = (batch_size, dimensions["input_size"])
            cases = {
                "random": torch.randn(shape, generator=generator),
                "zeros": torch.zeros(shape),
            }

            for case_name, inputs in cases.items():
                label = f"batch={batch_size}, input={case_name}"

                # Separate copies prevent in-place input changes from
                # affecting the other model's inputs.
                expected = baseline(inputs.clone())
                actual = candidate(inputs.clone())

                expected_shape = (
                    batch_size,
                    dimensions["output_size"],
                )

                for name, output in (
                    ("baseline", expected),
                    ("candidate", actual),
                ):
                    if output.shape != expected_shape:
                        raise AssertionError(
                            f"{label}: {name} returned shape "
                            f"{tuple(output.shape)}, expected {expected_shape}"
                        )

                    if not torch.isfinite(output).all().item():
                        raise AssertionError(
                            f"{label}: {name} produced NaN or infinity"
                        )

                try:
                    torch.testing.assert_close(
                        actual,
                        expected,
                        rtol=1e-5,
                        atol=1e-6,
                    )
                except AssertionError as error:
                    raise AssertionError(
                        f"{label}: output mismatch\n{error}"
                    ) from error

                print(f"PASS: {label}")
                cases_checked += 1

    print(f"Correctness check: PASS ({cases_checked} cases)")


if __name__ == "__main__":
    main()