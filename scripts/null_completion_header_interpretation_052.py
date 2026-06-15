#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_051 = ROOT / "artifacts/json/native_two_bit_header_mechanism_051.v1.json"

OUT_JSON = ROOT / "artifacts/json/null_completion_header_interpretation_052.v1.json"
OUT_CSV = ROOT / "artifacts/csv/null_completion_header_interpretation_052.v1.csv"
OUT_NOTE = ROOT / "notes/null_completion_header_interpretation_052.md"

STATES = ["O0", "O1", "B0", "B1"]
TARGETS = ["free_sum", "relay_max", "relay_sum"]

COMPLETION_LADDER = [
    {
        "level": 0,
        "name": "null",
        "shape": "empty relation",
        "reading": "no registered local relation",
    },
    {
        "level": 1,
        "name": "point",
        "shape": "one marked point",
        "reading": "a location is marked, but no transport is yet present",
    },
    {
        "level": 2,
        "name": "edge",
        "shape": "two points joined",
        "reading": "first transport relation",
    },
    {
        "level": 3,
        "name": "hinge",
        "shape": "open two-edge hinge",
        "reading": "two relations share a pivot but do not yet close",
    },
    {
        "level": 4,
        "name": "closed_face",
        "shape": "closed triangle",
        "reading": "boundary closes as a face",
    },
    {
        "level": 5,
        "name": "filled_cell",
        "shape": "filled triangle",
        "reading": "closed face carries interior completion",
    },
]

REQUIRED_PHRASES = [
    "null-completion header",
    "null -> point -> edge -> hinge -> closed face -> filled cell",
    "not native closure",
    "not Gap A closure",
    "not full role-labeled shared_B universe",
]

FORBIDDEN_PHRASES = [
    "Gap A is closed",
    "native closure achieved",
    "full shared_B universe derived",
    "null-completion is proven natively",
]


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def ladder_name(level):
    for row in COMPLETION_LADDER:
        if row["level"] == level:
            return row["name"]
    raise ValueError("unknown completion level " + str(level))


def expected_headers_from_completion(level, b, r):
    # The local four-state cell occupies the completion window 2..5:
    # edge, hinge, closed face, filled cell.
    #
    # H_free_sum is the completion level read modulo 4.
    # H_relay_max is only active in the branch shell.
    # H_relay_sum is ordinary rank release plus branch relief.
    return {
        "free_sum": level % 4,
        "relay_max": b * (3 * r - 2),
        "relay_sum": -3 + 3 * r + b * (2 - r),
    }


def missing_phrases(text, phrases):
    return [p for p in phrases if p not in text]


def found_phrases(text, phrases):
    return [p for p in phrases if p in text]


