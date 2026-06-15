#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_015 = ROOT / "artifacts/json/native_g60_anchor_node_path_edge_support_015.v1.json"
IN_016 = ROOT / "artifacts/json/native_g60_anchor_node_path_residue_pair_support_016.v1.json"
IN_014 = ROOT / "artifacts/json/c_path_cover_paper_boundary_audit_014.v1.json"

OUT_JSON = ROOT / "artifacts/json/native_g60_anchor_path_quotient_pair_theorem_017.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_g60_anchor_path_quotient_pair_theorem_017.v1.csv"
OUT_NOTE = ROOT / "notes/native_g60_anchor_path_quotient_pair_theorem_017.md"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    a015 = load_json(IN_015)
    a016 = load_json(IN_016)
    a014 = load_json(IN_014)

    if not a015.get("all_checks_pass"):
        raise SystemExit("015 all_checks_pass is not true")
    if not a016.get("all_checks_pass"):
        raise SystemExit("016 all_checks_pass is not true")
    if not a014.get("boundary_pass"):
        raise SystemExit("014 boundary_pass is not true")

    rows = []
    per_state = {}

    for state in ["O0", "O1", "B0", "B1"]:
        p016 = a016["per_state"][state]
        p015 = a015["per_state"][state]

        state_rows = []
        for step in p016["steps"]:
            out = {
                "state": state,
                "step": int(step["step"]),
                "from_pair": step["from_pair"],
                "to_pair": step["to_pair"],
                "from_residues": step["from_residues"],
                "to_residues": step["to_residues"],
                "residue_pair_supported": bool(step["residue_pair_supported"]),
                "residue_cross_hit_count": int(step["residue_cross_hit_count"]),
                "residue_cross_support_count": int(step["residue_cross_support_count"]),
            }
            rows.append(out)
            state_rows.append(out)

        per_state[state] = {
            "closed_path": p016["closed_path"],
            "literal_supported_step_count_015": int(p015["supported_step_count"]),
            "literal_total_step_count_015": int(p015["total_step_count"]),
            "residue_supported_step_count_016": int(p016["supported_step_count"]),
            "residue_total_step_count_016": int(p016["step_count"]),
            "residue_all_steps_supported": bool(p016["all_steps_supported"]),
            "steps": state_rows,
        }

    total_steps = len(rows)
    residue_supported = sum(1 for r in rows if r["residue_pair_supported"])

    checks = {
        "literal_edge_support_015_checks_pass": bool(a015.get("all_checks_pass")),
        "residue_pair_support_016_checks_pass": bool(a016.get("all_checks_pass")),
        "paper_boundary_014_pass": bool(a014.get("boundary_pass")),
        "literal_support_was_partial": a015.get("supported_anchor_path_step_count") == 1,
        "literal_support_total_was_12": a015.get("total_anchor_path_step_count") == 12,
        "residue_support_total_is_12": total_steps == 12,
        "residue_supported_count_is_12": residue_supported == 12,
        "residue_uncovered_count_is_0": total_steps - residue_supported == 0,
        "all_anchor_residue_pair_steps_supported": bool(a016.get("all_anchor_residue_pair_steps_supported")),
        "all_states_have_three_supported_residue_steps": all(
            per_state[s]["residue_supported_step_count_016"] == 3
            and per_state[s]["residue_total_step_count_016"] == 3
            for s in per_state
        ),
    }

    result = {
        "status": "native_g60_anchor_path_quotient_pair_theorem_recorded",
        "audit_id": "017",
        "inputs": {
            "literal_anchor_support_015": str(IN_015),
            "residue_pair_support_016": str(IN_016),
            "paper_boundary_014": str(IN_014),
        },
        "total_anchor_path_step_count": total_steps,
        "literal_supported_step_count_015": a015.get("supported_anchor_path_step_count"),
        "literal_unsupported_step_count_015": a015.get("unsupported_anchor_path_step_count"),
        "residue_pair_supported_step_count_016": residue_supported,
        "residue_pair_unsupported_step_count_016": total_steps - residue_supported,
        "per_state": per_state,
        "rows": rows,
        "checks": checks,
        "theorem_pass": all(checks.values()),
        "claim": (
            "Every Project 22 closed anchor node-path step is supported after projecting canonical G60 vertices "
            "to mod15 residue pairs. The anchor paths are not literal native G60 pair-walks, but they are fully "
            "supported as quotient-pair walks."
        ),
        "interpretation": (
            "Artifact 015 showed that literal G60 pair-walk support covers only 1/12 anchor path steps. Artifact 016 "
            "showed that mod15 residue-pair support covers 12/12. Thus the inherited anchor paths are quotient-visible "
            "native structures rather than arbitrary literal edge walks."
        ),
        "boundary": (
            "This proves quotient-pair support for inherited Project 22 anchor paths. It does not derive why these exact "
            "anchor paths are selected, does not derive the lift masks, does not test station fields, does not select unique "
            "relay mediators, does not derive the full role-labeled shared_B universe, and does not close Gap A."
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
            "step",
            "from_pair",
            "to_pair",
            "from_residues",
            "to_residues",
            "residue_pair_supported",
            "residue_cross_hit_count",
            "residue_cross_support_count",
        ])
        for r in rows:
            w.writerow([
                r["state"],
                r["step"],
                " ".join(str(x) for x in r["from_pair"]),
                " ".join(str(x) for x in r["to_pair"]),
                " ".join(str(x) for x in r["from_residues"]),
                " ".join(str(x) for x in r["to_residues"]),
                "1" if r["residue_pair_supported"] else "0",
                r["residue_cross_hit_count"],
                r["residue_cross_support_count"],
            ])

    lines = []
    lines.append("# Native G60 anchor path quotient-pair theorem 017")
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
    lines.append("- literal_supported_step_count_015: `" + str(result["literal_supported_step_count_015"]) + "/12`")
    lines.append("- residue_pair_supported_step_count_016: `" + str(result["residue_pair_supported_step_count_016"]) + "/12`")
    lines.append("- residue_pair_unsupported_step_count_016: `" + str(result["residue_pair_unsupported_step_count_016"]) + "`")
    lines.append("")
    lines.append("## Per state")
    lines.append("")
    for state in ["O0", "O1", "B0", "B1"]:
        p = per_state[state]
        lines.append("- " + state + ":")
        lines.append("  - closed_path: `" + str(p["closed_path"]) + "`")
        lines.append(
            "  - literal support 015: `"
            + str(p["literal_supported_step_count_015"])
            + "/"
            + str(p["literal_total_step_count_015"])
            + "`"
        )
        lines.append(
            "  - residue support 016: `"
            + str(p["residue_supported_step_count_016"])
            + "/"
            + str(p["residue_total_step_count_016"])
            + "`"
        )
        for r in p["steps"]:
            lines.append(
                "  - step "
                + str(r["step"])
                + " residues `"
                + str(r["from_residues"])
                + " -> "
                + str(r["to_residues"])
                + "`: hit_count `"
                + str(r["residue_cross_hit_count"])
                + "`, support_count `"
                + str(r["residue_cross_support_count"])
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
    print("literal_supported_step_count_015", result["literal_supported_step_count_015"])
    print("residue_pair_supported_step_count_016", residue_supported)
    print("residue_pair_unsupported_step_count_016", total_steps - residue_supported)


if __name__ == "__main__":
    main()
