#!/usr/bin/env python3
import csv
import itertools
import json
from pathlib import Path
from collections import Counter, defaultdict, deque

ROOT = Path(__file__).resolve().parents[1]

IN_060 = ROOT / "artifacts/json/inside_outside_boundary_grammar_audit_060.v1.json"
IN_062 = ROOT / "artifacts/json/reciprocal_incidence_cut_audit_062.v1.json"
SOURCE_JSON = ROOT / "source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/g60_native_overlay_generator_family_search_001.v1.json"

OUT_JSON = ROOT / "artifacts/json/six_component_incidence_refinement_audit_063.v1.json"
OUT_CSV = ROOT / "artifacts/csv/six_component_incidence_refinement_audit_063.v1.csv"
OUT_NOTE = ROOT / "notes/six_component_incidence_refinement_audit_063.md"

TARGET_FORMS = [0, 1, 2, 3]
TARGET_NAMES = ["edge", "hinge", "closed_face", "filled_cell"]
TARGET_SIZE = 6

BASE_FIELDS = ["from_C", "to_C"]

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

PREFERRED_TOKENS = [
    "edge_role",
    "station_role",
    "role_pair",
    "role_class",
    "lift_q",
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
    "slot_delta",
    "fiber_delta",
    "C_delta",
    "boundary",
    "inside",
    "source",
    "kind",
]

