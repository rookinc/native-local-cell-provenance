#!/usr/bin/env python3
import csv
import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]

IN_054 = ROOT / "artifacts/json/completion_ladder_native_source_probe_054.v1.json"
SOURCE_JSON = ROOT / "source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/g60_native_overlay_generator_family_search_001.v1.json"

OUT_JSON = ROOT / "artifacts/json/form_index_provenance_audit_055.v1.json"
OUT_CSV = ROOT / "artifacts/csv/form_index_provenance_audit_055.v1.csv"
OUT_NOTE = ROOT / "notes/form_index_provenance_audit_055.md"

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
]

NATIVE_PREFERRED_TOKENS = [
    "from_",
    "to_",
    "delta",
    "role",
    "slot",
    "fiber",
    "lift",
    "q",
    "A",
    "B",
    "C",
    "station",
    "edge",
    "local",
    "source",
    "column",
    "pair",
]

COEFFS = list(range(-12, 13))
OFFSETS = list(range(-60, 61))
TOP_N = 40

REQUIRED_PHRASES = [
    "form_index provenance audit",
    "answer-label leakage",
    "candidate source",
    "not native closure",
    "not Gap A closure",
    "not full role-labeled shared_B universe",
]

FORBIDDEN_PHRASES = [
    "Gap A is closed",
    "native closure achieved",
    "form_index is proven native",
    "answer-label leakage ruled out",
    "full shared_B universe derived",
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


def field_is_label_like(name):
    n = str(name).lower()
    return any(tok.lower() in n for tok in LABEL_TOKENS)


def field_is_native_like(name):
    n = str(name)
    return any(tok in n for tok in NATIVE_PREFERRED_TOKENS)


def flatten_scalars(row, prefix=""):
    out = {}
    if not isinstance(row, dict):
        return out

    for k, v in row.items():
        key = prefix + str(k)
        if isinstance(v, dict):
            out.update(flatten_scalars(v, key + "."))
        elif isinstance(v, (list, tuple)):
            # Keep only short numeric lists as aggregate candidates.
            nums = [as_int(x) for x in v]
            nums = [x for x in nums if x is not None]
            if nums and len(nums) == len(v) and len(nums) <= 20:
                out[key + ".__len"] = len(nums)
                out[key + ".__sum"] = sum(nums)
                out[key + ".__min"] = min(nums)
                out[key + ".__max"] = max(nums)
                out[key + ".__range"] = max(nums) - min(nums)
        else:
            iv = as_int(v)
            if iv is not None:
                out[key] = iv
            elif isinstance(v, str):
                out[key] = v

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
        if obj and all(isinstance(x, dict) for x in obj):
            if any("form_index" in x for x in obj):
                return obj, []
        for i, v in enumerate(obj):
            found, path = find_edge_records(v)
            if found is not None:
                return found, [i] + path
    return None, []


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


def affine_hits(feature_values, target_values):
    hits = []
    near = []

    x = feature_values
    y = target_values

    direct_err = sum(abs(x[k] - y[k]) for k in y)
    if direct_err == 0:
        hits.append({
            "match_kind": "direct",
            "a": 1,
            "c": 0,
            "l1_error": 0,
            "predicted": dict(x),
        })
    else:
        near.append({
            "match_kind": "direct",
            "a": 1,
            "c": 0,
            "l1_error": direct_err,
            "predicted": dict(x),
        })

    for a in COEFFS:
        if a == 0:
            continue
        needed = [y[k] - a * x[k] for k in y]
        counts = Counter(needed)
        c, _ = counts.most_common(1)[0]
        if c not in OFFSETS:
            continue

        pred = {k: a * x[k] + c for k in y}
        err = sum(abs(pred[k] - y[k]) for k in y)
        item = {
            "match_kind": "affine",
            "a": a,
            "c": c,
            "l1_error": err,
            "predicted": pred,
        }
        if err == 0:
            hits.append(item)
        else:
            near.append(item)

    hits.sort(key=lambda z: (abs(z["a"]) + abs(z["c"]), z["match_kind"]))
    near.sort(key=lambda z: (z["l1_error"], abs(z["a"]) + abs(z["c"]), z["match_kind"]))
    return hits, near


def order_hits(feature_values, target_values):
    xs = feature_values
    ys = target_values

    if len(set(xs.values())) != len(xs):
        return []

    ordered_keys_asc = [k for k, _ in sorted(xs.items(), key=lambda kv: (kv[1], kv[0]))]
    ordered_keys_desc = [k for k, _ in sorted(xs.items(), key=lambda kv: (-kv[1], kv[0]))]

    target_order = [k for k, _ in sorted(ys.items(), key=lambda kv: (kv[1], kv[0]))]

    hits = []
    if ordered_keys_asc == target_order:
        hits.append({
            "order_kind": "ascending_rank_matches_form_index",
            "ordered_form_indices": ordered_keys_asc,
            "feature_values": dict(xs),
        })
    if ordered_keys_desc == target_order:
        hits.append({
            "order_kind": "descending_rank_matches_form_index",
            "ordered_form_indices": ordered_keys_desc,
            "feature_values": dict(xs),
        })
    return hits


def signature_for_rows(rows, allowed_fields):
    parts = []
    for field in sorted(allowed_fields):
        vals = []
        for row in rows:
            scalars = flatten_scalars(row)
            if field in scalars:
                vals.append(scalars[field])
        vals = sorted(set(str(v) for v in vals))
        if vals:
            parts.append(field + "=" + ",".join(vals))
    return "|".join(parts)


def missing_phrases(text, phrases):
    return [p for p in phrases if p not in text]


def found_phrases(text, phrases):
    return [p for p in phrases if p in text]


def main():
    a054 = load_json(IN_054)
    source = load_json(SOURCE_JSON)

    if not a054.get("probe_pass"):
        raise SystemExit("054 probe_pass is not true")

    edge_records, edge_path = find_edge_records(source)
    if not edge_records:
        raise SystemExit("could not locate edge_records with form_index")

    rows_with_form = []
    for idx, row in enumerate(edge_records):
        fi = as_int(row.get("form_index"))
        if fi is not None:
            rr = dict(row)
            rr["_record_index"] = idx
            rows_with_form.append(rr)

    groups = defaultdict(list)
    for row in rows_with_form:
        groups[as_int(row.get("form_index"))].append(row)

    form_indices = sorted(groups.keys())
    target_form_index = {fi: fi for fi in form_indices}
    target_completion_level = {fi: fi + 2 for fi in form_indices}

    all_fields = set()
    label_like_fields = set()
    non_label_fields = set()
    native_like_fields = set()

    for row in rows_with_form:
        for k in flatten_scalars(row).keys():
            all_fields.add(k)
            if field_is_label_like(k):
                label_like_fields.add(k)
            else:
                non_label_fields.add(k)
                if field_is_native_like(k):
                    native_like_fields.add(k)

    group_features = {}
    for field in sorted(non_label_fields):
        values_by_group = {}
        ok = True
        for fi in form_indices:
            vals = []
            for row in groups[fi]:
                scalars = flatten_scalars(row)
                if field in scalars:
                    vals.append(scalars[field])
            st = stats(vals)
            if not st:
                ok = False
                break
            for stat_name, stat_val in st.items():
                feature = field + "__" + stat_name
                group_features.setdefault(feature, {})[fi] = stat_val
        if not ok:
            continue

    # Remove incomplete features.
    group_features = {
        k: v for k, v in group_features.items()
        if set(v.keys()) == set(form_indices)
    }

    exact_form_hits = []
    near_form_hits = []
    exact_completion_hits = []
    order_source_hits = []

    for feature, vals in group_features.items():
        hits, near = affine_hits(vals, target_form_index)
        for h in hits:
            exact_form_hits.append({
                "feature": feature,
                "feature_values": vals,
                **h,
                "native_like": field_is_native_like(feature),
                "label_like": field_is_label_like(feature),
            })
        for h in near[:2]:
            near_form_hits.append({
                "feature": feature,
                "feature_values": vals,
                **h,
                "native_like": field_is_native_like(feature),
                "label_like": field_is_label_like(feature),
            })

        hits2, _near2 = affine_hits(vals, target_completion_level)
        for h in hits2:
            exact_completion_hits.append({
                "feature": feature,
                "feature_values": vals,
                **h,
                "native_like": field_is_native_like(feature),
                "label_like": field_is_label_like(feature),
            })

        for oh in order_hits(vals, target_form_index):
            order_source_hits.append({
                "feature": feature,
                "native_like": field_is_native_like(feature),
                "label_like": field_is_label_like(feature),
                **oh,
            })

    def sort_hit(x):
        return (
            not x.get("native_like", False),
            abs(x.get("a", 0)) + abs(x.get("c", 0)),
            len(x.get("feature", "")),
            x.get("feature", ""),
        )

    exact_form_hits.sort(key=sort_hit)
    exact_completion_hits.sort(key=sort_hit)
    near_form_hits.sort(key=lambda x: (x["l1_error"], not x.get("native_like", False), len(x["feature"]), x["feature"]))
    order_source_hits.sort(key=lambda x: (not x.get("native_like", False), len(x["feature"]), x["feature"]))

    # Record-order risk.
    record_sequence = [as_int(row.get("form_index")) for row in rows_with_form]
    first_occurrence_order = []
    for fi in record_sequence:
        if fi not in first_occurrence_order:
            first_occurrence_order.append(fi)

    contiguous_blocks = []
    last = None
    for fi in record_sequence:
        if fi != last:
            contiguous_blocks.append(fi)
            last = fi

    form_index_equals_first_occurrence_order = first_occurrence_order == form_indices
    form_index_blocks_are_contiguous = contiguous_blocks == form_indices

    # Signature uniqueness without label fields.
    signature_fields = sorted(native_like_fields)[:80]
    signatures = {
        fi: signature_for_rows(groups[fi], signature_fields)
        for fi in form_indices
    }
    unique_native_signatures = len(set(signatures.values())) == len(signatures)

    label_like_present = sorted(label_like_fields)
    native_like_present = sorted(native_like_fields)

    independent_exact_hits = [h for h in exact_form_hits if not h["label_like"]]
    independent_order_hits = [h for h in order_source_hits if not h["label_like"]]

    candidate_source_found = bool(independent_exact_hits or independent_order_hits or unique_native_signatures)

    # This audit is intentionally conservative. Candidate source is not proof.
    native_provenance_confirmed = False
    answer_label_leakage_ruled_out = False

    if candidate_source_found and not form_index_blocks_are_contiguous:
        verdict = "form_index_has_independent_candidates_but_needs_validation"
    elif candidate_source_found and form_index_blocks_are_contiguous:
        verdict = "form_index_has_candidates_but_order_label_leakage_risk"
    else:
        verdict = "form_index_provenance_unresolved_label_like"

    statement = (
        "Artifact 055 is a form_index provenance audit. It checks whether the upstream form_index candidate from 054 has independent support "
        "from non-label edge_record fields, while explicitly preserving answer-label leakage as an unresolved risk."
    )

    boundary = (
        "This audit may find a candidate source, but it is not native closure. It does not prove form_index is native, "
        "does not rule out answer-label leakage, is not full role-labeled shared_B universe derivation, and is not Gap A closure."
    )

    combined = statement + "\n" + boundary
    missing = missing_phrases(combined, REQUIRED_PHRASES)
    forbidden = found_phrases(combined, FORBIDDEN_PHRASES)

    checks = {
        "probe_054_pass": bool(a054.get("probe_pass")),
        "source_json_exists": SOURCE_JSON.exists(),
        "edge_records_found": bool(edge_records),
        "rows_with_form_index_count": len(rows_with_form),
        "form_indices_are_0_1_2_3": form_indices == [0, 1, 2, 3],
        "form_index_group_count_is_4": len(form_indices) == 4,
        "form_index_group_sizes": {str(k): len(v) for k, v in groups.items()},
        "form_index_equals_first_occurrence_order": form_index_equals_first_occurrence_order,
        "form_index_blocks_are_contiguous": form_index_blocks_are_contiguous,
        "label_like_field_count": len(label_like_present),
        "non_label_field_count": len(non_label_fields),
        "native_like_field_count": len(native_like_present),
        "non_label_group_feature_count": len(group_features),
        "independent_exact_form_index_hit_count": len(independent_exact_hits),
        "independent_order_hit_count": len(independent_order_hits),
        "unique_native_signatures_by_form": unique_native_signatures,
        "candidate_source_found": candidate_source_found,
        "native_provenance_confirmed": native_provenance_confirmed,
        "answer_label_leakage_ruled_out": answer_label_leakage_ruled_out,
        "required_phrases_present": len(missing) == 0,
        "forbidden_phrases_absent": len(forbidden) == 0,
    }

    audit_pass = all([
        checks["probe_054_pass"],
        checks["source_json_exists"],
        checks["edge_records_found"],
        checks["form_indices_are_0_1_2_3"],
        checks["form_index_group_count_is_4"],
        checks["required_phrases_present"],
        checks["forbidden_phrases_absent"],
    ])

    result = {
        "status": "form_index_provenance_audit_recorded",
        "audit_id": "055",
        "inputs": {
            "completion_ladder_native_source_probe_054": str(IN_054),
            "source_json": str(SOURCE_JSON),
            "edge_records_path": edge_path,
        },
        "checks": checks,
        "audit_pass": audit_pass,
        "verdict": verdict,
        "statement": statement,
        "boundary": boundary,
        "form_indices": form_indices,
        "record_order": {
            "first_occurrence_order": first_occurrence_order,
            "contiguous_blocks": contiguous_blocks,
            "first_40_form_index_sequence": record_sequence[:40],
        },
        "field_inventory": {
            "label_like_fields": label_like_present,
            "native_like_fields_first_80": native_like_present[:80],
            "non_label_fields_first_80": sorted(non_label_fields)[:80],
        },
        "candidate_results": {
            "exact_form_index_hits_first": exact_form_hits[:TOP_N],
            "exact_completion_level_hits_first": exact_completion_hits[:TOP_N],
            "near_form_index_hits_first": near_form_hits[:TOP_N],
            "order_source_hits_first": order_source_hits[:TOP_N],
            "native_signatures_unique": unique_native_signatures,
            "native_signatures_by_form": signatures,
        },
        "interpretation": (
            "Artifact 054 found form_index as a candidate source for c_row and completion_level. "
            "Artifact 055 audits whether that field has independent support or whether it may be an answer-order label. "
            "Because answer-label leakage is not ruled out here, form_index remains a candidate source, not native provenance closure."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "kind",
            "feature",
            "native_like",
            "match_kind",
            "a",
            "c",
            "l1_error",
            "feature_values",
            "predicted",
        ])
        for kind, items in [
            ("exact_form_index", exact_form_hits[:TOP_N]),
            ("exact_completion_level", exact_completion_hits[:TOP_N]),
            ("near_form_index", near_form_hits[:TOP_N]),
            ("order_source", order_source_hits[:TOP_N]),
        ]:
            for item in items:
                w.writerow([
                    kind,
                    item.get("feature"),
                    item.get("native_like"),
                    item.get("match_kind", item.get("order_kind")),
                    item.get("a"),
                    item.get("c"),
                    item.get("l1_error", 0),
                    json.dumps(item.get("feature_values"), sort_keys=True),
                    json.dumps(item.get("predicted"), sort_keys=True),
                ])

    lines = []
    lines.append("# Form index provenance audit 055")
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
    lines.append("## Source under audit")
    lines.append("")
    lines.append("- source_json: `" + str(SOURCE_JSON.relative_to(ROOT)) + "`")
    lines.append("- edge_records_path: `" + str(edge_path) + "`")
    lines.append("")
    lines.append("## Record-order leakage checks")
    lines.append("")
    lines.append("- first_occurrence_order: `" + str(first_occurrence_order) + "`")
    lines.append("- contiguous_blocks: `" + str(contiguous_blocks) + "`")
    lines.append("- first_40_form_index_sequence: `" + str(record_sequence[:40]) + "`")
    lines.append("")
    lines.append("## Candidate source checks")
    lines.append("")
    lines.append("- independent_exact_form_index_hit_count: `" + str(len(independent_exact_hits)) + "`")
    lines.append("- independent_order_hit_count: `" + str(len(independent_order_hits)) + "`")
    lines.append("- unique_native_signatures_by_form: `" + str(unique_native_signatures) + "`")
    lines.append("- native_provenance_confirmed: `" + str(native_provenance_confirmed) + "`")
    lines.append("- answer_label_leakage_ruled_out: `" + str(answer_label_leakage_ruled_out) + "`")
    lines.append("")
    lines.append("## Exact form-index hits, first 10")
    lines.append("")
    lines.append("`" + str(exact_form_hits[:10]) + "`")
    lines.append("")
    lines.append("## Order-source hits, first 10")
    lines.append("")
    lines.append("`" + str(order_source_hits[:10]) + "`")
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
    print("first_occurrence_order", first_occurrence_order)
    print("contiguous_blocks", contiguous_blocks)
    print("exact_form_hits_first", exact_form_hits[:5])
    print("order_hits_first", order_source_hits[:5])


if __name__ == "__main__":
    main()
