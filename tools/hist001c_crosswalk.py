#!/usr/bin/env python3
"""HIST-001C read-only historical-to-Theory-State equation crosswalk."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from native_eset.historical.hist001c_crosswalk import inspect_noncanonical_crosswalk


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--graph-dir", type=Path)
    args = parser.parse_args()
    try:
        report = inspect_noncanonical_crosswalk(
            args.source_root, graph_dir=args.graph_dir,
        )
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({
            "status": "HIST001C_FAIL_CLOSED",
            "error": str(exc),
        }, sort_keys=True))
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
