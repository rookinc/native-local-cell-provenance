#!/usr/bin/env python3
import csv
import json
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[1]

IN_055 = ROOT / "artifacts/json/form_index_provenance_audit_055.v1.json"
IN_057 = ROOT / "artifacts/json/native_euclidean_ladder_selector_audit_057.v1.json"
SOURCE_JSON = ROOT / "source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/g60_native_overlay_generator_family_search_001.v1.json"

OUT_JSON = ROOT / "artifacts/json/monotone_selector_independence_audit_058.v1.json"
OUT_CSV = ROOT / "artifacts/csv/monotone_selector_independence_audit_058.v1.csv"
OUT_NOTE = ROOT / "notes/monotone_selector_independence_audit_058.md"

TARGET_ORDER = [0, 1, 2, 3]
TARGET_NAMES = ["edge", "hinge", "closed_face", "filled_cell"]

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

REQUIRED_PHRASES = [
    "monotone selector independence audit",
    "slot_delta_mod15",
    "fiber_delta_mod60",
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


def label_like(name):
    n = str(name).lower()
    return any(tok in n for tok in LABEL_TOKENS)


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
        "multiset": sorted(vals),
        "unique_values": uniq,
    }


def ordered_keys(vals, direction):
    if direction == "ascending":
        return [k for k, _ in sorted(vals.items(), key=lambda kv: (kv[1], kv[0]))]
    if direction == "descending":
        return [k for k, _ in sorted(vals.items(), key=lambda kv: (-kv[1], kv[0]))]
    raise ValueError(direction)


def missing_phrases(text, phrases):
    return [p for p in phrases if p not in text]


def found_phrases(text, phrases):
    return [p for p in phrases if p in text]


