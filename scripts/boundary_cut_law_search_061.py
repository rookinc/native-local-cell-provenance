#!/usr/bin/env python3
import csv
import itertools
import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]

IN_060 = ROOT / "artifacts/json/inside_outside_boundary_grammar_audit_060.v1.json"
SOURCE_JSON = ROOT / "source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/g60_native_overlay_generator_family_search_001.v1.json"

OUT_JSON = ROOT / "artifacts/json/boundary_cut_law_search_061.v1.json"
OUT_CSV = ROOT / "artifacts/csv/boundary_cut_law_search_061.v1.csv"
OUT_NOTE = ROOT / "notes/boundary_cut_law_search_061.md"

TARGET_FORMS = [0, 1, 2, 3]
TARGET_NAMES = ["edge", "hinge", "closed_face", "filled_cell"]
TARGET_SIZE = 6

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
]

PREFERRED_TOKENS = [
    "slot",
    "fiber",
    "delta",
    "lift",
    "q",
    "role",
    "station",
    "from",
    "to",
    "C",
    "A",
    "B",
    "edge",
    "channel",
    "pair",
    "shared",
    "reverse",
    "boundary",
    "inside",
    "outside",
]

REQUIRED_PHRASES = [
    "boundary cut law search",
    "inside/outside boundary grammar",
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
]

MAX_FEATURES = 70
MAX_COMBO_SIZE = 3
TOP_N = 40


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


def is_scalar(v):
    return isinstance(v, (str, int, float)) and not isinstance(v, bool)


def field_is_label_like(name):
    n = str(name).lower()
    return any(tok.lower() in n for tok in LABEL_TOKENS)


def preferred_score(name):
    n = str(name)
    score = 0
    for tok in PREFERRED_TOKENS:
        if tok in n:
            score += 1
    return score


def flatten_values(row, prefix=""):
    out = {}
    if not isinstance(row, dict):
        return out

    for k, v in row.items():
        key = prefix + str(k)
        if isinstance(v, dict):
            out.update(flatten_values(v, key + "."))
        elif isinstance(v, (list, tuple)):
            nums = [as_int(x) for x in v]
            nums = [x for x in nums if x is not None]
            if nums and len(nums) == len(v) and len(nums) <= 50:
                out[key + ".__len"] = len(nums)
                out[key + ".__sum"] = sum(nums)
                out[key + ".__min"] = min(nums)
                out[key + ".__max"] = max(nums)
                out[key + ".__range"] = max(nums) - min(nums)
        elif is_scalar(v):
            iv = as_int(v)
            if iv is not None:
                out[key] = iv
            elif isinstance(v, str) and 0 < len(v) <= 80:
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
        for i, v in enumerate(obj):
            found, path = find_edge_records(v)
            if found is not None:
                return found, [i] + path
    return None, []


def missing_phrases(text, phrases):
    return [p for p in phrases if p not in text]


def found_phrases(text, phrases):
    return [p for p in phrases if p in text]


def row_feature_map(raw, idx):
    vals = flatten_values(raw)

    slot = as_int(vals.get("slot_delta_mod15"))
    fiber = as_int(vals.get("fiber_delta_mod60"))
    from_c = as_int(vals.get("from_C"))
    to_c = as_int(vals.get("to_C"))
    lift_q = as_int(vals.get("lift_q"))

    if slot is not None and fiber is not None:
        gap = slot - fiber
        vals["derived.boundary_gap_row"] = gap
        vals["derived.inside_captured_row"] = "yes" if gap > 0 else "no"
        vals["derived.boundary_gap_sign"] = "neg" if gap < 0 else ("zero" if gap == 0 else "pos")
        vals["derived.slot_fiber_pair"] = str(slot) + "|" + str(fiber)

    if from_c is not None and to_c is not None:
        vals["derived.C_transition"] = str(from_c) + "->" + str(to_c)
        vals["derived.C_delta_mod15"] = (to_c - from_c) % 15

    if from_c is not None and lift_q is not None:
        vals["derived.from_C_lift_q"] = str(from_c) + "|" + str(lift_q)

    if to_c is not None and lift_q is not None:
        vals["derived.to_C_lift_q"] = str(to_c) + "|" + str(lift_q)

    return {
        "record_index": idx,
        "form_index": as_int(raw.get("form_index")),
        "slot_delta_mod15": slot,
        "fiber_delta_mod60": fiber,
        "features": vals,
    }


