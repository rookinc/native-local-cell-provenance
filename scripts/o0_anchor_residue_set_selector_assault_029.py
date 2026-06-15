#!/usr/bin/env python3
import csv
import json
import itertools
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_011 = ROOT / "artifacts/json/native_g60_unlifted_anchor_relay_cover_011.v1.json"
IN_020 = ROOT / "artifacts/json/native_g60_anchor_path_candidate_census_fixed_020.v1.json"
IN_028 = ROOT / "artifacts/json/native_g60_anchor_residue_set_selector_audit_028.v1.json"
G60_EDGES = ROOT / "source/project18_payload/g60_local_edges.csv"

OUT_JSON = ROOT / "artifacts/json/o0_anchor_residue_set_selector_assault_029.v1.json"
OUT_CSV = ROOT / "artifacts/csv/o0_anchor_residue_set_selector_assault_029.v1.csv"
OUT_NOTE = ROOT / "notes/o0_anchor_residue_set_selector_assault_029.md"

STATE = "O0"
RESIDUES = list(range(15))
C_VALUES = {2, 11, 14}


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_edges(path):
    edges = []
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            edges.append((int(row["local_u"]), int(row["local_v"])))
    return edges


def support_key(a, b):
    return tuple(sorted((int(a), int(b))))


def circular_distance(a, b, n=15):
    d = abs(int(a) - int(b)) % n
    return min(d, n - d)


def gap_signature(vals):
    xs = sorted(vals)
    gaps = []
    for i, x in enumerate(xs):
        y = xs[(i + 1) % len(xs)]
        gaps.append((y - x) % 15)
    return ",".join(str(g) for g in sorted(gaps))


def ordered_gap_signature(vals):
    xs = sorted(vals)
    gaps = []
    for i, x in enumerate(xs):
        y = xs[(i + 1) % len(xs)]
        gaps.append((y - x) % 15)
    return ",".join(str(g) for g in gaps)


def sig(vals):
    return ",".join(str(x) for x in sorted(vals))


def relay_obligations(a011):
    obs = []
    relay_hits = set()
    for row in a011["rows"]:
        if row["state"] != STATE:
            continue
        hits = sorted({int(h["hit"]) for h in row.get("unlifted_hits", [])})
        if hits:
            obs.append({
                "step": int(row.get("step", -1)),
                "allowed_hits": hits,
            })
            relay_hits.update(hits)
    return obs, relay_hits


def satisfies_obligations(s, obs):
    s = set(s)
    return all(s.intersection(ob["allowed_hits"]) for ob in obs)


def support_weight(a, b, residue_support):
    return len(residue_support.get(support_key(a, b), []))


def set_cut_weight(s, t, residue_support):
    total = 0
    supported = 0
    for a in s:
        for b in t:
            w = support_weight(a, b, residue_support)
            total += w
            if w:
                supported += 1
    return supported, total


def internal_weight(s, residue_support):
    total = 0
    supported = 0
    missing = 0
    for a, b in itertools.combinations(sorted(s), 2):
        w = support_weight(a, b, residue_support)
        total += w
        if w:
            supported += 1
        else:
            missing += 1
    return supported, total, missing


def c_distance_profile(s):
    dists = []
    nearest = []
    for x in sorted(s):
        ds = sorted(circular_distance(x, c) for c in C_VALUES)
        nearest.append(ds[0])
        dists.extend(ds)
    return {
        "nearest_c_distance_signature": ",".join(str(x) for x in sorted(nearest)),
        "sum_nearest_c_distance": sum(nearest),
        "min_nearest_c_distance": min(nearest),
        "max_nearest_c_distance": max(nearest),
        "all_c_distance_signature": ",".join(str(x) for x in sorted(dists)),
    }


