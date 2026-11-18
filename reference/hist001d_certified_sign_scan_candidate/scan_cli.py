"""Command-line access to the source-only mathematical sign coverage engine."""
from __future__ import annotations
import argparse
import importlib
import json
import sys
from pathlib import Path

from certified_sign_scan import (
    BRACKETS_HEX, SourceContract, SyntheticOracle, Unresolved,
    canonical_json, scan, validate_receipt, verify_source_replay,
)


def load_adapter(spec: str):
    if ":" not in spec:
        raise Unresolved("ADAPTER_EXPECTED_MODULE_COLON_FACTORY")
    module, factory = spec.split(":", 1)
    if not module or not factory or factory.startswith("_"):
        raise Unresolved("INVALID_ADAPTER_SPEC")
    obj = importlib.import_module(module)
    return getattr(obj, factory)()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Source-only HIST-001D strict sign scanner; no physical claims")
    p.add_argument("--adapter", help="Trusted source-bound replay adapter module:factory; see README")
    p.add_argument("--synthetic", action="store_true", help="Non-scientific smoke test only")
    p.add_argument("--uniqueness-parent-sha256", default="", help="SHA-256 of separately verified global uniqueness evidence")
    p.add_argument("--mode", choices=["theorem", "adaptive"], default="theorem")
    p.add_argument("--lens", choices=tuple(BRACKETS_HEX), action="append")
    p.add_argument("--max-evals-per-lens", type=int, default=128)
    p.add_argument("--out", help="Path for deterministic receipt JSON")
    p.add_argument("--check-receipt", help="Verify structural digest and scope, not scientific proof")
    p.add_argument("--replay-receipt", help="Recompute source-replayed receipt and compare byte-for-byte")
    args = p.parse_args(argv)
    if args.adapter and args.synthetic:
        p.error("cannot combine real adapter and synthetic mode")
    if args.replay_receipt and not args.adapter:
        p.error("source replay requires --adapter")
    if args.check_receipt:
        try:
            data = json.loads(Path(args.check_receipt).read_text(encoding="ascii"))
            validate_receipt(data)
            print("STRUCTURE_ONLY_PASS (not source authentication)")
            return 0
        except Exception as exc:
            print("UNRESOLVED:"+str(exc), file=sys.stderr)
            return 2
    uniqueness = "e"*64 if args.synthetic else args.uniqueness_parent_sha256
    scope = "SYNTHETIC_TEST_ONLY" if args.synthetic else "SOURCE_REPLAYED_CANDIDATE_MATH"
    contract = SourceContract(uniqueness_sha256=uniqueness, scope=scope)
    try:
        api = SyntheticOracle() if args.synthetic else (load_adapter(args.adapter) if args.adapter else None)
        if args.replay_receipt:
            data = json.loads(Path(args.replay_receipt).read_text(encoding="ascii"))
            verify_source_replay(data, api, contract,
                                 mode="THEOREM_COVER" if args.mode == "theorem" else "ADAPTIVE_COVER",
                                 max_evals_per_lens=args.max_evals_per_lens)
            print("SOURCE_REPLAY_BYTE_IDENTICAL_PASS (conditional mathematical scope only)")
            return 0
        result = scan(api, contract, mode="THEOREM_COVER" if args.mode == "theorem" else "ADAPTIVE_COVER",
                      lenses=tuple(args.lens) if args.lens else tuple(BRACKETS_HEX),
                      max_evals_per_lens=args.max_evals_per_lens)
        validate_receipt(result)
        if args.out:
            path = Path(args.out)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(canonical_json(result))
        else:
            sys.stdout.buffer.write(canonical_json(result))
        return 0 if result["status"] == "CERTIFIED_CONDITIONAL" else 2
    except Exception as exc:
        print("UNRESOLVED:"+type(exc).__name__+":"+str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