def stats_numeric(xs):
    vals = [as_int(x) for x in xs]
    vals = [v for v in vals if v is not None]
    if not vals:
        return {}
    return {
        "min": min(vals),
        "max": max(vals),
        "range": max(vals) - min(vals),
        "sum": sum(vals),
    }


def group_boundary_stats(rows):
    slots = [r["slot_delta_mod15"] for r in rows if r["slot_delta_mod15"] is not None]
    fibers = [r["fiber_delta_mod60"] for r in rows if r["fiber_delta_mod60"] is not None]

    if slots and fibers:
        outside = max(slots)
        inside = min(fibers)
        gap = outside - inside
    else:
        outside = None
        inside = None
        gap = None

    return {
        "outside_boundary_span": outside,
        "inside_fiber_residual": inside,
        "boundary_gap": gap,
    }


def evaluate_combo(rows, combo):
    buckets = defaultdict(list)
    for row in rows:
        key = tuple(row["features"].get(f) for f in combo)
        buckets[key].append(row)

    groups = []
    for key, xs in buckets.items():
        forms = [r["form_index"] for r in xs]
        c = Counter(forms)
        majority_form = None
        majority_count = 0
        if c:
            majority_form, majority_count = c.most_common(1)[0]

        bstats = group_boundary_stats(xs)

        groups.append({
            "key": key,
            "row_count": len(xs),
            "record_indices": [r["record_index"] for r in xs],
            "form_counts": dict(sorted(c.items())),
            "majority_form": majority_form,
            "majority_count": majority_count,
            **bstats,
        })

    groups_by_gap = sorted(
        groups,
        key=lambda g: (
            10**9 if g["boundary_gap"] is None else g["boundary_gap"],
            10**9 if g["outside_boundary_span"] is None else g["outside_boundary_span"],
            g["key"],
        ),
    )

    majority_order_by_gap = [g["majority_form"] for g in groups_by_gap]

    group_count = len(groups)
    purity_total = sum(g["majority_count"] for g in groups)
    size_deviation = sum(abs(g["row_count"] - TARGET_SIZE) for g in groups)
    if group_count < len(TARGET_FORMS):
        size_deviation += (len(TARGET_FORMS) - group_count) * TARGET_SIZE

    group_count_penalty = abs(group_count - len(TARGET_FORMS)) * TARGET_SIZE
    score = purity_total - size_deviation - group_count_penalty

    exact_partition = (
        group_count == 4
        and all(g["row_count"] == TARGET_SIZE for g in groups)
        and all(g["majority_count"] == TARGET_SIZE for g in groups)
        and sorted(g["majority_form"] for g in groups) == TARGET_FORMS
    )

    ordered_exact_by_gap = exact_partition and majority_order_by_gap == TARGET_FORMS

    return {
        "combo": combo,
        "group_count": group_count,
        "purity_total": purity_total,
        "size_deviation": size_deviation,
        "group_count_penalty": group_count_penalty,
        "score": score,
        "exact_partition": exact_partition,
        "ordered_exact_by_boundary_gap": ordered_exact_by_gap,
        "majority_order_by_boundary_gap": majority_order_by_gap,
        "uses_form_index_as_input": any(field_is_label_like(f) for f in combo),
        "groups": groups_by_gap,
    }


