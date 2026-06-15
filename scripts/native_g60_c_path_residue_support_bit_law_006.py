#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_004 = ROOT / "artifacts/json/native_g60_c_path_residue_support_004.v1.json"
IN_005 = ROOT / "artifacts/json/native_g60_c_path_residue_distance_005.v1.json"
IN_011 = ROOT / "source/project22_artifacts/json/lift_twist_local_answer_cell_generator_theorem_011.v1.json"

OUT_JSON = ROOT / "artifacts/json/native_g60_c_path_residue_support_bit_law_006.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_g60_c_path_residue_support_bit_law_006.v1.csv"
OUT_NOTE = ROOT / "notes/native_g60_c_path_residue_support_bit_law_006.md"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def predicted_direct_support(b, r, step):
    if b == 0:
        return step in (0, 1)
    return step == 2 * (1 - r)


def main():
    a004 = load_json(IN_004)
    a005 = load_json(IN_005)
    a011 = load_json(IN_011)

    if not a004.get("all_checks_pass"):
        raise SystemExit("004 all_checks_pass is not true")
    if not a005.get("all_checks_pass"):
        raise SystemExit("005 all_checks_pass is not true")
    if not a011.get("theorem_pass"):
        raise SystemExit("Project22 011 theorem_pass is not true")

    state_bits = {}
    for row in a011["generated_rows"]:
        state_bits[row["state"]] = {
            "shell_bit": int(row["shell_bit"]),
            "rank_bit": int(row["rank_bit"]),
        }

    distance_by_key = {}
    for row in a005["rows"]:
        distance_by_key[(row["state"], int(row["step"]))] = row

    rows = []
    mismatches = []

    for row in a004["rows"]:
        state = row["state"]
        step = int(row["step"])
        bits = state_bits[state]
        b = bits["shell_bit"]
        r = bits["rank_bit"]

        observed_direct = bool(row["directed_residue_supported"])
        predicted = predicted_direct_support(b, r, step)

        drow = distance_by_key.get((state, step), {})
        residue_distance = drow.get("residue_distance")
        shortest_path = drow.get("residue_shortest_path")

        out = {
            "state": state,
            "shell_bit": b,
            "rank_bit": r,
            "step": step,
            "from_c": int(row["from_c"]),
            "to_c": int(row["to_c"]),
            "observed_direct_residue_support": observed_direct,
            "predicted_direct_residue_support": predicted,
            "prediction_match": observed_direct == predicted,
            "residue_distance": residue_distance,
            "residue_shortest_path": shortest_path,
        }
        rows.append(out)
        if not out["prediction_match"]:
            mismatches.append(out)

    exact = len(mismatches) == 0

    support_rows = [r for r in rows if r["observed_direct_residue_support"]]
    unsupported_rows = [r for r in rows if not r["observed_direct_residue_support"]]

    support_profile = {
        "supported_count": len(support_rows),
        "unsupported_count": len(unsupported_rows),
        "supported_slots": [
            [r["state"], r["step"], r["from_c"], r["to_c"]]
            for r in support_rows
        ],
        "unsupported_slots": [
            [r["state"], r["step"], r["from_c"], r["to_c"], r["residue_distance"]]
            for r in unsupported_rows
        ],
    }

    checks = {
        "project22_011_theorem_pass": bool(a011.get("theorem_pass")),
        "residue_support_004_checks_pass": bool(a004.get("all_checks_pass")),
        "residue_distance_005_checks_pass": bool(a005.get("all_checks_pass")),
        "row_count_is_12": len(rows) == 12,
        "observed_supported_count_is_6": len(support_rows) == 6,
        "bit_step_law_exact": exact,
    }

    result = {
        "status": "native_g60_c_path_residue_support_bit_law_recorded",
        "audit_id": "006",
        "inputs": {
            "residue_support_004": str(IN_004),
            "residue_distance_005": str(IN_005),
            "project22_011": str(IN_011),
        },
        "candidate_law": (
            "direct residue support iff (shell_bit=0 and step in {0,1}) "
            "or (shell_bit=1 and step=2*(1-rank_bit))"
        ),
        "rows": rows,
        "mismatches": mismatches,
        "support_profile": support_profile,
        "checks": checks,
        "theorem_pass": all(checks.values()),
        "interpretation": (
            "The direct mod15 residue support pattern is generated exactly by a local bit/step law. "
            "This does not prove native local-cell provenance, but it shows that the half-supported quotient signal "
            "is structured by the same shell/rank bits that generate the local Lift & Twist cell."
        ),
        "boundary": (
            "This is a support-pattern law over the simple mod15 residue projection only. It does not derive the C paths, "
            "does not derive the local cell from native G60 provenance, does not derive the full role-labeled shared_B edge "
            "universe, and does not close Gap A."
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
            "observed_direct_residue_support",
            "predicted_direct_residue_support",
            "prediction_match",
            "residue_distance",
            "residue_shortest_path",
        ])
        for r in rows:
            w.writerow([
                r["state"],
                r["shell_bit"],
                r["rank_bit"],
                r["step"],
                r["from_c"],
                r["to_c"],
                "1" if r["observed_direct_residue_support"] else "0",
                "1" if r["predicted_direct_residue_support"] else "0",
                "1" if r["prediction_match"] else "0",
                r["residue_distance"],
                " ".join(str(x) for x in r["residue_shortest_path"]) if r["residue_shortest_path"] else "none",
            ])

    lines = []
    lines.append("# Native G60 C path residue support bit law 006")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Candidate law")
    lines.append("")
    lines.append(result["candidate_law"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- theorem_pass: `" + str(result["theorem_pass"]) + "`")
    lines.append("- bit_step_law_exact: `" + str(exact) + "`")
    lines.append("- supported_count: `" + str(len(support_rows)) + "`")
    lines.append("- unsupported_count: `" + str(len(unsupported_rows)) + "`")
    lines.append("")
    lines.append("## Supported slots")
    lines.append("")
    for x in support_profile["supported_slots"]:
        lines.append("- `" + str(x) + "`")
    lines.append("")
    lines.append("## Unsupported slots")
    lines.append("")
    for x in support_profile["unsupported_slots"]:
        lines.append("- `" + str(x) + "`")
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
    print("bit_step_law_exact", exact)
    print("supported_count", len(support_rows))
    print("unsupported_count", len(unsupported_rows))
    print("mismatch_count", len(mismatches))


if __name__ == "__main__":
    main()
