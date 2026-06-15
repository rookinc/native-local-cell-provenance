#!/usr/bin/env python3
import csv
import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOTS = [
    ROOT / "artifacts/json",
    ROOT / "imported",
    ROOT / "data",
    ROOT / "source",
    ROOT / "sources",
]

OUT_JSON = ROOT / "artifacts/json/station_provenance_inventory_038.v1.json"
OUT_CSV = ROOT / "artifacts/csv/station_provenance_inventory_038.v1.csv"
OUT_NOTE = ROOT / "notes/station_provenance_inventory_038.md"

TARGET_KEYS = [
    "state",
    "role",
    "role_pair",
    "edge_role",
    "station_role",
    "from_C",
    "to_C",
    "from_A",
    "to_A",
    "from_B",
    "to_B",
    "slot",
    "from_slot",
    "to_slot",
    "fiber",
    "from_fiber",
    "to_fiber",
    "A",
    "B",
    "C",
    "C_plus_1",
    "columns",
    "columns_key",
    "address_pair_source",
    "sheet",
    "sign",
    "cocycle",
    "lift",
    "source",
    "target",
    "from",
    "to",
    "key",
]

ROLE_TOKENS = ["IW", "XY", "ZT", "TI", "WX", "YZ", "W", "X", "Y", "Z", "T", "I"]
STATE_TOKENS = ["O0", "O1", "B0", "B1"]

MAX_DICTS_PER_FILE = 20000
MAX_EXAMPLES_PER_FILE = 12


def load_json(path):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f), None
    except Exception as e:
        return None, str(e)


def iter_json_files():
    seen = set()
    for root in ARTIFACT_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*.json"):
            if p in seen:
                continue
            seen.add(p)
            yield p


def scalarish(v):
    return isinstance(v, (str, int, float, bool)) or v is None


def compact_value(v):
    if scalarish(v):
        return v
    if isinstance(v, list):
        if len(v) <= 8 and all(scalarish(x) for x in v):
            return v
        if len(v) <= 4 and all(isinstance(x, list) for x in v):
            return v
        return "[list len %d]" % len(v)
    if isinstance(v, dict):
        return "{dict keys %d}" % len(v)
    return str(type(v).__name__)


def walk_dicts(obj, path="$", limit_box=None):
    if limit_box is None:
        limit_box = {"count": 0}

    if limit_box["count"] >= MAX_DICTS_PER_FILE:
        return

    if isinstance(obj, dict):
        limit_box["count"] += 1
        yield path, obj
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                yield from walk_dicts(v, path + "." + str(k), limit_box)

    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if limit_box["count"] >= MAX_DICTS_PER_FILE:
                return
            if isinstance(v, (dict, list)):
                yield from walk_dicts(v, path + "[" + str(i) + "]", limit_box)


def score_record(d):
    keys = set(d.keys())
    lower_keys = {str(k).lower() for k in keys}

    target_hits = [k for k in TARGET_KEYS if k in keys]
    lower_hits = [k for k in TARGET_KEYS if k.lower() in lower_keys]

    role_hits = []
    state_hits = []

    sample_values = []
    for k, v in d.items():
        if scalarish(v):
            sample_values.append(str(v))
        elif isinstance(v, list) and len(v) <= 8:
            sample_values.append(str(v))

    joined = " ".join(sample_values)

    for tok in ROLE_TOKENS:
        if tok in joined:
            role_hits.append(tok)

    for tok in STATE_TOKENS:
        if tok in joined:
            state_hits.append(tok)

    score = 0
    score += 3 * len(set(target_hits))
    score += 2 * len(set(lower_hits))
    score += 2 * len(set(role_hits))
    score += 2 * len(set(state_hits))

    if any(k in keys for k in ["from_C", "to_C", "C", "C_plus_1"]):
        score += 8
    if any(k in keys for k in ["slot", "fiber", "from_slot", "to_slot", "from_fiber", "to_fiber"]):
        score += 8
    if any(k in keys for k in ["address_pair_source", "columns", "columns_key"]):
        score += 8
    if any(k in keys for k in ["role", "role_pair", "edge_role", "station_role"]):
        score += 8

    return {
        "score": score,
        "target_key_hits": sorted(set(target_hits)),
        "lower_key_hits": sorted(set(lower_hits)),
        "role_token_hits": sorted(set(role_hits)),
        "state_token_hits": sorted(set(state_hits)),
    }


def summarize_file(path):
    data, err = load_json(path)
    rel = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)

    if err:
        return {
            "file": rel,
            "load_error": err,
            "dict_count_scanned": 0,
            "score": 0,
            "key_counts": {},
            "target_key_counts": {},
            "role_token_counts": {},
            "state_token_counts": {},
            "examples": [],
        }

    key_counts = Counter()
    target_key_counts = Counter()
    role_token_counts = Counter()
    state_token_counts = Counter()
    examples = []
    dict_count = 0
    best_score = 0

    for jpath, d in walk_dicts(data):
        dict_count += 1
        for k in d.keys():
            key_counts[str(k)] += 1

        s = score_record(d)
        best_score = max(best_score, s["score"])

        for k in s["target_key_hits"]:
            target_key_counts[k] += 1
        for k in s["role_token_hits"]:
            role_token_counts[k] += 1
        for k in s["state_token_hits"]:
            state_token_counts[k] += 1

        if s["score"] >= 18 and len(examples) < MAX_EXAMPLES_PER_FILE:
            compact = {}
            for k in sorted(d.keys()):
                if k in TARGET_KEYS or str(k) in s["target_key_hits"]:
                    compact[k] = compact_value(d[k])
            if not compact:
                for k in list(d.keys())[:12]:
                    compact[k] = compact_value(d[k])
            examples.append({
                "json_path": jpath,
                "score": s["score"],
                "target_key_hits": s["target_key_hits"],
                "role_token_hits": s["role_token_hits"],
                "state_token_hits": s["state_token_hits"],
                "record": compact,
            })

    return {
        "file": rel,
        "load_error": None,
        "dict_count_scanned": dict_count,
        "score": best_score,
        "key_counts": dict(key_counts.most_common(80)),
        "target_key_counts": dict(target_key_counts.most_common()),
        "role_token_counts": dict(role_token_counts.most_common()),
        "state_token_counts": dict(state_token_counts.most_common()),
        "examples": examples,
    }


