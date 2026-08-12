from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List


def extract_frequencies(script_path: Path) -> list[float]:
    """Return the frequency list declared in a single ACARS script."""
    text = script_path.read_text(encoding="utf-8")
    match = re.search(r"FREQUENCIES=\((.*?)\)", text, re.S)
    if not match:
        raise ValueError(f"No FREQUENCIES array found in {script_path}")

    tokens = [token.strip() for token in match.group(1).split() if token.strip()]
    return [float(token) for token in tokens]


def collect_acarsdec_frequencies(bin_dir: Path) -> list[float]:
    """Collect frequencies from all acars-dev*.sh scripts in a directory."""
    scripts = sorted(bin_dir.glob("acars-dev*.sh"))
    if not scripts:
        raise FileNotFoundError(f"No acars-dev scripts found in {bin_dir}")

    frequencies: List[float] = []
    for script_path in scripts:
        frequencies.extend(extract_frequencies(script_path))

    return sorted(frequencies)


def summarize_frequencies(frequencies: list[float]) -> dict[str, object]:
    """Return min, max, count, and any missing 0.025 MHz steps."""
    if not frequencies:
        raise ValueError("No frequencies to summarize")

    values = sorted(frequencies)
    start_mhz = int(round(values[0] * 1000))
    end_mhz = int(round(values[-1] * 1000))
    step_mhz = 25

    expected_mhz = list(range(start_mhz, end_mhz + step_mhz, step_mhz))
    actual_mhz = [int(round(freq * 1000)) for freq in values]

    missing = [value / 1000 for value in expected_mhz if value not in actual_mhz]
    return {
        "count": len(values),
        "min": values[0],
        "max": values[-1],
        "gaps": missing,
    }


def summarize_acarsdec_frequencies(bin_dir: Path) -> dict[str, object]:
    frequencies = collect_acarsdec_frequencies(bin_dir)
    return summarize_frequencies(frequencies)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize ACARSDEV frequency coverage")
    parser.add_argument(
        "bin_dir",
        nargs="?",
        default=str(Path(__file__).resolve().parents[2] / "bin"),
        help="Directory containing acars-dev*.sh scripts",
    )
    args = parser.parse_args()

    summary = summarize_acarsdec_frequencies(Path(args.bin_dir))
    gaps = summary["gaps"]
    print(f"Count: {summary['count']}")
    print(f"Minimum: {summary['min']:.3f}")
    print(f"Maximum: {summary['max']:.3f}")
    if gaps:
        print(f"Gaps: {len(gaps)} missing step(s) -> {', '.join(f'{value:.3f}' for value in gaps)}")
    else:
        print("Gaps: none")


if __name__ == "__main__":
    main()
