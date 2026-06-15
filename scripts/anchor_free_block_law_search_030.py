#!/usr/bin/env python3
import json
import itertools
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_011 = ROOT / "artifacts/json/native_g60_unlifted_anchor_relay_cover_011.v1.json"
IN_020 = ROOT / "artifacts/json/native_g60_anchor_path_candidate_census_fixed_020.v1.json"
IN_029 = ROOT / "artifacts/json/o0_anchor_residue_set_selector_assault_029.v1.json"

OUT_JSON = ROOT / "artifacts/json/anchor_free_block_law_search_030.v1.json"
OUT_NOTE = ROOT / "notes/anchor_free_block_law_search_030.md"

STATES = ["O0", "O1", "B0", "B1"]

C_VALUES = {
    "O0": {2, 11, 14},
    "O1": {1, 10, 13},
    "B0": {0, 2, 5},
    "B1": {2, 4, 5},
}


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def bits(state):
    return {
        "O0": (0, 0),
        "O1": (0, 1),
        "B0": (1, 0),
        "B1": (1, 1),
    }[state]


def sig(xs):
    return ",".join(str(x) for x in sorted(xs))


def modset(xs):
    return set(int(x) % 15 for x in xs)


def add_const(xs, k):
    return modset((x + k) for x in xs)


def mul_add(xs, a, k):
    return modset((a*x + k) for x in xs)


def union(*sets):
    out = set()
    for s in sets:
        out.update(s)
    return out


def relay_hits_by_state(a011):
    out = {s: set() for s in STATES}
    unique = {s: set() for s in STATES}
    for row in a011["rows"]:
        state = row["state"]
        if state not in out:
            continue
        hits = sorted({int(h["hit"]) for h in row.get("unlifted_hits", [])})
        out[state].update(hits)
        if len(hits) == 1:
            unique[state].update(hits)
    return out, unique


