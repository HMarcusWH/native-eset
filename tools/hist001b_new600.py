#!/usr/bin/env python3
"""Run 600 NEW independent transition-grid checks; NOT historic 600 prechecks."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from native_eset.historical.hist001b_prechecks import (
    independently_check_new_600_grid_cases,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = independently_check_new_600_grid_cases(args.source_root)
    except (ValueError, OSError, ImportError, OverflowError) as exc:
        print(json.dumps({
            "status": "HIST001B_NEW_600_GRID_DIAGNOSTIC_FAIL_CLOSED",
            "error": str(exc),
        }, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
