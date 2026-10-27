#!/usr/bin/env python3
import argparse, collections, hashlib, json
from pathlib import Path


def load_graph(root):
    byfile, graph = {}, {}
    paths = sorted(list(root.glob("*.jsonl")) + list(root.glob("*.jsonl.txt")))
    for path in paths:
        if path.name.startswith("TEMP_"):
            continue
        name = path.name.replace(".jsonl.txt","").replace(".jsonl","")
        rows = []
        with path.open(encoding="utf-8-sig") as fh:
            for line_no, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                obj = json.loads(line)
                if obj["id"] in graph:
                    raise ValueError(f"duplicate object id {obj['id']} at {path}:{line_no}")
                graph[obj["id"]] = obj
                rows.append(obj)
        byfile[name] = sorted(rows, key=lambda o: o["id"])
    return byfile, graph


def scope_key(v):
    if "scope" not in v or v["scope"] is None:
        return "__UNSCOPED__"
    s = v["scope"]
    if isinstance(s, (dict, list)):
        return json.dumps(s, sort_keys=True, separators=(",",":"))
    return str(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph-dir", required=True)
    ap.add_argument("--policy", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()


    policy_path = Path(args.policy)
    policy = json.loads(policy_path.read_text(encoding="utf-8-sig"))
    byfile, graph = load_graph(Path(args.graph_dir))
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)


    verdicts = sorted(byfile.get("verdicts", []), key=lambda o:o["id"])
    authorities = {x["id"]:x for x in byfile.get("authorities", [])}
    relations = sorted(byfile.get("relations", []), key=lambda o:o["id"])
    axis_auth = {k:set(v) for k,v in policy["axis_authority_scopes"].items()}
    scoped_values = set(policy["scope_rule"]["scoped_values_requiring_explicit_scope"])


    supersedes = collections.defaultdict(set)
    for r in relations:
        if r.get("predicate") == "SUPERSEDES" and r.get("subject") in authorities and r.get("object") in authorities:
            supersedes[r["subject"]].add(r["object"])


    def transitive_supersedes(a,b):
        if a == b:
            return False
        seen, stack = set(), [a]
        while stack:
            x = stack.pop()
            for y in supersedes.get(x, ()):
                if y == b:
                    return True
                if y not in seen:
                    seen.add(y); stack.append(y)
        return False


    def candidate_identity(v):
        if v.get("candidate_identity"):
            return v["candidate_identity"]
        obj = graph.get(v["subject"], {})
        return v["subject"] if obj.get("type") == "FiniteInstance" else None


    def relevant_authorities(v):
        wanted = axis_auth.get(v.get("axis"), set())
        rows = []
        for aid in v.get("authority_refs", []):
            a = authorities.get(aid)
            if not a:
                continue
            overlap = sorted(set(a.get("authority_scope", [])) & wanted)
            if overlap:
                rows.append((aid, overlap))
        return sorted(rows, key=lambda x:x[0])


    preserve = collections.defaultdict(list)
    for r in relations:
        if r.get("predicate") in {"PRESERVES","PRESERVES_NEGATIVE_RESULT","REPAIRS"} and str(r.get("subject","")).startswith("eset:verdict:") and str(r.get("object","")).startswith("eset:verdict:"):
            preserve[r["object"]].append({"by":r["subject"],"predicate":r["predicate"],"relation":r["id"]})
    for k in list(preserve):
        preserve[k] = sorted(preserve[k], key=lambda x:(x["by"],x["predicate"],x["relation"]))


    incoming_blocks = collections.defaultdict(list)
    for r in relations:
        if r.get("predicate") == "BLOCKS":
            incoming_blocks[r["object"]].append(r["subject"])


    blocking_states = {
        "OPEN","OPEN_BLOCKING","BLOCKED","FAILED","KILLED","NOT_ADMITTED",
        "NOT_VALIDATED","NOT_EXECUTED","NOT_OPENED","NOT_OPENED_BLOCKED","AUTHORITY_CONFLICT"
    }
    def declared_state(o):
        if not o:
            return None
        for f in ("status","current_status","value"):
            if f in o:
                return o[f]
        return o.get("derived_state")


    blocker_map = {}
    for target, blockers in incoming_blocks.items():
        rows = []
        for bid in sorted(blockers):
            bo = graph.get(bid)
            state = declared_state(bo)
            active = isinstance(state,str) and state in blocking_states
            if bo and bo.get("type") == "Requirement" and bo.get("status") not in {"SATISFIED","CLOSED","PASS","SUPERSEDED","NOT_APPLICABLE"}:
                active = True
            rows.append({"blocker":bid,"type":bo.get("type") if bo else None,"declared_state":state,"active_by_declared_state":active})
        blocker_map[target] = rows


    parts = collections.defaultdict(list)
    for v in verdicts:
        key = (v["subject"], candidate_identity(v), v["axis"], scope_key(v), v.get("resolution_facet", policy["facet_rule"]["default"]))
        parts[key].append(v)


    def suppressors(v, others):
        rv = [aid for aid,_ in relevant_authorities(v)]
        if not rv:
            return []
        hits = []
        for o in others:
            if o["id"] == v["id"]:
                continue
            ro = [aid for aid,_ in relevant_authorities(o)]
            if ro and all(any(transitive_supersedes(oa,va) for oa in ro) for va in rv):
                hits.append(o["id"])
        return sorted(hits)


    resolved = []
    for key, vals in sorted(parts.items(), key=lambda kv: tuple("" if x is None else str(x) for x in kv[0])):
        subject, candidate, axis, scope, facet = key
        suppressed = {}
        for v in vals:
            s = suppressors(v, vals)
            if s:
                suppressed[v["id"]] = s
        active = sorted([v for v in vals if v["id"] not in suppressed], key=lambda v:v["id"])
        gaps = [v["id"] for v in active if not relevant_authorities(v)]
        values = sorted({v["value"] for v in active})
        if gaps:
            state, status = "AUTHORITY_GAP", "FAIL_CLOSED"
        elif len(values) == 1:
            state, status = values[0], "RESOLVED"
        else:
            state, status = "AUTHORITY_CONFLICT", "FAIL_CLOSED"
        scope_issues = sorted(v["id"] for v in active if scope == "__UNSCOPED__" and v["value"] in scoped_values)
        rid = "resolve:" + hashlib.sha256("|".join("" if x is None else str(x) for x in key).encode()).hexdigest()[:20]
        resolved.append({
            "id":rid,"subject":subject,"candidate_identity":candidate,"axis":axis,"scope":scope,"facet":facet,
            "resolution_status":status,"resolved_state":state,
            "active_verdicts":sorted(v["id"] for v in active),"suppressed_verdicts":{k:suppressed[k] for k in sorted(suppressed)},
            "authority_basis":{v["id"]:[{"authority":aid,"matching_scopes":scopes} for aid,scopes in relevant_authorities(v)] for v in active},
            "effective_dates":{v["id"]:v.get("effective_date") for v in active if v.get("effective_date")},
            "preserved_history":{v["id"]:preserve.get(v["id"],[]) for v in vals if preserve.get(v["id"])},
            "scope_quality":"SCOPE_INCOMPLETE" if scope_issues else "EXPLICIT_OR_GLOBAL",
            "scope_issue_verdicts":scope_issues,"blocked_by":blocker_map.get(subject,[])
        })


    grouped = collections.defaultdict(list)
    for r in resolved:
        grouped[(r["subject"],r["axis"])].append(r)
    summaries = []
    for (subject,axis), rows in sorted(grouped.items()):
        states = sorted({r["resolved_state"] for r in rows})
        if "AUTHORITY_CONFLICT" in states:
            summary = "AUTHORITY_CONFLICT"
        elif "AUTHORITY_GAP" in states:
            summary = "AUTHORITY_GAP"
        elif len(states) == 1:
            summary = states[0]
        else:
            summary = "SCOPED_SET"
        summaries.append({
            "subject":subject,"axis":axis,"summary_state":summary,
            "partition_ids":[r["id"] for r in rows],"states":states,
            "scope_incomplete":any(r["scope_quality"]=="SCOPE_INCOMPLETE" for r in rows),
            "active_blockers":sum(1 for x in blocker_map.get(subject,[]) if x["active_by_declared_state"])
        })


    conflicts = [r for r in resolved if r["resolved_state"]=="AUTHORITY_CONFLICT"]
    gaps = [r for r in resolved if r["resolved_state"]=="AUTHORITY_GAP"]
    incomplete = [r for r in resolved if r["scope_quality"]=="SCOPE_INCOMPLETE"]
    missing_auth = sorted({aid for v in verdicts for aid in v.get("authority_refs",[]) if aid not in authorities})
    missing_end = sorted(r["id"] for r in relations if r.get("subject") not in graph or r.get("object") not in graph)
    killed = [v for v in verdicts if v.get("value")=="KILLED"]
    killed_non_instances = sorted(v["id"] for v in killed if graph.get(v["subject"],{}).get("type")!="FiniteInstance")


    canonical_objects = sorted(graph.values(), key=lambda o:o["id"])
    canonical_graph_bytes = json.dumps(canonical_objects,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    canonical_graph_sha256 = hashlib.sha256(canonical_graph_bytes).hexdigest()
    policy_semantic_bytes = json.dumps(policy,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    policy_semantic_sha256 = hashlib.sha256(policy_semantic_bytes).hexdigest()
    resolver_implementation_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

    audit = {
        "resolver_policy":policy["id"],"governing_authority":policy["governing_authority"],
        "canonical_graph_sha256":canonical_graph_sha256,"policy_semantic_sha256":policy_semantic_sha256,
        "resolver_implementation_sha256":resolver_implementation_sha256,
        "graph_files_scanned":len(byfile),"graph_objects_scanned":len(graph),"verdicts_scanned":len(verdicts),
        "resolution_partitions":len(resolved),"subject_axis_summaries":len(summaries),
        "authority_supersession_edges":sum(len(v) for v in supersedes.values()),
        "authority_conflicts":len(conflicts),"authority_gaps":len(gaps),"scope_incomplete":len(incomplete),
        "scope_incomplete_verdicts":[vid for r in incomplete for vid in r["scope_issue_verdicts"]],
        "scoped_set_summaries":sum(1 for s in summaries if s["summary_state"]=="SCOPED_SET"),
        "block_relations":sum(1 for r in relations if r.get("predicate")=="BLOCKS"),
        "blocked_targets":len(blocker_map),
        "targets_with_active_declared_blockers":sum(1 for rows in blocker_map.values() if any(x["active_by_declared_state"] for x in rows)),
        "claim_firewall":{
            "validated_verdicts":sum(1 for v in verdicts if v.get("value")=="VALIDATED"),
            "provider_admitted_verdicts":sum(1 for v in verdicts if v.get("value")=="PROVIDER_ADMITTED"),
            "killed_verdicts":len(killed),"killed_non_finite_instances":killed_non_instances,"resolver_inferred_promotions":0
        },
        "referential_checks":{"missing_authority_refs":missing_auth,"missing_relation_endpoints":missing_end},
        "pass_conditions":{
            "no_authority_conflict":not conflicts,"no_authority_gap":not gaps,
            "no_incomplete_scope":not incomplete,
            "no_missing_authority_refs":not missing_auth,"no_missing_relation_endpoints":not missing_end,
            "kill_scope_exact_finite_instance":not killed_non_instances,"no_inferred_promotion":True
        }
    }
    audit["resolver_execution_status"] = "PASS_SCOPED" if all(audit["pass_conditions"].values()) else "FAIL_CLOSED"


    resolved_path = out/"resolved_verdict_state_v0_2.jsonl"
    summary_path = out/"subject_axis_summary_v0_2.json"
    with resolved_path.open("w",encoding="utf-8") as fh:
        for r in resolved:
            fh.write(json.dumps(r,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n")
    summary_path.write_text(json.dumps(summaries,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    audit["resolved_output_sha256"] = hashlib.sha256(resolved_path.read_bytes()).hexdigest()
    audit["summary_output_sha256"] = hashlib.sha256(summary_path.read_bytes()).hexdigest()
    (out/"resolver_audit_v0_2.json").write_text(json.dumps(audit,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(audit,indent=2,sort_keys=True,ensure_ascii=False))


if __name__ == "__main__":
    main()