def main():
    a051 = load_json(IN_051)

    if not a051.get("theorem_candidate_pass"):
        raise SystemExit("051 theorem_candidate_pass is not true")

    rows_051 = {row["state"]: row for row in a051["state_rows"]}

    state_rows = []
    for state in STATES:
        row = rows_051[state]

        b = int(row["b"])
        r = int(row["r"])
        c_row = int(row["c_row"])

        completion_level = c_row + 2
        completion_name = ladder_name(completion_level)
        predicted = expected_headers_from_completion(completion_level, b, r)

        observed = {
            "free_sum": int(row["observed_free_sum"]),
            "relay_max": int(row["observed_relay_max"]),
            "relay_sum": int(row["observed_relay_sum"]),
        }

        state_rows.append({
            "state": state,
            "b": b,
            "r": r,
            "c_row": c_row,
            "completion_level": completion_level,
            "completion_name": completion_name,
            "anchor_col": int(row["anchor_col"]),
            "selected_candidate_index": int(row["selected_candidate_index"]),
            "observed_headers": observed,
            "predicted_headers": predicted,
            "free_sum_law": "completion_level mod 4",
            "relay_max_law": "branch-only hinge b*(3*r-2)",
            "relay_sum_law": "rank release plus branch relief -3+3*r+b*(2-r)",
            "all_match": observed == predicted,
        })

    predicted_by_target = {
        target: {row["state"]: row["predicted_headers"][target] for row in state_rows}
        for target in TARGETS
    }

    observed_by_target = {
        target: {row["state"]: row["observed_headers"][target] for row in state_rows}
        for target in TARGETS
    }

    local_window = [row["completion_level"] for row in state_rows]

    interpretation_claims = [
        {
            "claim": "The reduced four-state local cell occupies completion levels 2 through 5.",
            "evidence": "c_row values 0,1,2,3 lift to completion levels c_row+2 = 2,3,4,5.",
        },
        {
            "claim": "The free_sum header is the completion level read modulo 4.",
            "evidence": "levels 2,3,4,5 map to free_sum headers 2,3,0,1.",
        },
        {
            "claim": "The relay_max header is the branch hinge correction.",
            "evidence": "ordinary states O0/O1 vanish while branch states B0/B1 produce -2 and 1.",
        },
        {
            "claim": "The relay_sum header records rank release plus branch relief.",
            "evidence": "ordinary rank moves -3 to 0; branch relief shifts B0 and B1 to -1 and 1.",
        },
    ]

    closed_statement = (
        "Artifact 052 interprets the 051 bounded header as a null-completion header. "
        "The ladder is null -> point -> edge -> hinge -> closed face -> filled cell. "
        "The reduced local cell occupies the edge, hinge, closed-face, and filled-cell window, and the three remaining headers are exact readouts of that completion window."
    )

    boundary = (
        "This is an interpretation and consistency artifact, not native closure. "
        "It does not derive the completion ladder from the full native G60/shared_B universe; "
        "it is not full role-labeled shared_B universe derivation, and is not Gap A closure."
    )

    combined = closed_statement + "\n" + boundary
    missing = missing_phrases(combined, REQUIRED_PHRASES)
    forbidden = found_phrases(combined, FORBIDDEN_PHRASES)

    checks = {
        "native_two_bit_header_051_pass": bool(a051.get("theorem_candidate_pass")),
        "state_count_is_4": len(state_rows) == 4,
        "completion_window_is_2_3_4_5": local_window == [2, 3, 4, 5],
        "all_state_rows_match": all(row["all_match"] for row in state_rows),
        "free_sum_is_completion_level_mod4": predicted_by_target["free_sum"] == observed_by_target["free_sum"],
        "relay_max_is_branch_hinge": predicted_by_target["relay_max"] == observed_by_target["relay_max"],
        "relay_sum_is_release_relief": predicted_by_target["relay_sum"] == observed_by_target["relay_sum"],
        "required_phrases_present": len(missing) == 0,
        "forbidden_phrases_absent": len(forbidden) == 0,
    }

    interpretation_candidate_pass = all(checks.values())

    result = {
        "status": "null_completion_header_interpretation_recorded",
        "audit_id": "052",
        "inputs": {
            "native_two_bit_header_mechanism_051": str(IN_051),
        },
        "checks": checks,
        "interpretation_candidate_pass": interpretation_candidate_pass,
        "completion_ladder": COMPLETION_LADDER,
        "local_completion_window": local_window,
        "state_rows": state_rows,
        "observed_by_target": observed_by_target,
        "predicted_by_target": predicted_by_target,
        "interpretation_claims": interpretation_claims,
        "closed_statement": closed_statement,
        "boundary": boundary,
        "missing_required_phrases": missing,
        "forbidden_phrases_found": forbidden,
        "interpretation": (
            "Artifact 051 exactly recovered the bounded header from reduced two-bit local-cell coordinates. "
            "Artifact 052 gives that coordinate result a completion reading: the header records how null relation enters the local-cell completion ladder."
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
            "b",
            "r",
            "c_row",
            "completion_level",
            "completion_name",
            "anchor_col",
            "selected_candidate_index",
            "target",
            "observed",
            "predicted",
            "match",
        ])
        for row in state_rows:
            for target in TARGETS:
                w.writerow([
                    row["state"],
                    row["b"],
                    row["r"],
                    row["c_row"],
                    row["completion_level"],
                    row["completion_name"],
                    row["anchor_col"],
                    row["selected_candidate_index"],
                    target,
                    row["observed_headers"][target],
                    row["predicted_headers"][target],
                    row["observed_headers"][target] == row["predicted_headers"][target],
                ])

    lines = []
    lines.append("# Null-completion header interpretation 052")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- interpretation_candidate_pass: `" + str(interpretation_candidate_pass) + "`")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Closed statement")
    lines.append("")
    lines.append(closed_statement)
    lines.append("")
    lines.append("## Completion ladder")
    lines.append("")
    for row in COMPLETION_LADDER:
        lines.append("- " + str(row["level"]) + ": " + row["name"] + " - " + row["reading"])
    lines.append("")
    lines.append("## Local completion window")
    lines.append("")
    for row in state_rows:
        lines.append(
            "- {state}: c_row={c_row}, completion_level={level} ({name}), headers={headers}, match={match}".format(
                state=row["state"],
                c_row=row["c_row"],
                level=row["completion_level"],
                name=row["completion_name"],
                headers=[
                    row["predicted_headers"]["free_sum"],
                    row["predicted_headers"]["relay_max"],
                    row["predicted_headers"]["relay_sum"],
                ],
                match=row["all_match"],
            )
        )
    lines.append("")
    lines.append("## Interpretation claims")
    lines.append("")
    for row in interpretation_claims:
        lines.append("- " + row["claim"])
        lines.append("  - " + row["evidence"])
    lines.append("")
    lines.append("## Target readings")
    lines.append("")
    lines.append("- free_sum: completion_level mod 4")
    lines.append("- relay_max: branch-only hinge b*(3*r-2)")
    lines.append("- relay_sum: rank release plus branch relief -3+3*r+b*(2-r)")
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
    print("interpretation_candidate_pass", interpretation_candidate_pass)
    for k, v in checks.items():
        print(k, v)
    for row in state_rows:
        print(
            row["state"],
            "c_row", row["c_row"],
            "completion_level", row["completion_level"],
            row["completion_name"],
            "headers",
            [
                row["predicted_headers"]["free_sum"],
                row["predicted_headers"]["relay_max"],
                row["predicted_headers"]["relay_sum"],
            ],
            "match", row["all_match"],
        )


if __name__ == "__main__":
    main()