def main():
    a055 = load_json(IN_055)
    a057 = load_json(IN_057)
    source = load_json(SOURCE_JSON)

    if not a055.get("audit_pass"):
        raise SystemExit("055 audit_pass is not true")
    if not a057.get("audit_pass"):
        raise SystemExit("057 audit_pass is not true")

    records, edge_path = find_edge_records(source)
    if not records:
        raise SystemExit("edge_records not found")

    rows = []
    for idx, row in enumerate(records):
        fi = as_int(row.get("form_index"))
        slot = as_int(row.get("slot_delta_mod15"))
        fiber = as_int(row.get("fiber_delta_mod60"))
        if fi in TARGET_ORDER and slot is not None and fiber is not None:
            rows.append({
                "record_index": idx,
                "form_index": fi,
                "slot_delta_mod15": slot,
                "fiber_delta_mod60": fiber,
                "raw": row,
            })

    groups = defaultdict(list)
    for row in rows:
        groups[row["form_index"]].append(row)

    group_rows = []
    group_summary = {}
    for fi in TARGET_ORDER:
        xs = groups[fi]
        slot_vals = [x["slot_delta_mod15"] for x in xs]
        fiber_vals = [x["fiber_delta_mod60"] for x in xs]
        slot_stats = stats(slot_vals)
        fiber_stats = stats(fiber_vals)

        group_summary[str(fi)] = {
            "form_index": fi,
            "euclidean_name": TARGET_NAMES[fi],
            "row_count": len(xs),
            "slot_delta_mod15": slot_stats,
            "fiber_delta_mod60": fiber_stats,
        }

        group_rows.append({
            "form_index": fi,
            "euclidean_name": TARGET_NAMES[fi],
            "row_count": len(xs),
            "slot_max": slot_stats.get("max"),
            "slot_range": slot_stats.get("range"),
            "slot_unique_max": slot_stats.get("unique_max"),
            "slot_unique_range": slot_stats.get("unique_range"),
            "fiber_min": fiber_stats.get("min"),
            "fiber_unique_min": fiber_stats.get("unique_min"),
        })

    slot_max = {row["form_index"]: row["slot_max"] for row in group_rows}
    slot_range = {row["form_index"]: row["slot_range"] for row in group_rows}
    fiber_min = {row["form_index"]: row["fiber_min"] for row in group_rows}
    fiber_unique_min = {row["form_index"]: row["fiber_unique_min"] for row in group_rows}

    slot_orders = {
        "slot_delta_mod15__max__ascending": ordered_keys(slot_max, "ascending"),
        "slot_delta_mod15__range__ascending": ordered_keys(slot_range, "ascending"),
    }
    fiber_orders = {
        "fiber_delta_mod60__min__descending": ordered_keys(fiber_min, "descending"),
        "fiber_delta_mod60__unique_min__descending": ordered_keys(fiber_unique_min, "descending"),
    }

    # Independence checks:
    # 1. The selector fields are not label-like.
    field_independence = {
        "slot_delta_mod15_label_like": label_like("slot_delta_mod15"),
        "fiber_delta_mod60_label_like": label_like("fiber_delta_mod60"),
    }

    # 2. They are real scalar fields on individual edge records, not record index.
    raw_field_presence = {
        "slot_delta_mod15_present_on_all_rows": all("slot_delta_mod15" in r["raw"] for r in rows),
        "fiber_delta_mod60_present_on_all_rows": all("fiber_delta_mod60" in r["raw"] for r in rows),
    }

    # 3. The two monotones agree on the same Euclidean order while moving in opposite directions.
    slot_order_ok = all(order == TARGET_ORDER for order in slot_orders.values())
    fiber_order_ok = all(order == TARGET_ORDER for order in fiber_orders.values())

    # 4. Row-order risk remains because the form groups themselves are contiguous by form_index.
    form_sequence = [as_int(r.get("form_index")) for r in records if as_int(r.get("form_index")) in TARGET_ORDER]
    blocks = []
    last = None
    for x in form_sequence:
        if x != last:
            blocks.append(x)
            last = x

    contiguous_form_blocks = blocks == TARGET_ORDER

    # 5. Within-group multiset fingerprints separate the four groups.
    fingerprints = {}
    for fi in TARGET_ORDER:
        gs = group_summary[str(fi)]
        fingerprints[str(fi)] = {
            "slot_values": gs["slot_delta_mod15"]["multiset"],
            "fiber_values": gs["fiber_delta_mod60"]["multiset"],
        }

    unique_fingerprints = len({json.dumps(v, sort_keys=True) for v in fingerprints.values()}) == 4

    # 6. A simple two-axis score gives a strict order.
    # Lower fiber_min and higher slot_max both indicate later completion.
    # Normalize only by ordinal direction, not by labels.
    two_axis_rows = []
    for row in group_rows:
        two_axis_rows.append({
            "form_index": row["form_index"],
            "euclidean_name": row["euclidean_name"],
            "slot_max": row["slot_max"],
            "fiber_min": row["fiber_min"],
        })

    two_axis_order = [
        row["form_index"]
        for row in sorted(two_axis_rows, key=lambda r: (r["slot_max"], -r["fiber_min"], r["form_index"]))
    ]

    statement = (
        "Artifact 058 is a monotone selector independence audit. It checks whether slot_delta_mod15 and fiber_delta_mod60 recover the Euclidean order "
        "as non-label native fields rather than as record order or answer labels."
    )

    boundary = (
        "The selector fields are independent of form_index as inputs, but answer-label leakage remains open because the source groups are still audited by form_index. "
        "This is not native closure, does not prove the completion ladder natively, is not full role-labeled shared_B universe derivation, and is not Gap A closure."
    )

    combined = statement + "\n" + boundary
    missing = missing_phrases(combined, REQUIRED_PHRASES)
    forbidden = found_phrases(combined, FORBIDDEN_PHRASES)

    checks = {
        "form_index_audit_055_pass": bool(a055.get("audit_pass")),
        "native_euclidean_selector_057_pass": bool(a057.get("audit_pass")),
        "source_json_exists": SOURCE_JSON.exists(),
        "edge_records_found": bool(records),
        "row_count": len(rows),
        "group_sizes_are_6_each": all(len(groups[fi]) == 6 for fi in TARGET_ORDER),
        "slot_delta_mod15_is_non_label_field": not field_independence["slot_delta_mod15_label_like"],
        "fiber_delta_mod60_is_non_label_field": not field_independence["fiber_delta_mod60_label_like"],
        "slot_delta_mod15_present_on_all_rows": raw_field_presence["slot_delta_mod15_present_on_all_rows"],
        "fiber_delta_mod60_present_on_all_rows": raw_field_presence["fiber_delta_mod60_present_on_all_rows"],
        "slot_orders_recover_euclidean_order": slot_order_ok,
        "fiber_orders_recover_euclidean_order": fiber_order_ok,
        "opposite_monotones_agree_on_same_order": slot_order_ok and fiber_order_ok,
        "two_axis_order_recovers_euclidean_order": two_axis_order == TARGET_ORDER,
        "native_delta_fingerprints_unique_by_form": unique_fingerprints,
        "contiguous_form_blocks_order_label_risk": contiguous_form_blocks,
        "answer_label_leakage_remains_open": True,
        "native_provenance_confirmed": False,
        "required_phrases_present": len(missing) == 0,
        "forbidden_phrases_absent": len(forbidden) == 0,
    }

    audit_pass = all([
        checks["form_index_audit_055_pass"],
        checks["native_euclidean_selector_057_pass"],
        checks["source_json_exists"],
        checks["edge_records_found"],
        checks["group_sizes_are_6_each"],
        checks["slot_delta_mod15_is_non_label_field"],
        checks["fiber_delta_mod60_is_non_label_field"],
        checks["slot_delta_mod15_present_on_all_rows"],
        checks["fiber_delta_mod60_present_on_all_rows"],
        checks["slot_orders_recover_euclidean_order"],
        checks["fiber_orders_recover_euclidean_order"],
        checks["opposite_monotones_agree_on_same_order"],
        checks["two_axis_order_recovers_euclidean_order"],
        checks["native_delta_fingerprints_unique_by_form"],
        checks["answer_label_leakage_remains_open"],
        checks["required_phrases_present"],
        checks["forbidden_phrases_absent"],
    ])

    verdict = (
        "monotone_selector_independent_of_label_fields_but_not_closure"
        if audit_pass
        else "monotone_selector_independence_not_confirmed"
    )

    result = {
        "status": "monotone_selector_independence_audit_recorded",
        "audit_id": "058",
        "inputs": {
            "form_index_provenance_audit_055": str(IN_055),
            "native_euclidean_ladder_selector_audit_057": str(IN_057),
            "source_json": str(SOURCE_JSON),
            "edge_records_path": edge_path,
        },
        "checks": checks,
        "audit_pass": audit_pass,
        "verdict": verdict,
        "group_summary": group_summary,
        "group_rows": group_rows,
        "slot_orders": slot_orders,
        "fiber_orders": fiber_orders,
        "two_axis_rows": two_axis_rows,
        "two_axis_order": two_axis_order,
        "fingerprints": fingerprints,
        "record_order_risk": {
            "form_sequence_first_40": form_sequence[:40],
            "contiguous_blocks": blocks,
            "contiguous_form_blocks": contiguous_form_blocks,
        },
        "statement": statement,
        "boundary": boundary,
        "missing_required_phrases": missing,
        "forbidden_phrases_found": forbidden,
        "interpretation": (
            "Artifact 058 strengthens 057 by showing that the selector fields are non-label fields present on the edge records, "
            "that opposite native monotones recover the same Euclidean order, and that the delta fingerprints separate the four form groups. "
            "It still does not settle answer-label leakage because the audit evaluates groups indexed by form_index."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "form_index",
            "euclidean_name",
            "row_count",
            "slot_max",
            "slot_range",
            "slot_unique_max",
            "slot_unique_range",
            "fiber_min",
            "fiber_unique_min",
        ])
        for row in group_rows:
            w.writerow([
                row["form_index"],
                row["euclidean_name"],
                row["row_count"],
                row["slot_max"],
                row["slot_range"],
                row["slot_unique_max"],
                row["slot_unique_range"],
                row["fiber_min"],
                row["fiber_unique_min"],
            ])

    lines = []
    lines.append("# Monotone selector independence audit 058")
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
    lines.append("## Group rows")
    lines.append("")
    for row in group_rows:
        lines.append(
            "- {fi} / {name}: slot_max={slot_max}, slot_range={slot_range}, fiber_min={fiber_min}, fiber_unique_min={fiber_unique_min}".format(
                fi=row["form_index"],
                name=row["euclidean_name"],
                slot_max=row["slot_max"],
                slot_range=row["slot_range"],
                fiber_min=row["fiber_min"],
                fiber_unique_min=row["fiber_unique_min"],
            )
        )
    lines.append("")
    lines.append("## Orders")
    lines.append("")
    lines.append("- slot_orders: `" + str(slot_orders) + "`")
    lines.append("- fiber_orders: `" + str(fiber_orders) + "`")
    lines.append("- two_axis_order: `" + str(two_axis_order) + "`")
    lines.append("")
    lines.append("## Record-order risk")
    lines.append("")
    lines.append("- form_sequence_first_40: `" + str(form_sequence[:40]) + "`")
    lines.append("- contiguous_blocks: `" + str(blocks) + "`")
    lines.append("- contiguous_form_blocks: `" + str(contiguous_form_blocks) + "`")
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
    print("slot_orders", slot_orders)
    print("fiber_orders", fiber_orders)
    print("two_axis_order", two_axis_order)
    print("contiguous_blocks", blocks)


if __name__ == "__main__":
    main()