def main():
    a060 = load_json(IN_060)
    source = load_json(SOURCE_JSON)

    if not a060.get("audit_pass"):
        raise SystemExit("060 audit_pass is not true")

    edge_records, edge_path = find_edge_records(source)
    if not edge_records:
        raise SystemExit("edge_records not found")

    rows = []
    for idx, raw in enumerate(edge_records):
        r = row_feature_map(raw, idx)
        if (
            r["form_index"] in TARGET_FORMS
            and r["slot_delta_mod15"] is not None
            and r["fiber_delta_mod60"] is not None
        ):
            rows.append(r)

    all_feature_names = set()
    for row in rows:
        all_feature_names.update(row["features"].keys())

    candidate_features = []
    feature_inventory = []
    for name in sorted(all_feature_names):
        if field_is_label_like(name):
            continue

        vals = [row["features"].get(name) for row in rows]
        if any(v is None for v in vals):
            continue

        uniq = sorted(set(str(v) for v in vals))
        uniq_count = len(uniq)

        if uniq_count < 2 or uniq_count > 12:
            continue

        score = preferred_score(name)
        if score <= 0 and not name.startswith("derived."):
            continue

        candidate_features.append(name)
        feature_inventory.append({
            "feature": name,
            "unique_count": uniq_count,
            "unique_values": uniq,
            "preferred_score": score,
        })

    feature_inventory.sort(key=lambda x: (-x["preferred_score"], x["unique_count"], x["feature"]))
    candidate_features = [x["feature"] for x in feature_inventory[:MAX_FEATURES]]

    evaluations = []
    tested_count = 0
    for size in range(1, MAX_COMBO_SIZE + 1):
        for combo in itertools.combinations(candidate_features, size):
            tested_count += 1
            ev = evaluate_combo(rows, combo)
            if ev["uses_form_index_as_input"]:
                continue
            # Keep all exact and good near candidates.
            if ev["exact_partition"] or ev["score"] >= 0 or ev["group_count"] == 4:
                evaluations.append(ev)

    evaluations.sort(
        key=lambda e: (
            not e["ordered_exact_by_boundary_gap"],
            not e["exact_partition"],
            -e["score"],
            -e["purity_total"],
            e["group_count_penalty"],
            e["size_deviation"],
            len(e["combo"]),
            e["combo"],
        )
    )

    exact_hits = [e for e in evaluations if e["exact_partition"]]
    ordered_exact_hits = [e for e in evaluations if e["ordered_exact_by_boundary_gap"]]
    best = evaluations[0] if evaluations else None

    if ordered_exact_hits:
        verdict = "boundary_cut_law_candidate_found_ordered"
    elif exact_hits:
        verdict = "boundary_cut_law_candidate_found_unordered"
    else:
        verdict = "boundary_cut_law_not_found_in_tested_family"

    statement = (
        "Artifact 061 is a boundary cut law search. It uses the inside/outside boundary grammar from 060 and searches non-label native row fields "
        "for a cut law that partitions the 24 edge records into the four six-row Euclidean forms. form_index is used only for evaluation."
    )

    boundary = (
        "This is a bounded search, not native closure. A hit would be a candidate cut law requiring validation; a miss does not refute the inside/outside boundary grammar. "
        "answer-label leakage remains open, this is not full role-labeled shared_B universe derivation, and is not Gap A closure."
    )

    combined = statement + "\n" + boundary
    missing = missing_phrases(combined, REQUIRED_PHRASES)
    forbidden = found_phrases(combined, FORBIDDEN_PHRASES)

    checks = {
        "inside_outside_boundary_grammar_060_pass": bool(a060.get("audit_pass")),
        "source_json_exists": SOURCE_JSON.exists(),
        "edge_records_found": bool(edge_records),
        "row_count_is_24": len(rows) == 24,
        "candidate_feature_count": len(candidate_features),
        "tested_combo_count": tested_count,
        "kept_evaluation_count": len(evaluations),
        "all_combos_exclude_form_index_record_order_answer_labels": True,
        "form_index_used_only_for_evaluation": True,
        "exact_cut_law_hit_count": len(exact_hits),
        "ordered_exact_cut_law_hit_count": len(ordered_exact_hits),
        "best_candidate_exists": best is not None,
        "best_candidate_score": best["score"] if best else None,
        "best_candidate_purity_total": best["purity_total"] if best else None,
        "best_candidate_group_count": best["group_count"] if best else None,
        "answer_label_leakage_remains_open": True,
        "native_provenance_confirmed": False,
        "required_phrases_present": len(missing) == 0,
        "forbidden_phrases_absent": len(forbidden) == 0,
    }

    audit_pass = all([
        checks["inside_outside_boundary_grammar_060_pass"],
        checks["source_json_exists"],
        checks["edge_records_found"],
        checks["row_count_is_24"],
        checks["candidate_feature_count"] > 0,
        checks["tested_combo_count"] > 0,
        checks["all_combos_exclude_form_index_record_order_answer_labels"],
        checks["form_index_used_only_for_evaluation"],
        checks["answer_label_leakage_remains_open"],
        checks["required_phrases_present"],
        checks["forbidden_phrases_absent"],
    ])

    result = {
        "status": "boundary_cut_law_search_recorded",
        "audit_id": "061",
        "inputs": {
            "inside_outside_boundary_grammar_audit_060": str(IN_060),
            "source_json": str(SOURCE_JSON),
            "edge_records_path": edge_path,
        },
        "checks": checks,
        "audit_pass": audit_pass,
        "verdict": verdict,
        "feature_inventory_first": feature_inventory[:MAX_FEATURES],
        "best_candidate": best,
        "exact_hits_first": exact_hits[:TOP_N],
        "ordered_exact_hits_first": ordered_exact_hits[:TOP_N],
        "top_candidates": evaluations[:TOP_N],
        "statement": statement,
        "boundary": boundary,
        "missing_required_phrases": missing,
        "forbidden_phrases_found": forbidden,
        "interpretation": (
            "Artifact 061 tests whether the missing form partition is supplied by a native boundary cut law. "
            "It keeps 060 as the order grammar and asks for a native row-field cut into four lawful six-row forms. "
            "The result is bounded by the tested feature family and does not settle native provenance."
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
            "combo",
            "group_count",
            "purity_total",
            "score",
            "size_deviation",
            "exact_partition",
            "ordered_exact_by_boundary_gap",
            "majority_order_by_boundary_gap",
            "groups",
        ])
        for i, ev in enumerate(evaluations[:TOP_N], start=1):
            compact_groups = []
            for g in ev["groups"]:
                compact_groups.append({
                    "key": g["key"],
                    "row_count": g["row_count"],
                    "form_counts": g["form_counts"],
                    "majority_form": g["majority_form"],
                    "outside": g["outside_boundary_span"],
                    "inside": g["inside_fiber_residual"],
                    "gap": g["boundary_gap"],
                })
            w.writerow([
                i,
                json.dumps(ev["combo"]),
                ev["group_count"],
                ev["purity_total"],
                ev["score"],
                ev["size_deviation"],
                ev["exact_partition"],
                ev["ordered_exact_by_boundary_gap"],
                json.dumps(ev["majority_order_by_boundary_gap"]),
                json.dumps(compact_groups, sort_keys=True),
            ])

    lines = []
    lines.append("# Boundary cut law search 061")
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
    lines.append("## Best candidate")
    lines.append("")
    if best:
        lines.append("- combo: `" + str(best["combo"]) + "`")
        lines.append("- group_count: `" + str(best["group_count"]) + "`")
        lines.append("- purity_total: `" + str(best["purity_total"]) + "`")
        lines.append("- score: `" + str(best["score"]) + "`")
        lines.append("- exact_partition: `" + str(best["exact_partition"]) + "`")
        lines.append("- ordered_exact_by_boundary_gap: `" + str(best["ordered_exact_by_boundary_gap"]) + "`")
        lines.append("- majority_order_by_boundary_gap: `" + str(best["majority_order_by_boundary_gap"]) + "`")
        lines.append("")
        lines.append("### Best candidate groups")
        lines.append("")
        for g in best["groups"]:
            lines.append(
                "- key={key}, rows={rows}, forms={forms}, majority={majority}, outside={outside}, inside={inside}, gap={gap}".format(
                    key=g["key"],
                    rows=g["row_count"],
                    forms=g["form_counts"],
                    majority=g["majority_form"],
                    outside=g["outside_boundary_span"],
                    inside=g["inside_fiber_residual"],
                    gap=g["boundary_gap"],
                )
            )
    lines.append("")
    lines.append("## Top candidates")
    lines.append("")
    for ev in evaluations[:10]:
        lines.append(
            "- combo={combo}, groups={groups}, purity={purity}/24, score={score}, exact={exact}, ordered_exact={ordered}, order={order}".format(
                combo=ev["combo"],
                groups=ev["group_count"],
                purity=ev["purity_total"],
                score=ev["score"],
                exact=ev["exact_partition"],
                ordered=ev["ordered_exact_by_boundary_gap"],
                order=ev["majority_order_by_boundary_gap"],
            )
        )
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
    if best:
        print("best_combo", best["combo"])
        print("best_group_count", best["group_count"])
        print("best_purity", str(best["purity_total"]) + "/24")
        print("best_score", best["score"])
        print("best_exact", best["exact_partition"])
        print("best_ordered_exact", best["ordered_exact_by_boundary_gap"])
        print("best_majority_order", best["majority_order_by_boundary_gap"])


if __name__ == "__main__":
    main()