def main():
    files = list(iter_json_files())
    summaries = []

    for idx, path in enumerate(files, 1):
        if idx == 1 or idx % 10 == 0:
            print("scanning", idx, "of", len(files))
        summaries.append(summarize_file(path))

    summaries.sort(key=lambda x: (x["score"], sum(x["target_key_counts"].values())), reverse=True)

    promising = [
        s for s in summaries
        if s["score"] >= 18 or s["target_key_counts"] or s["role_token_counts"] or s["state_token_counts"]
    ]

    high_value_key_totals = Counter()
    for s in summaries:
        high_value_key_totals.update(s["target_key_counts"])

    files_with_station_like_fields = [
        s for s in summaries
        if any(k in s["target_key_counts"] for k in [
            "role", "role_pair", "edge_role", "station_role",
            "from_C", "to_C", "slot", "fiber", "A", "B", "C",
            "columns", "address_pair_source",
        ])
    ]

    files_with_state_rows = [
        s for s in summaries
        if s["state_token_counts"]
    ]

    files_with_role_rows = [
        s for s in summaries
        if s["role_token_counts"]
    ]

    has_station_layer = bool(files_with_station_like_fields)
    has_state_layer = bool(files_with_state_rows)
    has_role_layer = bool(files_with_role_rows)

    suggested_next = []
    if has_station_layer:
        suggested_next.append("Build 039 as a station-field scalar provenance audit over the top station-like files.")
    else:
        suggested_next.append("Import or locate the station/provenance artifact before attempting scalar provenance.")

    if has_role_layer:
        suggested_next.append("Join role/role_pair rows to relay/free scalar targets by state or role-pair.")
    else:
        suggested_next.append("Search upstream projects for WXYZTI/shared_B/reverse_partner role rows.")

    if has_state_layer:
        suggested_next.append("Use O0/O1/B0/B1 state rows as the first join key.")
    else:
        suggested_next.append("Add or derive O0/O1/B0/B1 labels for local-cell provenance records.")

    checks = {
        "json_files_scanned": len(files),
        "promising_file_count": len(promising),
        "has_station_like_field_layer": has_station_layer,
        "has_state_token_layer": has_state_layer,
        "has_role_token_layer": has_role_layer,
        "inventory_complete": True,
    }

    result = {
        "status": "station_provenance_inventory_recorded",
        "audit_id": "038",
        "question": "Which available artifacts expose station/register/provenance fields that could explain the scalar laws left open by 037?",
        "checks": checks,
        "high_value_key_totals": dict(high_value_key_totals.most_common()),
        "top_files": promising[:25],
        "files_with_station_like_fields": [s["file"] for s in files_with_station_like_fields[:25]],
        "files_with_state_rows": [s["file"] for s in files_with_state_rows[:25]],
        "files_with_role_rows": [s["file"] for s in files_with_role_rows[:25]],
        "suggested_next": suggested_next,
        "interpretation": (
            "Artifact 037 showed that the scalar laws are not directly explained by thin mediator/C summary features. "
            "This inventory checks whether the current repository contains richer station, lift, role, slot, fiber, column, "
            "or address provenance fields that could support the next scalar-provenance audit."
        ),
        "boundary": (
            "This is an inventory only. It does not prove scalar provenance and does not close Gap A. "
            "If station-like fields are absent, the next step is to import or locate the upstream provenance artifacts."
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
            "dict_count_scanned",
            "target_key_counts",
            "role_token_counts",
            "state_token_counts",
            "example_count",
        ])
        for rank, s in enumerate(promising[:80], 1):
            w.writerow([
                rank,
                s["file"],
                s["score"],
                s["dict_count_scanned"],
                json.dumps(s["target_key_counts"], sort_keys=True),
                json.dumps(s["role_token_counts"], sort_keys=True),
                json.dumps(s["state_token_counts"], sort_keys=True),
                len(s["examples"]),
            ])

    lines = []
    lines.append("# Station provenance inventory 038")
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
    for k, v in list(high_value_key_totals.most_common(30)):
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Top candidate files")
    lines.append("")
    if promising:
        for i, s in enumerate(promising[:15], 1):
            lines.append(str(i) + ". `" + s["file"] + "`")
            lines.append("   - score: `" + str(s["score"]) + "`")
            lines.append("   - target_key_counts: `" + str(s["target_key_counts"]) + "`")
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
    print("promising_file_count", len(promising))
    print("has_station_like_field_layer", has_station_layer)
    print("has_state_token_layer", has_state_layer)
    print("has_role_token_layer", has_role_layer)
    print("top_files")
    for s in promising[:10]:
        print("-", s["score"], s["file"])


if __name__ == "__main__":
    main()
