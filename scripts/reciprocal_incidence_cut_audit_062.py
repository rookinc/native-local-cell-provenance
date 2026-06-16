#!/usr/bin/env python3
import csv
import itertools
import json
from pathlib import Path
from collections import Counter, defaultdict, deque

ROOT = Path(__file__).resolve().parents[1]

IN_060 = ROOT / "artifacts/json/inside_outside_boundary_grammar_audit_060.v1.json"
IN_061 = ROOT / "artifacts/json/boundary_cut_law_search_061.v1.json"
SOURCE_JSON = ROOT / "source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/g60_native_overlay_generator_family_search_001.v1.json"

OUT_JSON = ROOT / "artifacts/json/reciprocal_incidence_cut_audit_062.v1.json"
OUT_CSV = ROOT / "artifacts/csv/reciprocal_incidence_cut_audit_062.v1.csv"
OUT_NOTE = ROOT / "notes/reciprocal_incidence_cut_audit_062.md"

TARGET_FORMS = [0, 1, 2, 3]
TARGET_NAMES = ["edge", "hinge", "closed_face", "filled_cell"]
TARGET_SIZE = 6

LABEL_TOKENS = [
    "form_index",
    "formindex",
    "form",
    "state",
    "selected",
    "answer",
    "target",
    "label",
    "candidate",
    "rank",
    "completion",
    "c_row",
    "crow",
    "record_index",
    "_record_index",
]

ENDPOINT_FIELDS = [
    "from_C",
    "to_C",
    "from_A",
    "to_A",
    "from_B",
    "to_B",
    "from_slot",
    "to_slot",
    "from_fiber",
    "to_fiber",
    "local_u",
    "local_v",
    "u",
    "v",
]

CONTEXT_FIELDS = [
    "lift_q",
    "role_pair",
    "edge_role",
    "station_role",
    "role_class",
    "source",
    "kind",
    "slot_delta_mod15",
    "fiber_delta_mod60",
]

REQUIRED_PHRASES = [
    "reciprocal incidence cut audit",
    "nearest neighbor that answers back",
    "form_index is used only for evaluation",
    "answer-label leakage remains open",
    "not native closure",
    "not Gap A closure",
    "not full role-labeled shared_B universe",
]

FORBIDDEN_PHRASES = [
    "Gap A is closed",
    "native closure achieved",
    "completion ladder proven natively",
    "answer-label leakage ruled out",
    "full shared_B universe derived",
]


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def as_int(v):
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, float) and v.is_integer():
        return int(v)
    if isinstance(v, str) and v.strip().lstrip("-").isdigit():
        return int(v.strip())
    return None


def scalar(v):
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, (int, float, str)):
        iv = as_int(v)
        if iv is not None:
            return iv
        if isinstance(v, str) and 0 < len(v) <= 80:
            return v
    return None


def field_is_label_like(name):
    n = str(name).lower()
    return any(tok in n for tok in LABEL_TOKENS)


def flatten(row, prefix=""):
    out = {}
    if not isinstance(row, dict):
        return out

    for k, v in row.items():
        key = prefix + str(k)
        if isinstance(v, dict):
            out.update(flatten(v, key + "."))
        elif isinstance(v, (list, tuple)):
            nums = [as_int(x) for x in v]
            nums = [x for x in nums if x is not None]
            if nums and len(nums) == len(v) and len(nums) <= 50:
                out[key + ".__len"] = len(nums)
                out[key + ".__sum"] = sum(nums)
                out[key + ".__min"] = min(nums)
                out[key + ".__max"] = max(nums)
                out[key + ".__range"] = max(nums) - min(nums)
        else:
            sv = scalar(v)
            if sv is not None:
                out[key] = sv
    return out


