#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_002 = ROOT / "artifacts/json/source_ledger_and_target_alignment_002.v1.json"
IN_007 = ROOT / "artifacts/json/native_g60_c_path_residue_two_hop_relay_007.v1.json"
IN_011 = ROOT / "source/project22_artifacts/json/lift_twist_local_answer_cell_generator_theorem_011.v1.json"

OUT_JSON = ROOT / "artifacts/json/native_g60_c_relay_anchor_mediation_008.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_g60_c_relay_anchor_mediation_008.v1.csv"
OUT_NOTE = ROOT / "notes/native_g60_c_relay_anchor_mediation_008.md"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    a002 = load_json(IN_002)
    a007 = load_json(IN_007)
    a011 = load_json(IN_011)

    if not a002.get("ready_for_native_search"):
        raise SystemExit("002 ready_for_native_search is not true")
    if not a007.get("theorem_pass"):
        raise SystemExit("007 theorem_pass is not true")
    if not a011.get("theorem_pass"):
        raise SystemExit("Project22 011 theorem_pass is not true")

    local = {}
    for row in a011["generated_rows"]:
        local[row["state"]] = {
            "c_values": set(int(x) for x in row["c_values"]),
            "anchor_residues": set(int(x) for x in row["anchor_residues"]),
            "overlap": set(int(x) for x in row["overlap"]),
            "c_path": [int(x) for x in row["c_path"]],
        }

    rows = []
    anchor_mediated = []
    c_value_mediated = []
    overlap_mediated = []

    for row in a007["unsupported_rows"]:
        state = row["state"]
        mediators = set(int(x) for x in row["mediators"])

        c_values = local[state]["c_values"]
        anchor_residues = local[state]["anchor_residues"]
        overlap = local[state]["overlap"]

        anchor_hits = sorted(mediators.intersection(anchor_residues))
        c_value_hits = sorted(mediators.intersection(c_values))
        overlap_hits = sorted(mediators.intersection(overlap))

        out = {
            "state": state,
            "shell_bit": int(row["shell_bit"]),
            "rank_bit": int(row["rank_bit"]),
            "step": int(row["step"]),
            "from_c": int(row["from_c"]),
            "to_c": int(row["to_c"]),
            "mediators": sorted(mediators),
            "anchor_residues": sorted(anchor_residues),
            "c_values": sorted(c_values),
            "overlap": sorted(overlap),
            "anchor_mediator_hits": anchor_hits,
            "c_value_mediator_hits": c_value_hits,
            "overlap_mediator_hits": overlap_hits,
            "anchor_mediated": len(anchor_hits) > 0,
            "c_value_mediated": len(c_value_hits) > 0,
            "overlap_mediated": len(overlap_hits) > 0,
            "anchor_hit_count": len(anchor_hits),
            "c_value_hit_count": len(c_value_hits),
            "overlap_hit_count": len(overlap_hits),
        }

        rows.append(out)

        if out["anchor_mediated"]:
            anchor_mediated.append(out)
        if out["c_value_mediated"]:
            c_value_mediated.append(out)
        if out["overlap_mediated"]:
            overlap_mediated.append(out)

    unsupported_count = len(rows)
    anchor_mediated_count = len(anchor_mediated)
    c_value_mediated_count = len(c_value_mediated)
    overlap_mediated_count = len(overlap_mediated)

    unique_anchor_mediated_count = sum(1 for r in rows if r["anchor_hit_count"] == 1)

    checks = {
        "source_ledger_ready": bool(a002.get("ready_for_native_search")),
        "relay_007_theorem_pass": bool(a007.get("theorem_pass")),
        "project22_011_theorem_pass": bool(a011.get("theorem_pass")),
        "unsupported_row_count_is_6": unsupported_count == 6,
        "all_unsupported_have_two_hop_relay": bool(a007.get("checks", {}).get("all_unsupported_have_two_hop_relay")),
        "all_unsupported_are_anchor_mediated": anchor_mediated_count == unsupported_count,
        "not_all_unsupported_are_c_value_mediated": c_value_mediated_count < unsupported_count,
        "not_all_unsupported_are_overlap_mediated": overlap_mediated_count < unsupported_count,
    }

    result = {
        "status": "native_g60_c_relay_anchor_mediation_recorded",
        "audit_id": "008",
        "inputs": {
            "source_ledger_002": str(IN_002),
            "two_hop_relay_007": str(IN_007),
            "project22_011": str(IN_011),
        },
        "unsupported_count": unsupported_count,
        "anchor_mediated_count": anchor_mediated_count,
        "c_value_mediated_count": c_value_mediated_count,
        "overlap_mediated_count": overlap_mediated_count,
        "unique_anchor_mediated_count": unique_anchor_mediated_count,
        "rows": rows,
        "checks": checks,
        "theorem_pass": all(checks.values()),
        "claim": (
            "Every unsupported C transition from artifact 006 has a two-hop residue relay from artifact 007 "
            "whose mediator intersects the same state's Project 22 anchor residue set. The mediation is not "
            "explained by C values or overlap markers alone."
        ),
        "interpretation": (
            "The missing half of the direct C-residue support pattern is repaired through the anchor-residue payload "
            "of the same local state. This suggests that C-side closure and anchor-side residue structure are coupled "
            "inside the local Lift & Twist cell."
        ),
        "boundary": (
            "This is an anchor-mediation audit over the simple mod15 residue quotient. It does not select a unique mediator "
            "in every case, does not derive the local cell from native G60 provenance, does not test station fields or lifted masks, "
            "does not derive the full role-labeled shared_B edge universe, and does not close Gap A."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "state",
            "shell_bit",
            "rank_bit",
            "step",
            "from_c",
            "to_c",
            "mediators",
            "anchor_residues",
            "anchor_mediator_hits",
            "anchor_mediated",
            "c_values",
            "c_value_mediator_hits",
            "c_value_mediated",
            "overlap",
            "overlap_mediator_hits",
            "overlap_mediated",
        ])
        for r in rows:
            w.writerow([
                r["state"],
                r["shell_bit"],
                r["rank_bit"],
                r["step"],
                r["from_c"],
                r["to_c"],
                " ".join(str(x) for x in r["mediators"]),
                " ".join(str(x) for x in r["anchor_residues"]),
                " ".join(str(x) for x in r["anchor_mediator_hits"]) or "none",
                "1" if r["anchor_mediated"] else "0",
                " ".join(str(x) for x in r["c_values"]),
                " ".join(str(x) for x in r["c_value_mediator_hits"]) or "none",
                "1" if r["c_value_mediated"] else "0",
                " ".join(str(x) for x in r["overlap"]) or "none",
                " ".join(str(x) for x in r["overlap_mediator_hits"]) or "none",
                "1" if r["overlap_mediated"] else "0",
            ])

    lines = []
    lines.append("# Native G60 C relay anchor mediation 008")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Question")
    lines.append("")
    lines.append("Are the missing C transitions repaired through same-state anchor residues?")
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- theorem_pass: `" + str(result["theorem_pass"]) + "`")
    lines.append("- unsupported_count: `" + str(unsupported_count) + "`")
    lines.append("- anchor_mediated_count: `" + str(anchor_mediated_count) + "`")
    lines.append("- c_value_mediated_count: `" + str(c_value_mediated_count) + "`")
    lines.append("- overlap_mediated_count: `" + str(overlap_mediated_count) + "`")
    lines.append("- unique_anchor_mediated_count: `" + str(unique_anchor_mediated_count) + "`")
    lines.append("")
    lines.append("## Anchor-mediated relays")
    lines.append("")
    for r in rows:
        lines.append(
            "- "
            + r["state"]
            + " step "
            + str(r["step"])
            + ": `"
            + str(r["from_c"])
            + " -> "
            + str(r["to_c"])
            + "`, mediators `"
            + str(r["mediators"])
            + "`, anchor hits `"
            + str(r["anchor_mediator_hits"])
            + "`"
        )
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Claim")
    lines.append("")
    lines.append(result["claim"])
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(result["interpretation"])
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
    print("theorem_pass", result["theorem_pass"])
    print("unsupported_count", unsupported_count)
    print("anchor_mediated_count", anchor_mediated_count)
    print("c_value_mediated_count", c_value_mediated_count)
    print("overlap_mediated_count", overlap_mediated_count)
    print("unique_anchor_mediated_count", unique_anchor_mediated_count)


if __name__ == "__main__":
    main()
