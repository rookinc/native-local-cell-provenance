#!/usr/bin/env python3
import csv
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
THEORY_ROOT = ROOT.parent

SCAN_ROOTS = [
    THEORY_ROOT / "16-fifteen-thalion-ring",
    THEORY_ROOT / "17-g900-theorem-proof",
    THEORY_ROOT / "18-g900-kernel-admission",
    THEORY_ROOT / "21-gap-a-answer-pair-generator",
    THEORY_ROOT / "22-lift-and-twist",
    THEORY_ROOT / "23-local-cell-to-reduced-universe",
    ROOT,
]

OUT_JSON = ROOT / "artifacts/json/upstream_station_provenance_locator_039.v1.json"
OUT_CSV = ROOT / "artifacts/csv/upstream_station_provenance_locator_039.v1.csv"
OUT_NOTE = ROOT / "notes/upstream_station_provenance_locator_039.md"

SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
}

HIGH_VALUE_KEYS = [
    "slot",
    "from_slot",
    "to_slot",
    "fiber",
    "from_fiber",
    "to_fiber",
    "A",
    "B",
    "C",
    "from_A",
    "to_A",
    "from_B",
    "to_B",
    "from_C",
    "to_C",
    "columns",
    "columns_key",
    "address_pair_source",
    "role_pair",
    "edge_role",
    "station_role",
    "role",
    "shared_B",
    "reverse_partner",
    "from_address",
    "to_address",
    "from_label",
    "to_label",
    "from_vertex",
    "to_vertex",
    "source",
    "target",
    "kind",
    "q",
    "lift_q",
    "wrap",
    "sheet",
    "sign",
]

ROLE_TOKENS = [
    "WX",
    "YZ",
    "TI",
    "XY",
    "ZT",
    "IW",
    "shared_B",
    "reverse_partner",
]

STATE_TOKENS = ["O0", "O1", "B0", "B1"]

MAX_DICTS_PER_FILE = 50000
MAX_EXAMPLES = 8


def iter_json_files():
    seen = set()
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*.json"):
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            if p in seen:
                continue
            seen.add(p)
            yield p


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as e:
        return None, str(e)


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


def compact(v):
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    if isinstance(v, list):
        if len(v) <= 10 and all(isinstance(x, (str, int, float, bool)) or x is None for x in v):
            return v
        return "[list len %d]" % len(v)
    if isinstance(v, dict):
        return "{dict keys %d}" % len(v)
    return str(type(v).__name__)


def relpath(p):
    try:
        return str(p.relative_to(THEORY_ROOT))
    except Exception:
        return str(p)


def score_record(d):
    keys = set(str(k) for k in d.keys())
    text_bits = []

    for k, v in d.items():
        text_bits.append(str(k))
        if isinstance(v, (str, int, float, bool)) or v is None:
            text_bits.append(str(v))
        elif isinstance(v, list) and len(v) <= 12:
            text_bits.append(str(v))

    text = " ".join(text_bits)

    key_hits = [k for k in HIGH_VALUE_KEYS if k in keys]
    role_hits = [tok for tok in ROLE_TOKENS if tok in text]
    state_hits = [tok for tok in STATE_TOKENS if tok in text]

    score = 0
    score += 5 * len(key_hits)
    score += 4 * len(role_hits)
    score += 2 * len(state_hits)

    if any(k in keys for k in ["slot", "from_slot", "to_slot", "fiber", "from_fiber", "to_fiber"]):
        score += 20
    if any(k in keys for k in ["A", "B", "C", "from_A", "to_A", "from_B", "to_B", "from_C", "to_C"]):
        score += 16
    if any(k in keys for k in ["role_pair", "edge_role", "station_role", "role"]):
        score += 16
    if any(k in keys for k in ["columns", "columns_key", "address_pair_source"]):
        score += 16
    if any(tok in text for tok in ["WX", "YZ", "TI", "XY", "ZT", "IW"]):
        score += 16

    return score, key_hits, role_hits, state_hits


def summarize_file(path, index, total):
    if index == 1 or index % 25 == 0:
        print("scanning", index, "of", total, relpath(path))

    data, err = load_json(path)
    if err:
        return {
            "file": relpath(path),
            "load_error": err,
            "dict_count": 0,
            "score": 0,
            "key_counts": {},
            "role_token_counts": {},
            "state_token_counts": {},
            "examples": [],
        }

    key_counts = Counter()
    role_counts = Counter()
    state_counts = Counter()
    examples = []
    dict_count = 0
    best_score = 0

    for jpath, d in walk_dicts(data):
        dict_count += 1
        for k in d.keys():
            if str(k) in HIGH_VALUE_KEYS:
                key_counts[str(k)] += 1

        score, key_hits, role_hits, state_hits = score_record(d)
        best_score = max(best_score, score)

        for tok in role_hits:
            role_counts[tok] += 1
        for tok in state_hits:
            state_counts[tok] += 1

        if score >= 40 and len(examples) < MAX_EXAMPLES:
            rec = {}
            for k, v in d.items():
                if str(k) in HIGH_VALUE_KEYS or str(k) in key_hits:
                    rec[str(k)] = compact(v)
            if not rec:
                for k in list(d.keys())[:16]:
                    rec[str(k)] = compact(d[k])
            examples.append({
                "json_path": jpath,
                "score": score,
                "key_hits": key_hits,
                "role_hits": role_hits,
                "state_hits": state_hits,
                "record": rec,
            })

    return {
        "file": relpath(path),
        "load_error": None,
        "dict_count": dict_count,
        "score": best_score,
        "key_counts": dict(key_counts.most_common()),
        "role_token_counts": dict(role_counts.most_common()),
        "state_token_counts": dict(state_counts.most_common()),
        "examples": examples,
    }


