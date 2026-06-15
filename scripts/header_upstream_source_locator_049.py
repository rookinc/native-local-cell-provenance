#!/usr/bin/env python3
import csv
import json
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[1]

IN_045 = ROOT / "artifacts/json/shared_residual_correction_grammar_045.v1.json"
IN_047 = ROOT / "artifacts/json/header_source_audit_047.v1.json"
IN_048 = ROOT / "artifacts/json/local_scalar_provenance_frontier_048.v1.json"

SOURCE_ROOT = ROOT / "source/upstream_station_provenance"

OUT_JSON = ROOT / "artifacts/json/header_upstream_source_locator_049.v1.json"
OUT_CSV = ROOT / "artifacts/csv/header_upstream_source_locator_049.v1.csv"
OUT_NOTE = ROOT / "notes/header_upstream_source_locator_049.md"

STATES = ["O0", "O1", "B0", "B1"]

STATE_C_PATHS = {
    "O0": [11, 2, 14, 11],
    "O1": [13, 1, 10, 13],
    "B0": [2, 5, 0, 2],
    "B1": [4, 5, 2, 4],
}

C_TRANSITION_TO_STATE = {}
for state, path in STATE_C_PATHS.items():
    for i in range(len(path) - 1):
        C_TRANSITION_TO_STATE[(path[i], path[i + 1])] = state

STATE_KEYS = [
    "state",
    "state_key",
    "state_label",
    "local_state",
    "anchor_state",
    "cell_state",
    "name",
    "key",
]

COEFFS = list(range(-8, 9))
OFFSETS = list(range(-30, 31))
TOP_N = 30
MAX_CANDIDATES = 100000


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def as_int(v):
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, float) and v.is_integer():
        return int(v)
    if isinstance(v, str) and v.strip().lstrip("-").isdigit():
        return int(v.strip())
    return None


def short_path(path):
    s = "/".join(str(x) for x in path)
    if len(s) > 220:
        return s[:100] + ".../" + s[-100:]
    return s


def is_num(v):
    return as_int(v) is not None


def state_from_row(row):
    if not isinstance(row, dict):
        return None

    for k in STATE_KEYS:
        v = row.get(k)
        if isinstance(v, str) and v in STATES:
            return v

    fc = as_int(row.get("from_C"))
    tc = as_int(row.get("to_C"))
    if fc is not None and tc is not None:
        return C_TRANSITION_TO_STATE.get((fc, tc))

    return None


def numeric_fields(row):
    out = {}
    if not isinstance(row, dict):
        return out

    for k, v in row.items():
        iv = as_int(v)
        if iv is not None:
            out[k] = iv

    pairs = [
        ("A_delta", "from_A", "to_A", 15),
        ("B_delta", "from_B", "to_B", 15),
        ("C_delta", "from_C", "to_C", 15),
        ("slot_delta", "from_slot", "to_slot", 15),
        ("fiber_delta_mod15", "from_fiber", "to_fiber", 15),
        ("fiber_delta_mod60", "from_fiber", "to_fiber", 60),
    ]
    for name, a, b, mod in pairs:
        av = as_int(row.get(a))
        bv = as_int(row.get(b))
        if av is not None and bv is not None:
            out[name] = (bv - av) % mod

    return out


def stats(vals):
    vals = [as_int(v) for v in vals]
    vals = [v for v in vals if v is not None]
    if not vals:
        return {}

    uniq = sorted(set(vals))
    return {
        "count": len(vals),
        "sum": sum(vals),
        "min": min(vals),
        "max": max(vals),
        "range": max(vals) - min(vals),
        "unique_count": len(uniq),
        "unique_sum": sum(uniq),
        "unique_min": min(uniq),
        "unique_max": max(uniq),
        "unique_range": max(uniq) - min(uniq),
    }


def add_candidate(candidates, source_file, source_path, kind, feature, values):
    if len(candidates) >= MAX_CANDIDATES:
        return

    clean = {}
    for state in STATES:
        if state not in values:
            return
        iv = as_int(values[state])
        if iv is None:
            return
        clean[state] = iv

    key = (
        str(source_file),
        source_path,
        kind,
        feature,
        tuple(clean[s] for s in STATES),
    )

    if key in candidates:
        return

    candidates[key] = {
        "source_file": str(source_file),
        "source_path": source_path,
        "kind": kind,
        "feature": feature,
        "family": kind + "::" + feature,
        "values": clean,
    }


