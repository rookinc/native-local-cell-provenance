#!/usr/bin/env python3
import csv
import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]

IMPORT_ROOT = ROOT / "source/upstream_station_provenance"
MANIFEST = IMPORT_ROOT / "manifest_040.v1.json"

OUT_JSON = ROOT / "artifacts/json/imported_station_row_extract_041.v1.json"
OUT_CSV = ROOT / "artifacts/csv/imported_station_row_extract_041.v1.csv"
OUT_NOTE = ROOT / "notes/imported_station_row_extract_041.md"

CORE_FIELDS = [
    "station_role",
    "role_pair",
    "edge_role",
    "role_class",
    "from_A",
    "from_B",
    "from_C",
    "from_slot",
    "from_fiber",
    "to_A",
    "to_B",
    "to_C",
    "to_slot",
    "to_fiber",
    "lift_q",
    "source",
    "kind",
]

NUMERIC_FIELDS = [
    "from_A",
    "from_B",
    "from_C",
    "from_slot",
    "from_fiber",
    "to_A",
    "to_B",
    "to_C",
    "to_slot",
    "to_fiber",
    "lift_q",
]

ROLE_CLASSES = {"shared_B", "reverse_partner"}
STATION_ROLES = {"WX", "YZ", "TI", "XY", "ZT", "IW"}

MAX_DICTS_PER_FILE = 200000


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def walk_dicts(obj, path="$", box=None):
    if box is None:
        box = {"count": 0}

    if box["count"] >= MAX_DICTS_PER_FILE:
        return

    if isinstance(obj, dict):
        box["count"] += 1
        yield path, obj
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                yield from walk_dicts(v, path + "." + str(k), box)

    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if box["count"] >= MAX_DICTS_PER_FILE:
                return
            if isinstance(v, (dict, list)):
                yield from walk_dicts(v, path + "[" + str(i) + "]", box)


def rel(path):
    try:
        return str(path.relative_to(ROOT))
    except Exception:
        return str(path)


def clean_value(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, int):
        return v
    if isinstance(v, float) and v.is_integer():
        return int(v)
    if isinstance(v, str):
        s = v.strip()
        if s.lstrip("-").isdigit():
            return int(s)
        return s
    return v


def is_station_row(d):
    keys = set(d.keys())

    has_transition = ("from_C" in keys and "to_C" in keys)
    has_role = any(k in keys for k in ["station_role", "role_pair", "edge_role", "role_class"])
    has_payload = any(k in keys for k in [
        "from_A",
        "from_B",
        "from_slot",
        "from_fiber",
        "to_A",
        "to_B",
        "to_slot",
        "to_fiber",
        "lift_q",
    ])

    return has_transition and has_role and has_payload


def infer_role_class(row):
    for k in ["edge_role", "role_class", "kind", "source"]:
        v = row.get(k)
        if isinstance(v, str) and v in ROLE_CLASSES:
            return v

    for k in ["role_pair", "station_role"]:
        v = row.get(k)
        if isinstance(v, str) and v in ROLE_CLASSES:
            return v

    return None


def infer_station_role(row):
    for k in ["station_role", "edge_role", "role"]:
        v = row.get(k)
        if isinstance(v, str) and v in STATION_ROLES:
            return v
    return row.get("station_role")


def normalize_row(source_file, json_path, d):
    row = {
        "source_file": source_file,
        "json_path": json_path,
    }

    for k in CORE_FIELDS:
        if k in d:
            row[k] = clean_value(d[k])
        else:
            row[k] = None

    row["station_role"] = infer_station_role(row)
    row["role_class"] = infer_role_class(row)

    if row.get("from_fiber") is not None and row.get("from_C") is not None:
        row["from_fiber_mod15"] = int(row["from_fiber"]) % 15
        row["from_fiber_matches_C"] = row["from_fiber_mod15"] == int(row["from_C"])
    else:
        row["from_fiber_mod15"] = None
        row["from_fiber_matches_C"] = None

    if row.get("to_fiber") is not None and row.get("to_C") is not None:
        row["to_fiber_mod15"] = int(row["to_fiber"]) % 15
        row["to_fiber_matches_C"] = row["to_fiber_mod15"] == int(row["to_C"])
    else:
        row["to_fiber_mod15"] = None
        row["to_fiber_matches_C"] = None

    if row.get("from_C") is not None and row.get("to_C") is not None:
        row["C_delta_mod15"] = (int(row["to_C"]) - int(row["from_C"])) % 15
    else:
        row["C_delta_mod15"] = None

    return row