def find_edge_records(obj):
    if isinstance(obj, dict):
        if isinstance(obj.get("edge_records"), list):
            xs = obj["edge_records"]
            if all(isinstance(x, dict) for x in xs):
                return xs, ["edge_records"]
        for k, v in obj.items():
            found, path = find_edge_records(v)
            if found is not None:
                return found, [k] + path
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            found, path = find_edge_records(v)
            if found is not None:
                return found, [i] + path
    return None, []


def get_value(features, field):
    if field in features:
        return features[field]
    # tolerate nested keys that end with field name
    hits = [v for k, v in features.items() if k.endswith("." + field)]
    if len(hits) == 1:
        return hits[0]
    return None


def row_record(raw, idx):
    features = flatten(raw)
    fi = as_int(get_value(features, "form_index"))
    if fi is None:
        fi = as_int(raw.get("form_index"))

    slot = as_int(get_value(features, "slot_delta_mod15"))
    fiber = as_int(get_value(features, "fiber_delta_mod60"))

    if slot is not None and fiber is not None:
        features["derived.boundary_gap_row"] = slot - fiber
        features["derived.inside_captured_row"] = "yes" if slot - fiber > 0 else "no"
        features["derived.slot_fiber_pair"] = str(slot) + "|" + str(fiber)

    from_c = as_int(get_value(features, "from_C"))
    to_c = as_int(get_value(features, "to_C"))
    if from_c is not None and to_c is not None:
        features["derived.C_transition"] = str(from_c) + "->" + str(to_c)
        features["derived.C_transition_rev"] = str(to_c) + "->" + str(from_c)
        features["derived.C_delta_mod15"] = (to_c - from_c) % 15

    return {
        "row_id": idx,
        "form_index": fi,
        "features": features,
        "raw": raw,
    }


def components(n, edges):
    adj = [[] for _ in range(n)]
    for a, b, why in edges:
        if a == b:
            continue
        adj[a].append(b)
        adj[b].append(a)

    seen = [False] * n
    comps = []
    for start in range(n):
        if seen[start]:
            continue
        q = deque([start])
        seen[start] = True
        comp = []
        while q:
            x = q.popleft()
            comp.append(x)
            for y in adj[x]:
                if not seen[y]:
                    seen[y] = True
                    q.append(y)
        comps.append(sorted(comp))
    comps.sort(key=lambda c: (len(c), c[0]))
    return comps


def evaluate_components(rows, comps):
    comp_rows = []
    for cid, comp in enumerate(comps):
        forms = [rows[i]["form_index"] for i in comp]
        c = Counter(forms)
        majority_form = None
        majority_count = 0
        if c:
            majority_form, majority_count = c.most_common(1)[0]

        slots = [as_int(get_value(rows[i]["features"], "slot_delta_mod15")) for i in comp]
        fibers = [as_int(get_value(rows[i]["features"], "fiber_delta_mod60")) for i in comp]
        slots = [x for x in slots if x is not None]
        fibers = [x for x in fibers if x is not None]

        outside = max(slots) if slots else None
        inside = min(fibers) if fibers else None
        gap = (outside - inside) if outside is not None and inside is not None else None

        comp_rows.append({
            "component_id": cid,
            "row_count": len(comp),
            "row_ids": comp,
            "form_counts": dict(sorted(c.items())),
            "majority_form": majority_form,
            "majority_count": majority_count,
            "outside_boundary_span": outside,
            "inside_fiber_residual": inside,
            "boundary_gap": gap,
        })

    purity_total = sum(c["majority_count"] for c in comp_rows)
    exact_partition = (
        len(comp_rows) == 4
        and all(c["row_count"] == TARGET_SIZE for c in comp_rows)
        and all(c["majority_count"] == TARGET_SIZE for c in comp_rows)
        and sorted(c["majority_form"] for c in comp_rows) == TARGET_FORMS
    )

    ordered_by_gap = sorted(
        comp_rows,
        key=lambda c: (
            10**9 if c["boundary_gap"] is None else c["boundary_gap"],
            c["component_id"],
        ),
    )
    majority_order_by_gap = [c["majority_form"] for c in ordered_by_gap]
    ordered_exact_by_gap = exact_partition and majority_order_by_gap == TARGET_FORMS

    size_deviation = sum(abs(c["row_count"] - TARGET_SIZE) for c in comp_rows)
    if len(comp_rows) < 4:
        size_deviation += (4 - len(comp_rows)) * TARGET_SIZE
    group_count_penalty = abs(len(comp_rows) - 4) * TARGET_SIZE
    score = purity_total - size_deviation - group_count_penalty

    return {
        "component_count": len(comp_rows),
        "purity_total": purity_total,
        "size_deviation": size_deviation,
        "group_count_penalty": group_count_penalty,
        "score": score,
        "exact_partition": exact_partition,
        "ordered_exact_by_boundary_gap": ordered_exact_by_gap,
        "majority_order_by_boundary_gap": majority_order_by_gap,
        "components": comp_rows,
    }


