#!/usr/bin/env python3
import csv
import itertools
import json
from pathlib import Path
from collections import Counter, defaultdict, deque

ROOT = Path(__file__).resolve().parents[1]

IN_064 = ROOT / "artifacts/json/transition_microcell_aggregation_audit_064.v1.json"
IN_065 = ROOT / "artifacts/json/skeptic_boundary_checkpoint_065.v1.json"
SOURCE_JSON = ROOT / "source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/g60_native_overlay_generator_family_search_001.v1.json"

OUT_JSON = ROOT / "artifacts/json/two_by_three_by_four_grid_audit_066.v1.json"
OUT_CSV = ROOT / "artifacts/csv/two_by_three_by_four_grid_audit_066.v1.csv"
OUT_NOTE = ROOT / "notes/two_by_three_by_four_grid_audit_066.md"

TARGET_FORMS = [0, 1, 2, 3]
TARGET_NAMES = ["edge", "hinge", "closed_face", "filled_cell"]

LABEL_TOKENS = [
    "form_index",
    "formindex",
    "form",
    "state",
    "selected",
    "answer",
    "target",
    "label",
    "candidate",
    "rank",
    "completion",
    "c_row",
    "crow",
    "record_index",
    "_record_index",
    "majority_form",
]

REQUIRED_PHRASES = [
    "two-sheet three-channel four-level grid audit",
    "2 x 3 x 4",
    "form_index is used only for evaluation",
    "answer-label leakage remains open",
    "not native closure",
    "not Gap A closure",
    "not full role-labeled shared_B universe",
]

FORBIDDEN_PHRASES = [
    "Gap A is closed",
    "native closure achieved",
    "completion ladder proven natively",
    "answer-label leakage ruled out",
    "full shared_B universe derived",
    "the universe has a belly button",
    "cosmology is derived",
    "ontology is proven",
]


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


def scalar(v):
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        iv = as_int(v)
        return iv if iv is not None else v
    if isinstance(v, str) and 0 < len(v) <= 100:
        iv = as_int(v)
        return iv if iv is not None else v
    return None


def field_is_label_like(name):
    n = str(name).lower()
    return any(tok in n for tok in LABEL_TOKENS)


def flatten(row, prefix=""):
    out = {}
    if not isinstance(row, dict):
        return out
    for k, v in row.items():
        key = prefix + str(k)
        if isinstance(v, dict):
            out.update(flatten(v, key + "."))
        elif isinstance(v, (list, tuple)):
            nums = [as_int(x) for x in v]
            nums = [x for x in nums if x is not None]
            if nums and len(nums) == len(v) and len(nums) <= 50:
                out[key + ".__len"] = len(nums)
                out[key + ".__sum"] = sum(nums)
                out[key + ".__min"] = min(nums)
                out[key + ".__max"] = max(nums)
                out[key + ".__range"] = max(nums) - min(nums)
        else:
            sv = scalar(v)
            if sv is not None:
                out[key] = sv
    return out


def find_edge_records(obj):
    if isinstance(obj, dict):
        if isinstance(obj.get("edge_records"), list):
            xs = obj["edge_records"]
            if all(isinstance(x, dict) for x in xs):
                return xs, ["edge_records"]
        for k, v in obj.items():
            found, path = find_edge_records(v)
            if found is not None:
                return found, [k] + path
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            found, path = find_edge_records(v)
            if found is not None:
                return found, [i] + path
    return None, []


def get_value(features, field):
    if field in features:
        return features[field]
    hits = [v for k, v in features.items() if k.endswith("." + field)]
    if len(hits) == 1:
        return hits[0]
    return None


def row_record(raw, idx):
    features = flatten(raw)

    form_index = as_int(get_value(features, "form_index"))
    if form_index is None:
        form_index = as_int(raw.get("form_index"))

    slot = as_int(get_value(features, "slot_delta_mod15"))
    fiber = as_int(get_value(features, "fiber_delta_mod60"))
    from_c = as_int(get_value(features, "from_C"))
    to_c = as_int(get_value(features, "to_C"))

    if slot is not None and fiber is not None:
        features["derived.boundary_gap_row"] = slot - fiber
        features["derived.inside_captured_row"] = "yes" if slot - fiber > 0 else "no"
        features["derived.boundary_gap_sign"] = "neg" if slot - fiber < 0 else ("zero" if slot - fiber == 0 else "pos")
        features["derived.slot_fiber_pair"] = str(slot) + "|" + str(fiber)

    if from_c is not None and to_c is not None:
        features["derived.C_transition"] = str(from_c) + "->" + str(to_c)
        features["derived.C_transition_rev"] = str(to_c) + "->" + str(from_c)
        features["derived.C_delta_mod15"] = (to_c - from_c) % 15
        for m in [2, 3, 4, 5, 6]:
            features["derived.C_delta_mod15_mod_" + str(m)] = ((to_c - from_c) % 15) % m

    return {
        "row_id": idx,
        "form_index": form_index,
        "features": features,
        "raw": raw,
    }