def main():
    files = list(iter_json_files())
    summaries = []

    for i, path in enumerate(files, 1):
        summaries.append(summarize_file(path, i, len(files)))

    summaries.sort(
        key=lambda s: (
            s["score"],
            sum(s["key_counts"].values()),
            sum(s["role_token_counts"].values()),
        ),
        reverse=True,
    )

    useful = [
        s for s in summaries
        if s["score"] >= 40
        or any(k in s["key_counts"] for k in [
            "slot", "fiber", "from_A", "to_A", "from_B", "to_B",
            "role_pair", "edge_role", "station_role", "address_pair_source",
            "columns",
        ])
    ]

    totals = Counter()
    role_totals = Counter()
    state_totals = Counter()

    for s in summaries:
        totals.update(s["key_counts"])
        role_totals.update(s["role_token_counts"])
        state_totals.update(s["state_token_counts"])

    rich_files = [
        s for s in summaries
        if any(k in s["key_counts"] for k in [
            "slot", "from_slot", "to_slot", "fiber", "from_fiber", "to_fiber",
            "from_A", "to_A", "from_B", "to_B",
            "role_pair", "edge_role", "station_role",
            "columns", "address_pair_source",
        ])
    ]

    checks = {
        "scan_root_count": len([p for p in SCAN_ROOTS if p.exists()]),
        "json_files_scanned": len(files),
        "useful_file_count": len(useful),
        "rich_station_file_count": len(rich_files),
        "has_slot_or_fiber": any(k in totals for k in ["slot", "fiber", "from_slot", "to_slot", "from_fiber", "to_fiber"]),
        "has_AB_fields": any(k in totals for k in ["A", "B", "from_A", "to_A", "from_B", "to_B"]),
        "has_role_pair_fields": any(k in totals for k in ["role_pair", "edge_role", "station_role"]),
        "has_column_address_fields": any(k in totals for k in ["columns", "address_pair_source", "columns_key"]),
        "locator_complete": True,
    }

    suggested_next = []
    if rich_files:
        suggested_next.append("Import the top rich station files into source/upstream_station_provenance.")
        suggested_next.append("Build 040 to join rich station rows to scalar targets from 032 and 035.")
    else:
        suggested_next.append("No rich station file found in scanned roots. Search wider or regenerate station provenance from Project21 scripts.")

    result = {
        "status": "upstream_station_provenance_locator_recorded",
        "audit_id": "039",
        "scan_roots": [str(p) for p in SCAN_ROOTS if p.exists()],
        "checks": checks,
        "high_value_key_totals": dict(totals.most_common()),
        "role_token_totals": dict(role_totals.most_common()),
        "state_token_totals": dict(state_totals.most_common()),
        "top_useful_files": useful[:40],
        "top_rich_station_files": rich_files[:40],
        "suggested_next": suggested_next,
        "interpretation": (
            "Artifact 038 showed that the current Project24 JSONs do not carry enough rich station/register provenance "
            "to explain the scalar laws left open by 037. This locator searches upstream sibling projects for slot, fiber, "
            "A/B/C, role-pair, station-role, columns, and address-source fields."
        ),
        "boundary": (
            "This is a locator only. It identifies candidate provenance sources but does not import them, join them, "
            "derive scalar laws, or close Gap A."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "rank",
            "file",
            "score",
            "dict_count",
            "key_counts",
            "role_token_counts",
            "state_token_counts",
            "example_count",
        ])
        for rank, s in enumerate(useful[:120], 1):
            w.writerow([
                rank,
                s["file"],
                s["score"],
                s["dict_count"],
                json.dumps(s["key_counts"], sort_keys=True),
                json.dumps(s["role_token_counts"], sort_keys=True),
                json.dumps(s["state_token_counts"], sort_keys=True),
                len(s["examples"]),
            ])

    lines = []
    lines.append("# Upstream station provenance locator 039")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## High-value key totals")
    lines.append("")
    for k, v in list(totals.most_common(40)):
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Top rich station files")
    lines.append("")
    if rich_files:
        for i, s in enumerate(rich_files[:20], 1):
            lines.append(str(i) + ". `" + s["file"] + "`")
            lines.append("   - score: `" + str(s["score"]) + "`")
            lines.append("   - key_counts: `" + str(s["key_counts"]) + "`")
            lines.append("   - role_token_counts: `" + str(s["role_token_counts"]) + "`")
            lines.append("   - state_token_counts: `" + str(s["state_token_counts"]) + "`")
            if s["examples"]:
                ex = s["examples"][0]
                lines.append("   - first_example_path: `" + str(ex["json_path"]) + "`")
                lines.append("   - first_example_record: `" + str(ex["record"]) + "`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Suggested next")
    lines.append("")
    for item in suggested_next:
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
    print("status", result["status"])
    print("json_files_scanned", len(files))
    print("useful_file_count", len(useful))
    print("rich_station_file_count", len(rich_files))
    print("has_slot_or_fiber", checks["has_slot_or_fiber"])
    print("has_AB_fields", checks["has_AB_fields"])
    print("has_role_pair_fields", checks["has_role_pair_fields"])
    print("has_column_address_fields", checks["has_column_address_fields"])
    print("top_rich_station_files")
    for s in rich_files[:12]:
        print("-", s["score"], s["file"])


if __name__ == "__main__":
    main()
