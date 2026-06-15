#!/usr/bin/env python3
import csv
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_052 = ROOT / "artifacts/json/null_completion_header_interpretation_052.v1.json"
IN_053 = ROOT / "artifacts/json/completion_ladder_provenance_frontier_053.v1.json"
LOCATOR_049 = ROOT / "scripts/header_upstream_source_locator_049.py"

SOURCE_ROOT = ROOT / "source/upstream_station_provenance"

OUT_JSON = ROOT / "artifacts/json/completion_ladder_native_source_probe_054.v1.json"
OUT_CSV = ROOT / "artifacts/csv/completion_ladder_native_source_probe_054.v1.csv"
OUT_NOTE = ROOT / "notes/completion_ladder_native_source_probe_054.md"

STATES = ["O0", "O1", "B0", "B1"]

REQUIRED_PHRASES = [
    "completion ladder source probe",
    "completion_level",
    "c_row",
    "not native closure",
    "not Gap A closure",
    "not full role-labeled shared_B universe",
]

FORBIDDEN_PHRASES = [
    "Gap A is closed",
    "native closure achieved",
    "completion ladder proven natively",
    "full shared_B universe derived",
]


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_locator_module():
    spec = importlib.util.spec_from_file_location("locator049", LOCATOR_049)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def missing_phrases(text, phrases):
    return [p for p in phrases if p not in text]


def found_phrases(text, phrases):
    return [p for p in phrases if p in text]


def first_compact(items, n=10):
    out = []
    for item in items[:n]:
        out.append({
            "source_file": item.get("source_file"),
            "source_path": item.get("source_path"),
            "kind": item.get("kind"),
            "feature": item.get("feature"),
            "match_kind": item.get("match_kind"),
            "a": item.get("a"),
            "c": item.get("c"),
            "l1_error": item.get("l1_error"),
            "values": item.get("values"),
            "predicted": item.get("predicted"),
        })
    return out


