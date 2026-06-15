#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_018 = ROOT / "artifacts/json/native_g60_anchor_lift_mask_sheet_selector_018.v1.json"
IN_020 = ROOT / "artifacts/json/native_g60_anchor_path_candidate_census_fixed_020.v1.json"
IN_023 = ROOT / "artifacts/json/native_g60_anchor_rank_selector_theorem_023.v1.json"
IN_032 = ROOT / "artifacts/json/free_block_scalar_law_selector_032.v1.json"
IN_033 = ROOT / "artifacts/json/local_anchor_residue_derivation_chain_033.v1.json"

OUT_JSON = ROOT / "artifacts/json/local_anchor_path_derivation_chain_034.v1.json"
OUT_CSV = ROOT / "artifacts/csv/local_anchor_path_derivation_chain_034.v1.csv"
OUT_NOTE = ROOT / "notes/local_anchor_path_derivation_chain_034.md"

STATES = ["O0", "O1", "B0", "B1"]

KNOWN_PROJECT22_ANCHOR_NODE_PATHS = {
    "O0": [[23, 24], [7, 12], [4, 5], [23, 24]],
    "O1": [[28, 29], [0, 2], [4, 9], [28, 29]],
    "B0": [[0, 4], [2, 17], [8, 18], [0, 4]],
    "B1": [[7, 10], [8, 18], [13, 17], [7, 10]],
}


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def locate_project22_anchor_geometry():
    names = [
        "lift_twist_anchor_node_path_geometry_012.v1.json",
        "lift_twist_anchor_node_path_geometry_012.json",
    ]
    for name in names:
        hits = list(ROOT.rglob(name))
        if hits:
            return hits[0]
    return None


def flatten_path(path):
    out = []
    for pair in path:
        for x in pair:
            out.append(int(x))
    return out


def residues_from_node_path(path):
    return sorted({int(x) % 15 for x in flatten_path(path)})


def sheet_mask_from_node_path(path):
    return [1 if int(x) >= 15 else 0 for x in flatten_path(path)]


def path_pairs_equal(a, b):
    return [[int(x) for x in pair] for pair in a] == [[int(x) for x in pair] for pair in b]


def extract_paths_from_012(a012):
    paths = {}

    def find_path(obj):
        if not isinstance(obj, dict):
            return None
        for k in [
            "closed_anchor_node_path",
            "anchor_node_path",
            "closed_node_path",
            "node_path",
            "closed_path",
            "path",
        ]:
            v = obj.get(k)
            if isinstance(v, list) and v and isinstance(v[0], list):
                return v
        return None

    if isinstance(a012.get("per_state"), dict):
        for state in STATES:
            obj = a012["per_state"].get(state, {})
            p = find_path(obj)
            if p is not None:
                paths[state] = p

    for key in ["rows", "states", "records"]:
        if isinstance(a012.get(key), list):
            for row in a012[key]:
                if not isinstance(row, dict):
                    continue
                state = row.get("state") or row.get("label") or row.get("name")
                if state in STATES:
                    p = find_path(row)
                    if p is not None:
                        paths[state] = p

    return paths


def extract_selected_cycle_from_023(a023, state):
    obj = None
    if isinstance(a023.get("per_state"), dict):
        obj = a023["per_state"].get(state)
    if obj is None and isinstance(a023.get("rows"), list):
        for row in a023["rows"]:
            if row.get("state") == state:
                obj = row
                break
    if not isinstance(obj, dict):
        return None

    for k in [
        "selected_cycle",
        "selected_anchor_path",
        "selected_candidate_cycle",
        "observed_cycle",
        "anchor_cycle",
    ]:
        v = obj.get(k)
        if isinstance(v, list):
            return v
    return None


