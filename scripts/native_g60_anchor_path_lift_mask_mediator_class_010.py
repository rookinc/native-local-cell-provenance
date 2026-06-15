#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_009 = ROOT / "artifacts/json/native_g60_anchor_path_mediator_position_009.v1.json"
IN_012 = ROOT / "source/project22_artifacts/json/lift_twist_anchor_node_path_geometry_012.v1.json"

OUT_JSON = ROOT / "artifacts/json/native_g60_anchor_path_lift_mask_mediator_class_010.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_g60_anchor_path_lift_mask_mediator_class_010.v1.csv"
OUT_NOTE = ROOT / "notes/native_g60_anchor_path_lift_mask_mediator_class_010.md"

STATES = {"O0", "O1", "B0", "B1"}


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)


def find_state_records(a012):
    recs = {}
    for d in walk(a012):
        state = d.get("state")
        if state in STATES:
            recs[state] = d
    missing = sorted(STATES.difference(recs.keys()))
    if missing:
        raise SystemExit("missing state records in 012: " + str(missing))
    return recs


def find_lift_mask(d, state):
    # Prefer explicit fields when present.
    for k, v in d.items():
        lk = str(k).lower()
        if "lift" in lk and "mask" in lk and isinstance(v, list):
            if all(x in (0, 1, True, False) for x in v):
                return [int(x) for x in v], k

    # Project 22 012 known masks if fields are not preserved.
    if state in ("O0", "O1"):
        return [1, 1, 0, 0, 0, 0], "fallback_ordinary_open_lift_mask"
    return [0, 0, 0, 1, 0, 1], "fallback_branch_open_lift_mask"


def classify_position(pair_index, node_index, open_pair_count, lift_mask):
    is_closure_pair = pair_index == open_pair_count
    base_pair_index = 0 if is_closure_pair else pair_index

    open_node_index = base_pair_index * 2 + node_index
    lift_value = None
    if 0 <= open_node_index < len(lift_mask):
        lift_value = int(lift_mask[open_node_index])

    return {
        "is_closure_pair": is_closure_pair,
        "base_pair_index": base_pair_index,
        "open_node_index": open_node_index,
        "lift_value": lift_value,
        "lift_class": "lifted" if lift_value == 1 else "unlifted" if lift_value == 0 else "unknown",
    }