def share_endpoint_edges(rows, fields):
    buckets = defaultdict(list)
    for i, row in enumerate(rows):
        for f in fields:
            x = get_value(row["features"], f)
            if x is not None:
                buckets[(f, x)].append(i)
    edges = set()
    for ids in buckets.values():
        for a, b in itertools.combinations(ids, 2):
            edges.add(tuple(sorted((a, b))))
    return sorted(edges)


def components(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        if a == b:
            continue
        adj[a].append(b)
        adj[b].append(a)

    seen = [False] * n
    comps = []
    for start in range(n):
        if seen[start]:
            continue
        q = deque([start])
        seen[start] = True
        comp = []
        while q:
            x = q.popleft()
            comp.append(x)
            for y in adj[x]:
                if not seen[y]:
                    seen[y] = True
                    q.append(y)
        comps.append(sorted(comp))
    comps.sort(key=lambda c: (len(c), c[0]))
    return comps


def build_microcells(rows):
    base_edges = share_endpoint_edges(rows, ["from_C", "to_C"])
    base_components = components(len(rows), base_edges)

    base_id_by_row = {}
    for cid, comp in enumerate(base_components):
        for rid in comp:
            base_id_by_row[rid] = cid

    buckets = defaultdict(list)
    for i, row in enumerate(rows):
        base_id = base_id_by_row[i]
        c_delta = get_value(row["features"], "derived.C_delta_mod15")
        buckets[(base_id, c_delta)].append(i)

    microcells = []
    for mid, (key, ids) in enumerate(sorted(buckets.items(), key=lambda kv: (kv[0][0], str(kv[0][1])))):
        forms = [rows[i]["form_index"] for i in ids]
        c = Counter(forms)
        maj, cnt = c.most_common(1)[0]
        microcells.append({
            "microcell_id": mid,
            "base_component_id": key[0],
            "C_delta_mod15": key[1],
            "row_ids": ids,
            "source_record_ids": [rows[i]["row_id"] for i in ids],
            "row_count": len(ids),
            "form_counts": dict(sorted(c.items())),
            "majority_form": maj,
            "majority_count": cnt,
            "pure": cnt == len(ids),
        })
    return base_components, microcells


def collect_candidate_fields(rows):
    fields = set()
    for r in rows:
        fields.update(r["features"].keys())

    out = []
    for f in sorted(fields):
        if field_is_label_like(f):
            continue
        vals = [get_value(r["features"], f) for r in rows]
        if any(v is None for v in vals):
            continue
        uniq = sorted(set(str(v) for v in vals))
        if 2 <= len(uniq) <= 12:
            out.append({
                "field": f,
                "unique_count": len(uniq),
                "unique_values": uniq,
            })
    return out


def form_counts_for_rows(rows, ids):
    c = Counter(rows[i]["form_index"] for i in ids)
    return dict(sorted(c.items()))


def evaluate_sheet_field(rows, microcells, field):
    buckets = defaultdict(list)
    for i, r in enumerate(rows):
        buckets[get_value(r["features"], field)].append(i)

    group_sizes = sorted(len(v) for v in buckets.values())
    form_balanced = all(form_counts_for_rows(rows, ids) == {0: 3, 1: 3, 2: 3, 3: 3} for ids in buckets.values())

    split_all_microcells = True
    for mc in microcells:
        vals = [get_value(rows[i]["features"], field) for i in mc["row_ids"]]
        if len(vals) != 2 or len(set(vals)) != 2:
            split_all_microcells = False
            break

    exact = len(buckets) == 2 and group_sizes == [12, 12] and form_balanced and split_all_microcells

    return {
        "field": field,
        "value_count": len(buckets),
        "group_sizes": group_sizes,
        "form_balanced_3_each": form_balanced,
        "splits_every_microcell_1_plus_1": split_all_microcells,
        "exact_sheet_candidate": exact,
        "groups": [
            {
                "value": str(k),
                "row_count": len(v),
                "form_counts": form_counts_for_rows(rows, v),
            }
            for k, v in sorted(buckets.items(), key=lambda kv: str(kv[0]))
        ],
    }


def evaluate_channel_field(rows, field):
    buckets = defaultdict(list)
    for i, r in enumerate(rows):
        buckets[get_value(r["features"], field)].append(i)

    group_sizes = sorted(len(v) for v in buckets.values())
    form_balanced = all(form_counts_for_rows(rows, ids) == {0: 2, 1: 2, 2: 2, 3: 2} for ids in buckets.values())
    exact = len(buckets) == 3 and group_sizes == [8, 8, 8] and form_balanced

    return {
        "field": field,
        "value_count": len(buckets),
        "group_sizes": group_sizes,
        "form_balanced_2_each": form_balanced,
        "exact_channel_candidate": exact,
        "groups": [
            {
                "value": str(k),
                "row_count": len(v),
                "form_counts": form_counts_for_rows(rows, v),
            }
            for k, v in sorted(buckets.items(), key=lambda kv: str(kv[0]))
        ],
    }


def evaluate_sheet_channel_pair(rows, sheet_field, channel_field):
    buckets = defaultdict(list)
    for i, r in enumerate(rows):
        key = (get_value(r["features"], sheet_field), get_value(r["features"], channel_field))
        buckets[key].append(i)

    group_sizes = sorted(len(v) for v in buckets.values())
    each_has_one_per_level = all(form_counts_for_rows(rows, ids) == {0: 1, 1: 1, 2: 1, 3: 1} for ids in buckets.values())
    exact = len(buckets) == 6 and group_sizes == [4, 4, 4, 4, 4, 4] and each_has_one_per_level

    return {
        "sheet_field": sheet_field,
        "channel_field": channel_field,
        "value_count": len(buckets),
        "group_sizes": group_sizes,
        "each_sheet_channel_has_one_per_level": each_has_one_per_level,
        "exact_sheet_channel_grid": exact,
    }


def microcell_feature_map(mc):
    feats = {
        "base_component_id": mc["base_component_id"],
        "C_delta_mod15": mc["C_delta_mod15"],
    }
    c = as_int(mc["C_delta_mod15"])
    b = as_int(mc["base_component_id"])
    if c is not None:
        for m in [2, 3, 4, 5, 6]:
            feats["C_delta_mod15_mod_" + str(m)] = c % m
    if b is not None:
        for m in [2, 3, 4, 5, 6]:
            feats["base_component_id_mod_" + str(m)] = b % m
    if c is not None and b is not None:
        feats["base_plus_C_delta_mod3"] = (b + c) % 3
        feats["base_plus_C_delta_mod4"] = (b + c) % 4
        feats["base_minus_C_delta_mod3"] = (b - c) % 3
        feats["base_minus_C_delta_mod4"] = (b - c) % 4
    return feats


def evaluate_microcell_channel(microcells, field, feature_maps):
    buckets = defaultdict(list)
    for mc in microcells:
        buckets[feature_maps[mc["microcell_id"]].get(field)].append(mc)

    if None in buckets:
        return None

    sizes = sorted(len(v) for v in buckets.values())
    balanced = True
    for cells in buckets.values():
        counts = Counter(mc["majority_form"] for mc in cells)
        if dict(sorted(counts.items())) != {0: 1, 1: 1, 2: 1, 3: 1}:
            balanced = False

    exact = len(buckets) == 3 and sizes == [4, 4, 4] and balanced

    return {
        "field": field,
        "value_count": len(buckets),
        "group_sizes": sizes,
        "one_microcell_per_level": balanced,
        "exact_microcell_channel_candidate": exact,
        "groups": [
            {
                "value": str(k),
                "microcell_count": len(v),
                "levels": dict(sorted(Counter(mc["majority_form"] for mc in v).items())),
            }
            for k, v in sorted(buckets.items(), key=lambda kv: str(kv[0]))
        ],
    }


def phrase_missing(text, phrases):
    return [p for p in phrases if p not in text]


def phrase_found(text, phrases):
    return [p for p in phrases if p in text]


def main():
    a064 = load_json(IN_064)
    a065 = load_json(IN_065)
    source = load_json(SOURCE_JSON)

    if not a064.get("audit_pass"):
        raise SystemExit("064 audit_pass is not true")
    if not a065.get("audit_pass"):
        raise SystemExit("065 audit_pass is not true")

    edge_records, edge_path = find_edge_records(source)
    if not edge_records:
        raise SystemExit("edge_records not found")

    all_rows = [row_record(raw, idx) for idx, raw in enumerate(edge_records)]
    rows = [
        r for r in all_rows
        if r["form_index"] in TARGET_FORMS
        and get_value(r["features"], "slot_delta_mod15") is not None
        and get_value(r["features"], "fiber_delta_mod60") is not None
    ]

    base_components, microcells = build_microcells(rows)

    candidates = collect_candidate_fields(rows)

    sheet_tests = []
    channel_tests = []
    for item in candidates:
        field = item["field"]
        if item["unique_count"] == 2:
            sheet_tests.append(evaluate_sheet_field(rows, microcells, field))
        if item["unique_count"] == 3:
            channel_tests.append(evaluate_channel_field(rows, field))

    sheet_hits = [x for x in sheet_tests if x["exact_sheet_candidate"]]
    channel_hits = [x for x in channel_tests if x["exact_channel_candidate"]]

    grid_pair_tests = []
    for s in sheet_hits:
        for c in channel_hits:
            grid_pair_tests.append(evaluate_sheet_channel_pair(rows, s["field"], c["field"]))
    grid_pair_hits = [x for x in grid_pair_tests if x["exact_sheet_channel_grid"]]

    feature_maps = {mc["microcell_id"]: microcell_feature_map(mc) for mc in microcells}
    mc_fields = sorted({k for fm in feature_maps.values() for k in fm.keys()})
    mc_channel_tests = []
    for field in mc_fields:
        ev = evaluate_microcell_channel(microcells, field, feature_maps)
        if ev is not None:
            mc_channel_tests.append(ev)

    mc_channel_hits = [x for x in mc_channel_tests if x["exact_microcell_channel_candidate"]]

    all_microcells_pure = all(mc["pure"] for mc in microcells)
    all_microcells_two_rows = all(mc["row_count"] == 2 for mc in microcells)
    microcells_per_level = dict(sorted(Counter(mc["majority_form"] for mc in microcells).items()))

    if grid_pair_hits:
        verdict = "two_sheet_three_channel_four_level_grid_candidate_found"
    elif sheet_hits or channel_hits or mc_channel_hits:
        verdict = "partial_two_by_three_by_four_grid_signal_found"
    else:
        verdict = "two_by_three_by_four_grid_not_confirmed_in_tested_family"

    statement = (
        "Artifact 066 is a two-sheet three-channel four-level grid audit. It tests the 2 x 3 x 4 reading of the 24-row local register. "
        "form_index is used only for evaluation."
    )

    boundary = (
        "This is a finite local grid audit, not native closure. A hit would be a candidate requiring validation; a miss would only bound the tested grid family. "
        "answer-label leakage remains open, this is not full role-labeled shared_B universe, and is not Gap A closure."
    )

    combined = statement + "\n" + boundary
    missing = phrase_missing(combined, REQUIRED_PHRASES)
    forbidden = phrase_found(combined, FORBIDDEN_PHRASES)

    checks = {
        "transition_microcell_aggregation_064_pass": bool(a064.get("audit_pass")),
        "skeptic_boundary_checkpoint_065_pass": bool(a065.get("audit_pass")),
        "source_json_exists": SOURCE_JSON.exists(),
        "edge_records_found": bool(edge_records),
        "row_count_is_24": len(rows) == 24,
        "base_component_count": len(base_components),
        "microcell_count_is_12": len(microcells) == 12,
        "all_microcells_are_form_pure": all_microcells_pure,
        "all_microcells_have_two_rows": all_microcells_two_rows,
        "microcells_per_level_is_3_each": microcells_per_level == {0: 3, 1: 3, 2: 3, 3: 3},
        "candidate_row_field_count": len(candidates),
        "sheet_candidate_hit_count": len(sheet_hits),
        "channel_candidate_hit_count": len(channel_hits),
        "sheet_channel_grid_hit_count": len(grid_pair_hits),
        "microcell_channel_hit_count": len(mc_channel_hits),
        "form_index_used_only_for_evaluation": True,
        "answer_label_leakage_remains_open": True,
        "native_provenance_confirmed": False,
        "required_phrases_present": len(missing) == 0,
        "forbidden_phrases_absent": len(forbidden) == 0,
    }

    audit_pass = all([
        checks["transition_microcell_aggregation_064_pass"],
        checks["skeptic_boundary_checkpoint_065_pass"],
        checks["source_json_exists"],
        checks["edge_records_found"],
        checks["row_count_is_24"],
        checks["microcell_count_is_12"],
        checks["all_microcells_are_form_pure"],
        checks["all_microcells_have_two_rows"],
        checks["microcells_per_level_is_3_each"],
        checks["form_index_used_only_for_evaluation"],
        checks["answer_label_leakage_remains_open"],
        checks["required_phrases_present"],
        checks["forbidden_phrases_absent"],
    ])

    result = {
        "status": "two_by_three_by_four_grid_audit_recorded",
        "audit_id": "066",
        "audit_pass": audit_pass,
        "verdict": verdict,
        "inputs": {
            "transition_microcell_aggregation_audit_064": str(IN_064),
            "skeptic_boundary_checkpoint_065": str(IN_065),
            "source_json": str(SOURCE_JSON),
            "edge_records_path": edge_path,
        },
        "checks": checks,
        "base_component_sizes": [len(c) for c in base_components],
        "microcells": microcells,
        "sheet_hits": sheet_hits,
        "channel_hits": channel_hits,
        "sheet_channel_grid_hits": grid_pair_hits,
        "microcell_channel_hits": mc_channel_hits,
        "top_sheet_tests": sheet_tests[:30],
        "top_channel_tests": channel_tests[:30],
        "top_microcell_channel_tests": mc_channel_tests[:40],
        "statement": statement,
        "boundary": boundary,
        "missing_required_phrases": missing,
        "forbidden_phrases_found": forbidden,
        "interpretation": (
            "Artifact 066 tests whether the visible register should be read as two sheets, three channels, and four levels. "
            "The strongest already-locked support is that 12 form-pure microcells exist and distribute three per level. "
            "The audit asks whether native fields supply the two-sheet and three-channel coordinates."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["class", "field_a", "field_b", "exact", "details"])
        for x in sheet_hits:
            w.writerow(["sheet_hit", x["field"], "", x["exact_sheet_candidate"], json.dumps(x["groups"], sort_keys=True)])
        for x in channel_hits:
            w.writerow(["channel_hit", x["field"], "", x["exact_channel_candidate"], json.dumps(x["groups"], sort_keys=True)])
        for x in grid_pair_hits:
            w.writerow(["sheet_channel_grid_hit", x["sheet_field"], x["channel_field"], x["exact_sheet_channel_grid"], json.dumps(x, sort_keys=True)])
        for x in mc_channel_hits:
            w.writerow(["microcell_channel_hit", x["field"], "", x["exact_microcell_channel_candidate"], json.dumps(x["groups"], sort_keys=True)])

    lines = []
    lines.append("# Two-sheet three-channel four-level grid audit 066")
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
    lines.append("## Statement")
    lines.append("")
    lines.append(statement)
    lines.append("")
    lines.append("## Microcell support")
    lines.append("")
    lines.append("- base_component_sizes: `" + str(result["base_component_sizes"]) + "`")
    lines.append("- microcells_per_level: `" + str(microcells_per_level) + "`")
    lines.append("- all_microcells_are_form_pure: `" + str(all_microcells_pure) + "`")
    lines.append("- all_microcells_have_two_rows: `" + str(all_microcells_two_rows) + "`")
    lines.append("")
    lines.append("## Sheet hits")
    lines.append("")
    if sheet_hits:
        for x in sheet_hits:
            lines.append("- " + x["field"] + ": sizes=" + str(x["group_sizes"]) + ", splits_microcells=" + str(x["splits_every_microcell_1_plus_1"]))
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Channel hits")
    lines.append("")
    if channel_hits:
        for x in channel_hits:
            lines.append("- " + x["field"] + ": sizes=" + str(x["group_sizes"]))
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Sheet-channel grid hits")
    lines.append("")
    if grid_pair_hits:
        for x in grid_pair_hits:
            lines.append("- sheet=" + x["sheet_field"] + ", channel=" + x["channel_field"])
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Microcell channel hits")
    lines.append("")
    if mc_channel_hits:
        for x in mc_channel_hits:
            lines.append("- " + x["field"] + ": sizes=" + str(x["group_sizes"]))
    else:
        lines.append("- none")
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
    print("audit_pass", audit_pass)
    print("verdict", verdict)
    for k, v in checks.items():
        print(k, v)
    print("microcells_per_level", microcells_per_level)
    print("sheet_hits_first", [x["field"] for x in sheet_hits[:10]])
    print("channel_hits_first", [x["field"] for x in channel_hits[:10]])
    print("sheet_channel_grid_hits_first", [(x["sheet_field"], x["channel_field"]) for x in grid_pair_hits[:10]])
    print("microcell_channel_hits_first", [x["field"] for x in mc_channel_hits[:10]])


if __name__ == "__main__":
    main()