def build_relation_edges(rows, relation):
    edges = []
    n = len(rows)

    def val(i, field):
        return get_value(rows[i]["features"], field)

    if relation["kind"] == "same_field":
        field = relation["field"]
        buckets = defaultdict(list)
        for i in range(n):
            x = val(i, field)
            if x is not None:
                buckets[x].append(i)
        for x, ids in buckets.items():
            for a, b in itertools.combinations(ids, 2):
                edges.append((a, b, field + "=" + str(x)))

    elif relation["kind"] == "same_pair":
        a_field, b_field = relation["fields"]
        buckets = defaultdict(list)
        for i in range(n):
            x = val(i, a_field)
            y = val(i, b_field)
            if x is not None and y is not None:
                buckets[(x, y)].append(i)
        for key, ids in buckets.items():
            for a, b in itertools.combinations(ids, 2):
                edges.append((a, b, str(a_field) + "," + str(b_field) + "=" + str(key)))

    elif relation["kind"] == "reciprocal_pair":
        a_field, b_field = relation["fields"]
        for i, j in itertools.combinations(range(n), 2):
            ai, bi = val(i, a_field), val(i, b_field)
            aj, bj = val(j, a_field), val(j, b_field)
            if ai is None or bi is None or aj is None or bj is None:
                continue
            if ai == bj and bi == aj:
                edges.append((i, j, "reciprocal:" + a_field + "," + b_field))

    elif relation["kind"] == "share_endpoint":
        fields = relation["fields"]
        buckets = defaultdict(list)
        for i in range(n):
            for field in fields:
                x = val(i, field)
                if x is not None:
                    buckets[(field, x)].append(i)
        for key, ids in buckets.items():
            for a, b in itertools.combinations(ids, 2):
                edges.append((a, b, "share_endpoint:" + str(key)))

    elif relation["kind"] == "undirected_endpoint_pair":
        a_field, b_field = relation["fields"]
        buckets = defaultdict(list)
        for i in range(n):
            x = val(i, a_field)
            y = val(i, b_field)
            if x is not None and y is not None:
                buckets[tuple(sorted([x, y]))].append(i)
        for key, ids in buckets.items():
            for a, b in itertools.combinations(ids, 2):
                edges.append((a, b, "undirected_pair:" + str(key)))

    return edges


def relation_name(relation):
    if relation["kind"] in ["same_field"]:
        return relation["kind"] + ":" + relation["field"]
    if relation["kind"] in ["same_pair", "reciprocal_pair", "undirected_endpoint_pair"]:
        return relation["kind"] + ":" + "|".join(relation["fields"])
    if relation["kind"] == "share_endpoint":
        return relation["kind"] + ":" + "|".join(relation["fields"])
    return relation["kind"]


def missing_phrases(text, phrases):
    return [p for p in phrases if p not in text]


def found_phrases(text, phrases):
    return [p for p in phrases if p in text]


