import argparse
import json
import re
from pathlib import Path
from typing import Any

from analysis import extract_structured_intake


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run intake extraction for each call in a JSONL file.",
    )
    parser.add_argument(
        "input_file",
        help="Path to the input JSONL file.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Directory where one JSON output file per call will be written.",
    )
    return parser.parse_args()


def _load_jsonl(input_file: str) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []

    with open(input_file, encoding="utf-8") as file_handle:
        for line_number, raw_line in enumerate(file_handle, start=1):
            line = raw_line.strip()
            if not line:
                continue

            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError(f"Line {line_number} must contain a JSON object.")

            calls.append(payload)

    return calls


def _sanitize_filename(value: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    return sanitized or "call"


def _output_filename(payload: dict[str, Any], index: int) -> str:
    payload_id = payload.get("id")
    if isinstance(payload_id, str) and payload_id.strip():
        return f"{_sanitize_filename(payload_id.strip())}.json"

    return f"call_{index:05d}.json"


def main() -> int:
    args = _parse_args()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    calls = _load_jsonl(args.input_file)

    for index, payload in enumerate(calls, start=1):
        result = extract_structured_intake(payload)
        output_path = output_dir / _output_filename(payload, index)
        output_path.write_text(f"{json.dumps(result, indent=2)}\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