def main():
    a011 = load_json(IN_011)
    a020 = load_json(IN_020)
    a028 = load_json(IN_028)

    if not a011.get("theorem_pass"):
        raise SystemExit("011 theorem_pass is not true")
    if not a020.get("theorem_pass"):
        raise SystemExit("020 theorem_pass is not true")
    if a028.get("status") != "native_g60_anchor_residue_set_selector_audit_recorded":
        raise SystemExit("028 status unexpected")

    edges = load_edges(G60_EDGES)
    residue_support = {}
    for u, v in edges:
        residue_support.setdefault(support_key(u % 15, v % 15), []).append((u, v))

    observed = set(int(x) for x in a020["per_state"][STATE]["anchor_residue_set"])
    obs, relay_hits = relay_obligations(a011)

    rows = []

    for cand in itertools.combinations(RESIDUES, 6):
        s = set(cand)
        if not satisfies_obligations(s, obs):
            continue

        relay_block = s.intersection(relay_hits)
        free_block = s.difference(relay_hits)
        comp = set(RESIDUES).difference(s)
        c_overlap = s.intersection(C_VALUES)

        internal_supported, internal_total, internal_missing = internal_weight(s, residue_support)
        boundary_supported, boundary_total = set_cut_weight(s, comp, residue_support)
        c_cut_supported, c_cut_weight = set_cut_weight(s, C_VALUES, residue_support)
        free_to_c_supported, free_to_c_weight = set_cut_weight(free_block, C_VALUES, residue_support)
        relay_to_free_supported, relay_to_free_weight = set_cut_weight(relay_block, free_block, residue_support)

        cdist = c_distance_profile(s)

        features = {
            "sum_residues": sum(s),
            "sum_mod15": sum(s) % 15,
            "gap_signature": gap_signature(s),
            "ordered_gap_signature": ordered_gap_signature(s),
            "relay_block_signature": sig(relay_block),
            "relay_block_count": len(relay_block),
            "free_block_signature": sig(free_block),
            "free_block_count": len(free_block),
            "c_overlap_signature": sig(c_overlap),
            "c_overlap_count": len(c_overlap),
            "no_c_overlap": len(c_overlap) == 0,
            "internal_supported_pair_count": internal_supported,
            "internal_support_weight": internal_total,
            "internal_missing_pair_count": internal_missing,
            "boundary_supported_pair_count": boundary_supported,
            "boundary_support_weight": boundary_total,
            "c_cut_supported_pair_count": c_cut_supported,
            "c_cut_weight": c_cut_weight,
            "free_to_c_supported_pair_count": free_to_c_supported,
            "free_to_c_weight": free_to_c_weight,
            "relay_to_free_supported_pair_count": relay_to_free_supported,
            "relay_to_free_weight": relay_to_free_weight,
        }
        features.update(cdist)

        rows.append({
            "candidate_index": len(rows),
            "residue_set": sorted(s),
            "matches_observed": s == observed,
            "features": features,
        })

    observed_rows = [r for r in rows if r["matches_observed"]]
    observed_found = len(observed_rows) == 1
    observed_row = observed_rows[0] if observed_found else None

    feature_names = sorted(rows[0]["features"].keys())

    exact_selectors = []
    if observed_found:
        for width in (1, 2, 3, 4):
            for combo in itertools.combinations(feature_names, width):
                obs_val = tuple(observed_row["features"][name] for name in combo)
                matches = [
                    r for r in rows
                    if tuple(r["features"][name] for name in combo) == obs_val
                ]
                if len(matches) == 1 and matches[0]["matches_observed"]:
                    exact_selectors.append({
                        "features": list(combo),
                        "observed_values": list(obs_val),
                        "width": width,
                    })
            if exact_selectors:
                break

    checks = {
        "unlifted_relay_cover_011_theorem_pass": bool(a011.get("theorem_pass")),
        "candidate_census_020_theorem_pass": bool(a020.get("theorem_pass")),
        "residue_selector_audit_028_recorded": a028.get("status") == "native_g60_anchor_residue_set_selector_audit_recorded",
        "g60_edge_count_is_120": len(edges) == 120,
        "observed_o0_residue_set_found": observed_found,
        "exact_o0_selector_found": len(exact_selectors) > 0,
    }

    result = {
        "status": "o0_anchor_residue_set_selector_assault_recorded",
        "audit_id": "029",
        "state": STATE,
        "inputs": {
            "unlifted_relay_cover_011": str(IN_011),
            "candidate_census_fixed_020": str(IN_020),
            "residue_set_selector_audit_028": str(IN_028),
            "g60_edges": str(G60_EDGES),
        },
        "observed_residue_set": sorted(observed),
        "relay_hits": sorted(relay_hits),
        "c_values": sorted(C_VALUES),
        "candidate_count": len(rows),
        "observed_found": observed_found,
        "observed_candidate_index": observed_row["candidate_index"] if observed_found else None,
        "observed_features": observed_row["features"] if observed_found else None,
        "exact_selectors_first_50": exact_selectors[:50],
        "exact_selector_count": len(exact_selectors),
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": (
            "Artifact 028 showed that simple scalar residue-set features did not select O0. This assault adds relational "
            "features: relay/free decomposition, C-distance profiles, gap signatures, and quotient support cuts. If an exact "
            "selector appears, O0 may be reachable without station fields. If no exact selector appears, the next layer is "
            "almost certainly station/provenance structure."
        ),
        "boundary": (
            "This is an O0-only selector assault. Any exact selector found here is a candidate direction, not a native theorem "
            "until independently justified and generalized. This does not close Gap A."
        ),
        "rows": rows,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "candidate_index",
            "matches_observed",
            "residue_set",
            "sum_residues",
            "sum_mod15",
            "gap_signature",
            "relay_block_signature",
            "free_block_signature",
            "c_overlap_signature",
            "no_c_overlap",
            "nearest_c_distance_signature",
            "sum_nearest_c_distance",
            "internal_support_weight",
            "boundary_support_weight",
            "c_cut_weight",
            "free_to_c_weight",
            "relay_to_free_weight",
        ])
        for r in rows:
            f = r["features"]
            w.writerow([
                r["candidate_index"],
                "1" if r["matches_observed"] else "0",
                json.dumps(r["residue_set"]),
                f["sum_residues"],
                f["sum_mod15"],
                f["gap_signature"],
                f["relay_block_signature"],
                f["free_block_signature"],
                f["c_overlap_signature"],
                "1" if f["no_c_overlap"] else "0",
                f["nearest_c_distance_signature"],
                f["sum_nearest_c_distance"],
                f["internal_support_weight"],
                f["boundary_support_weight"],
                f["c_cut_weight"],
                f["free_to_c_weight"],
                f["relay_to_free_weight"],
            ])

    lines = []
    lines.append("# O0 anchor residue-set selector assault 029")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- all_checks_pass: `" + str(result["all_checks_pass"]) + "`")
    lines.append("- candidate_count: `" + str(len(rows)) + "`")
    lines.append("- observed_found: `" + str(observed_found) + "`")
    lines.append("- observed_candidate_index: `" + str(result["observed_candidate_index"]) + "`")
    lines.append("- exact_selector_count: `" + str(len(exact_selectors)) + "`")
    lines.append("")
    lines.append("## Observed set")
    lines.append("")
    lines.append("- observed_residue_set: `" + str(sorted(observed)) + "`")
    lines.append("- relay_hits: `" + str(sorted(relay_hits)) + "`")
    lines.append("- c_values: `" + str(sorted(C_VALUES)) + "`")
    if observed_found:
        lines.append("- observed_features: `" + str(observed_row["features"]) + "`")
    lines.append("")
    lines.append("## Exact selectors first 50")
    lines.append("")
    if exact_selectors:
        for item in exact_selectors[:50]:
            lines.append("- `" + str(item) + "`")
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
    print("wrote", OUT_CSV)
    print("wrote", OUT_NOTE)
    print("status", result["status"])
    print("all_checks_pass", result["all_checks_pass"])
    print("candidate_count", len(rows))
    print("observed_found", observed_found)
    print("exact_selector_count", len(exact_selectors))
    print("first_exact_selector", exact_selectors[0] if exact_selectors else None)


if __name__ == "__main__":
    main()
