from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List


def extract_frequencies(script_path: Path) -> list[float]:
    """Return the frequency list declared in a single VDL2 script."""
    text = script_path.read_text(encoding="utf-8")
    match = re.search(r"FREQUENCIES=\((.*?)\)", text, re.S)
    if not match:
        raise ValueError(f"No FREQUENCIES array found in {script_path}")

    tokens = [token.strip() for token in match.group(1).split() if token.strip()]
    return [float(token) for token in tokens]


def collect_vdl2_frequencies(bin_dir: Path) -> list[float]:
    """Collect frequencies from all vdl2-dev*.sh scripts in a directory."""
    scripts = sorted(bin_dir.glob("vdl2-dev*.sh"))
    if not scripts:
        raise FileNotFoundError(f"No vdl2-dev scripts found in {bin_dir}")

    frequencies: List[float] = []
    for script_path in scripts:
        frequencies.extend(extract_frequencies(script_path))

    return sorted(frequencies)


def summarize_frequencies(frequencies: list[float]) -> dict[str, object]:
    """Return min, max, count, and any missing 0.025 MHz steps."""
    if not frequencies:
        raise ValueError("No frequencies to summarize")

    values = sorted(frequencies)
    start = values[0]
    end = values[-1]
    expected: List[float] = []
    current = start
    while current <= end + 1e-9:
        expected.append(round(current, 3))
        current += 0.025

    missing = [value for value in expected if value not in values]
    return {
        "count": len(values),
        "min": values[0],
        "max": values[-1],
        "gaps": missing,
    }


def summarize_vdl2_frequencies(bin_dir: Path) -> dict[str, object]:
    frequencies = collect_vdl2_frequencies(bin_dir)
    return summarize_frequencies(frequencies)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize VDL2 frequency coverage")
    parser.add_argument(
        "bin_dir",
        nargs="?",
        default=str(Path(__file__).resolve().parents[2] / "bin"),
        help="Directory containing vdl2-dev*.sh scripts",
    )
    args = parser.parse_args()

    summary = summarize_vdl2_frequencies(Path(args.bin_dir))
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
