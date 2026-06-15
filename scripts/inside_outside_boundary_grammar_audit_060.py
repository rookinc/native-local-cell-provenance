#!/usr/bin/env python3
import csv
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]

IN_058 = ROOT / "artifacts/json/monotone_selector_independence_audit_058.v1.json"
IN_059 = ROOT / "artifacts/json/native_delta_partition_reconstruction_059.v1.json"
SOURCE_JSON = ROOT / "source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/g60_native_overlay_generator_family_search_001.v1.json"

OUT_JSON = ROOT / "artifacts/json/inside_outside_boundary_grammar_audit_060.v1.json"
OUT_CSV = ROOT / "artifacts/csv/inside_outside_boundary_grammar_audit_060.v1.csv"
OUT_NOTE = ROOT / "notes/inside_outside_boundary_grammar_audit_060.md"

TARGET_FORMS = [0, 1, 2, 3]
TARGET_NAMES = ["edge", "hinge", "closed_face", "filled_cell"]

REQUIRED_PHRASES = [
    "inside/outside boundary grammar",
    "outside boundary span",
    "inside fiber residual",
    "boundary_gap",
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
        "values": sorted(vals),
        "unique_values": uniq,
    }


def strict_inc(xs):
    return all(xs[i] < xs[i + 1] for i in range(len(xs) - 1))


def strict_dec(xs):
    return all(xs[i] > xs[i + 1] for i in range(len(xs) - 1))


def missing_phrases(text, phrases):
    return [p for p in phrases if p not in text]


def found_phrases(text, phrases):
    return [p for p in phrases if p in text]


