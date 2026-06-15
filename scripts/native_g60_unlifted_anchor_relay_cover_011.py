#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_010 = ROOT / "artifacts/json/native_g60_anchor_path_lift_mask_mediator_class_010.v1.json"

OUT_JSON = ROOT / "artifacts/json/native_g60_unlifted_anchor_relay_cover_011.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_g60_unlifted_anchor_relay_cover_011.v1.csv"
OUT_NOTE = ROOT / "notes/native_g60_unlifted_anchor_relay_cover_011.md"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    a010 = load_json(IN_010)

    if not a010.get("theorem_pass"):
        raise SystemExit("010 theorem_pass is not true")

    rows = []
    covered = []
    uncovered = []

    for prof in a010["transition_profiles"]:
        unlifted_hits = []
        lifted_hits = []
        closure_hits = []

        for hit in prof["hit_records"]:
            rec = {
                "state": prof["state"],
                "shell_bit": int(hit["shell_bit"]),
                "rank_bit": int(hit["rank_bit"]),
                "step": int(prof["step"]),
                "from_c": int(prof["from_c"]),
                "to_c": int(prof["to_c"]),
                "hit": int(hit["hit"]),
                "pair_index": int(hit["pair_index"]),
                "node_index": int(hit["node_index"]),
                "node": int(hit["node"]),
                "lift_value": int(hit["lift_value"]),
                "lift_class": hit["lift_class"],
                "is_closure_pair": bool(hit["is_closure_pair"]),
            }
            if rec["lift_class"] == "unlifted":
                unlifted_hits.append(rec)
            if rec["lift_class"] == "lifted":
                lifted_hits.append(rec)
            if rec["is_closure_pair"]:
                closure_hits.append(rec)

        out = {
            "state": prof["state"],
            "shell_bit": int(unlifted_hits[0]["shell_bit"]) if unlifted_hits else None,
            "rank_bit": int(unlifted_hits[0]["rank_bit"]) if unlifted_hits else None,
            "step": int(prof["step"]),
            "from_c": int(prof["from_c"]),
            "to_c": int(prof["to_c"]),
            "unlifted_hit_count": len(unlifted_hits),
            "lifted_hit_count": len(lifted_hits),
            "closure_hit_count": len(closure_hits),
            "unlifted_hits": unlifted_hits,
            "lifted_hits": lifted_hits,
            "closure_hits": closure_hits,
            "covered_by_unlifted_anchor_path": len(unlifted_hits) > 0,
            "unique_unlifted_hit": len(unlifted_hits) == 1,
        }

        rows.append(out)
        if out["covered_by_unlifted_anchor_path"]:
            covered.append(out)
        else:
            uncovered.append(out)

    transition_count = len(rows)
    covered_count = len(covered)
    unique_unlifted_count = sum(1 for r in rows if r["unique_unlifted_hit"])
    total_unlifted_hits = sum(r["unlifted_hit_count"] for r in rows)
    total_lifted_hits = sum(r["lifted_hit_count"] for r in rows)
    total_closure_hits = sum(r["closure_hit_count"] for r in rows)

    checks = {
        "lift_mask_class_010_theorem_pass": bool(a010.get("theorem_pass")),
        "unsupported_transition_count_is_6": transition_count == 6,
        "all_transitions_have_unlifted_anchor_cover": covered_count == transition_count,
        "uncovered_count_is_0": len(uncovered) == 0,
        "unlifted_hit_count_matches_010": total_unlifted_hits == a010.get("unlifted_hit_count"),
        "lifted_hit_count_matches_010": total_lifted_hits == a010.get("lifted_hit_count"),
    }

    result = {
        "status": "native_g60_unlifted_anchor_relay_cover_recorded",
        "audit_id": "011",
        "inputs": {
            "lift_mask_mediator_class_010": str(IN_010),
        },
        "transition_count": transition_count,
        "covered_count": covered_count,
        "uncovered_count": len(uncovered),
        "unique_unlifted_count": unique_unlifted_count,
        "total_unlifted_hits": total_unlifted_hits,
        "total_lifted_hits": total_lifted_hits,
        "total_closure_hits": total_closure_hits,
        "rows": rows,
        "uncovered": uncovered,
        "checks": checks,
        "theorem_pass": all(checks.values()),
        "claim": (
            "Every unsupported C transition is covered by at least one same-state unlifted anchor-path mediator. "
            "The unlifted anchor-path layer repairs all six missing direct C-residue transitions."
        ),
        "interpretation": (
            "Artifact 010 showed that most anchor-path mediator hits are unlifted. Artifact 011 sharpens this: "
            "unlifted anchor-path positions are sufficient to cover every missing C relay. This suggests the missing "
            "C-side closure is carried by the unlifted anchor layer, while lifted positions may be secondary or exceptional."
        ),
        "boundary": (
            "This is a cover theorem, not a unique selector theorem. It does not select a unique mediator for every transition, "
            "does not derive the anchor paths or lift masks from native G60 provenance, does not test station fields, does not "
            "derive the full role-labeled shared_B edge universe, and does not close Gap A."
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
            "covered_by_unlifted_anchor_path",
            "unique_unlifted_hit",
            "unlifted_hit_count",
            "lifted_hit_count",
            "closure_hit_count",
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
                "1" if r["covered_by_unlifted_anchor_path"] else "0",
                "1" if r["unique_unlifted_hit"] else "0",
                r["unlifted_hit_count"],
                r["lifted_hit_count"],
                r["closure_hit_count"],
                json.dumps(r["unlifted_hits"], sort_keys=True),
            ])

    lines = []
    lines.append("# Native G60 unlifted anchor relay cover 011")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Question")
    lines.append("")
    lines.append("Does the unlifted anchor-path layer cover every missing C relay?")
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- theorem_pass: `" + str(result["theorem_pass"]) + "`")
    lines.append("- transition_count: `" + str(transition_count) + "`")
    lines.append("- covered_count: `" + str(covered_count) + "`")
    lines.append("- uncovered_count: `" + str(len(uncovered)) + "`")
    lines.append("- unique_unlifted_count: `" + str(unique_unlifted_count) + "`")
    lines.append("- total_unlifted_hits: `" + str(total_unlifted_hits) + "`")
    lines.append("- total_lifted_hits: `" + str(total_lifted_hits) + "`")
    lines.append("- total_closure_hits: `" + str(total_closure_hits) + "`")
    lines.append("")
    lines.append("## Transition cover")
    lines.append("")
    for r in rows:
        hit_summary = [
            [h["hit"], h["pair_index"], h["node_index"], h["node"]]
            for h in r["unlifted_hits"]
        ]
        lines.append(
            "- "
            + r["state"]
            + " step "
            + str(r["step"])
            + " `"
            + str(r["from_c"])
            + " -> "
            + str(r["to_c"])
            + "`: unlifted hits `"
            + str(hit_summary)
            + "`, unique `"
            + str(r["unique_unlifted_hit"])
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
    print("transition_count", transition_count)
    print("covered_count", covered_count)
    print("uncovered_count", len(uncovered))
    print("unique_unlifted_count", unique_unlifted_count)
    print("total_unlifted_hits", total_unlifted_hits)
    print("total_lifted_hits", total_lifted_hits)
    print("total_closure_hits", total_closure_hits)


if __name__ == "__main__":
    main()