def signature(row):
    keys = [
        "station_role",
        "role_pair",
        "edge_role",
        "role_class",
        "from_A",
        "from_B",
        "from_C",
        "from_slot",
        "from_fiber",
        "to_A",
        "to_B",
        "to_C",
        "to_slot",
        "to_fiber",
        "lift_q",
    ]
    return tuple((k, row.get(k)) for k in keys)


def compact_counts(rows):
    return {
        "row_count": len(rows),
        "station_role_counts": dict(Counter(str(r.get("station_role")) for r in rows).most_common()),
        "role_pair_counts": dict(Counter(str(r.get("role_pair")) for r in rows).most_common()),
        "edge_role_counts": dict(Counter(str(r.get("edge_role")) for r in rows).most_common()),
        "role_class_counts": dict(Counter(str(r.get("role_class")) for r in rows).most_common()),
        "transition_count": len(set((r.get("from_C"), r.get("to_C")) for r in rows)),
        "lift_q_counts": dict(Counter(str(r.get("lift_q")) for r in rows).most_common()),
    }


def main():
    manifest = load_json(MANIFEST)

    copied = manifest.get("copied", [])
    files = []
    for item in copied:
        imported = item.get("imported_rel_to_project_root")
        if imported:
            p = ROOT / imported
            if p.exists():
                files.append(p)

    raw_rows = []

    for i, path in enumerate(files, 1):
        print("extracting", i, "of", len(files), rel(path))
        data = load_json(path)
        for jpath, d in walk_dicts(data):
            if is_station_row(d):
                raw_rows.append(normalize_row(rel(path), jpath, d))

    by_sig = {}
    sources_by_sig = defaultdict(list)

    for row in raw_rows:
        sig = signature(row)
        if sig not in by_sig:
            by_sig[sig] = dict(row)
        sources_by_sig[sig].append({
            "source_file": row["source_file"],
            "json_path": row["json_path"],
        })

    unique_rows = []
    for sig, row in by_sig.items():
        row = dict(row)
        row["source_count"] = len(sources_by_sig[sig])
        row["sources"] = sources_by_sig[sig][:12]
        unique_rows.append(row)

    canonical_source_marker = "wxyzti_station_provenance_law_audit_010.v1.json"
    canonical_raw = [
        r for r in raw_rows
        if canonical_source_marker in r["source_file"]
        and r.get("role_class") in ROLE_CLASSES
        and r.get("role_pair") is not None
        and r.get("lift_q") is not None
    ]

    canonical_by_sig = {}
    canonical_sources = defaultdict(list)
    for row in canonical_raw:
        sig = signature(row)
        if sig not in canonical_by_sig:
            canonical_by_sig[sig] = dict(row)
        canonical_sources[sig].append({
            "source_file": row["source_file"],
            "json_path": row["json_path"],
        })

    canonical_rows = []
    for sig, row in canonical_by_sig.items():
        row = dict(row)
        row["source_count"] = len(canonical_sources[sig])
        row["sources"] = canonical_sources[sig][:12]
        canonical_rows.append(row)

    canonical_rows.sort(key=lambda r: (
        str(r.get("role_pair")),
        str(r.get("role_class")),
        str(r.get("station_role")),
        int(r.get("from_C")) if r.get("from_C") is not None else -1,
        int(r.get("to_C")) if r.get("to_C") is not None else -1,
    ))

    unique_rows.sort(key=lambda r: (
        str(r.get("source_file")),
        str(r.get("role_pair")),
        str(r.get("role_class")),
        str(r.get("station_role")),
        int(r.get("from_C")) if r.get("from_C") is not None else -1,
        int(r.get("to_C")) if r.get("to_C") is not None else -1,
    ))

    canonical_counts = compact_counts(canonical_rows)
    unique_counts = compact_counts(unique_rows)

    station_roles_all_four = all(
        canonical_counts["station_role_counts"].get(role, 0) == 4
        for role in STATION_ROLES
    )

    role_classes_12_12 = (
        canonical_counts["role_class_counts"].get("shared_B", 0) == 12
        and canonical_counts["role_class_counts"].get("reverse_partner", 0) == 12
    )

    all_fiber_mod15_matches = all(
        r.get("from_fiber_matches_C") is not False
        and r.get("to_fiber_matches_C") is not False
        for r in canonical_rows
    )

    checks = {
        "manifest_040_loaded": True,
        "imported_file_count": len(files),
        "raw_station_row_count": len(raw_rows),
        "unique_station_signature_count": len(unique_rows),
        "canonical_source_marker_found": bool(canonical_rows),
        "canonical_station_row_count": len(canonical_rows),
        "canonical_transition_count": canonical_counts["transition_count"],
        "canonical_station_roles_all_four": station_roles_all_four,
        "canonical_role_classes_12_12": role_classes_12_12,
        "canonical_fiber_mod15_matches_C": all_fiber_mod15_matches,
    }

    extract_pass = (
        checks["imported_file_count"] >= 20
        and checks["raw_station_row_count"] > 0
        and checks["canonical_station_row_count"] == 24
        and checks["canonical_transition_count"] == 12
        and checks["canonical_station_roles_all_four"]
        and checks["canonical_role_classes_12_12"]
        and checks["canonical_fiber_mod15_matches_C"]
    )

    result = {
        "status": "imported_station_row_extract_recorded",
        "audit_id": "041",
        "input_manifest": str(MANIFEST.relative_to(ROOT)),
        "checks": checks,
        "extract_pass": extract_pass,
        "canonical_counts": canonical_counts,
        "unique_counts": unique_counts,
        "canonical_rows": canonical_rows,
        "unique_rows_first_200": unique_rows[:200],
        "interpretation": (
            "This extracts and normalizes the imported WXYZTI station rows. "
            "The canonical 010 source is treated as the stable 24-row realized station table for later scalar-provenance joins."
        ),
        "boundary": (
            "This is a row extraction and schema-normalization artifact. It does not join the station rows to 032/035 scalar targets, "
            "does not derive scalar laws, does not derive the full role-labeled shared_B universe, and does not close Gap A."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    csv_fields = [
        "source_file",
        "json_path",
        "station_role",
        "role_pair",
        "edge_role",
        "role_class",
        "from_A",
        "from_B",
        "from_C",
        "from_slot",
        "from_fiber",
        "to_A",
        "to_B",
        "to_C",
        "to_slot",
        "to_fiber",
        "lift_q",
        "from_fiber_mod15",
        "to_fiber_mod15",
        "C_delta_mod15",
        "source_count",
    ]

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=csv_fields)
        w.writeheader()
        for row in canonical_rows:
            w.writerow({k: row.get(k) for k in csv_fields})

    lines = []
    lines.append("# Imported station row extract 041")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- extract_pass: `" + str(extract_pass) + "`")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Canonical counts")
    lines.append("")
    for k, v in canonical_counts.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Canonical rows")
    lines.append("")
    for i, r in enumerate(canonical_rows, 1):
        lines.append(
            str(i) + ". "
            + "role_pair=`" + str(r.get("role_pair")) + "` "
            + "role_class=`" + str(r.get("role_class")) + "` "
            + "station_role=`" + str(r.get("station_role")) + "` "
            + "C=`" + str(r.get("from_C")) + "->" + str(r.get("to_C")) + "` "
            + "A=`" + str(r.get("from_A")) + "->" + str(r.get("to_A")) + "` "
            + "B=`" + str(r.get("from_B")) + "->" + str(r.get("to_B")) + "` "
            + "slot=`" + str(r.get("from_slot")) + "->" + str(r.get("to_slot")) + "` "
            + "fiber=`" + str(r.get("from_fiber")) + "->" + str(r.get("to_fiber")) + "` "
            + "lift_q=`" + str(r.get("lift_q")) + "`"
        )
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
    print("extract_pass", extract_pass)
    print("raw_station_row_count", len(raw_rows))
    print("unique_station_signature_count", len(unique_rows))
    print("canonical_station_row_count", len(canonical_rows))
    print("canonical_transition_count", canonical_counts["transition_count"])
    print("canonical_station_role_counts", canonical_counts["station_role_counts"])
    print("canonical_role_class_counts", canonical_counts["role_class_counts"])
    print("canonical_fiber_mod15_matches_C", all_fiber_mod15_matches)


if __name__ == "__main__":
    main()