def add_stats_candidates(candidates, source_file, source_path, kind, base_feature, by_state_vals):
    per_stat = defaultdict(dict)

    for state, vals in by_state_vals.items():
        st = stats(vals)
        for stat_name, stat_val in st.items():
            per_stat[stat_name][state] = stat_val

    for stat_name, values in per_stat.items():
        add_candidate(
            candidates,
            source_file,
            source_path,
            kind,
            base_feature + "__" + stat_name,
            values,
        )


def collect_from_state_map(candidates, source_file, path, obj):
    if not isinstance(obj, dict):
        return

    if not all(k in obj for k in STATES):
        return

    values = {s: obj[s] for s in STATES}

    # Direct numeric state map.
    if all(is_num(values[s]) for s in STATES):
        add_candidate(
            candidates,
            source_file,
            short_path(path),
            "state_map_direct",
            "value",
            {s: as_int(values[s]) for s in STATES},
        )
        return

    # State map to lists of numbers.
    if all(isinstance(values[s], list) for s in STATES):
        add_stats_candidates(
            candidates,
            source_file,
            short_path(path),
            "state_map_list",
            "list",
            values,
        )
        return

    # State map to dicts.
    if all(isinstance(values[s], dict) for s in STATES):
        common = set.intersection(*(set(values[s].keys()) for s in STATES))
        for k in sorted(common):
            kv = {s: values[s].get(k) for s in STATES}
            if all(is_num(kv[s]) for s in STATES):
                add_candidate(
                    candidates,
                    source_file,
                    short_path(path),
                    "state_map_dict",
                    str(k),
                    {s: as_int(kv[s]) for s in STATES},
                )
            elif all(isinstance(kv[s], list) for s in STATES):
                add_stats_candidates(
                    candidates,
                    source_file,
                    short_path(path + [k]),
                    "state_map_dict_list",
                    str(k),
                    kv,
                )


def collect_from_row_list(candidates, source_file, path, xs):
    if not isinstance(xs, list):
        return
    if not xs or not all(isinstance(x, dict) for x in xs):
        return

    groups = defaultdict(list)
    for row in xs:
        state = state_from_row(row)
        if state in STATES:
            groups[state].append(row)

    if not all(s in groups and groups[s] for s in STATES):
        return

    add_candidate(
        candidates,
        source_file,
        short_path(path),
        "row_group",
        "row_count",
        {s: len(groups[s]) for s in STATES},
    )

    all_fields = set()
    for rows in groups.values():
        for row in rows:
            all_fields.update(numeric_fields(row).keys())

    for field in sorted(all_fields):
        by_state_vals = {}
        for state in STATES:
            vals = []
            for row in groups[state]:
                nf = numeric_fields(row)
                if field in nf:
                    vals.append(nf[field])
            by_state_vals[state] = vals

        add_stats_candidates(
            candidates,
            source_file,
            short_path(path),
            "row_group_field",
            field,
            by_state_vals,
        )


def walk(candidates, source_file, path, obj):
    if len(candidates) >= MAX_CANDIDATES:
        return

    if isinstance(obj, dict):
        collect_from_state_map(candidates, source_file, path, obj)
        for k, v in obj.items():
            walk(candidates, source_file, path + [k], v)
    elif isinstance(obj, list):
        collect_from_row_list(candidates, source_file, path, obj)
        for i, v in enumerate(obj):
            if i < 300:
                walk(candidates, source_file, path + [i], v)


def exact_and_near(candidates, target_values):
    exact = []
    near = []

    for cand in candidates.values():
        x = cand["values"]
        y = target_values

        # Direct exact.
        direct_err = sum(abs(x[s] - y[s]) for s in STATES)
        if direct_err == 0:
            item = dict(cand)
            item.update({
                "match_kind": "direct",
                "a": 1,
                "c": 0,
                "l1_error": 0,
                "predicted": x,
                "complexity": len(cand["feature"]) / 1000.0,
            })
            exact.append(item)
        else:
            item = dict(cand)
            item.update({
                "match_kind": "direct",
                "a": 1,
                "c": 0,
                "l1_error": direct_err,
                "predicted": x,
                "complexity": direct_err * 1000 + len(cand["feature"]) / 1000.0,
            })
            near.append(item)

        # Affine exact or near: y = a*x + c.
        for a in COEFFS:
            if a == 0:
                continue
            needed = [y[s] - a * x[s] for s in STATES]
            counts = Counter(needed)
            c, _ = counts.most_common(1)[0]
            if c not in OFFSETS:
                continue
            pred = {s: a * x[s] + c for s in STATES}
            err = sum(abs(pred[s] - y[s]) for s in STATES)

            item = dict(cand)
            item.update({
                "match_kind": "affine",
                "a": a,
                "c": c,
                "l1_error": err,
                "predicted": pred,
                "complexity": err * 1000 + abs(a) + abs(c) + len(cand["feature"]) / 1000.0,
            })
            if err == 0:
                exact.append(item)
            else:
                near.append(item)

    exact.sort(key=lambda z: (z["complexity"], z["source_file"], z["source_path"], z["feature"]))
    near.sort(key=lambda z: (z["l1_error"], z["complexity"], z["source_file"], z["source_path"], z["feature"]))

    return exact[:TOP_N], near[:TOP_N]


