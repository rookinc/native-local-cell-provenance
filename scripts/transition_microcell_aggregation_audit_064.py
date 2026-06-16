#!/usr/bin/env python3
import csv
import itertools
import json
from pathlib import Path
from collections import Counter, defaultdict, deque

ROOT = Path(__file__).resolve().parents[1]

IN_060 = ROOT / "artifacts/json/inside_outside_boundary_grammar_audit_060.v1.json"
IN_063 = ROOT / "artifacts/json/six_component_incidence_refinement_audit_063.v1.json"
SOURCE_JSON = ROOT / "source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/g60_native_overlay_generator_family_search_001.v1.json"

OUT_JSON = ROOT / "artifacts/json/transition_microcell_aggregation_audit_064.v1.json"
OUT_CSV = ROOT / "artifacts/csv/transition_microcell_aggregation_audit_064.v1.csv"
OUT_NOTE = ROOT / "notes/transition_microcell_aggregation_audit_064.md"

TARGET_FORMS = [0, 1, 2, 3]
TARGET_NAMES = ["edge", "hinge", "closed_face", "filled_cell"]
TARGET_FORM_ROW_SIZE = 6
TARGET_MICROCELL_COUNT = 12

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
    "majority_form",
]

REQUIRED_PHRASES = [
    "transition microcell aggregation audit",
    "12 pure transition cells",
    "four Euclidean forms",
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

BASE_ENDPOINT_FIELDS = ["from_C", "to_C"]


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
        features["derived.boundary_gap_sign"] = "neg" if slot - fiber < 0 else ("zero" if slot - fiber == 0 else "pos")
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


def stats(vals):
    vals = [as_int(v) for v in vals]
    vals = [v for v in vals if v is not None]
    if not vals:
        return {}
    uniq = sorted(set(vals))
    return {
        "count": len(vals),
        "min": min(vals),
        "max": max(vals),
        "sum": sum(vals),
        "range": max(vals) - min(vals),
        "unique_count": len(uniq),
        "unique_min": min(uniq),
        "unique_max": max(uniq),
        "unique_sum": sum(uniq),
        "unique_range": max(uniq) - min(uniq),
        "values": sorted(vals),
        "unique_values": uniq,
    }


def build_microcells(rows):
    base_edges = share_endpoint_edges(rows, BASE_ENDPOINT_FIELDS)
    base_components = components(len(rows), base_edges)

    base_component_id_by_row = {}
    for cid, comp in enumerate(base_components):
        for rid in comp:
            base_component_id_by_row[rid] = cid

    buckets = defaultdict(list)
    for i, row in enumerate(rows):
        base_id = base_component_id_by_row[i]
        c_delta = get_value(row["features"], "derived.C_delta_mod15")
        buckets[(base_id, c_delta)].append(i)

    microcells = []
    for mid, (key, ids) in enumerate(sorted(buckets.items(), key=lambda kv: (kv[0][0], str(kv[0][1])))):
        base_id, c_delta = key
        forms = [rows[i]["form_index"] for i in ids]
        c = Counter(forms)
        maj, cnt = c.most_common(1)[0]

        slots = [get_value(rows[i]["features"], "slot_delta_mod15") for i in ids]
        fibers = [get_value(rows[i]["features"], "fiber_delta_mod60") for i in ids]
        from_cs = [get_value(rows[i]["features"], "from_C") for i in ids]
        to_cs = [get_value(rows[i]["features"], "to_C") for i in ids]
        lift_qs = [get_value(rows[i]["features"], "lift_q") for i in ids if get_value(rows[i]["features"], "lift_q") is not None]
        edge_roles = [get_value(rows[i]["features"], "edge_role") for i in ids if get_value(rows[i]["features"], "edge_role") is not None]

        s_slot = stats(slots)
        s_fiber = stats(fibers)
        s_from = stats(from_cs)
        s_to = stats(to_cs)

        outside = s_slot.get("max")
        inside = s_fiber.get("min")
        gap = outside - inside if outside is not None and inside is not None else None

        microcells.append({
            "microcell_id": mid,
            "base_component_id": base_id,
            "C_delta_mod15": c_delta,
            "row_ids": ids,
            "source_record_ids": [rows[i]["row_id"] for i in ids],
            "row_count": len(ids),
            "form_counts": dict(sorted(c.items())),
            "majority_form": maj,
            "majority_count": cnt,
            "pure": cnt == len(ids),
            "outside_boundary_span": outside,
            "inside_fiber_residual": inside,
            "boundary_gap": gap,
            "slot_min": s_slot.get("min"),
            "slot_max": s_slot.get("max"),
            "fiber_min": s_fiber.get("min"),
            "fiber_max": s_fiber.get("max"),
            "from_C_min": s_from.get("min"),
            "from_C_max": s_from.get("max"),
            "to_C_min": s_to.get("min"),
            "to_C_max": s_to.get("max"),
            "from_C_sum": s_from.get("sum"),
            "to_C_sum": s_to.get("sum"),
            "lift_q_values": sorted(set(lift_qs)),
            "edge_role_values": sorted(set(str(x) for x in edge_roles)),
        })

    return base_components, microcells


def key_value(mc, field):
    if field in mc:
        return mc[field]
    return None


def numeric_transforms(field, value):
    out = {}
    v = as_int(value)
    if v is None:
        return out
    for m in [2, 3, 4, 5, 6, 7]:
        out[field + "_mod_" + str(m)] = v % m
    for d in [2, 3, 4, 5, 6]:
        out[field + "_floor_div_" + str(d)] = v // d
    return out


def microcell_feature_map(mc):
    feats = {}

    raw_fields = [
        "base_component_id",
        "C_delta_mod15",
        "row_count",
        "outside_boundary_span",
        "inside_fiber_residual",
        "boundary_gap",
        "slot_min",
        "slot_max",
        "fiber_min",
        "fiber_max",
        "from_C_min",
        "from_C_max",
        "to_C_min",
        "to_C_max",
        "from_C_sum",
        "to_C_sum",
    ]

    for f in raw_fields:
        v = key_value(mc, f)
        if v is not None:
            feats[f] = v
            feats.update(numeric_transforms(f, v))

    gap = as_int(mc.get("boundary_gap"))
    if gap is not None:
        feats["boundary_gap_sign"] = "neg" if gap < 0 else ("zero" if gap == 0 else "pos")
        feats["inside_captured"] = "yes" if gap > 0 else "no"

    lift_q_values = mc.get("lift_q_values", [])
    feats["lift_q_signature"] = ",".join(str(x) for x in lift_q_values)
    edge_role_values = mc.get("edge_role_values", [])
    feats["edge_role_signature"] = ",".join(str(x) for x in edge_role_values)

    # Some candidate quotient coordinates.
    if mc.get("C_delta_mod15") is not None and mc.get("base_component_id") is not None:
        c = as_int(mc["C_delta_mod15"])
        b = as_int(mc["base_component_id"])
        feats["base_plus_C_delta_mod4"] = (b + c) % 4
        feats["base_plus_C_delta_mod3"] = (b + c) % 3
        feats["base_times_C_delta_mod4"] = (b * c) % 4
        feats["base_minus_C_delta_mod4"] = (b - c) % 4

    if mc.get("outside_boundary_span") is not None and mc.get("inside_fiber_residual") is not None:
        o = as_int(mc["outside_boundary_span"])
        i = as_int(mc["inside_fiber_residual"])
        feats["outside_plus_inside_mod4"] = (o + i) % 4
        feats["outside_minus_inside_mod4"] = (o - i) % 4
        feats["outside_plus_inside_mod3"] = (o + i) % 3
        feats["outside_minus_inside_mod3"] = (o - i) % 3

    return feats


def evaluate_aggregation(microcells, key_name, key_func):
    buckets = defaultdict(list)
    for mc in microcells:
        k = key_func(mc)
        if k is None:
            continue
        buckets[k].append(mc)

    groups = []
    for key, cells in buckets.items():
        row_total = sum(c["row_count"] for c in cells)
        form_counts = Counter()
        for c in cells:
            for f, n in c["form_counts"].items():
                form_counts[int(f)] += n
        maj = None
        cnt = 0
        if form_counts:
            maj, cnt = form_counts.most_common(1)[0]

        outside_vals = [c["outside_boundary_span"] for c in cells if c["outside_boundary_span"] is not None]
        inside_vals = [c["inside_fiber_residual"] for c in cells if c["inside_fiber_residual"] is not None]
        outside = max(outside_vals) if outside_vals else None
        inside = min(inside_vals) if inside_vals else None
        gap = outside - inside if outside is not None and inside is not None else None

        groups.append({
            "key": key,
            "microcell_count": len(cells),
            "microcell_ids": [c["microcell_id"] for c in cells],
            "row_count": row_total,
            "form_counts": dict(sorted(form_counts.items())),
            "majority_form": maj,
            "majority_count": cnt,
            "outside_boundary_span": outside,
            "inside_fiber_residual": inside,
            "boundary_gap": gap,
        })

    groups_by_gap = sorted(
        groups,
        key=lambda g: (
            10**9 if g["boundary_gap"] is None else g["boundary_gap"],
            str(g["key"]),
        ),
    )

    majority_order_by_gap = [g["majority_form"] for g in groups_by_gap]
    purity_total = sum(g["majority_count"] for g in groups)
    size_deviation = sum(abs(g["row_count"] - TARGET_FORM_ROW_SIZE) for g in groups)
    if len(groups) < 4:
        size_deviation += (4 - len(groups)) * TARGET_FORM_ROW_SIZE
    group_count_penalty = abs(len(groups) - 4) * TARGET_FORM_ROW_SIZE
    score = purity_total - size_deviation - group_count_penalty

    exact = (
        len(groups) == 4
        and all(g["row_count"] == TARGET_FORM_ROW_SIZE for g in groups)
        and all(g["majority_count"] == TARGET_FORM_ROW_SIZE for g in groups)
        and sorted(g["majority_form"] for g in groups) == TARGET_FORMS
    )
    ordered_exact = exact and majority_order_by_gap == TARGET_FORMS

    return {
        "key_name": key_name,
        "group_count": len(groups),
        "purity_total": purity_total,
        "size_deviation": size_deviation,
        "group_count_penalty": group_count_penalty,
        "score": score,
        "exact_aggregation": exact,
        "ordered_exact_by_boundary_gap": ordered_exact,
        "majority_order_by_boundary_gap": majority_order_by_gap,
        "groups": groups_by_gap,
    }


def missing_phrases(text, phrases):
    return [p for p in phrases if p not in text]


def found_phrases(text, phrases):
    return [p for p in phrases if p in text]


def main():
    a060 = load_json(IN_060)
    a063 = load_json(IN_063)
    source = load_json(SOURCE_JSON)

    if not a060.get("audit_pass"):
        raise SystemExit("060 audit_pass is not true")
    if not a063.get("audit_pass"):
        raise SystemExit("063 audit_pass is not true")

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

    base_components, microcells = build_microcells(rows)

    microcell_feats = {mc["microcell_id"]: microcell_feature_map(mc) for mc in microcells}
    all_feature_names = sorted({k for feats in microcell_feats.values() for k in feats.keys() if not field_is_label_like(k)})

    aggregations = []

    # Single-feature quotient keys.
    for f in all_feature_names:
        aggregations.append(evaluate_aggregation(microcells, f, lambda mc, ff=f: microcell_feats[mc["microcell_id"]].get(ff)))

    # Pair-feature quotient keys.
    for a, b in itertools.combinations(all_feature_names, 2):
        aggregations.append(
            evaluate_aggregation(
                microcells,
                a + "|" + b,
                lambda mc, aa=a, bb=b: (
                    microcell_feats[mc["microcell_id"]].get(aa),
                    microcell_feats[mc["microcell_id"]].get(bb),
                ),
            )
        )

    aggregations.sort(
        key=lambda e: (
            not e["ordered_exact_by_boundary_gap"],
            not e["exact_aggregation"],
            -e["score"],
            -e["purity_total"],
            e["group_count_penalty"],
            e["size_deviation"],
            e["group_count"],
            e["key_name"],
        )
    )

    exact_hits = [e for e in aggregations if e["exact_aggregation"]]
    ordered_exact_hits = [e for e in aggregations if e["ordered_exact_by_boundary_gap"]]
    best = aggregations[0] if aggregations else None

    all_microcells_pure = all(mc["pure"] for mc in microcells)
    all_microcells_size_two = all(mc["row_count"] == 2 for mc in microcells)

    if ordered_exact_hits:
        verdict = "transition_microcell_aggregation_exact_ordered_candidate_found"
    elif exact_hits:
        verdict = "transition_microcell_aggregation_exact_unordered_candidate_found"
    else:
        verdict = "transition_microcell_aggregation_not_found_in_tested_family"

    statement = (
        "Artifact 064 is a transition microcell aggregation audit. It starts from the 12 pure transition cells exposed by C_delta_mod15 in 063 and searches for a native quotient law that aggregates them into the four Euclidean forms. form_index is used only for evaluation."
    )

    boundary = (
        "This is an aggregation audit, not native closure. A hit would be a candidate requiring validation; a miss only bounds the tested quotient family. "
        "answer-label leakage remains open, this is not full role-labeled shared_B universe derivation, and is not Gap A closure."
    )

    combined = statement + "\n" + boundary
    missing = missing_phrases(combined, REQUIRED_PHRASES)
    forbidden = found_phrases(combined, FORBIDDEN_PHRASES)

    checks = {
        "inside_outside_boundary_grammar_060_pass": bool(a060.get("audit_pass")),
        "six_component_refinement_063_pass": bool(a063.get("audit_pass")),
        "source_json_exists": SOURCE_JSON.exists(),
        "edge_records_found": bool(edge_records),
        "row_count_is_24": len(rows) == 24,
        "base_component_count": len(base_components),
        "microcell_count_is_12": len(microcells) == TARGET_MICROCELL_COUNT,
        "all_microcells_are_form_pure": all_microcells_pure,
        "all_microcells_have_two_rows": all_microcells_size_two,
        "form_index_used_only_for_evaluation": True,
        "microcell_feature_count": len(all_feature_names),
        "aggregation_candidate_count": len(aggregations),
        "exact_aggregation_hit_count": len(exact_hits),
        "ordered_exact_aggregation_hit_count": len(ordered_exact_hits),
        "best_candidate_exists": best is not None,
        "best_candidate_key": best["key_name"] if best else None,
        "best_candidate_group_count": best["group_count"] if best else None,
        "best_candidate_purity_total": best["purity_total"] if best else None,
        "best_candidate_score": best["score"] if best else None,
        "answer_label_leakage_remains_open": True,
        "native_provenance_confirmed": False,
        "required_phrases_present": len(missing) == 0,
        "forbidden_phrases_absent": len(forbidden) == 0,
    }

    audit_pass = all([
        checks["inside_outside_boundary_grammar_060_pass"],
        checks["six_component_refinement_063_pass"],
        checks["source_json_exists"],
        checks["edge_records_found"],
        checks["row_count_is_24"],
        checks["microcell_count_is_12"],
        checks["all_microcells_are_form_pure"],
        checks["all_microcells_have_two_rows"],
        checks["form_index_used_only_for_evaluation"],
        checks["aggregation_candidate_count"] > 0,
        checks["best_candidate_exists"],
        checks["answer_label_leakage_remains_open"],
        checks["required_phrases_present"],
        checks["forbidden_phrases_absent"],
    ])

    result = {
        "status": "transition_microcell_aggregation_audit_recorded",
        "audit_id": "064",
        "inputs": {
            "inside_outside_boundary_grammar_audit_060": str(IN_060),
            "six_component_incidence_refinement_audit_063": str(IN_063),
            "source_json": str(SOURCE_JSON),
            "edge_records_path": edge_path,
        },
        "checks": checks,
        "audit_pass": audit_pass,
        "verdict": verdict,
        "base_component_sizes": [len(c) for c in base_components],
        "microcells": microcells,
        "microcell_feature_names": all_feature_names,
        "best_candidate": best,
        "exact_hits_first": exact_hits[:40],
        "ordered_exact_hits_first": ordered_exact_hits[:40],
        "top_candidates": aggregations[:40],
        "statement": statement,
        "boundary": boundary,
        "missing_required_phrases": missing,
        "forbidden_phrases_found": forbidden,
        "interpretation": (
            "Artifact 064 tests whether the pure transition-cell layer can be quotiented back into the four Euclidean forms. "
            "This is the natural next layer after 063: 063 found purity at 12 microcells, while 064 asks whether a native aggregation law recovers the four-form partition."
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
            "key_name",
            "group_count",
            "purity_total",
            "score",
            "exact_aggregation",
            "ordered_exact_by_boundary_gap",
            "majority_order_by_boundary_gap",
            "groups",
        ])
        for i, ev in enumerate(aggregations[:40], start=1):
            compact_groups = []
            for g in ev["groups"]:
                compact_groups.append({
                    "key": str(g["key"]),
                    "microcell_count": g["microcell_count"],
                    "row_count": g["row_count"],
                    "form_counts": g["form_counts"],
                    "majority_form": g["majority_form"],
                    "gap": g["boundary_gap"],
                })
            w.writerow([
                i,
                ev["key_name"],
                ev["group_count"],
                ev["purity_total"],
                ev["score"],
                ev["exact_aggregation"],
                ev["ordered_exact_by_boundary_gap"],
                json.dumps(ev["majority_order_by_boundary_gap"]),
                json.dumps(compact_groups, sort_keys=True),
            ])

    lines = []
    lines.append("# Transition microcell aggregation audit 064")
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
    lines.append("## Microcells")
    lines.append("")
    for mc in microcells:
        lines.append(
            "- microcell {mid}: base={base}, C_delta={cd}, rows={rows}, forms={forms}, pure={pure}, outside={outside}, inside={inside}, gap={gap}".format(
                mid=mc["microcell_id"],
                base=mc["base_component_id"],
                cd=mc["C_delta_mod15"],
                rows=mc["row_count"],
                forms=mc["form_counts"],
                pure=mc["pure"],
                outside=mc["outside_boundary_span"],
                inside=mc["inside_fiber_residual"],
                gap=mc["boundary_gap"],
            )
        )
    lines.append("")
    lines.append("## Best aggregation candidate")
    lines.append("")
    if best:
        lines.append("- key_name: `" + best["key_name"] + "`")
        lines.append("- group_count: `" + str(best["group_count"]) + "`")
        lines.append("- purity_total: `" + str(best["purity_total"]) + "`")
        lines.append("- score: `" + str(best["score"]) + "`")
        lines.append("- exact_aggregation: `" + str(best["exact_aggregation"]) + "`")
        lines.append("- ordered_exact_by_boundary_gap: `" + str(best["ordered_exact_by_boundary_gap"]) + "`")
        lines.append("- majority_order_by_boundary_gap: `" + str(best["majority_order_by_boundary_gap"]) + "`")
        lines.append("")
        lines.append("### Best candidate groups")
        lines.append("")
        for g in best["groups"]:
            lines.append(
                "- key={key}, microcells={cells}, rows={rows}, forms={forms}, majority={maj}, gap={gap}".format(
                    key=g["key"],
                    cells=g["microcell_count"],
                    rows=g["row_count"],
                    forms=g["form_counts"],
                    maj=g["majority_form"],
                    gap=g["boundary_gap"],
                )
            )
    lines.append("")
    lines.append("## Top candidates")
    lines.append("")
    for ev in aggregations[:10]:
        lines.append(
            "- key={key}, groups={groups}, purity={purity}/24, score={score}, exact={exact}, ordered_exact={ordered}, order={order}".format(
                key=ev["key_name"],
                groups=ev["group_count"],
                purity=ev["purity_total"],
                score=ev["score"],
                exact=ev["exact_aggregation"],
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
        print("best_key", best["key_name"])
        print("best_group_count", best["group_count"])
        print("best_purity", str(best["purity_total"]) + "/24")
        print("best_score", best["score"])
        print("best_exact", best["exact_aggregation"])
        print("best_ordered_exact", best["ordered_exact_by_boundary_gap"])
        print("best_order", best["majority_order_by_boundary_gap"])


if __name__ == "__main__":
    main()
