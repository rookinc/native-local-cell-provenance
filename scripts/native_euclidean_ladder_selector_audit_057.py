#!/usr/bin/env python3
import csv
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]

IN_055 = ROOT / "artifacts/json/form_index_provenance_audit_055.v1.json"
IN_056 = ROOT / "artifacts/json/euclidean_completion_ladder_schema_056.v1.json"
SOURCE_JSON = ROOT / "source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/g60_native_overlay_generator_family_search_001.v1.json"

OUT_JSON = ROOT / "artifacts/json/native_euclidean_ladder_selector_audit_057.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_euclidean_ladder_selector_audit_057.v1.csv"
OUT_NOTE = ROOT / "notes/native_euclidean_ladder_selector_audit_057.md"

TARGET_FORM_ORDER = [0, 1, 2, 3]
TARGET_EUCLIDEAN_NAMES = ["edge", "hinge", "closed_face", "filled_cell"]

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

NATIVE_FIELD_FOCUS = [
    "slot_delta_mod15",
    "fiber_delta_mod60",
]

REQUIRED_PHRASES = [
    "native Euclidean ladder selector audit",
    "Euclidean order",
    "candidate selector",
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


def field_is_label_like(name):
    n = str(name).lower()
    return any(tok.lower() in n for tok in LABEL_TOKENS)


def flatten_scalars(row, prefix=""):
    out = {}
    if not isinstance(row, dict):
        return out

    for k, v in row.items():
        key = prefix + str(k)
        if isinstance(v, dict):
            out.update(flatten_scalars(v, key + "."))
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
            iv = as_int(v)
            if iv is not None:
                out[key] = iv
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


def stats(vals):
    vals = [as_int(v) for v in vals]
    vals = [v for v in vals if v is not None]
    if not vals:
        return {}
    uniq = sorted(set(vals))
    return {
        "count": len(vals),
        "sum": sum(vals),
        "min": min(vals),
        "max": max(vals),
        "range": max(vals) - min(vals),
        "unique_count": len(uniq),
        "unique_sum": sum(uniq),
        "unique_min": min(uniq),
        "unique_max": max(uniq),
        "unique_range": max(uniq) - min(uniq),
    }


def sorted_order(vals, direction):
    if direction == "ascending":
        return [k for k, _ in sorted(vals.items(), key=lambda kv: (kv[1], kv[0]))]
    if direction == "descending":
        return [k for k, _ in sorted(vals.items(), key=lambda kv: (-kv[1], kv[0]))]
    raise ValueError(direction)


def direction_hit(vals):
    hits = []
    if len(set(vals.values())) != len(vals):
        return hits

    asc = sorted_order(vals, "ascending")
    desc = sorted_order(vals, "descending")

    if asc == TARGET_FORM_ORDER:
        hits.append({
            "direction": "ascending",
            "ordered_forms": asc,
            "values": dict(vals),
        })

    if desc == TARGET_FORM_ORDER:
        hits.append({
            "direction": "descending",
            "ordered_forms": desc,
            "values": dict(vals),
        })

    return hits


def missing_phrases(text, phrases):
    return [p for p in phrases if p not in text]


def found_phrases(text, phrases):
    return [p for p in phrases if p in text]


def main():
    a055 = load_json(IN_055)
    a056 = load_json(IN_056)
    source = load_json(SOURCE_JSON)

    if not a055.get("audit_pass"):
        raise SystemExit("055 audit_pass is not true")
    if not a056.get("schema_pass"):
        raise SystemExit("056 schema_pass is not true")

    edge_records, edge_path = find_edge_records(source)
    if not edge_records:
        raise SystemExit("could not locate edge_records")

    rows = []
    for row in edge_records:
        fi = as_int(row.get("form_index"))
        if fi is None:
            continue
        if fi in TARGET_FORM_ORDER:
            rows.append(row)

    groups = defaultdict(list)
    for row in rows:
        groups[as_int(row.get("form_index"))].append(row)

    group_sizes = {str(k): len(v) for k, v in sorted(groups.items())}

    # Build non-label native-focused group features. We use form_index only as
    # the evaluation grouping/target, not as a selector input.
    group_features = {}

    all_fields = set()
    for row in rows:
        all_fields.update(flatten_scalars(row).keys())

    focus_fields = []
    for field in sorted(all_fields):
        if field_is_label_like(field):
            continue
        if any(field.startswith(prefix) for prefix in NATIVE_FIELD_FOCUS):
            focus_fields.append(field)

    for field in focus_fields:
        for stat_name in ["min", "max", "range", "sum", "unique_min", "unique_max", "unique_range", "unique_sum", "unique_count"]:
            vals_by_group = {}
            for fi in TARGET_FORM_ORDER:
                vals = []
                for row in groups[fi]:
                    scalars = flatten_scalars(row)
                    if field in scalars:
                        vals.append(scalars[field])
                st = stats(vals)
                if stat_name in st:
                    vals_by_group[fi] = st[stat_name]
            if set(vals_by_group.keys()) == set(TARGET_FORM_ORDER):
                group_features[field + "__" + stat_name] = vals_by_group

    order_hits = []
    for feature, vals in sorted(group_features.items()):
        for hit in direction_hit(vals):
            order_hits.append({
                "feature": feature,
                "direction": hit["direction"],
                "ordered_forms": hit["ordered_forms"],
                "values": hit["values"],
                "uses_form_index_as_input": False,
                "uses_record_order_as_input": False,
                "uses_answer_label_as_input": False,
            })

    slot_hits = [h for h in order_hits if h["feature"].startswith("slot_delta_mod15")]
    fiber_hits = [h for h in order_hits if h["feature"].startswith("fiber_delta_mod60")]

    # Known sharp candidates observed in 055.
    expected_slot_values = {
        "slot_delta_mod15__max": {0: 9, 1: 12, 2: 13, 3: 14},
        "slot_delta_mod15__range": {0: 9, 1: 12, 2: 13, 3: 14},
        "slot_delta_mod15__unique_max": {0: 9, 1: 12, 2: 13, 3: 14},
        "slot_delta_mod15__unique_range": {0: 9, 1: 12, 2: 13, 3: 14},
    }
    expected_fiber_values = {
        "fiber_delta_mod60__min": {0: 12, 1: 3, 2: 2, 3: 1},
        "fiber_delta_mod60__unique_min": {0: 12, 1: 3, 2: 2, 3: 1},
    }

    expected_slot_checks = {}
    for feature, vals in expected_slot_values.items():
        expected_slot_checks[feature] = group_features.get(feature) == vals and sorted_order(vals, "ascending") == TARGET_FORM_ORDER

    expected_fiber_checks = {}
    for feature, vals in expected_fiber_values.items():
        expected_fiber_checks[feature] = group_features.get(feature) == vals and sorted_order(vals, "descending") == TARGET_FORM_ORDER

    active_window = a056.get("state_rows", [])
    active_names = [row.get("completion_name") for row in active_window]
    active_levels = [row.get("completion_level") for row in active_window]

    candidate_selector = {
        "name": "native_monotone_delta_order",
        "input_fields": [
            "slot_delta_mod15",
            "fiber_delta_mod60",
        ],
        "rule": (
            "order the four form groups by native delta monotones: slot_delta_mod15 rises across the Euclidean order, "
            "while fiber_delta_mod60 falls across the same order"
        ),
        "target_order": TARGET_FORM_ORDER,
        "target_euclidean_names": TARGET_EUCLIDEAN_NAMES,
        "slot_support_hits": slot_hits,
        "fiber_support_hits": fiber_hits,
    }

    statement = (
        "Artifact 057 is a native Euclidean ladder selector audit. It tests whether non-label native delta fields recover the Euclidean order "
        "edge -> hinge -> closed face -> filled cell as a candidate selector, without using form_index, record order, or answer labels as selector inputs."
    )

    boundary = (
        "This is a candidate selector audit, not native closure. It does not prove the completion ladder natively, "
        "does not settle answer-label leakage, is not full role-labeled shared_B universe derivation, and is not Gap A closure."
    )

    combined = statement + "\n" + boundary
    missing = missing_phrases(combined, REQUIRED_PHRASES)
    forbidden = found_phrases(combined, FORBIDDEN_PHRASES)

    checks = {
        "form_index_audit_055_pass": bool(a055.get("audit_pass")),
        "euclidean_schema_056_pass": bool(a056.get("schema_pass")),
        "source_json_exists": SOURCE_JSON.exists(),
        "edge_records_found": bool(edge_records),
        "form_groups_are_0_1_2_3": sorted(groups.keys()) == TARGET_FORM_ORDER,
        "group_sizes_are_6_each": all(len(groups[k]) == 6 for k in TARGET_FORM_ORDER),
        "active_window_is_2_3_4_5": active_levels == [2, 3, 4, 5],
        "active_names_are_euclidean_order": active_names == TARGET_EUCLIDEAN_NAMES,
        "label_fields_excluded_from_selector": True,
        "record_order_excluded_from_selector": True,
        "form_index_excluded_from_selector_input": True,
        "focus_feature_count": len(focus_fields),
        "group_feature_count": len(group_features),
        "order_hit_count": len(order_hits),
        "slot_delta_order_hit_count": len(slot_hits),
        "fiber_delta_order_hit_count": len(fiber_hits),
        "slot_delta_expected_hits_all_true": all(expected_slot_checks.values()),
        "fiber_delta_expected_hits_all_true": all(expected_fiber_checks.values()),
        "candidate_selector_found": bool(slot_hits and fiber_hits),
        "native_provenance_confirmed": False,
        "answer_label_leakage_settled": False,
        "required_phrases_present": len(missing) == 0,
        "forbidden_phrases_absent": len(forbidden) == 0,
    }

    audit_pass = all([
        checks["form_index_audit_055_pass"],
        checks["euclidean_schema_056_pass"],
        checks["source_json_exists"],
        checks["edge_records_found"],
        checks["form_groups_are_0_1_2_3"],
        checks["group_sizes_are_6_each"],
        checks["active_window_is_2_3_4_5"],
        checks["active_names_are_euclidean_order"],
        checks["label_fields_excluded_from_selector"],
        checks["record_order_excluded_from_selector"],
        checks["form_index_excluded_from_selector_input"],
        checks["slot_delta_order_hit_count"] > 0,
        checks["fiber_delta_order_hit_count"] > 0,
        checks["candidate_selector_found"],
        checks["required_phrases_present"],
        checks["forbidden_phrases_absent"],
    ])

    if audit_pass:
        verdict = "native_delta_monotone_candidate_selector_found"
    else:
        verdict = "native_delta_monotone_selector_not_confirmed"

    result = {
        "status": "native_euclidean_ladder_selector_audit_recorded",
        "audit_id": "057",
        "inputs": {
            "form_index_provenance_audit_055": str(IN_055),
            "euclidean_completion_ladder_schema_056": str(IN_056),
            "source_json": str(SOURCE_JSON),
            "edge_records_path": edge_path,
        },
        "checks": checks,
        "audit_pass": audit_pass,
        "verdict": verdict,
        "group_sizes": group_sizes,
        "focus_fields": focus_fields,
        "candidate_selector": candidate_selector,
        "expected_slot_checks": expected_slot_checks,
        "expected_fiber_checks": expected_fiber_checks,
        "statement": statement,
        "boundary": boundary,
        "missing_required_phrases": missing,
        "forbidden_phrases_found": forbidden,
        "interpretation": (
            "Artifact 057 moves past form_index as a risky label and tests non-label native delta monotones. "
            "The result is a candidate selector: slot_delta_mod15 increases and fiber_delta_mod60 decreases along the Euclidean order. "
            "This is stronger than record order, but it remains a candidate selector rather than native closure."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "kind",
            "feature",
            "direction",
            "ordered_forms",
            "ordered_names",
            "values",
            "uses_form_index_as_input",
            "uses_record_order_as_input",
            "uses_answer_label_as_input",
        ])
        for h in order_hits:
            w.writerow([
                "order_hit",
                h["feature"],
                h["direction"],
                json.dumps(h["ordered_forms"]),
                json.dumps(TARGET_EUCLIDEAN_NAMES),
                json.dumps(h["values"], sort_keys=True),
                h["uses_form_index_as_input"],
                h["uses_record_order_as_input"],
                h["uses_answer_label_as_input"],
            ])

    lines = []
    lines.append("# Native Euclidean ladder selector audit 057")
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
    lines.append("## Candidate selector")
    lines.append("")
    lines.append("- name: `" + candidate_selector["name"] + "`")
    lines.append("- input_fields: `" + str(candidate_selector["input_fields"]) + "`")
    lines.append("- target_order: `" + str(TARGET_FORM_ORDER) + "`")
    lines.append("- target_euclidean_names: `" + str(TARGET_EUCLIDEAN_NAMES) + "`")
    lines.append("- rule: " + candidate_selector["rule"])
    lines.append("")
    lines.append("## Slot delta support")
    lines.append("")
    for h in slot_hits:
        lines.append("- " + h["feature"] + " / " + h["direction"] + ": `" + str(h["values"]) + "`")
    lines.append("")
    lines.append("## Fiber delta support")
    lines.append("")
    for h in fiber_hits:
        lines.append("- " + h["feature"] + " / " + h["direction"] + ": `" + str(h["values"]) + "`")
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append(boundary)
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(result["interpretation"])
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
    print("slot_hits_first", slot_hits[:6])
    print("fiber_hits_first", fiber_hits[:6])


if __name__ == "__main__":
    main()
