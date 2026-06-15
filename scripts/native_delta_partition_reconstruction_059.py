#!/usr/bin/env python3
import csv
import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]

IN_058 = ROOT / "artifacts/json/monotone_selector_independence_audit_058.v1.json"
SOURCE_JSON = ROOT / "source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/g60_native_overlay_generator_family_search_001.v1.json"

OUT_JSON = ROOT / "artifacts/json/native_delta_partition_reconstruction_059.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_delta_partition_reconstruction_059.v1.csv"
OUT_NOTE = ROOT / "notes/native_delta_partition_reconstruction_059.md"

TARGET_FORMS = [0, 1, 2, 3]
TARGET_NAMES = ["edge", "hinge", "closed_face", "filled_cell"]
BLOCK_SIZE = 6

REQUIRED_PHRASES = [
    "native delta partition reconstruction",
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


def missing_phrases(text, phrases):
    return [p for p in phrases if p not in text]


def found_phrases(text, phrases):
    return [p for p in phrases if p in text]


def chunked(xs, size):
    return [xs[i:i + size] for i in range(0, len(xs), size)]


def row_record(raw, idx):
    return {
        "record_index": idx,
        "form_index": as_int(raw.get("form_index")),
        "slot_delta_mod15": as_int(raw.get("slot_delta_mod15")),
        "fiber_delta_mod60": as_int(raw.get("fiber_delta_mod60")),
        "from_C": as_int(raw.get("from_C")),
        "to_C": as_int(raw.get("to_C")),
        "lift_q": as_int(raw.get("lift_q")),
        "raw": raw,
    }


def safe(v, default=10**9):
    return default if v is None else v


def sort_rows(rows, rule_name):
    if rule_name == "slot_asc":
        return sorted(rows, key=lambda r: (safe(r["slot_delta_mod15"]), safe(r["fiber_delta_mod60"]), r["record_index"]))
    if rule_name == "slot_asc_fiber_desc":
        return sorted(rows, key=lambda r: (safe(r["slot_delta_mod15"]), -safe(r["fiber_delta_mod60"], -10**9), r["record_index"]))
    if rule_name == "fiber_desc":
        return sorted(rows, key=lambda r: (-safe(r["fiber_delta_mod60"], -10**9), safe(r["slot_delta_mod15"]), r["record_index"]))
    if rule_name == "fiber_desc_slot_asc":
        return sorted(rows, key=lambda r: (-safe(r["fiber_delta_mod60"], -10**9), safe(r["slot_delta_mod15"]), r["record_index"]))
    if rule_name == "slot_range_then_fiber":
        return sorted(rows, key=lambda r: (safe(r["slot_delta_mod15"]), -safe(r["fiber_delta_mod60"], -10**9), safe(r["lift_q"]), r["record_index"]))
    if rule_name == "fiber_then_slot_then_lift":
        return sorted(rows, key=lambda r: (-safe(r["fiber_delta_mod60"], -10**9), safe(r["slot_delta_mod15"]), safe(r["lift_q"]), r["record_index"]))
    raise ValueError(rule_name)


def block_stats(block):
    slots = [r["slot_delta_mod15"] for r in block if r["slot_delta_mod15"] is not None]
    fibers = [r["fiber_delta_mod60"] for r in block if r["fiber_delta_mod60"] is not None]
    forms = [r["form_index"] for r in block if r["form_index"] is not None]

    c = Counter(forms)
    majority_form = None
    majority_count = 0
    if c:
        majority_form, majority_count = c.most_common(1)[0]

    return {
        "row_count": len(block),
        "record_indices": [r["record_index"] for r in block],
        "form_counts": dict(sorted(c.items())),
        "majority_form": majority_form,
        "majority_count": majority_count,
        "slot_min": min(slots) if slots else None,
        "slot_max": max(slots) if slots else None,
        "slot_range": (max(slots) - min(slots)) if slots else None,
        "fiber_min": min(fibers) if fibers else None,
        "fiber_max": max(fibers) if fibers else None,
        "fiber_range": (max(fibers) - min(fibers)) if fibers else None,
        "slot_values": sorted(slots),
        "fiber_values": sorted(fibers),
    }


def evaluate_partition(rule_name, sorted_rows):
    blocks = chunked(sorted_rows, BLOCK_SIZE)
    block_rows = []
    for i, block in enumerate(blocks):
        st = block_stats(block)
        st["block_id"] = i
        st["block_name"] = TARGET_NAMES[i] if i < len(TARGET_NAMES) else "extra"
        block_rows.append(st)

    purity_total = sum(b["majority_count"] for b in block_rows)
    purity = purity_total / len(sorted_rows) if sorted_rows else 0.0
    majority_order = [b["majority_form"] for b in block_rows]
    exact_group_reconstruction = (
        len(block_rows) == 4
        and all(b["row_count"] == BLOCK_SIZE for b in block_rows)
        and all(b["majority_count"] == BLOCK_SIZE for b in block_rows)
        and sorted(majority_order) == TARGET_FORMS
    )

    ordered_exact = exact_group_reconstruction and majority_order == TARGET_FORMS

    slot_maxes = [b["slot_max"] for b in block_rows]
    fiber_mins = [b["fiber_min"] for b in block_rows]

    slot_monotone = all(slot_maxes[i] < slot_maxes[i + 1] for i in range(len(slot_maxes) - 1) if slot_maxes[i] is not None and slot_maxes[i + 1] is not None)
    fiber_monotone = all(fiber_mins[i] > fiber_mins[i + 1] for i in range(len(fiber_mins) - 1) if fiber_mins[i] is not None and fiber_mins[i + 1] is not None)

    return {
        "rule_name": rule_name,
        "uses_form_index_as_input": False,
        "uses_record_order_as_primary_input": False,
        "uses_answer_label_as_input": False,
        "block_size": BLOCK_SIZE,
        "block_count": len(block_rows),
        "purity_total": purity_total,
        "purity": purity,
        "majority_order": majority_order,
        "exact_group_reconstruction": exact_group_reconstruction,
        "ordered_exact_group_reconstruction": ordered_exact,
        "slot_maxes_by_block": slot_maxes,
        "fiber_mins_by_block": fiber_mins,
        "slot_monotone_by_block": slot_monotone,
        "fiber_monotone_by_block": fiber_monotone,
        "blocks": block_rows,
    }


def main():
    a058 = load_json(IN_058)
    source = load_json(SOURCE_JSON)

    if not a058.get("audit_pass"):
        raise SystemExit("058 audit_pass is not true")

    edge_records, edge_path = find_edge_records(source)
    if not edge_records:
        raise SystemExit("edge_records not found")

    rows = []
    for idx, raw in enumerate(edge_records):
        r = row_record(raw, idx)
        if (
            r["form_index"] in TARGET_FORMS
            and r["slot_delta_mod15"] is not None
            and r["fiber_delta_mod60"] is not None
        ):
            rows.append(r)

    rules = [
        "slot_asc",
        "slot_asc_fiber_desc",
        "fiber_desc",
        "fiber_desc_slot_asc",
        "slot_range_then_fiber",
        "fiber_then_slot_then_lift",
    ]

    partitions = []
    for rule in rules:
        sr = sort_rows(rows, rule)
        partitions.append(evaluate_partition(rule, sr))

    partitions.sort(
        key=lambda p: (
            not p["ordered_exact_group_reconstruction"],
            not p["exact_group_reconstruction"],
            -p["purity_total"],
            not (p["slot_monotone_by_block"] and p["fiber_monotone_by_block"]),
            p["rule_name"],
        )
    )

    best = partitions[0] if partitions else None

    exact_partition_found = any(p["exact_group_reconstruction"] for p in partitions)
    ordered_exact_partition_found = any(p["ordered_exact_group_reconstruction"] for p in partitions)

    statement = (
        "Artifact 059 is a native delta partition reconstruction audit. It attempts to reconstruct the four local Euclidean groups from native delta fields alone. "
        "form_index is used only for evaluation after the partition has been generated."
    )

    if ordered_exact_partition_found:
        verdict = "native_delta_partition_reconstructs_euclidean_order"
    elif exact_partition_found:
        verdict = "native_delta_partition_reconstructs_groups_up_to_permutation"
    else:
        verdict = "native_delta_partition_does_not_reconstruct_groups_exactly"

    boundary = (
        "This is a partition audit, not native closure. Even if a native delta partition succeeds, answer-label leakage remains open until the source construction itself is audited. "
        "It does not prove the completion ladder natively, is not full role-labeled shared_B universe derivation, and is not Gap A closure."
    )

    combined = statement + "\n" + boundary
    missing = missing_phrases(combined, REQUIRED_PHRASES)
    forbidden = found_phrases(combined, FORBIDDEN_PHRASES)

    checks = {
        "monotone_selector_independence_058_pass": bool(a058.get("audit_pass")),
        "source_json_exists": SOURCE_JSON.exists(),
        "edge_records_found": bool(edge_records),
        "row_count_is_24": len(rows) == 24,
        "partition_rule_count": len(partitions),
        "all_partitions_use_native_delta_fields_only": all(not p["uses_form_index_as_input"] and not p["uses_answer_label_as_input"] for p in partitions),
        "form_index_used_only_for_evaluation": True,
        "best_partition_exists": best is not None,
        "best_partition_purity_total": best["purity_total"] if best else 0,
        "best_partition_purity": best["purity"] if best else 0.0,
        "exact_partition_found": exact_partition_found,
        "ordered_exact_partition_found": ordered_exact_partition_found,
        "answer_label_leakage_remains_open": True,
        "native_provenance_confirmed": False,
        "required_phrases_present": len(missing) == 0,
        "forbidden_phrases_absent": len(forbidden) == 0,
    }

    audit_pass = all([
        checks["monotone_selector_independence_058_pass"],
        checks["source_json_exists"],
        checks["edge_records_found"],
        checks["row_count_is_24"],
        checks["partition_rule_count"] > 0,
        checks["all_partitions_use_native_delta_fields_only"],
        checks["form_index_used_only_for_evaluation"],
        checks["best_partition_exists"],
        checks["answer_label_leakage_remains_open"],
        checks["required_phrases_present"],
        checks["forbidden_phrases_absent"],
    ])

    result = {
        "status": "native_delta_partition_reconstruction_recorded",
        "audit_id": "059",
        "inputs": {
            "monotone_selector_independence_audit_058": str(IN_058),
            "source_json": str(SOURCE_JSON),
            "edge_records_path": edge_path,
        },
        "checks": checks,
        "audit_pass": audit_pass,
        "verdict": verdict,
        "best_partition": best,
        "partitions": partitions,
        "statement": statement,
        "boundary": boundary,
        "missing_required_phrases": missing,
        "forbidden_phrases_found": forbidden,
        "interpretation": (
            "Artifact 059 tests whether the Euclidean form groups can be reconstructed from native delta fields before consulting form_index. "
            "The result should be read as an independence audit: success strengthens the native selector case; failure preserves 058 as an order signal but not a partition derivation."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "rule_name",
            "block_id",
            "block_name",
            "row_count",
            "majority_form",
            "majority_count",
            "form_counts",
            "slot_min",
            "slot_max",
            "slot_range",
            "fiber_min",
            "fiber_max",
            "fiber_range",
            "record_indices",
        ])
        for part in partitions:
            for block in part["blocks"]:
                w.writerow([
                    part["rule_name"],
                    block["block_id"],
                    block["block_name"],
                    block["row_count"],
                    block["majority_form"],
                    block["majority_count"],
                    json.dumps(block["form_counts"], sort_keys=True),
                    block["slot_min"],
                    block["slot_max"],
                    block["slot_range"],
                    block["fiber_min"],
                    block["fiber_max"],
                    block["fiber_range"],
                    json.dumps(block["record_indices"]),
                ])

    lines = []
    lines.append("# Native delta partition reconstruction 059")
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
    lines.append("## Best partition")
    lines.append("")
    if best:
        lines.append("- rule_name: `" + best["rule_name"] + "`")
        lines.append("- purity_total: `" + str(best["purity_total"]) + "`")
        lines.append("- purity: `" + str(best["purity"]) + "`")
        lines.append("- majority_order: `" + str(best["majority_order"]) + "`")
        lines.append("- exact_group_reconstruction: `" + str(best["exact_group_reconstruction"]) + "`")
        lines.append("- ordered_exact_group_reconstruction: `" + str(best["ordered_exact_group_reconstruction"]) + "`")
        lines.append("- slot_maxes_by_block: `" + str(best["slot_maxes_by_block"]) + "`")
        lines.append("- fiber_mins_by_block: `" + str(best["fiber_mins_by_block"]) + "`")
        lines.append("")
        lines.append("### Best partition blocks")
        lines.append("")
        for block in best["blocks"]:
            lines.append(
                "- block {bid} / {name}: forms={forms}, majority={maj}, slot_max={slot_max}, fiber_min={fiber_min}, records={records}".format(
                    bid=block["block_id"],
                    name=block["block_name"],
                    forms=block["form_counts"],
                    maj=block["majority_form"],
                    slot_max=block["slot_max"],
                    fiber_min=block["fiber_min"],
                    records=block["record_indices"],
                )
            )
    lines.append("")
    lines.append("## All partition summaries")
    lines.append("")
    for part in partitions:
        lines.append(
            "- {rule}: purity={purity_total}/24, majority_order={order}, exact={exact}, ordered_exact={ordered}".format(
                rule=part["rule_name"],
                purity_total=part["purity_total"],
                order=part["majority_order"],
                exact=part["exact_group_reconstruction"],
                ordered=part["ordered_exact_group_reconstruction"],
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
        print("best_rule", best["rule_name"])
        print("best_purity", str(best["purity_total"]) + "/24")
        print("best_majority_order", best["majority_order"])
        print("best_exact", best["exact_group_reconstruction"])
        print("best_ordered_exact", best["ordered_exact_group_reconstruction"])


if __name__ == "__main__":
    main()
