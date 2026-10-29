#!/usr/bin/env python3
"""Inspect original width-paired RNG signatures; diagnostic only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from native_eset.historical.hist001b_rng_forensics import inspect_width_streams


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oracle-root", type=Path, required=True)
    parser.add_argument("--diagnostic-root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = inspect_width_streams(
            oracle_root=args.oracle_root,
            diagnostic_root=args.diagnostic_root,
        )
        body = json.dumps(result, sort_keys=True, indent=2) + "\n"
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("x", encoding="utf-8") as file:
                file.write(body)
        print(body, end="")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({
            "status": "HIST001B_RNG_WIDTH_FORENSICS_FAIL_CLOSED",
            "error": str(exc),
        }, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