def small_header_targets(a045):
    out = {}
    for row in a045["rows"]:
        if row["classification"] == "small_header_residual_remaining":
            out[row["target"]] = {
                "base_feature": row["base_feature"],
                "residual": {s: int(row["residual"][s]) for s in STATES},
                "residual_bit_law": row["residual_bit_law"],
            }
    return out


def family_counts(items):
    c = Counter()
    for item in items:
        c[item["family"]] += 1
    return dict(c.most_common())


def main():
    a045 = load_json(IN_045)
    a047 = load_json(IN_047)
    a048 = load_json(IN_048)

    if not a045["checks"].get("shared_header_grammar_pass"):
        raise SystemExit("045 shared_header_grammar_pass is not true")
    if not a047.get("audit_pass"):
        raise SystemExit("047 audit_pass is not true")
    if not a048.get("frontier_pass"):
        raise SystemExit("048 frontier_pass is not true")

    if not SOURCE_ROOT.exists():
        raise SystemExit("missing source root " + str(SOURCE_ROOT))

    candidates = {}
    json_files = sorted(SOURCE_ROOT.rglob("*.json"))

    for idx, path in enumerate(json_files, start=1):
        print("scanning", idx, "of", len(json_files), path)
        try:
            data = load_json(path)
        except Exception as e:
            print("skip unreadable", path, e)
            continue
        rel = path.relative_to(ROOT)
        walk(candidates, rel, [], data)

    headers = small_header_targets(a045)
    per_header = {}
    csv_rows = []

    for target, target_info in sorted(headers.items()):
        exact, near = exact_and_near(candidates, target_info["residual"])
        per_header[target] = {
            "base_feature": target_info["base_feature"],
            "residual": target_info["residual"],
            "residual_bit_law": target_info["residual_bit_law"],
            "exact_upstream_source_count": len(exact),
            "nearest_upstream_source_count": len(near),
            "exact_upstream_sources_first": exact,
            "nearest_upstream_sources_first": near,
            "exact_family_counts": family_counts(exact),
            "near_family_counts": family_counts(near[:10]),
            "upstream_source_found": len(exact) > 0,
        }

        for kind, items in [("exact", exact), ("nearest", near[:20])]:
            for item in items:
                csv_rows.append([
                    target,
                    kind,
                    item["match_kind"],
                    item["source_file"],
                    item["source_path"],
                    item["kind"],
                    item["feature"],
                    item["a"],
                    item["c"],
                    item["l1_error"],
                    json.dumps(item["values"], sort_keys=True),
                    json.dumps(item["predicted"], sort_keys=True),
                ])

    exact_family_sets = []
    near_family_sets = []
    for target in sorted(per_header):
        exact_family_sets.append(set(per_header[target]["exact_family_counts"].keys()))
        near_family_sets.append(set(per_header[target]["near_family_counts"].keys()))

    shared_exact_families = sorted(set.intersection(*exact_family_sets)) if exact_family_sets else []
    shared_near_families = sorted(set.intersection(*near_family_sets)) if near_family_sets else []

    upstream_source_found_for_all = all(per_header[t]["upstream_source_found"] for t in per_header)

    checks = {
        "shared_header_045_pass": bool(a045["checks"].get("shared_header_grammar_pass")),
        "header_source_047_pass": bool(a047.get("audit_pass")),
        "frontier_048_pass": bool(a048.get("frontier_pass")),
        "source_root_exists": SOURCE_ROOT.exists(),
        "json_file_count": len(json_files),
        "candidate_count": len(candidates),
        "remaining_header_target_count": len(per_header),
        "remaining_headers_are_free_sum_relay_max_relay_sum": sorted(per_header.keys()) == ["free_sum", "relay_max", "relay_sum"],
        "upstream_source_found_for_all": upstream_source_found_for_all,
        "shared_exact_upstream_family_exists": len(shared_exact_families) > 0,
        "shared_near_upstream_family_exists": len(shared_near_families) > 0,
    }

    audit_pass = all([
        checks["shared_header_045_pass"],
        checks["header_source_047_pass"],
        checks["frontier_048_pass"],
        checks["source_root_exists"],
        checks["json_file_count"] > 0,
        checks["candidate_count"] > 0,
        checks["remaining_headers_are_free_sum_relay_max_relay_sum"],
    ])

    if checks["upstream_source_found_for_all"]:
        verdict = "upstream_header_source_candidates_found_for_all"
    elif any(per_header[t]["upstream_source_found"] for t in per_header):
        verdict = "partial_upstream_header_source_candidates_found"
    elif checks["shared_near_upstream_family_exists"]:
        verdict = "shared_near_upstream_family_but_no_exact_source"
    else:
        verdict = "upstream_header_source_not_found_in_imported_sources"

    result = {
        "status": "header_upstream_source_locator_recorded",
        "audit_id": "049",
        "inputs": {
            "shared_header_grammar_045": str(IN_045),
            "header_source_audit_047": str(IN_047),
            "local_scalar_frontier_048": str(IN_048),
            "source_root": str(SOURCE_ROOT),
        },
        "checks": checks,
        "audit_pass": audit_pass,
        "verdict": verdict,
        "json_files_scanned": [str(p.relative_to(ROOT)) for p in json_files],
        "per_header": per_header,
        "shared_exact_upstream_families": shared_exact_families,
        "shared_near_upstream_families": shared_near_families,
        "interpretation": (
            "Artifact 047 left the bounded two-bit header as an open provenance target within the tested station-feature family. "
            "This locator scans the imported upstream provenance files for state-indexed, transition-indexed, or affine readouts matching "
            "the remaining header residuals."
        ),
        "boundary": (
            "This is an upstream source locator, not a derivation. Exact hits would be candidates requiring independent validation. "
            "No hit does not refute the local scalar normal form; it means the header source is not present in the imported source family scanned here. "
            "This does not derive the full role-labeled shared_B universe and is not Gap A closure."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "target",
            "kind",
            "match_kind",
            "source_file",
            "source_path",
            "source_kind",
            "feature",
            "a",
            "c",
            "l1_error",
            "values",
            "predicted",
        ])
        for row in csv_rows:
            w.writerow(row)

    lines = []
    lines.append("# Header upstream source locator 049")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- audit_pass: `" + str(audit_pass) + "`")
    lines.append("- verdict: `" + verdict + "`")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Header targets")
    lines.append("")
    for target in sorted(per_header):
        p = per_header[target]
        lines.append("- " + target + ":")
        lines.append("  - base_feature: `" + p["base_feature"] + "`")
        lines.append("  - residual: `" + str(p["residual"]) + "`")
        lines.append("  - exact_upstream_source_count: `" + str(p["exact_upstream_source_count"]) + "`")
        lines.append("  - upstream_source_found: `" + str(p["upstream_source_found"]) + "`")
        lines.append("  - exact_family_counts: `" + str(p["exact_family_counts"]) + "`")
        lines.append("  - near_family_counts: `" + str(p["near_family_counts"]) + "`")
        lines.append("  - exact_upstream_sources_first_5: `" + str(p["exact_upstream_sources_first"][:5]) + "`")
        lines.append("  - nearest_upstream_sources_first_5: `" + str(p["nearest_upstream_sources_first"][:5]) + "`")
    lines.append("")
    lines.append("## Shared families")
    lines.append("")
    lines.append("- shared_exact_upstream_families: `" + str(shared_exact_families) + "`")
    lines.append("- shared_near_upstream_families: `" + str(shared_near_families) + "`")
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
    print("audit_pass", audit_pass)
    print("verdict", verdict)
    for k, v in checks.items():
        print(k, v)
    for target in sorted(per_header):
        p = per_header[target]
        print(
            target,
            "exact_upstream_sources", p["exact_upstream_source_count"],
            "nearest", p["nearest_upstream_sources_first"][:2],
        )
    print("shared_exact_upstream_families", shared_exact_families[:10])
    print("shared_near_upstream_families", shared_near_families[:10])


if __name__ == "__main__":
    main()
