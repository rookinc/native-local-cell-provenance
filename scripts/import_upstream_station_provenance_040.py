#!/usr/bin/env python3
import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEORY_ROOT = ROOT.parent

IN_039 = ROOT / "artifacts/json/upstream_station_provenance_locator_039.v1.json"

IMPORT_ROOT = ROOT / "source/upstream_station_provenance"
MANIFEST = IMPORT_ROOT / "manifest_040.v1.json"

OUT_JSON = ROOT / "artifacts/json/upstream_station_provenance_import_040.v1.json"
OUT_CSV = ROOT / "artifacts/csv/upstream_station_provenance_import_040.v1.csv"
OUT_NOTE = ROOT / "notes/upstream_station_provenance_import_040.md"

PREFERRED_BASENAMES = [
    "wxyzti_station_provenance_law_audit_010.v1.json",
    "wxyzti_g30_shadow_sheet_audit_011.v1.json",
    "wxyzti_same_sheet_wrap_carry_audit_012.v1.json",
    "wxyzti_ambiguous_source_split_audit_014.v1.json",
    "wxyzti_reverse_partner_vs_sharedB_audit_016.v1.json",
    "wxyzti_sharedB_residual_law_search_017.v1.json",
    "wxyzti_role_class_invariant_audit_018.v1.json",
    "wxyzti_station_transform_map_audit_019.v1.json",
    "wxyzti_shared_reverse_pair_coupling_audit_021.v1.json",
    "wxyzti_answer_pair_candidate_universe_audit_022.v1.json",
    "wxyzti_station_transition_feature_inspection_009.v1.json",
    "c_transition_overlay_delta_generator_001.v1.json",
]


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def safe_copy_rel(rel):
    src = THEORY_ROOT / rel
    dst = IMPORT_ROOT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return src, dst


def summarize_json(path):
    data = load_json(path)
    summary = {
        "status": data.get("status") if isinstance(data, dict) else None,
        "audit_id": data.get("audit_id") if isinstance(data, dict) else None,
        "row_count": None,
        "keys_top_level": [],
    }

    if isinstance(data, dict):
        summary["keys_top_level"] = sorted(list(data.keys()))[:80]
        for k in ["row_count", "semantic_row_count", "shared_row_count", "reverse_row_count", "candidate_count"]:
            if k in data:
                summary["row_count"] = data[k]
                break
        if summary["row_count"] is None and isinstance(data.get("rows"), list):
            summary["row_count"] = len(data["rows"])

    return summary


def main():
    locator = load_json(IN_039)

    rich = locator.get("top_rich_station_files", [])
    by_rel = {item["file"]: item for item in rich}

    selected = []
    used_basenames = set()

    # First import preferred basenames if present, preferring first locator ranking.
    for basename in PREFERRED_BASENAMES:
        for item in rich:
            rel = item["file"]
            if Path(rel).name == basename and basename not in used_basenames:
                selected.append(item)
                used_basenames.add(basename)
                break

    # Then add any remaining high-ranked unique basenames up to a reasonable local cache.
    for item in rich:
        basename = Path(item["file"]).name
        if basename in used_basenames:
            continue
        if len(selected) >= 24:
            break
        selected.append(item)
        used_basenames.add(basename)

    copied = []
    missing = []

    for item in selected:
        rel = item["file"]
        src = THEORY_ROOT / rel
        if not src.exists():
            missing.append(rel)
            continue
        src, dst = safe_copy_rel(rel)
        imported_rel = str(dst.relative_to(ROOT))
        src_summary = summarize_json(dst)
        copied.append({
            "source_rel_to_theory_root": rel,
            "imported_rel_to_project_root": imported_rel,
            "score": item.get("score"),
            "key_counts": item.get("key_counts", {}),
            "role_token_counts": item.get("role_token_counts", {}),
            "state_token_counts": item.get("state_token_counts", {}),
            "source_summary": src_summary,
        })

    checks = {
        "locator_039_complete": bool(locator.get("checks", {}).get("locator_complete")),
        "locator_has_rich_station_files": bool(locator.get("checks", {}).get("rich_station_file_count", 0) > 0),
        "selected_file_count": len(selected),
        "copied_file_count": len(copied),
        "missing_file_count": len(missing),
        "copied_all_selected_existing": len(missing) == 0,
        "manifest_written": True,
    }

    manifest = {
        "status": "upstream_station_provenance_manifest_recorded",
        "audit_id": "040",
        "import_root": str(IMPORT_ROOT.relative_to(ROOT)),
        "copied": copied,
        "missing": missing,
        "checks": checks,
        "boundary": (
            "This manifest imports upstream station/provenance artifacts into Project24 for local joining. "
            "It does not derive scalar laws and does not close Gap A."
        ),
    }

    IMPORT_ROOT.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = {
        "status": "upstream_station_provenance_import_recorded",
        "audit_id": "040",
        "input_locator": str(IN_039),
        "manifest": str(MANIFEST.relative_to(ROOT)),
        "checks": checks,
        "copied": copied,
        "missing": missing,
        "suggested_next": [
            "Build 041 to inspect imported row schemas and extract station rows.",
            "Build 042 to join station rows against scalar targets from 032 and 035.",
        ],
        "interpretation": (
            "This imports the upstream WXYZTI station/register layer found by 039 into a stable local Project24 source folder. "
            "The imported layer contains slot/fiber/A/B/C/role-pair/station-role/lift-q fields needed after 037."
        ),
        "boundary": (
            "This is an import and manifest artifact. It does not prove scalar provenance, does not derive the role-labeled shared_B universe, and does not close Gap A."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rank", "source", "imported", "score", "status", "row_count"])
        for i, item in enumerate(copied, 1):
            w.writerow([
                i,
                item["source_rel_to_theory_root"],
                item["imported_rel_to_project_root"],
                item["score"],
                item["source_summary"].get("status"),
                item["source_summary"].get("row_count"),
            ])

    lines = []
    lines.append("# Upstream station provenance import 040")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Imported files")
    lines.append("")
    for i, item in enumerate(copied, 1):
        lines.append(str(i) + ". `" + item["imported_rel_to_project_root"] + "`")
        lines.append("   - source: `" + item["source_rel_to_theory_root"] + "`")
        lines.append("   - score: `" + str(item["score"]) + "`")
        lines.append("   - status: `" + str(item["source_summary"].get("status")) + "`")
        lines.append("   - row_count: `" + str(item["source_summary"].get("row_count")) + "`")
    if missing:
        lines.append("")
        lines.append("## Missing")
        lines.append("")
        for rel in missing:
            lines.append("- `" + rel + "`")
    lines.append("")
    lines.append("## Suggested next")
    lines.append("")
    for item in result["suggested_next"]:
        lines.append("- " + item)
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
    print("wrote", MANIFEST)
    print("status", result["status"])
    print("selected_file_count", len(selected))
    print("copied_file_count", len(copied))
    print("missing_file_count", len(missing))
    for item in copied:
        print("-", item["imported_rel_to_project_root"])


if __name__ == "__main__":
    main()
