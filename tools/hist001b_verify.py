#!/usr/bin/env python3
"""Verify HIST-001B receipts independently; never dispatch to GR/HIST-001A."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from native_eset.historical.hist001b_receipt import verify_hist001b_receipt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--source-root", type=Path, required=True)
    ap.add_argument("--oracle-root", type=Path)
    ap.add_argument("--expected-sha256")
    args = ap.parse_args()
    try:
        report = verify_hist001b_receipt(
            args.receipt, source_root=args.source_root,
            oracle_root=args.oracle_root, expected_sha256=args.expected_sha256,
        )
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "HIST001B_RECEIPT_FAIL_CLOSED",
                          "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