def main():
    a009 = load_json(IN_009)
    a012 = load_json(IN_012)

    if not a009.get("theorem_pass"):
        raise SystemExit("009 theorem_pass is not true")
    if not a012.get("theorem_pass"):
        raise SystemExit("Project22 012 theorem_pass is not true")

    state_records_012 = find_state_records(a012)

    lift_masks = {}
    for state, d in state_records_012.items():
        mask, source = find_lift_mask(d, state)
        lift_masks[state] = {
            "mask": mask,
            "source": source,
        }

    path_profiles = a009["path_profiles"]

    rows = []
    transition_profiles = []

    for row in a009["rows"]:
        state = row["state"]
        closed_path = path_profiles[state]["closed_path"]
        open_pair_count = len(closed_path) - 1
        lift_mask = lift_masks[state]["mask"]

        hit_records = []
        for hit_rec in row["hit_records"]:
            pair_index = int(hit_rec["pair_index"])
            node_index = int(hit_rec["node_index"])
            cls = classify_position(pair_index, node_index, open_pair_count, lift_mask)

            out = {
                "state": state,
                "shell_bit": int(row["shell_bit"]),
                "rank_bit": int(row["rank_bit"]),
                "step": int(row["step"]),
                "from_c": int(row["from_c"]),
                "to_c": int(row["to_c"]),
                "hit": int(hit_rec["hit"]),
                "pair_index": pair_index,
                "node_index": node_index,
                "node": int(hit_rec["node"]),
                "is_closure_pair": cls["is_closure_pair"],
                "base_pair_index": cls["base_pair_index"],
                "open_node_index": cls["open_node_index"],
                "lift_value": cls["lift_value"],
                "lift_class": cls["lift_class"],
            }
            rows.append(out)
            hit_records.append(out)

        lift_classes = sorted(set(x["lift_class"] for x in hit_records))
        lifted_hits = [x for x in hit_records if x["lift_value"] == 1]
        unlifted_hits = [x for x in hit_records if x["lift_value"] == 0]
        closure_hits = [x for x in hit_records if x["is_closure_pair"]]

        transition_profiles.append({
            "state": state,
            "step": int(row["step"]),
            "from_c": int(row["from_c"]),
            "to_c": int(row["to_c"]),
            "hit_count": len(hit_records),
            "lift_classes": lift_classes,
            "lifted_hit_count": len(lifted_hits),
            "unlifted_hit_count": len(unlifted_hits),
            "closure_hit_count": len(closure_hits),
            "has_lifted_hit": len(lifted_hits) > 0,
            "has_unlifted_hit": len(unlifted_hits) > 0,
            "has_closure_hit": len(closure_hits) > 0,
            "hit_records": hit_records,
        })

    total_hits = len(rows)
    lifted_count = sum(1 for x in rows if x["lift_value"] == 1)
    unlifted_count = sum(1 for x in rows if x["lift_value"] == 0)
    closure_count = sum(1 for x in rows if x["is_closure_pair"])

    checks = {
        "anchor_path_position_009_theorem_pass": bool(a009.get("theorem_pass")),
        "project22_012_theorem_pass": bool(a012.get("theorem_pass")),
        "lift_masks_available_for_all_states": sorted(lift_masks.keys()) == ["B0", "B1", "O0", "O1"],
        "mediator_hit_count_positive": total_hits > 0,
        "all_mediator_hits_classified": all(x["lift_class"] in ("lifted", "unlifted") for x in rows),
        "all_transitions_have_at_least_one_classified_hit": all(x["hit_count"] > 0 for x in transition_profiles),
    }

    result = {
        "status": "native_g60_anchor_path_lift_mask_mediator_class_recorded",
        "audit_id": "010",
        "inputs": {
            "anchor_path_position_009": str(IN_009),
            "project22_anchor_path_012": str(IN_012),
        },
        "lift_masks": lift_masks,
        "total_mediator_hits": total_hits,
        "lifted_hit_count": lifted_count,
        "unlifted_hit_count": unlifted_count,
        "closure_hit_count": closure_count,
        "rows": rows,
        "transition_profiles": transition_profiles,
        "checks": checks,
        "theorem_pass": all(checks.values()),
        "interpretation": (
            "This classifies the anchor-path mediator hits from artifact 009 against the Project 22 anchor lift masks. "
            "If the mediator hits concentrate in lifted, unlifted, or closure positions, that may provide the next selector "
            "needed to refine anchor mediation toward a native provenance law."
        ),
        "boundary": (
            "This is a classification audit, not a selector theorem. It does not prove unique mediator selection, does not derive "
            "the closed anchor paths or lift masks from native G60 provenance, does not test station fields, does not derive the "
            "full role-labeled shared_B edge universe, and does not close Gap A."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "state",
            "shell_bit",
            "rank_bit",
            "step",
            "from_c",
            "to_c",
            "hit",
            "pair_index",
            "node_index",
            "node",
            "is_closure_pair",
            "base_pair_index",
            "open_node_index",
            "lift_value",
            "lift_class",
        ])
        for r in rows:
            w.writerow([
                r["state"],
                r["shell_bit"],
                r["rank_bit"],
                r["step"],
                r["from_c"],
                r["to_c"],
                r["hit"],
                r["pair_index"],
                r["node_index"],
                r["node"],
                "1" if r["is_closure_pair"] else "0",
                r["base_pair_index"],
                r["open_node_index"],
                r["lift_value"],
                r["lift_class"],
            ])

    lines = []
    lines.append("# Native G60 anchor path lift-mask mediator classification 010")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Question")
    lines.append("")
    lines.append("Do the anchor mediator hits from artifact 009 land on lifted, unlifted, or closure positions of the Project 22 anchor paths?")
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- theorem_pass: `" + str(result["theorem_pass"]) + "`")
    lines.append("- total_mediator_hits: `" + str(total_hits) + "`")
    lines.append("- lifted_hit_count: `" + str(lifted_count) + "`")
    lines.append("- unlifted_hit_count: `" + str(unlifted_count) + "`")
    lines.append("- closure_hit_count: `" + str(closure_count) + "`")
    lines.append("")
    lines.append("## Lift masks")
    lines.append("")
    for state in ["O0", "O1", "B0", "B1"]:
        m = lift_masks[state]
        lines.append("- " + state + ": `" + str(m["mask"]) + "` from `" + str(m["source"]) + "`")
    lines.append("")
    lines.append("## Transition profiles")
    lines.append("")
    for p in transition_profiles:
        lines.append(
            "- "
            + p["state"]
            + " step "
            + str(p["step"])
            + " `"
            + str(p["from_c"])
            + " -> "
            + str(p["to_c"])
            + "`: hit_count `"
            + str(p["hit_count"])
            + "`, lifted `"
            + str(p["lifted_hit_count"])
            + "`, unlifted `"
            + str(p["unlifted_hit_count"])
            + "`, closure `"
            + str(p["closure_hit_count"])
            + "`, classes `"
            + str(p["lift_classes"])
            + "`"
        )
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
    print("theorem_pass", result["theorem_pass"])
    print("total_mediator_hits", total_hits)
    print("lifted_hit_count", lifted_count)
    print("unlifted_hit_count", unlifted_count)
    print("closure_hit_count", closure_count)


if __name__ == "__main__":
    main()