def main():
    a052 = load_json(IN_052)
    a053 = load_json(IN_053)

    if not a052.get("interpretation_candidate_pass"):
        raise SystemExit("052 interpretation_candidate_pass is not true")
    if not a053.get("frontier_pass"):
        raise SystemExit("053 frontier_pass is not true")

    locator = load_locator_module()

    if not SOURCE_ROOT.exists():
        raise SystemExit("missing source root " + str(SOURCE_ROOT))

    state_rows = {row["state"]: row for row in a052["state_rows"]}

    targets = {
        "completion_level": {s: int(state_rows[s]["completion_level"]) for s in STATES},
        "c_row": {s: int(state_rows[s]["c_row"]) for s in STATES},
        "completion_offset_plus_two_check": {s: int(state_rows[s]["completion_level"]) - 2 for s in STATES},
    }

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
        locator.walk(candidates, rel, [], data)

    per_target = {}
    csv_rows = []

    for target_name, target_values in targets.items():
        exact, near = locator.exact_and_near(candidates, target_values)

        per_target[target_name] = {
            "target_values": target_values,
            "exact_source_count": len(exact),
            "nearest_source_count": len(near),
            "exact_sources_first": first_compact(exact, 20),
            "nearest_sources_first": first_compact(near, 20),
            "source_found": len(exact) > 0,
        }

        for kind, items in [("exact", exact[:20]), ("nearest", near[:20])]:
            for item in items:
                csv_rows.append([
                    target_name,
                    kind,
                    item.get("match_kind"),
                    item.get("source_file"),
                    item.get("source_path"),
                    item.get("kind"),
                    item.get("feature"),
                    item.get("a"),
                    item.get("c"),
                    item.get("l1_error"),
                    json.dumps(item.get("values"), sort_keys=True),
                    json.dumps(item.get("predicted"), sort_keys=True),
                ])

    completion_source_found = per_target["completion_level"]["source_found"]
    c_row_source_found = per_target["c_row"]["source_found"]
    offset_check_source_found = per_target["completion_offset_plus_two_check"]["source_found"]

    if completion_source_found:
        verdict = "completion_level_source_candidate_found"
    elif c_row_source_found or offset_check_source_found:
        verdict = "c_row_source_candidate_found_but_plus_two_still_needs_native_reading"
    else:
        verdict = "completion_ladder_source_not_found_in_imported_upstream"

    source_statement = (
        "Artifact 054 is a completion ladder source probe. It scans the imported upstream provenance cache for exact or affine candidate sources "
        "of completion_level and c_row. A hit would be a candidate requiring validation, not native closure."
    )

    boundary = (
        "This is a targeted source probe, not native closure. It does not derive the completion ladder from the full native G60/shared_B universe, "
        "it is not full role-labeled shared_B universe derivation, and is not Gap A closure."
    )

    combined = source_statement + "\n" + boundary
    missing = missing_phrases(combined, REQUIRED_PHRASES)
    forbidden = found_phrases(combined, FORBIDDEN_PHRASES)

    checks = {
        "null_completion_header_052_pass": bool(a052.get("interpretation_candidate_pass")),
        "completion_frontier_053_pass": bool(a053.get("frontier_pass")),
        "source_root_exists": SOURCE_ROOT.exists(),
        "json_file_count": len(json_files),
        "candidate_count": len(candidates),
        "target_completion_level_is_2_3_4_5": [targets["completion_level"][s] for s in STATES] == [2, 3, 4, 5],
        "target_c_row_is_0_1_2_3": [targets["c_row"][s] for s in STATES] == [0, 1, 2, 3],
        "completion_source_found": completion_source_found,
        "c_row_source_found": c_row_source_found,
        "offset_check_source_found": offset_check_source_found,
        "required_phrases_present": len(missing) == 0,
        "forbidden_phrases_absent": len(forbidden) == 0,
    }

    probe_pass = all([
        checks["null_completion_header_052_pass"],
        checks["completion_frontier_053_pass"],
        checks["source_root_exists"],
        checks["json_file_count"] > 0,
        checks["candidate_count"] > 0,
        checks["target_completion_level_is_2_3_4_5"],
        checks["target_c_row_is_0_1_2_3"],
        checks["required_phrases_present"],
        checks["forbidden_phrases_absent"],
    ])

    result = {
        "status": "completion_ladder_native_source_probe_recorded",
        "audit_id": "054",
        "inputs": {
            "null_completion_header_interpretation_052": str(IN_052),
            "completion_ladder_provenance_frontier_053": str(IN_053),
            "source_root": str(SOURCE_ROOT),
            "locator_module": str(LOCATOR_049),
        },
        "checks": checks,
        "probe_pass": probe_pass,
        "verdict": verdict,
        "targets": targets,
        "per_target": per_target,
        "source_statement": source_statement,
        "boundary": boundary,
        "missing_required_phrases": missing,
        "forbidden_phrases_found": forbidden,
        "interpretation": (
            "The completion ladder is now the provenance target. This probe checks whether the current imported upstream cache already contains "
            "a candidate source for the completion level vector or the c_row vector."
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
    lines.append("# Completion ladder native source probe 054")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- probe_pass: `" + str(probe_pass) + "`")
    lines.append("- verdict: `" + verdict + "`")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Targets")
    lines.append("")
    for target_name, target_values in targets.items():
        lines.append("- " + target_name + ": `" + str(target_values) + "`")
    lines.append("")
    lines.append("## Candidate source results")
    lines.append("")
    for target_name in sorted(per_target):
        p = per_target[target_name]
        lines.append("- " + target_name + ":")
        lines.append("  - exact_source_count: `" + str(p["exact_source_count"]) + "`")
        lines.append("  - source_found: `" + str(p["source_found"]) + "`")
        lines.append("  - exact_sources_first_5: `" + str(p["exact_sources_first"][:5]) + "`")
        lines.append("  - nearest_sources_first_5: `" + str(p["nearest_sources_first"][:5]) + "`")
    lines.append("")
    lines.append("## Source statement")
    lines.append("")
    lines.append(source_statement)
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
    print("probe_pass", probe_pass)
    print("verdict", verdict)
    for k, v in checks.items():
        print(k, v)
    for target_name in sorted(per_target):
        p = per_target[target_name]
        print(
            target_name,
            "exact_source_count", p["exact_source_count"],
            "nearest", p["nearest_sources_first"][:2],
        )


if __name__ == "__main__":
    main()
