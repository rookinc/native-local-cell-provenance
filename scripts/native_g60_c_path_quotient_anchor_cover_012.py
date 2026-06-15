#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_006 = ROOT / "artifacts/json/native_g60_c_path_residue_support_bit_law_006.v1.json"
IN_011 = ROOT / "artifacts/json/native_g60_unlifted_anchor_relay_cover_011.v1.json"

OUT_JSON = ROOT / "artifacts/json/native_g60_c_path_quotient_anchor_cover_012.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_g60_c_path_quotient_anchor_cover_012.v1.csv"
OUT_NOTE = ROOT / "notes/native_g60_c_path_quotient_anchor_cover_012.md"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def key(row):
    return (row["state"], int(row["step"]))


def main():
    a006 = load_json(IN_006)
    a011 = load_json(IN_011)

    if not a006.get("theorem_pass"):
        raise SystemExit("006 theorem_pass is not true")
    if not a011.get("theorem_pass"):
        raise SystemExit("011 theorem_pass is not true")

    relay_by_key = {key(r): r for r in a011["rows"]}

    rows = []
    direct_rows = []
    relay_rows = []
    uncovered_rows = []

    for r in a006["rows"]:
        k = key(r)

        observed_direct = bool(r["observed_direct_residue_support"])
        predicted_direct = bool(r["predicted_direct_residue_support"])
        prediction_match = bool(r["prediction_match"])

        relay = relay_by_key.get(k)
        relay_covered = False
        unlifted_hits = []
        if relay is not None:
            relay_covered = bool(relay["covered_by_unlifted_anchor_path"])
            unlifted_hits = relay["unlifted_hits"]

        if observed_direct:
            support_class = "direct_residue"
            covered = True
        elif relay_covered:
            support_class = "unlifted_anchor_relay"
            covered = True
        else:
            support_class = "uncovered"
            covered = False

        out = {
            "state": r["state"],
            "shell_bit": int(r["shell_bit"]),
            "rank_bit": int(r["rank_bit"]),
            "step": int(r["step"]),
            "from_c": int(r["from_c"]),
            "to_c": int(r["to_c"]),
            "observed_direct_residue_support": observed_direct,
            "predicted_direct_residue_support": predicted_direct,
            "bit_law_prediction_match": prediction_match,
            "unlifted_anchor_relay_cover": relay_covered,
            "unlifted_hit_count": len(unlifted_hits),
            "unlifted_hits": unlifted_hits,
            "support_class": support_class,
            "covered": covered,
        }
        rows.append(out)

        if support_class == "direct_residue":
            direct_rows.append(out)
        elif support_class == "unlifted_anchor_relay":
            relay_rows.append(out)
        else:
            uncovered_rows.append(out)

    coverage_by_state = {}
    for r in rows:
        coverage_by_state.setdefault(r["state"], []).append({
            "step": r["step"],
            "from_c": r["from_c"],
            "to_c": r["to_c"],
            "support_class": r["support_class"],
            "covered": r["covered"],
        })

    checks = {
        "bit_law_006_theorem_pass": bool(a006.get("theorem_pass")),
        "unlifted_cover_011_theorem_pass": bool(a011.get("theorem_pass")),
        "total_c_path_step_count_is_12": len(rows) == 12,
        "direct_residue_count_is_6": len(direct_rows) == 6,
        "unlifted_anchor_relay_count_is_6": len(relay_rows) == 6,
        "uncovered_count_is_0": len(uncovered_rows) == 0,
        "all_steps_covered": all(r["covered"] for r in rows),
        "all_direct_steps_match_bit_law": all(r["bit_law_prediction_match"] for r in direct_rows),
        "all_relay_steps_match_bit_law_complement": all(
            (not r["predicted_direct_residue_support"]) and r["bit_law_prediction_match"]
            for r in relay_rows
        ),
    }

    result = {
        "status": "native_g60_c_path_quotient_anchor_cover_recorded",
        "audit_id": "012",
        "inputs": {
            "bit_law_006": str(IN_006),
            "unlifted_cover_011": str(IN_011),
        },
        "total_c_path_step_count": len(rows),
        "direct_residue_count": len(direct_rows),
        "unlifted_anchor_relay_count": len(relay_rows),
        "uncovered_count": len(uncovered_rows),
        "coverage_by_state": coverage_by_state,
        "rows": rows,
        "checks": checks,
        "theorem_pass": all(checks.values()),
        "claim": (
            "Every Project 22 C-path step is covered by one of two mechanisms: direct mod15 G60 residue support "
            "or same-state unlifted anchor-path relay support. The bit/step law from artifact 006 selects the direct half, "
            "and artifact 011 covers the complementary relay half."
        ),
        "interpretation": (
            "The Project 22 C paths are not literal G60 paths, but they are fully covered by a coupled quotient-anchor mechanism. "
            "Direct quotient support accounts for six steps. The remaining six are repaired by the same state's unlifted anchor-path layer."
        ),
        "boundary": (
            "This is a C-path cover theorem over the mod15 residue quotient plus inherited Project 22 anchor paths and lift masks. "
            "It does not derive the anchor paths or lift masks from native G60 provenance, does not select unique mediators for every relay, "
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
            "support_class",
            "covered",
            "observed_direct_residue_support",
            "predicted_direct_residue_support",
            "unlifted_anchor_relay_cover",
            "unlifted_hit_count",
            "unlifted_hits",
        ])
        for r in rows:
            w.writerow([
                r["state"],
                r["shell_bit"],
                r["rank_bit"],
                r["step"],
                r["from_c"],
                r["to_c"],
                r["support_class"],
                "1" if r["covered"] else "0",
                "1" if r["observed_direct_residue_support"] else "0",
                "1" if r["predicted_direct_residue_support"] else "0",
                "1" if r["unlifted_anchor_relay_cover"] else "0",
                r["unlifted_hit_count"],
                json.dumps(r["unlifted_hits"], sort_keys=True),
            ])

    lines = []
    lines.append("# Native G60 C path quotient-anchor cover 012")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Claim")
    lines.append("")
    lines.append(result["claim"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- theorem_pass: `" + str(result["theorem_pass"]) + "`")
    lines.append("- total_c_path_step_count: `" + str(len(rows)) + "`")
    lines.append("- direct_residue_count: `" + str(len(direct_rows)) + "`")
    lines.append("- unlifted_anchor_relay_count: `" + str(len(relay_rows)) + "`")
    lines.append("- uncovered_count: `" + str(len(uncovered_rows)) + "`")
    lines.append("")
    lines.append("## Coverage by state")
    lines.append("")
    for state in ["O0", "O1", "B0", "B1"]:
        lines.append("- " + state + ":")
        for x in coverage_by_state.get(state, []):
            lines.append(
                "  - step "
                + str(x["step"])
                + " `"
                + str(x["from_c"])
                + " -> "
                + str(x["to_c"])
                + "`: `"
                + x["support_class"]
                + "`"
            )
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
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
    print("total_c_path_step_count", len(rows))
    print("direct_residue_count", len(direct_rows))
    print("unlifted_anchor_relay_count", len(relay_rows))
    print("uncovered_count", len(uncovered_rows))


if __name__ == "__main__":
    main()