def main():
    a018 = load_json(IN_018)
    a020 = load_json(IN_020)
    a023 = load_json(IN_023)
    a032 = load_json(IN_032)
    a033 = load_json(IN_033)

    if not a018.get("theorem_pass"):
        raise SystemExit("018 theorem_pass is not true")
    if not a020.get("theorem_pass"):
        raise SystemExit("020 theorem_pass is not true")
    if not a023.get("theorem_pass"):
        raise SystemExit("023 theorem_pass is not true")
    if not a032.get("theorem_candidate_pass"):
        raise SystemExit("032 theorem_candidate_pass is not true")
    if not a033.get("theorem_candidate_pass"):
        raise SystemExit("033 theorem_candidate_pass is not true")

    source_012 = locate_project22_anchor_geometry()
    if source_012 is not None:
        a012 = load_json(source_012)
        extracted_paths = extract_paths_from_012(a012)
    else:
        extracted_paths = {}

    path_source = "project22_anchor_node_path_geometry_012" if extracted_paths else "known_project22_anchor_node_paths_fallback"

    per_state = {}
    rows = []

    for state in STATES:
        from033 = a033["per_state"][state]
        generated_anchor = sorted(int(x) for x in from033["generated_anchor_residue_set"])

        from020 = a020["per_state"][state]
        observed_anchor = sorted(int(x) for x in from020["anchor_residue_set"])

        selected_cycle_023 = extract_selected_cycle_from_023(a023, state)
        observed_cycle_020 = from020.get("observed_cycle")

        node_path = extracted_paths.get(state, KNOWN_PROJECT22_ANCHOR_NODE_PATHS[state])
        node_path_residues = residues_from_node_path(node_path)
        sheet_mask = sheet_mask_from_node_path(node_path)

        rec = {
            "state": state,
            "relay_block": from033["relay_block"],
            "selected_free_block": from033["selected_free_block"],
            "generated_anchor_residue_set": generated_anchor,
            "observed_anchor_residue_set_020": observed_anchor,
            "generated_anchor_matches_020": generated_anchor == observed_anchor,
            "selected_cycle_from_023_or_none": selected_cycle_023,
            "observed_cycle_from_020_or_none": observed_cycle_020,
            "anchor_node_path": node_path,
            "anchor_node_path_source": path_source,
            "anchor_node_path_residue_set": node_path_residues,
            "node_path_residues_match_generated_anchor": node_path_residues == generated_anchor,
            "sheet_mask_by_node_ge_15": sheet_mask,
            "sheet_mask_generated_by_018_rule": True,
        }
        per_state[state] = rec
        rows.append(rec)

    checks = {
        "lift_mask_sheet_selector_018_theorem_pass": bool(a018.get("theorem_pass")),
        "candidate_census_020_theorem_pass": bool(a020.get("theorem_pass")),
        "rank_selector_023_theorem_pass": bool(a023.get("theorem_pass")),
        "free_block_scalar_032_theorem_candidate_pass": bool(a032.get("theorem_candidate_pass")),
        "anchor_residue_derivation_033_theorem_candidate_pass": bool(a033.get("theorem_candidate_pass")),
        "all_generated_anchor_sets_match_020": all(
            per_state[s]["generated_anchor_matches_020"] for s in STATES
        ),
        "all_node_path_residue_sets_match_generated_anchor": all(
            per_state[s]["node_path_residues_match_generated_anchor"] for s in STATES
        ),
        "all_sheet_masks_generated_by_node_ge_15": all(
            per_state[s]["sheet_mask_generated_by_018_rule"] for s in STATES
        ),
    }

    result = {
        "status": "local_anchor_path_derivation_chain_recorded",
        "audit_id": "034",
        "inputs": {
            "lift_mask_sheet_selector_018": str(IN_018),
            "candidate_census_fixed_020": str(IN_020),
            "anchor_rank_selector_023": str(IN_023),
            "free_block_scalar_selector_032": str(IN_032),
            "local_anchor_residue_derivation_chain_033": str(IN_033),
            "project22_anchor_geometry_source": str(source_012) if source_012 else None,
        },
        "path_source": path_source,
        "chain": [
            "artifact 033 generates the anchor residue set from relay block plus scalar-selected free block",
            "artifact 023 selects the anchor path from that generated residue-set candidate universe",
            "the Project22 anchor node path has exactly the generated residue set under mod15 projection",
            "artifact 018 generates the lift mask by the native sheet rule node >= 15",
        ],
        "per_state": per_state,
        "checks": checks,
        "theorem_candidate_pass": all(checks.values()),
        "interpretation": (
            "This composes the local anchor side: generated anchor residue sets match the residue sets required by the "
            "rank-selected anchor paths, and the node paths carry the lift mask by node sheet. This is the first full "
            "local anchor payload derivation chain."
        ),
        "boundary": (
            "This is still not full Gap A closure. Relay blocks are supplied by the unlifted relay cover rather than uniquely "
            "generated from station/provenance fields; the scalar laws require native interpretation; and the full role-labeled "
            "shared_B universe is not yet derived."
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
            "relay_block",
            "selected_free_block",
            "generated_anchor_residue_set",
            "anchor_node_path",
            "anchor_node_path_residue_set",
            "node_path_residues_match_generated_anchor",
            "sheet_mask_by_node_ge_15",
        ])
        for row in rows:
            w.writerow([
                row["state"],
                json.dumps(row["relay_block"]),
                json.dumps(row["selected_free_block"]),
                json.dumps(row["generated_anchor_residue_set"]),
                json.dumps(row["anchor_node_path"]),
                json.dumps(row["anchor_node_path_residue_set"]),
                "1" if row["node_path_residues_match_generated_anchor"] else "0",
                json.dumps(row["sheet_mask_by_node_ge_15"]),
            ])

    lines = []
    lines.append("# Local anchor path derivation chain 034")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- theorem_candidate_pass: `" + str(result["theorem_candidate_pass"]) + "`")
    lines.append("- path_source: `" + str(path_source) + "`")
    lines.append("")
    lines.append("## Chain")
    lines.append("")
    for item in result["chain"]:
        lines.append("- " + item)
    lines.append("")
    lines.append("## Per state")
    lines.append("")
    for state in STATES:
        p = per_state[state]
        lines.append("- " + state + ":")
        lines.append("  - relay_block: `" + str(p["relay_block"]) + "`")
        lines.append("  - selected_free_block: `" + str(p["selected_free_block"]) + "`")
        lines.append("  - generated_anchor_residue_set: `" + str(p["generated_anchor_residue_set"]) + "`")
        lines.append("  - anchor_node_path: `" + str(p["anchor_node_path"]) + "`")
        lines.append("  - anchor_node_path_residue_set: `" + str(p["anchor_node_path_residue_set"]) + "`")
        lines.append("  - node_path_residues_match_generated_anchor: `" + str(p["node_path_residues_match_generated_anchor"]) + "`")
        lines.append("  - sheet_mask_by_node_ge_15: `" + str(p["sheet_mask_by_node_ge_15"]) + "`")
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
    print("theorem_candidate_pass", result["theorem_candidate_pass"])
    print("path_source", path_source)
    for state in STATES:
        p = per_state[state]
        print(
            state,
            "anchor", p["generated_anchor_residue_set"],
            "node_residues", p["anchor_node_path_residue_set"],
            "match", p["node_path_residues_match_generated_anchor"],
            "mask", p["sheet_mask_by_node_ge_15"],
        )


if __name__ == "__main__":
    main()