def main():
    a058 = load_json(IN_058)
    a059 = load_json(IN_059)
    source = load_json(SOURCE_JSON)

    if not a058.get("audit_pass"):
        raise SystemExit("058 audit_pass is not true")
    if not a059.get("audit_pass"):
        raise SystemExit("059 audit_pass is not true")

    records, edge_path = find_edge_records(source)
    if not records:
        raise SystemExit("edge_records not found")

    rows = []
    for idx, raw in enumerate(records):
        fi = as_int(raw.get("form_index"))
        slot = as_int(raw.get("slot_delta_mod15"))
        fiber = as_int(raw.get("fiber_delta_mod60"))
        if fi in TARGET_FORMS and slot is not None and fiber is not None:
            rows.append({
                "record_index": idx,
                "form_index": fi,
                "euclidean_name": TARGET_NAMES[fi],
                "slot_delta_mod15": slot,
                "fiber_delta_mod60": fiber,
                "lift_q": as_int(raw.get("lift_q")),
                "from_C": as_int(raw.get("from_C")),
                "to_C": as_int(raw.get("to_C")),
            })

    groups = defaultdict(list)
    for row in rows:
        groups[row["form_index"]].append(row)

    group_rows = []
    for fi in TARGET_FORMS:
        xs = groups[fi]
        slot_vals = [r["slot_delta_mod15"] for r in xs]
        fiber_vals = [r["fiber_delta_mod60"] for r in xs]
        slot = stats(slot_vals)
        fiber = stats(fiber_vals)

        outside_boundary_span = slot["max"]
        inside_fiber_residual = fiber["min"]
        boundary_gap = outside_boundary_span - inside_fiber_residual

        group_rows.append({
            "form_index": fi,
            "euclidean_name": TARGET_NAMES[fi],
            "row_count": len(xs),
            "outside_boundary_span": outside_boundary_span,
            "outside_boundary_range": slot["range"],
            "outside_boundary_unique_max": slot["unique_max"],
            "inside_fiber_residual": inside_fiber_residual,
            "inside_fiber_unique_min": fiber["unique_min"],
            "boundary_gap": boundary_gap,
            "inside_captured": boundary_gap > 0,
            "slot_values": slot["values"],
            "fiber_values": fiber["values"],
            "slot_unique_values": slot["unique_values"],
            "fiber_unique_values": fiber["unique_values"],
        })

    outside_series = [r["outside_boundary_span"] for r in group_rows]
    inside_series = [r["inside_fiber_residual"] for r in group_rows]
    gap_series = [r["boundary_gap"] for r in group_rows]
    captured_series = [r["inside_captured"] for r in group_rows]

    boundary_phases = []
    for row in group_rows:
        if row["boundary_gap"] <= 0:
            phase = "outside_relation_without_inside_capture"
        elif row["euclidean_name"] == "hinge":
            phase = "inside_capture_begins_at_open_turn"
        elif row["euclidean_name"] == "closed_face":
            phase = "inside_separated_by_closed_boundary"
        elif row["euclidean_name"] == "filled_cell":
            phase = "inside_admitted_as_carried_content"
        else:
            phase = "inside_captured"
        rr = dict(row)
        rr["inside_outside_phase"] = phase
        boundary_phases.append(rr)

    # Sort by gap alone, as a candidate inside/outside depth order.
    gap_order = [
        r["form_index"]
        for r in sorted(group_rows, key=lambda r: (r["boundary_gap"], r["form_index"]))
    ]

    # Sort by the two-axis rule: outside asc, inside desc.
    two_axis_order = [
        r["form_index"]
        for r in sorted(group_rows, key=lambda r: (r["outside_boundary_span"], -r["inside_fiber_residual"], r["form_index"]))
    ]

    statement = (
        "Artifact 060 is an inside/outside boundary grammar audit. It reads slot_delta_mod15 as outside boundary span, "
        "fiber_delta_mod60 as inside fiber residual, and boundary_gap = outside boundary span minus inside fiber residual."
    )

    interpretation = (
        "The Euclidean order is recovered by a paired inside/outside grammar: outside boundary span rises while inside fiber residual falls. "
        "The edge state is the only state with non-positive boundary_gap; hinge begins inside capture; closed_face separates inside by boundary; filled_cell admits inside as carried content."
    )

    boundary = (
        "This is an inside/outside boundary grammar audit, not native closure. It uses form_index only to evaluate the four known groups, so answer-label leakage remains open. "
        "It does not prove the completion ladder natively, is not full role-labeled shared_B universe derivation, and is not Gap A closure."
    )

    combined = statement + "\n" + interpretation + "\n" + boundary
    missing = missing_phrases(combined, REQUIRED_PHRASES)
    forbidden = found_phrases(combined, FORBIDDEN_PHRASES)

    checks = {
        "monotone_selector_independence_058_pass": bool(a058.get("audit_pass")),
        "native_delta_partition_059_pass": bool(a059.get("audit_pass")),
        "source_json_exists": SOURCE_JSON.exists(),
        "edge_records_found": bool(records),
        "row_count_is_24": len(rows) == 24,
        "group_sizes_are_6_each": all(len(groups[fi]) == 6 for fi in TARGET_FORMS),
        "outside_boundary_span_strictly_increases": strict_inc(outside_series),
        "inside_fiber_residual_strictly_decreases": strict_dec(inside_series),
        "boundary_gap_strictly_increases": strict_inc(gap_series),
        "edge_only_non_positive_boundary_gap": captured_series == [False, True, True, True],
        "gap_order_recovers_euclidean_order": gap_order == TARGET_FORMS,
        "two_axis_order_recovers_euclidean_order": two_axis_order == TARGET_FORMS,
        "partition_negative_from_059_preserved": a059.get("checks", {}).get("exact_partition_found") is False,
        "form_index_used_only_for_evaluation": True,
        "answer_label_leakage_remains_open": True,
        "native_provenance_confirmed": False,
        "required_phrases_present": len(missing) == 0,
        "forbidden_phrases_absent": len(forbidden) == 0,
    }

    audit_pass = all([
        checks["monotone_selector_independence_058_pass"],
        checks["native_delta_partition_059_pass"],
        checks["source_json_exists"],
        checks["edge_records_found"],
        checks["row_count_is_24"],
        checks["group_sizes_are_6_each"],
        checks["outside_boundary_span_strictly_increases"],
        checks["inside_fiber_residual_strictly_decreases"],
        checks["boundary_gap_strictly_increases"],
        checks["edge_only_non_positive_boundary_gap"],
        checks["gap_order_recovers_euclidean_order"],
        checks["two_axis_order_recovers_euclidean_order"],
        checks["partition_negative_from_059_preserved"],
        checks["answer_label_leakage_remains_open"],
        checks["required_phrases_present"],
        checks["forbidden_phrases_absent"],
    ])

    verdict = (
        "inside_outside_boundary_grammar_candidate_found"
        if audit_pass
        else "inside_outside_boundary_grammar_not_confirmed"
    )

    result = {
        "status": "inside_outside_boundary_grammar_audit_recorded",
        "audit_id": "060",
        "inputs": {
            "monotone_selector_independence_audit_058": str(IN_058),
            "native_delta_partition_reconstruction_059": str(IN_059),
            "source_json": str(SOURCE_JSON),
            "edge_records_path": edge_path,
        },
        "checks": checks,
        "audit_pass": audit_pass,
        "verdict": verdict,
        "group_rows": group_rows,
        "boundary_phases": boundary_phases,
        "series": {
            "outside_boundary_span": outside_series,
            "inside_fiber_residual": inside_series,
            "boundary_gap": gap_series,
            "inside_captured": captured_series,
            "gap_order": gap_order,
            "two_axis_order": two_axis_order,
        },
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
            "form_index",
            "euclidean_name",
            "row_count",
            "outside_boundary_span",
            "inside_fiber_residual",
            "boundary_gap",
            "inside_captured",
            "inside_outside_phase",
            "slot_values",
            "fiber_values",
        ])
        for row in boundary_phases:
            w.writerow([
                row["form_index"],
                row["euclidean_name"],
                row["row_count"],
                row["outside_boundary_span"],
                row["inside_fiber_residual"],
                row["boundary_gap"],
                row["inside_captured"],
                row["inside_outside_phase"],
                json.dumps(row["slot_values"]),
                json.dumps(row["fiber_values"]),
            ])

    lines = []
    lines.append("# Inside/outside boundary grammar audit 060")
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
    lines.append("## Boundary phases")
    lines.append("")
    for row in boundary_phases:
        lines.append(
            "- {name}: outside={outside}, inside={inside}, boundary_gap={gap}, captured={captured}, phase={phase}".format(
                name=row["euclidean_name"],
                outside=row["outside_boundary_span"],
                inside=row["inside_fiber_residual"],
                gap=row["boundary_gap"],
                captured=row["inside_captured"],
                phase=row["inside_outside_phase"],
            )
        )
    lines.append("")
    lines.append("## Series")
    lines.append("")
    lines.append("- outside_boundary_span: `" + str(outside_series) + "`")
    lines.append("- inside_fiber_residual: `" + str(inside_series) + "`")
    lines.append("- boundary_gap: `" + str(gap_series) + "`")
    lines.append("- inside_captured: `" + str(captured_series) + "`")
    lines.append("- gap_order: `" + str(gap_order) + "`")
    lines.append("- two_axis_order: `" + str(two_axis_order) + "`")
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
    print("outside_boundary_span", outside_series)
    print("inside_fiber_residual", inside_series)
    print("boundary_gap", gap_series)
    print("inside_captured", captured_series)
    print("gap_order", gap_order)
    print("two_axis_order", two_axis_order)


if __name__ == "__main__":
    main()
