#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_048 = ROOT / "artifacts/json/local_scalar_provenance_frontier_048.v1.json"
IN_049 = ROOT / "artifacts/json/header_upstream_source_locator_049.v1.json"

OUT_JSON = ROOT / "artifacts/json/header_frontier_after_upstream_locator_050.v1.json"
OUT_CSV = ROOT / "artifacts/csv/header_frontier_after_upstream_locator_050.v1.csv"
OUT_NOTE = ROOT / "notes/header_frontier_after_upstream_locator_050.md"

REQUIRED_PHRASES = [
    "bounded header remains open",
    "not Gap A closure",
    "not native closure",
    "not full role-labeled shared_B universe",
    "not broader same-layer search",
]

FORBIDDEN_PHRASES = [
    "Gap A is closed",
    "native closure achieved",
    "bounded header derived",
    "full shared_B universe derived",
    "header source found",
]


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def missing_phrases(text, phrases):
    return [p for p in phrases if p not in text]


def found_phrases(text, phrases):
    return [p for p in phrases if p in text]


def main():
    a048 = load_json(IN_048)
    a049 = load_json(IN_049)

    if not a048.get("frontier_pass"):
        raise SystemExit("048 frontier_pass is not true")
    if not a049.get("audit_pass"):
        raise SystemExit("049 audit_pass is not true")

    closed_or_stabilized = [
        {
            "item": "local_scalar_provenance_normal_form",
            "status": "stabilized",
            "evidence": "048 records the local scalar-provenance normal form after 046 and 047.",
        },
        {
            "item": "same_layer_station_header_source_absent",
            "status": "bounded_negative",
            "evidence": "047 reports header_source_remains_open_small_bit_header_only.",
        },
        {
            "item": "imported_upstream_header_source_absent",
            "status": "bounded_negative",
            "evidence": "049 reports upstream_header_source_not_found_in_imported_sources.",
        },
        {
            "item": "header_target_set",
            "status": "stabilized",
            "evidence": "049 confirms the remaining headers are exactly free_sum, relay_max, and relay_sum.",
        },
    ]

    open_items = [
        {
            "item": "free_sum_header_source",
            "status": "open",
            "evidence": "049 found no exact upstream source for free_sum.",
        },
        {
            "item": "relay_max_header_source",
            "status": "open",
            "evidence": "049 found no exact upstream source for relay_max.",
        },
        {
            "item": "relay_sum_header_source",
            "status": "open",
            "evidence": "049 found no exact upstream source for relay_sum.",
        },
        {
            "item": "native_two_bit_header_mechanism",
            "status": "open",
            "evidence": "The bounded header remains open after same-layer and imported-upstream searches.",
        },
        {
            "item": "full_role_labeled_shared_B_universe",
            "status": "open",
            "evidence": "048 and 049 explicitly do not derive the full role-labeled shared_B universe.",
        },
        {
            "item": "Gap_A_closure",
            "status": "open",
            "evidence": "048 and 049 explicitly state this is not Gap A closure.",
        },
    ]

    plateau_statement = (
        "After 049, Project 24 has a sharper frontier. The local scalar-provenance normal form remains stable, "
        "but the bounded header remains open. The bounded header was not sourced by the same-layer station-feature audit "
        "and was not found in the imported upstream provenance scan. This is not native closure, not full role-labeled shared_B universe derivation, "
        "and not Gap A closure."
    )

    next_attack = (
        "The next attack should be a header-source attack, not broader same-layer search. It should target a new source for the bounded header: "
        "a native two-bit header mechanism, a richer source import beyond the current upstream cache, or a theorem-level explanation "
        "of why the remaining residuals are small after station-register compression."
    )

    combined = plateau_statement + "\n" + next_attack
    missing = missing_phrases(combined, REQUIRED_PHRASES)
    forbidden = found_phrases(combined, FORBIDDEN_PHRASES)

    checks = {
        "frontier_048_pass": bool(a048.get("frontier_pass")),
        "locator_049_pass": bool(a049.get("audit_pass")),
        "locator_049_verdict_is_no_source": a049.get("verdict") == "upstream_header_source_not_found_in_imported_sources",
        "remaining_header_target_count_is_3": a049.get("checks", {}).get("remaining_header_target_count") == 3,
        "remaining_headers_are_free_sum_relay_max_relay_sum": bool(a049.get("checks", {}).get("remaining_headers_are_free_sum_relay_max_relay_sum")),
        "upstream_source_found_for_all_is_false": not bool(a049.get("checks", {}).get("upstream_source_found_for_all")),
        "shared_exact_upstream_family_exists_is_false": not bool(a049.get("checks", {}).get("shared_exact_upstream_family_exists")),
        "shared_near_upstream_family_exists_is_false": not bool(a049.get("checks", {}).get("shared_near_upstream_family_exists")),
        "required_phrases_present": len(missing) == 0,
        "forbidden_phrases_absent": len(forbidden) == 0,
    }

    frontier_pass = all(checks.values())

    result = {
        "status": "header_frontier_after_upstream_locator_recorded",
        "audit_id": "050",
        "inputs": {
            "local_scalar_provenance_frontier_048": str(IN_048),
            "header_upstream_source_locator_049": str(IN_049),
        },
        "checks": checks,
        "frontier_pass": frontier_pass,
        "plateau_statement": plateau_statement,
        "next_attack": next_attack,
        "closed_or_stabilized": closed_or_stabilized,
        "open_items": open_items,
        "missing_required_phrases": missing,
        "forbidden_phrases_found": forbidden,
        "imported_upstream_scan_summary": {
            "json_file_count": a049.get("checks", {}).get("json_file_count"),
            "candidate_count": a049.get("checks", {}).get("candidate_count"),
            "verdict": a049.get("verdict"),
        },
        "interpretation": (
            "This artifact records the post-049 frontier. The header survived both same-layer station-feature search and imported-upstream source location. "
            "The result narrows the next problem to a new native header mechanism, richer source import, or theorem-level explanation."
        ),
        "boundary": (
            "This is a frontier record, not a new derivation. It does not derive the bounded header, does not derive the full role-labeled shared_B universe, "
            "and is not Gap A closure."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["group", "item", "status", "evidence"])
        for row in closed_or_stabilized:
            w.writerow(["closed_or_stabilized", row["item"], row["status"], row["evidence"]])
        for row in open_items:
            w.writerow(["open", row["item"], row["status"], row["evidence"]])

    lines = []
    lines.append("# Header frontier after upstream locator 050")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- frontier_pass: `" + str(frontier_pass) + "`")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Plateau statement")
    lines.append("")
    lines.append(plateau_statement)
    lines.append("")
    lines.append("## Closed or stabilized")
    lines.append("")
    for row in closed_or_stabilized:
        lines.append("- " + row["item"] + ": `" + row["status"] + "`")
        lines.append("  - " + row["evidence"])
    lines.append("")
    lines.append("## Open")
    lines.append("")
    for row in open_items:
        lines.append("- " + row["item"] + ": `" + row["status"] + "`")
        lines.append("  - " + row["evidence"])
    lines.append("")
    lines.append("## Imported upstream scan summary")
    lines.append("")
    lines.append("- json_file_count: `" + str(a049.get("checks", {}).get("json_file_count")) + "`")
    lines.append("- candidate_count: `" + str(a049.get("checks", {}).get("candidate_count")) + "`")
    lines.append("- verdict: `" + str(a049.get("verdict")) + "`")
    lines.append("")
    lines.append("## Next attack")
    lines.append("")
    lines.append(next_attack)
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append(result["boundary"])
    lines.append("")

    OUT_NOTE.write_text("\n".join(lines), encoding="utf-8")

    print("wrote", OUT_JSON)
    print("wrote", OUT_CSV)
    print("wrote", OUT_NOTE)
    print("status", result["status"])
    print("frontier_pass", frontier_pass)
    for k, v in checks.items():
        print(k, v)
    print("closed_or_stabilized", len(closed_or_stabilized))
    print("open_items", len(open_items))


if __name__ == "__main__":
    main()