def main():
    a011 = load_json(IN_011)
    a020 = load_json(IN_020)
    a029 = load_json(IN_029)

    if not a011.get("theorem_pass"):
        raise SystemExit("011 theorem_pass is not true")
    if not a020.get("theorem_pass"):
        raise SystemExit("020 theorem_pass is not true")
    if not a029.get("all_checks_pass"):
        raise SystemExit("029 all_checks_pass is not true")

    relay_hits, unique_hits = relay_hits_by_state(a011)

    rows = []
    for state in STATES:
        observed_set = set(int(x) for x in a020["per_state"][state]["anchor_residue_set"])
        relay = set(relay_hits[state])
        free = observed_set.difference(relay)
        cvals = set(C_VALUES[state])
        b, r = bits(state)

        rows.append({
            "state": state,
            "shell_bit": b,
            "rank_bit": r,
            "observed_set": sorted(observed_set),
            "relay_block": sorted(relay),
            "unique_relay_hits": sorted(unique_hits[state]),
            "free_block": sorted(free),
            "free_size": len(free),
            "c_values": sorted(cvals),
            "c_overlap_free": sorted(free.intersection(cvals)),
            "free_signature": sig(free),
            "relay_signature": sig(relay),
            "c_signature": sig(cvals),
        })

    # Candidate law families. We test small interpretable transforms.
    law_hits = []

    def test_law(name, fn):
        preds = {}
        ok = True
        for row in rows:
            pred = fn(row)
            preds[row["state"]] = sorted(pred)
            if set(pred) != set(row["free_block"]):
                ok = False
        if ok:
            law_hits.append({
                "name": name,
                "predictions": preds,
            })

    for k in range(15):
        test_law("free = relay + %d" % k, lambda row, k=k: add_const(row["relay_block"], k))

    for k in range(15):
        test_law("free = C + %d" % k, lambda row, k=k: add_const(row["c_values"], k))

    for a in range(15):
        for k in range(15):
            test_law(
                "free = %d*relay + %d" % (a, k),
                lambda row, a=a, k=k: mul_add(row["relay_block"], a, k),
            )
            test_law(
                "free = %d*C + %d" % (a, k),
                lambda row, a=a, k=k: mul_add(row["c_values"], a, k),
            )

    # State-dependent affine constants from bits:
    # free = relay + (p0 + pb*b + pr*r + pbr*b*r)
    for coeffs in itertools.product(range(15), repeat=4):
        p0, pb, pr, pbr = coeffs

        def k_of(row, p0=p0, pb=pb, pr=pr, pbr=pbr):
            b = row["shell_bit"]
            r = row["rank_bit"]
            return (p0 + pb*b + pr*r + pbr*b*r) % 15

        test_law(
            "free = relay + k(b,r), k=%s" % (str(coeffs),),
            lambda row, k_of=k_of: add_const(row["relay_block"], k_of(row)),
        )

    # Keep report manageable.
    law_hits = law_hits[:50]

    # Search for per-state offset relation between relay and free.
    per_state_offset_summaries = {}
    for row in rows:
        relay = set(row["relay_block"])
        free = set(row["free_block"])
        offsets = []
        for k in range(15):
            if add_const(relay, k) == free:
                offsets.append(k)
        c_offsets = []
        for k in range(15):
            if add_const(row["c_values"], k) == free:
                c_offsets.append(k)
        per_state_offset_summaries[row["state"]] = {
            "relay_to_free_offsets": offsets,
            "c_to_free_offsets": c_offsets,
        }

    checks = {
        "unlifted_relay_cover_011_theorem_pass": bool(a011.get("theorem_pass")),
        "candidate_census_020_theorem_pass": bool(a020.get("theorem_pass")),
        "o0_selector_029_checks_pass": bool(a029.get("all_checks_pass")),
        "all_free_blocks_nonempty": all(row["free_size"] > 0 for row in rows),
        "o0_free_block_is_8_9_12": [r for r in rows if r["state"] == "O0"][0]["free_block"] == [8, 9, 12],
    }

    result = {
        "status": "anchor_free_block_law_search_recorded",
        "audit_id": "030",
        "inputs": {
            "unlifted_relay_cover_011": str(IN_011),
            "candidate_census_fixed_020": str(IN_020),
            "o0_selector_assault_029": str(IN_029),
        },
        "rows": rows,
        "per_state_offset_summaries": per_state_offset_summaries,
        "exact_law_hits_first_50": law_hits,
        "exact_law_hit_count_reported": len(law_hits),
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": (
            "This searches for a common law generating the free block from relay hits or C values. "
            "If no common transform appears, the free block likely requires station/provenance context or a richer relational law."
        ),
        "boundary": (
            "This is a law search over observed free blocks. It does not prove native provenance, does not select relay mediators, "
            "does not derive the full shared_B universe, and does not close Gap A."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = []
    lines.append("# Anchor free-block law search 030")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- all_checks_pass: `" + str(result["all_checks_pass"]) + "`")
    lines.append("- exact_law_hit_count_reported: `" + str(result["exact_law_hit_count_reported"]) + "`")
    lines.append("")
    lines.append("## Blocks")
    lines.append("")
    for row in rows:
        lines.append("- " + row["state"] + ":")
        lines.append("  - bits: `(" + str(row["shell_bit"]) + ", " + str(row["rank_bit"]) + ")`")
        lines.append("  - observed_set: `" + str(row["observed_set"]) + "`")
        lines.append("  - relay_block: `" + str(row["relay_block"]) + "`")
        lines.append("  - free_block: `" + str(row["free_block"]) + "`")
        lines.append("  - c_values: `" + str(row["c_values"]) + "`")
        lines.append("  - c_overlap_free: `" + str(row["c_overlap_free"]) + "`")
        lines.append("  - offset_summary: `" + str(per_state_offset_summaries[row["state"]]) + "`")
    lines.append("")
    lines.append("## Exact law hits first 50")
    lines.append("")
    if law_hits:
        for hit in law_hits:
            lines.append("- `" + hit["name"] + "` -> `" + str(hit["predictions"]) + "`")
    else:
        lines.append("- none")
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
    print("wrote", OUT_NOTE)
    print("status", result["status"])
    print("all_checks_pass", result["all_checks_pass"])
    print("exact_law_hit_count_reported", len(law_hits))
    for row in rows:
        print(row["state"], "relay", row["relay_block"], "free", row["free_block"], "c", row["c_values"])
    print("first_law_hit", law_hits[0] if law_hits else None)


if __name__ == "__main__":
    main()