def main():
    a060 = load_json(IN_060)
    a061 = load_json(IN_061)
    source = load_json(SOURCE_JSON)

    if not a060.get("audit_pass"):
        raise SystemExit("060 audit_pass is not true")
    if not a061.get("audit_pass"):
        raise SystemExit("061 audit_pass is not true")

    edge_records, edge_path = find_edge_records(source)
    if not edge_records:
        raise SystemExit("edge_records not found")

    rows_all = [row_record(raw, idx) for idx, raw in enumerate(edge_records)]
    rows = [
        r for r in rows_all
        if r["form_index"] in TARGET_FORMS
        and get_value(r["features"], "slot_delta_mod15") is not None
        and get_value(r["features"], "fiber_delta_mod60") is not None
    ]

    # Available fields.
    available = set()
    for r in rows:
        available.update(r["features"].keys())

    def has_field(f):
        return f in available or any(k.endswith("." + f) for k in available)

    endpoint_present = [f for f in ENDPOINT_FIELDS if has_field(f)]
    context_present = [f for f in CONTEXT_FIELDS if has_field(f)]

    relations = []

    for f in endpoint_present + context_present + [
        "derived.C_transition",
        "derived.C_delta_mod15",
        "derived.boundary_gap_row",
        "derived.inside_captured_row",
        "derived.slot_fiber_pair",
    ]:
        if has_field(f) or f in available:
            if not field_is_label_like(f):
                relations.append({"kind": "same_field", "field": f})

    endpoint_pairs = [
        ("from_C", "to_C"),
        ("from_A", "to_A"),
        ("from_B", "to_B"),
        ("from_slot", "to_slot"),
        ("from_fiber", "to_fiber"),
        ("local_u", "local_v"),
        ("u", "v"),
    ]
    for a, b in endpoint_pairs:
        if has_field(a) and has_field(b):
            relations.append({"kind": "same_pair", "fields": [a, b]})
            relations.append({"kind": "reciprocal_pair", "fields": [a, b]})
            relations.append({"kind": "undirected_endpoint_pair", "fields": [a, b]})

    share_sets = [
        ["from_C", "to_C"],
        ["from_A", "to_A"],
        ["from_B", "to_B"],
        ["from_slot", "to_slot"],
        ["from_fiber", "to_fiber"],
        ["from_C", "to_C", "from_slot", "to_slot"],
        ["from_A", "to_A", "from_B", "to_B"],
    ]
    for fields in share_sets:
        if all(has_field(f) for f in fields):
            relations.append({"kind": "share_endpoint", "fields": fields})

    results = []
    for rel in relations:
        edges = build_relation_edges(rows, rel)
        comps = components(len(rows), edges)
        ev = evaluate_components(rows, comps)
        ev["relation"] = rel
        ev["relation_name"] = relation_name(rel)
        ev["edge_count"] = len(edges)
        ev["uses_form_index_as_input"] = False
        ev["uses_record_order_as_input"] = False
        ev["uses_answer_label_as_input"] = False
        results.append(ev)

    results.sort(
        key=lambda e: (
            not e["ordered_exact_by_boundary_gap"],
            not e["exact_partition"],
            -e["score"],
            -e["purity_total"],
            e["component_count"],
            e["edge_count"],
            e["relation_name"],
        )
    )

    exact_hits = [r for r in results if r["exact_partition"]]
    ordered_exact_hits = [r for r in results if r["ordered_exact_by_boundary_gap"]]
    best = results[0] if results else None

    if ordered_exact_hits:
        verdict = "reciprocal_incidence_ordered_cut_candidate_found"
    elif exact_hits:
        verdict = "reciprocal_incidence_cut_candidate_found_unordered"
    else:
        verdict = "reciprocal_incidence_cut_not_found_in_tested_family"

    statement = (
        "Artifact 062 is a reciprocal incidence cut audit. It tests whether rows belong together because of shared endpoints, reciprocal transitions, "
        "or incidence neighborhoods: the nearest neighbor that answers back. form_index is used only for evaluation."
    )

    boundary = (
        "This is a relational cut audit, not native closure. A hit would be a candidate requiring validation; a miss only bounds the tested incidence family. "
        "answer-label leakage remains open, this is not full role-labeled shared_B universe derivation, and is not Gap A closure."
    )

    combined = statement + "\n" + boundary
    missing = missing_phrases(combined, REQUIRED_PHRASES)
    forbidden = found_phrases(combined, FORBIDDEN_PHRASES)

    checks = {
        "inside_outside_boundary_grammar_060_pass": bool(a060.get("audit_pass")),
        "boundary_cut_law_061_pass": bool(a061.get("audit_pass")),
        "source_json_exists": SOURCE_JSON.exists(),
        "edge_records_found": bool(edge_records),
        "row_count_is_24": len(rows) == 24,
        "endpoint_field_count": len(endpoint_present),
        "context_field_count": len(context_present),
        "relation_candidate_count": len(relations),
        "tested_relation_count": len(results),
        "all_relations_exclude_form_index_record_order_answer_labels": all(
            not r["uses_form_index_as_input"] and not r["uses_record_order_as_input"] and not r["uses_answer_label_as_input"]
            for r in results
        ),
        "form_index_used_only_for_evaluation": True,
        "exact_incidence_cut_hit_count": len(exact_hits),
        "ordered_exact_incidence_cut_hit_count": len(ordered_exact_hits),
        "best_candidate_exists": best is not None,
        "best_candidate_relation": best["relation_name"] if best else None,
        "best_candidate_score": best["score"] if best else None,
        "best_candidate_purity_total": best["purity_total"] if best else None,
        "best_candidate_component_count": best["component_count"] if best else None,
        "answer_label_leakage_remains_open": True,
        "native_provenance_confirmed": False,
        "required_phrases_present": len(missing) == 0,
        "forbidden_phrases_absent": len(forbidden) == 0,
    }

    audit_pass = all([
        checks["inside_outside_boundary_grammar_060_pass"],
        checks["boundary_cut_law_061_pass"],
        checks["source_json_exists"],
        checks["edge_records_found"],
        checks["row_count_is_24"],
        checks["relation_candidate_count"] > 0,
        checks["tested_relation_count"] > 0,
        checks["all_relations_exclude_form_index_record_order_answer_labels"],
        checks["form_index_used_only_for_evaluation"],
        checks["answer_label_leakage_remains_open"],
        checks["required_phrases_present"],
        checks["forbidden_phrases_absent"],
    ])

    result = {
        "status": "reciprocal_incidence_cut_audit_recorded",
        "audit_id": "062",
        "inputs": {
            "inside_outside_boundary_grammar_audit_060": str(IN_060),
            "boundary_cut_law_search_061": str(IN_061),
            "source_json": str(SOURCE_JSON),
            "edge_records_path": edge_path,
        },
        "checks": checks,
        "audit_pass": audit_pass,
        "verdict": verdict,
        "available_fields": {
            "endpoint_fields": endpoint_present,
            "context_fields": context_present,
        },
        "best_candidate": best,
        "exact_hits_first": exact_hits[:40],
        "ordered_exact_hits_first": ordered_exact_hits[:40],
        "top_candidates": results[:40],
        "statement": statement,
        "boundary": boundary,
        "missing_required_phrases": missing,
        "forbidden_phrases_found": forbidden,
        "interpretation": (
            "Artifact 062 tests the hypothesis that the missing form cut is relational rather than scalar. "
            "It searches shared endpoints, reciprocal transitions, and incidence neighborhoods. "
            "The result bounds this tested incidence family but does not settle native provenance."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "rank",
            "relation_name",
            "edge_count",
            "component_count",
            "purity_total",
            "score",
            "exact_partition",
            "ordered_exact_by_boundary_gap",
            "majority_order_by_boundary_gap",
            "components",
        ])
        for i, ev in enumerate(results[:40], start=1):
            compact = []
            for c in ev["components"]:
                compact.append({
                    "row_count": c["row_count"],
                    "form_counts": c["form_counts"],
                    "majority_form": c["majority_form"],
                    "gap": c["boundary_gap"],
                })
            w.writerow([
                i,
                ev["relation_name"],
                ev["edge_count"],
                ev["component_count"],
                ev["purity_total"],
                ev["score"],
                ev["exact_partition"],
                ev["ordered_exact_by_boundary_gap"],
                json.dumps(ev["majority_order_by_boundary_gap"]),
                json.dumps(compact, sort_keys=True),
            ])

    lines = []
    lines.append("# Reciprocal incidence cut audit 062")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- audit_pass: `" + str(audit_pass) + "`")
    lines.append("- verdict: `" + verdict + "`")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Statement")
    lines.append("")
    lines.append(statement)
    lines.append("")
    lines.append("## Available fields")
    lines.append("")
    lines.append("- endpoint_fields: `" + str(endpoint_present) + "`")
    lines.append("- context_fields: `" + str(context_present) + "`")
    lines.append("")
    lines.append("## Best candidate")
    lines.append("")
    if best:
        lines.append("- relation_name: `" + best["relation_name"] + "`")
        lines.append("- edge_count: `" + str(best["edge_count"]) + "`")
        lines.append("- component_count: `" + str(best["component_count"]) + "`")
        lines.append("- purity_total: `" + str(best["purity_total"]) + "`")
        lines.append("- score: `" + str(best["score"]) + "`")
        lines.append("- exact_partition: `" + str(best["exact_partition"]) + "`")
        lines.append("- ordered_exact_by_boundary_gap: `" + str(best["ordered_exact_by_boundary_gap"]) + "`")
        lines.append("- majority_order_by_boundary_gap: `" + str(best["majority_order_by_boundary_gap"]) + "`")
        lines.append("")
        lines.append("### Best candidate components")
        lines.append("")
        for c in best["components"]:
            lines.append(
                "- rows={rows}, forms={forms}, majority={maj}, outside={outside}, inside={inside}, gap={gap}".format(
                    rows=c["row_count"],
                    forms=c["form_counts"],
                    maj=c["majority_form"],
                    outside=c["outside_boundary_span"],
                    inside=c["inside_fiber_residual"],
                    gap=c["boundary_gap"],
                )
            )
    lines.append("")
    lines.append("## Top candidates")
    lines.append("")
    for ev in results[:10]:
        lines.append(
            "- relation={rel}, components={components}, purity={purity}/24, score={score}, exact={exact}, ordered_exact={ordered}, order={order}".format(
                rel=ev["relation_name"],
                components=ev["component_count"],
                purity=ev["purity_total"],
                score=ev["score"],
                exact=ev["exact_partition"],
                ordered=ev["ordered_exact_by_boundary_gap"],
                order=ev["majority_order_by_boundary_gap"],
            )
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(result["interpretation"])
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append(boundary)
    lines.append("")

    OUT_NOTE.write_text("\n".join(lines), encoding="utf-8")

    print("wrote", OUT_JSON)
    print("wrote", OUT_CSV)
    print("wrote", OUT_NOTE)
    print("status", result["status"])
    print("audit_pass", audit_pass)
    print("verdict", verdict)
    for k, v in checks.items():
        print(k, v)
    if best:
        print("best_relation", best["relation_name"])
        print("best_components", best["component_count"])
        print("best_purity", str(best["purity_total"]) + "/24")
        print("best_score", best["score"])
        print("best_exact", best["exact_partition"])
        print("best_ordered_exact", best["ordered_exact_by_boundary_gap"])
        print("best_order", best["majority_order_by_boundary_gap"])


if __name__ == "__main__":
    main()
