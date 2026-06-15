#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_020 = ROOT / "artifacts/json/native_g60_anchor_path_candidate_census_fixed_020.v1.json"
IN_022 = ROOT / "artifacts/json/native_g60_anchor_rank_fingerprint_law_022.v1.json"

OUT_JSON = ROOT / "artifacts/json/native_g60_anchor_rank_selector_theorem_023.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_g60_anchor_rank_selector_theorem_023.v1.csv"
OUT_NOTE = ROOT / "notes/native_g60_anchor_rank_selector_theorem_023.md"

STATES = ["O0", "O1", "B0", "B1"]


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def bits(state):
    if state == "O0":
        return 0, 0
    if state == "O1":
        return 0, 1
    if state == "B0":
        return 1, 0
    if state == "B1":
        return 1, 1
    raise ValueError(state)


def rank_law(b, r):
    return 2 + 7*b + 2*r - b*r


def main():
    a020 = load_json(IN_020)
    a022 = load_json(IN_022)

    if not a020.get("theorem_pass"):
        raise SystemExit("020 theorem_pass is not true")
    if not a022.get("theorem_pass"):
        raise SystemExit("022 theorem_pass is not true")

    rows = []
    per_state = {}

    for state in STATES:
        b, r = bits(state)
        target_rank = rank_law(b, r)

        candidates = [x for x in a020["rows"] if x["state"] == state]
        selected = [x for x in candidates if int(x["rank_by_best_support_sum_desc"]) == target_rank]

        observed = [x for x in candidates if x["matches_observed_cycle"]]
        observed_cycle = a020["per_state"][state]["observed_cycle"]

        selected_count = len(selected)
        selected_matches_observed = (
            selected_count == 1
            and len(observed) == 1
            and selected[0]["matches_observed_cycle"]
        )

        row = {
            "state": state,
            "shell_bit": b,
            "rank_bit": r,
            "target_rank": target_rank,
            "candidate_count": len(candidates),
            "selected_count": selected_count,
            "selected_candidate_index": selected[0]["candidate_index"] if selected_count == 1 else None,
            "selected_cycle": selected[0]["cycle"] if selected_count == 1 else None,
            "observed_cycle": observed_cycle,
            "selected_matches_observed": selected_matches_observed,
            "observed_candidate_index": observed[0]["candidate_index"] if observed else None,
        }

        rows.append(row)
        per_state[state] = row

    checks = {
        "candidate_census_020_theorem_pass": bool(a020.get("theorem_pass")),
        "rank_fingerprint_022_theorem_pass": bool(a022.get("theorem_pass")),
        "state_count_is_4": len(rows) == 4,
        "all_states_select_one_candidate": all(r["selected_count"] == 1 for r in rows),
        "all_selected_candidates_match_observed": all(r["selected_matches_observed"] for r in rows),
        "target_rank_profile_matches_022": {
            state: per_state[state]["target_rank"] for state in STATES
        } == a022["target_rank_profile"],
    }

    result = {
        "status": "native_g60_anchor_rank_selector_theorem_recorded",
        "audit_id": "023",
        "inputs": {
            "candidate_census_fixed_020": str(IN_020),
            "rank_fingerprint_law_022": str(IN_022),
        },
        "rank_law": "rank = 2 + 7*b + 2*r - b*r",
        "rows": rows,
        "per_state": per_state,
        "checks": checks,
        "theorem_pass": all(checks.values()),
        "claim": (
            "Given the corrected candidate census from artifact 020 and the rank law from artifact 022, "
            "the selected support-rank candidate in each state exactly recovers the observed Project 22 anchor path."
        ),
        "interpretation": (
            "This combines the candidate census and rank fingerprint into a bounded selector theorem. "
            "It shows that the observed anchor paths are exactly recoverable from state bits plus support-rank order "
            "inside the quotient-pair candidate universe. The remaining question is whether the rank law itself has "
            "native provenance rather than being inferred from the observed four-state target."
        ),
        "boundary": (
            "This is conditional on the observed anchor residue sets, observed pair-size profiles, and the rank law from artifact 022. "
            "It does not prove the rank law is native, does not derive anchor residue sets, does not test station fields, "
            "does not select unique relay mediators, does not derive the full role-labeled shared_B universe, and does not close Gap A."
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
            "target_rank",
            "candidate_count",
            "selected_count",
            "selected_candidate_index",
            "observed_candidate_index",
            "selected_matches_observed",
            "selected_cycle",
        ])
        for r in rows:
            w.writerow([
                r["state"],
                r["shell_bit"],
                r["rank_bit"],
                r["target_rank"],
                r["candidate_count"],
                r["selected_count"],
                r["selected_candidate_index"],
                r["observed_candidate_index"],
                "1" if r["selected_matches_observed"] else "0",
                json.dumps(r["selected_cycle"]),
            ])

    lines = []
    lines.append("# Native G60 anchor rank selector theorem 023")
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
    lines.append("- rank_law: `" + result["rank_law"] + "`")
    lines.append("")
    lines.append("## Per state")
    lines.append("")
    for state in STATES:
        r = per_state[state]
        lines.append("- " + state + ":")
        lines.append("  - bits: `(" + str(r["shell_bit"]) + ", " + str(r["rank_bit"]) + ")`")
        lines.append("  - target_rank: `" + str(r["target_rank"]) + "`")
        lines.append("  - candidate_count: `" + str(r["candidate_count"]) + "`")
        lines.append("  - selected_candidate_index: `" + str(r["selected_candidate_index"]) + "`")
        lines.append("  - observed_candidate_index: `" + str(r["observed_candidate_index"]) + "`")
        lines.append("  - selected_matches_observed: `" + str(r["selected_matches_observed"]) + "`")
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
    for state in STATES:
        r = per_state[state]
        print(state, "target_rank", r["target_rank"], "selected", r["selected_candidate_index"], "observed", r["observed_candidate_index"], "match", r["selected_matches_observed"])


if __name__ == "__main__":
    main()
