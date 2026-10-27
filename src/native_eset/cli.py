"""Native ESET command-line control plane. Every graph and verification action is read-only."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from native_eset.controls import FlatGRLambdaCDM
from native_eset.capabilities import CAPABILITIES


def _root() -> Path:
    """Editable repository checkout root; no hidden network or Drive access."""
    return Path(__file__).resolve().parents[2]


def emit(data: object) -> None:
    print(json.dumps(data,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False))


def _parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(prog="eset")
    sub=p.add_subparsers(dest="command",required=True)
    sub.add_parser("status")
    sub.add_parser("doctor")
    co=sub.add_parser("control",help="Independent GR-LambdaCDM comparison only")
    co.add_argument("--z",nargs="+",type=float,default=[0.0,1.0,3.0])
    run=sub.add_parser("run",help="Execute source-locked control RunSpec")
    run.add_argument("--spec",required=True)
    run.add_argument("--out",default="runs")
    vr=sub.add_parser("verify",help="Verify locally stored run receipt/artifact hashes")
    vr.add_argument("--receipt",required=True)
    vr.add_argument("--expected-sha256", default=None)
    graph=sub.add_parser("graph",help="Read-only sealed ESET graph")
    g=graph.add_subparsers(dest="graph_command",required=True)
    for cmd in ("status","validate","node","neighbors","path","impact","blockers","explain","diff","prepare"):
        q=g.add_parser(cmd)
        q.add_argument("--graph-dir", default=None)
        if cmd in {"status","validate","node","neighbors","path","impact","blockers","explain","diff","prepare"}:
            q.add_argument("--lock",default="config/graph_snapshot.lock.json")
        if cmd in {"node","neighbors","impact","blockers","explain"}:
            q.add_argument("id")
        if cmd=="path":
            q.add_argument("start");q.add_argument("target")
        if cmd == "neighbors":
            predicate_group = q.add_mutually_exclusive_group(required=True)
            predicate_group.add_argument("--predicates", default=None)
            predicate_group.add_argument("--predicate", default=None)
        if cmd in {"path", "impact"}:
            q.add_argument("--predicates", required=cmd == "path", default="DEPENDS_ON,REQUIRES,REQUIRES_DOMAIN")
        if cmd in {"neighbors","path"}:
            q.add_argument("--direction",choices=["in","out"],default="out")
        if cmd=="explain":
            q.add_argument("--axis",default=None);q.add_argument("--scope",default=None)
        if cmd=="diff":
            q.add_argument("--other",required=True)
            q.add_argument("--other-lock",required=True)
        if cmd=="prepare":
            q.add_argument("--destination",required=True)
    return p


def _graph(args: argparse.Namespace) -> int:
    from native_eset.graph.snapshot import GraphSnapshot
    from native_eset.graph.query import GraphQuery
    from native_eset.graph.resolver_adapter import run_pinned_resolver
    from native_eset.sources.acquire import prepare_verified_snapshot
    lock=Path(args.lock)
    if not lock.is_file() and str(lock)=="config/graph_snapshot.lock.json":
        lock=Path(__file__).resolve().parent/"graph/graph_snapshot.lock.json"
    if args.graph_command=="status" and not getattr(args,"graph_dir",None):
        info=json.loads(lock.read_text(encoding="utf-8"))
        emit({"status":"SEALED_SOURCE_LOCK_AVAILABLE_SNAPSHOT_NOT_EMBEDDED",
              "release":info["release_version"],"expected_sha256":info["graph_sha256"],
              "graph_files_required":info["file_count"],"physical_provider":"NOT_ADMITTED_BY_BOOTSTRAP"})
        return 0
    if args.graph_command=="prepare":
        if not args.graph_dir:
            raise ValueError("--graph-dir source files required for prepare")
        emit(prepare_verified_snapshot(Path(args.graph_dir),lock,Path(args.destination)))
        return 0
    if not getattr(args,"graph_dir",None):
        raise ValueError("--graph-dir is required for verified local graph queries")
    snapshot=GraphSnapshot.load(args.graph_dir,lock,
        vocabulary_file=Path(__file__).resolve().parent/"graph/vocabulary_v0_7_2.json")
    q=GraphQuery(snapshot)
    if args.graph_command in {"status","validate"}:
        result=snapshot.statistics()
        if args.graph_command=="validate":
            v=run_pinned_resolver(snapshot)
            result["resolver_status"]=v.audit["resolver_execution_status"]
            result["resolver_partitions"]=len(v.partitions)
            result["resolver_summaries"]=len(v.summaries)
        emit(result)
    elif args.graph_command=="node":emit({"graph_sha256": snapshot.graph_sha256, "record": q.node(args.id)})
    elif args.graph_command=="neighbors":
        preds=args.predicate or args.predicates
        emit({"graph_sha256":snapshot.graph_sha256,"neighbors":q.neighbors(args.id,preds.split(','),direction=args.direction)})
    elif args.graph_command=="path":emit(q.shortest_path(args.start,args.target,args.predicates.split(','),direction=args.direction))
    elif args.graph_command=="impact":emit(q.impact(args.id, args.predicates.split(",")))
    elif args.graph_command=="blockers":emit(q.blockers(args.id))
    elif args.graph_command=="explain":emit(run_pinned_resolver(snapshot).explain(args.id,args.axis,args.scope))
    elif args.graph_command=="diff":
        other=GraphSnapshot.load(args.other,args.other_lock,
                vocabulary_file=Path(__file__).resolve().parent/"graph/vocabulary_v0_7_2.json")
        emit(q.diff(other))
    return 0


def main() -> int:
    args=_parser().parse_args()
    try:
        if args.command=="status":
            emit({"repo":"Native ESET bootstrap infrastructure v0.1.0",
                  "science_status":"INFRASTRUCTURE_ONLY_NOT_ESET_PHYSICS",
                  "backend_capabilities":{k:{"executable":v.executable,"observables":list(v.observables),
                                             "role":v.model_role} for k,v in sorted(CAPABILITIES.items())},
                  "physical_outputs_authorized":[]})
        elif args.command=="doctor":
            from native_eset.graph.resolver_adapter import approved_lock
            from native_eset.evidence.receipts import source_tree_digest
            from native_eset import __version__
            lock = approved_lock()
            emit({"status": "LOCAL_PACKAGE_INTEGRITY_PASS_NOT_DEPLOYMENT_APPROVAL", "version": __version__,
                  "graph_lock_available": True, "graph_source_files_embedded": False,
                  "resolver_script_source_verified": True, "resolver_policy_bytes_verified": True,
                  "approved_graph_sha256": lock["graph_sha256"], "package_sha256": source_tree_digest(),
                  "historical_ESET_backends": "NOT_IMPORTED", "native_ESET_physics": "NOT_IMPLEMENTED",
                  "GitHub_CI": "NOT_VERIFIED_BY_LOCAL_DOCTOR"})
        elif args.command=="control":
            ctl=FlatGRLambdaCDM()
            emit({"control":"EXTERNAL_GR_LAMBDA_CDM_NOT_NATIVE_ESET",
                  "E_of_z":[{"z":z,"E":ctl.E(z)} for z in args.z]})
        elif args.command=="run":
            from native_eset.runner import RunSpec,run_control
            emit(run_control(RunSpec.read(args.spec),Path(args.out)))
        elif args.command=="verify":
            from native_eset.evidence.receipts import verify_run_receipt
            emit(verify_run_receipt(Path(args.receipt), expected_sha256=args.expected_sha256))
        elif args.command=="graph":return _graph(args)
        return 0
    except (OSError, ValueError, RuntimeError, KeyError, TypeError, ArithmeticError, PermissionError) as exc:
        category = "INPUT_OR_INFRASTRUCTURE_ERROR_NOT_THEORY_FALSIFICATION"
        if type(exc).__name__ in {"UnsupportedCapability", "NotImplementedError"}:
            category = "BLOCKED_NOT_IMPLEMENTED"
        elif type(exc).__name__ == "NumericalNonconvergence":
            category = "NUMERICAL_NONCONVERGENCE"
        elif type(exc).__name__ in {"GraphIntegrityError", "ReceiptIntegrityError"}:
            category = "INTEGRITY_FAILURE"
        emit({"status": "FAIL_CLOSED", "failure_category": category,
              "error_type": type(exc).__name__, "message": str(exc)})
        return 2