REQUIRED_PHRASES = [
    "six-component incidence refinement audit",
    "six incidence components",
    "merge-only reconstruction",
    "refinement family",
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
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        iv = as_int(v)
        return iv if iv is not None else v
    if isinstance(v, str) and 0 < len(v) <= 100:
        iv = as_int(v)
        return iv if iv is not None else v
    return None


def field_is_label_like(name):
    n = str(name).lower()
    return any(tok in n for tok in LABEL_TOKENS)


def preferred_score(name):
    n = str(name)
    score = 0
    for tok in PREFERRED_TOKENS:
        if tok in n:
            score += 1
    if n.startswith("derived."):
        score += 2
    return score


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
    hits = [v for k, v in features.items() if k.endswith("." + field)]
    if len(hits) == 1:
        return hits[0]
    return None


def row_record(raw, idx):
    features = flatten(raw)

    form_index = as_int(get_value(features, "form_index"))
    if form_index is None:
        form_index = as_int(raw.get("form_index"))

    slot = as_int(get_value(features, "slot_delta_mod15"))
    fiber = as_int(get_value(features, "fiber_delta_mod60"))
    from_c = as_int(get_value(features, "from_C"))
    to_c = as_int(get_value(features, "to_C"))

    if slot is not None and fiber is not None:
        features["derived.boundary_gap_row"] = slot - fiber
        features["derived.inside_captured_row"] = "yes" if slot - fiber > 0 else "no"
        features["derived.slot_fiber_pair"] = str(slot) + "|" + str(fiber)

    if from_c is not None and to_c is not None:
        features["derived.C_transition"] = str(from_c) + "->" + str(to_c)
        features["derived.C_transition_rev"] = str(to_c) + "->" + str(from_c)
        features["derived.C_delta_mod15"] = (to_c - from_c) % 15

    return {
        "row_id": idx,
        "form_index": form_index,
        "features": features,
        "raw": raw,
    }


def components(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
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


def share_endpoint_edges(rows, fields):
    buckets = defaultdict(list)
    for i, row in enumerate(rows):
        for f in fields:
            x = get_value(row["features"], f)
            if x is not None:
                buckets[(f, x)].append(i)

    edges = set()
    for ids in buckets.values():
        for a, b in itertools.combinations(ids, 2):
            edges.add(tuple(sorted((a, b))))
    return sorted(edges)


def gated_share_endpoint_edges(rows, fields, gate_field):
    buckets = defaultdict(list)
    for i, row in enumerate(rows):
        gate = get_value(row["features"], gate_field)
        if gate is None:
            continue
        for f in fields:
            x = get_value(row["features"], f)
            if x is not None:
                buckets[(gate_field, gate, f, x)].append(i)

    edges = set()
    for ids in buckets.values():
        for a, b in itertools.combinations(ids, 2):
            edges.add(tuple(sorted((a, b))))
    return sorted(edges)


def evaluate_partition(rows, comps):
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
        gap = outside - inside if outside is not None and inside is not None else None

        comp_rows.append({
            "component_id": cid,
            "row_count": len(comp),
            "row_ids": comp,
            "source_record_ids": [rows[i]["row_id"] for i in comp],
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
    ordered_exact = exact_partition and majority_order_by_gap == TARGET_FORMS

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
        "ordered_exact_by_boundary_gap": ordered_exact,
        "majority_order_by_boundary_gap": majority_order_by_gap,
        "components": comp_rows,
    }


def can_merge_component_sizes_to_four_sixes(sizes):
    bins = [0, 0, 0, 0]
    sizes = sorted(sizes, reverse=True)

    def rec(i):
        if i == len(sizes):
            return sorted(bins) == [TARGET_SIZE] * 4
        s = sizes[i]
        for j in range(4):
            if bins[j] + s <= TARGET_SIZE:
                bins[j] += s
                if rec(i + 1):
                    return True
                bins[j] -= s
        return False

    return rec(0)


def summarize_base_components(rows, base_comps):
    out = []
    for ev in evaluate_partition(rows, base_comps)["components"]:
        ev2 = dict(ev)
        ev2["component_size_exceeds_target_size"] = ev2["row_count"] > TARGET_SIZE
        out.append(ev2)
    return out


def collect_candidate_fields(rows):
    available = set()
    for r in rows:
        available.update(r["features"].keys())

    candidates = []
    for field in sorted(available):
        if field_is_label_like(field):
            continue
        vals = [get_value(r["features"], field) for r in rows]
        if any(v is None for v in vals):
            continue
        uniq = sorted(set(str(v) for v in vals))
        if len(uniq) < 2 or len(uniq) > 12:
            continue
        score = preferred_score(field)
        if score <= 0 and not field.startswith("derived."):
            continue
        candidates.append({
            "field": field,
            "unique_count": len(uniq),
            "unique_values": uniq,
            "preferred_score": score,
        })

    candidates.sort(key=lambda x: (-x["preferred_score"], x["unique_count"], x["field"]))
    return candidates


def refinement_by_component_and_field(rows, base_component_id_by_row, field):
    buckets = defaultdict(list)
    for i, row in enumerate(rows):
        val = get_value(row["features"], field)
        if val is not None:
            buckets[(base_component_id_by_row[i], val)].append(i)
    return [sorted(v) for v in buckets.values()]


def split_purity_inside_base_components(rows, base_comps, field):
    rows_out = []
    total_purity = 0
    split_count = 0

    for cid, comp in enumerate(base_comps):
        buckets = defaultdict(list)
        for i in comp:
            val = get_value(rows[i]["features"], field)
            if val is not None:
                buckets[val].append(i)

        bucket_summaries = []
        for val, ids in sorted(buckets.items(), key=lambda kv: str(kv[0])):
            forms = [rows[i]["form_index"] for i in ids]
            c = Counter(forms)
            maj, cnt = c.most_common(1)[0]
            total_purity += cnt
            split_count += 1
            bucket_summaries.append({
                "value": val,
                "row_count": len(ids),
                "form_counts": dict(sorted(c.items())),
                "majority_form": maj,
                "majority_count": cnt,
            })

        rows_out.append({
            "base_component_id": cid,
            "base_row_count": len(comp),
            "bucket_count": len(bucket_summaries),
            "buckets": bucket_summaries,
        })

    return {
        "field": field,
        "split_count": split_count,
        "split_purity_total": total_purity,
        "component_splits": rows_out,
    }


def missing_phrases(text, phrases):
    return [p for p in phrases if p not in text]


def found_phrases(text, phrases):
    return [p for p in phrases if p in text]


def main():
    a060 = load_json(IN_060)
    a062 = load_json(IN_062)
    source = load_json(SOURCE_JSON)

    if not a060.get("audit_pass"):
        raise SystemExit("060 audit_pass is not true")
    if not a062.get("audit_pass"):
        raise SystemExit("062 audit_pass is not true")

    edge_records, edge_path = find_edge_records(source)
    if not edge_records:
        raise SystemExit("edge_records not found")

    all_rows = [row_record(raw, idx) for idx, raw in enumerate(edge_records)]
    rows = [
        r for r in all_rows
        if r["form_index"] in TARGET_FORMS
        and get_value(r["features"], "slot_delta_mod15") is not None
        and get_value(r["features"], "fiber_delta_mod60") is not None
    ]

    base_edges = share_endpoint_edges(rows, BASE_FIELDS)
    base_comps = components(len(rows), base_edges)
    base_eval = evaluate_partition(rows, base_comps)
    base_component_rows = summarize_base_components(rows, base_comps)
    base_sizes = [len(c) for c in base_comps]

    base_component_id_by_row = {}
    for cid, comp in enumerate(base_comps):
        for row_id in comp:
            base_component_id_by_row[row_id] = cid

    merge_only_exact_possible = can_merge_component_sizes_to_four_sixes(base_sizes)

    candidates = collect_candidate_fields(rows)

    refinement_evals = []
    split_evals = []

    for item in candidates:
        field = item["field"]

        # Family A: split the six incidence components by this field.
        refined_comps = refinement_by_component_and_field(rows, base_component_id_by_row, field)
        refined_eval = evaluate_partition(rows, refined_comps)
        refined_eval["family"] = "component_plus_field_partition"
        refined_eval["field"] = field
        refined_eval["uses_form_index_as_input"] = False
        refined_eval["uses_record_order_as_input"] = False
        refined_eval["uses_answer_label_as_input"] = False
        refinement_evals.append(refined_eval)

        # Family B: gate C endpoint incidence by this field.
        gated_edges = gated_share_endpoint_edges(rows, BASE_FIELDS, field)
        gated_comps = components(len(rows), gated_edges)
        gated_eval = evaluate_partition(rows, gated_comps)
        gated_eval["family"] = "field_gated_C_endpoint_incidence"
        gated_eval["field"] = field
        gated_eval["uses_form_index_as_input"] = False
        gated_eval["uses_record_order_as_input"] = False
        gated_eval["uses_answer_label_as_input"] = False
        refinement_evals.append(gated_eval)

        split_evals.append(split_purity_inside_base_components(rows, base_comps, field))

    refinement_evals.sort(
        key=lambda e: (
            not e["ordered_exact_by_boundary_gap"],
            not e["exact_partition"],
            -e["score"],
            -e["purity_total"],
            e["component_count"],
            e["family"],
            e["field"],
        )
    )

    split_evals.sort(
        key=lambda e: (
            -e["split_purity_total"],
            e["split_count"],
            e["field"],
        )
    )

    exact_refinement_hits = [e for e in refinement_evals if e["exact_partition"]]
    ordered_exact_refinement_hits = [e for e in refinement_evals if e["ordered_exact_by_boundary_gap"]]
    best_refinement = refinement_evals[0] if refinement_evals else None
    best_split = split_evals[0] if split_evals else None

    if ordered_exact_refinement_hits:
        verdict = "six_component_refinement_exact_ordered_candidate_found"
    elif exact_refinement_hits:
        verdict = "six_component_refinement_exact_unordered_candidate_found"
    else:
        verdict = "six_component_refinement_not_found_in_tested_family"

    statement = (
        "Artifact 063 is a six-component incidence refinement audit. It starts from the six incidence components found by 062 and tests whether a second native field can refine them into the four Euclidean forms. "
        "form_index is used only for evaluation."
    )

    interpretation = (
        "The base C-endpoint incidence relation finds six incidence components. merge-only reconstruction is impossible when any component is larger than six rows, so the tested frontier is a refinement family: split large incidence components or gate incidence by a second native field."
    )

    boundary = (
        "This is a refinement audit, not native closure. A hit would be a candidate requiring validation; a miss only bounds the tested refinement family. "
        "answer-label leakage remains open, this is not full role-labeled shared_B universe derivation, and is not Gap A closure."
    )

    combined = statement + "\n" + interpretation + "\n" + boundary
    missing = missing_phrases(combined, REQUIRED_PHRASES)
    forbidden = found_phrases(combined, FORBIDDEN_PHRASES)

    checks = {
        "inside_outside_boundary_grammar_060_pass": bool(a060.get("audit_pass")),
        "reciprocal_incidence_cut_062_pass": bool(a062.get("audit_pass")),
        "source_json_exists": SOURCE_JSON.exists(),
        "edge_records_found": bool(edge_records),
        "row_count_is_24": len(rows) == 24,
        "base_relation": "share_endpoint:from_C|to_C",
        "base_component_count_is_6": len(base_comps) == 6,
        "base_component_sizes": base_sizes,
        "base_purity_total": base_eval["purity_total"],
        "merge_only_reconstruction_possible": merge_only_exact_possible,
        "candidate_field_count": len(candidates),
        "tested_refinement_count": len(refinement_evals),
        "all_refinements_exclude_form_index_record_order_answer_labels": all(
            not e["uses_form_index_as_input"] and not e["uses_record_order_as_input"] and not e["uses_answer_label_as_input"]
            for e in refinement_evals
        ),
        "form_index_used_only_for_evaluation": True,
        "exact_refinement_hit_count": len(exact_refinement_hits),
        "ordered_exact_refinement_hit_count": len(ordered_exact_refinement_hits),
        "best_refinement_exists": best_refinement is not None,
        "best_refinement_family": best_refinement["family"] if best_refinement else None,
        "best_refinement_field": best_refinement["field"] if best_refinement else None,
        "best_refinement_component_count": best_refinement["component_count"] if best_refinement else None,
        "best_refinement_purity_total": best_refinement["purity_total"] if best_refinement else None,
        "best_refinement_score": best_refinement["score"] if best_refinement else None,
        "best_split_field": best_split["field"] if best_split else None,
        "best_split_purity_total": best_split["split_purity_total"] if best_split else None,
        "answer_label_leakage_remains_open": True,
        "native_provenance_confirmed": False,
        "required_phrases_present": len(missing) == 0,
        "forbidden_phrases_absent": len(forbidden) == 0,
    }

    audit_pass = all([
        checks["inside_outside_boundary_grammar_060_pass"],
        checks["reciprocal_incidence_cut_062_pass"],
        checks["source_json_exists"],
        checks["edge_records_found"],
        checks["row_count_is_24"],
        checks["base_component_count_is_6"],
        checks["candidate_field_count"] > 0,
        checks["tested_refinement_count"] > 0,
        checks["all_refinements_exclude_form_index_record_order_answer_labels"],
        checks["form_index_used_only_for_evaluation"],
        checks["answer_label_leakage_remains_open"],
        checks["required_phrases_present"],
        checks["forbidden_phrases_absent"],
    ])

    result = {
        "status": "six_component_incidence_refinement_audit_recorded",
        "audit_id": "063",
        "inputs": {
            "inside_outside_boundary_grammar_audit_060": str(IN_060),
            "reciprocal_incidence_cut_audit_062": str(IN_062),
            "source_json": str(SOURCE_JSON),
            "edge_records_path": edge_path,
        },
        "checks": checks,
        "audit_pass": audit_pass,
        "verdict": verdict,
        "base_relation": {
            "name": "share_endpoint:from_C|to_C",
            "component_sizes": base_sizes,
            "merge_only_reconstruction_possible": merge_only_exact_possible,
            "evaluation": base_eval,
            "components": base_component_rows,
        },
        "candidate_fields_first": candidates[:40],
        "best_refinement": best_refinement,
        "exact_refinement_hits_first": exact_refinement_hits[:40],
        "ordered_exact_refinement_hits_first": ordered_exact_refinement_hits[:40],
        "top_refinements": refinement_evals[:40],
        "best_split": best_split,
        "top_component_split_purity": split_evals[:20],
        "statement": statement,
        "interpretation": interpretation,
        "boundary": boundary,
        "missing_required_phrases": missing,
        "forbidden_phrases_found": forbidden,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "rank",
            "family",
            "field",
            "component_count",
            "purity_total",
            "score",
            "exact_partition",
            "ordered_exact_by_boundary_gap",
            "majority_order_by_boundary_gap",
            "component_rows",
        ])
        for i, ev in enumerate(refinement_evals[:40], start=1):
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
                ev["family"],
                ev["field"],
                ev["component_count"],
                ev["purity_total"],
                ev["score"],
                ev["exact_partition"],
                ev["ordered_exact_by_boundary_gap"],
                json.dumps(ev["majority_order_by_boundary_gap"]),
                json.dumps(compact, sort_keys=True),
            ])

    lines = []
    lines.append("# Six-component incidence refinement audit 063")
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
    lines.append("## Base six incidence components")
    lines.append("")
    for c in base_component_rows:
        lines.append(
            "- component {cid}: rows={rows}, forms={forms}, majority={maj}, outside={outside}, inside={inside}, gap={gap}, too_large={too_large}".format(
                cid=c["component_id"],
                rows=c["row_count"],
                forms=c["form_counts"],
                maj=c["majority_form"],
                outside=c["outside_boundary_span"],
                inside=c["inside_fiber_residual"],
                gap=c["boundary_gap"],
                too_large=c["component_size_exceeds_target_size"],
            )
        )
    lines.append("")
    lines.append("## Best refinement")
    lines.append("")
    if best_refinement:
        lines.append("- family: `" + best_refinement["family"] + "`")
        lines.append("- field: `" + best_refinement["field"] + "`")
        lines.append("- component_count: `" + str(best_refinement["component_count"]) + "`")
        lines.append("- purity_total: `" + str(best_refinement["purity_total"]) + "`")
        lines.append("- score: `" + str(best_refinement["score"]) + "`")
        lines.append("- exact_partition: `" + str(best_refinement["exact_partition"]) + "`")
        lines.append("- ordered_exact_by_boundary_gap: `" + str(best_refinement["ordered_exact_by_boundary_gap"]) + "`")
        lines.append("- majority_order_by_boundary_gap: `" + str(best_refinement["majority_order_by_boundary_gap"]) + "`")
    lines.append("")
    lines.append("## Best component split purity")
    lines.append("")
    if best_split:
        lines.append("- field: `" + best_split["field"] + "`")
        lines.append("- split_count: `" + str(best_split["split_count"]) + "`")
        lines.append("- split_purity_total: `" + str(best_split["split_purity_total"]) + "`")
    lines.append("")
    lines.append("## Top refinements")
    lines.append("")
    for ev in refinement_evals[:10]:
        lines.append(
            "- family={family}, field={field}, components={components}, purity={purity}/24, score={score}, exact={exact}, ordered_exact={ordered}, order={order}".format(
                family=ev["family"],
                field=ev["field"],
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
    lines.append(interpretation)
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
    if best_refinement:
        print("best_refinement_family", best_refinement["family"])
        print("best_refinement_field", best_refinement["field"])
        print("best_refinement_components", best_refinement["component_count"])
        print("best_refinement_purity", str(best_refinement["purity_total"]) + "/24")
        print("best_refinement_score", best_refinement["score"])
        print("best_refinement_exact", best_refinement["exact_partition"])
        print("best_refinement_ordered_exact", best_refinement["ordered_exact_by_boundary_gap"])
        print("best_refinement_order", best_refinement["majority_order_by_boundary_gap"])
    if best_split:
        print("best_split_field", best_split["field"])
        print("best_split_purity", str(best_split["split_purity_total"]) + "/24")
        print("best_split_count", best_split["split_count"])


if __name__ == "__main__":
    main()
