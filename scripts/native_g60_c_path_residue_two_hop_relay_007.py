#!/usr/bin/env python3
import csv
import json
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_004 = ROOT / "artifacts/json/native_g60_c_path_residue_support_004.v1.json"
IN_005 = ROOT / "artifacts/json/native_g60_c_path_residue_distance_005.v1.json"
IN_006 = ROOT / "artifacts/json/native_g60_c_path_residue_support_bit_law_006.v1.json"
G60_EDGES = ROOT / "source/project18_payload/g60_local_edges.csv"

OUT_JSON = ROOT / "artifacts/json/native_g60_c_path_residue_two_hop_relay_007.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_g60_c_path_residue_two_hop_relay_007.v1.csv"
OUT_NOTE = ROOT / "notes/native_g60_c_path_residue_two_hop_relay_007.md"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_edges(path):
    edges = []
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            edges.append((int(row["local_u"]), int(row["local_v"])))
    return edges


def main():
    a004 = load_json(IN_004)
    a005 = load_json(IN_005)
    a006 = load_json(IN_006)

    if not a004.get("all_checks_pass"):
        raise SystemExit("004 all_checks_pass is not true")
    if not a005.get("all_checks_pass"):
        raise SystemExit("005 all_checks_pass is not true")
    if not a006.get("theorem_pass"):
        raise SystemExit("006 theorem_pass is not true")

    edges = load_edges(G60_EDGES)

    adj = defaultdict(set)
    support_edges = defaultdict(list)

    for u, v in edges:
        ru = u % 15
        rv = v % 15
        adj[ru].add(rv)
        adj[rv].add(ru)
        support_edges[tuple(sorted((ru, rv)))].append((u, v))

    rows = []
    unsupported_rows = []

    for r in a006["rows"]:
        if r["observed_direct_residue_support"]:
            continue

        state = r["state"]
        b = int(r["shell_bit"])
        rank = int(r["rank_bit"])
        step = int(r["step"])
        src = int(r["from_c"])
        dst = int(r["to_c"])

        mediators = sorted(adj[src].intersection(adj[dst]))

        relay_records = []
        for m in mediators:
            left_key = tuple(sorted((src, m)))
            right_key = tuple(sorted((m, dst)))
            relay_records.append({
                "mediator": m,
                "left_support_count": len(support_edges[left_key]),
                "right_support_count": len(support_edges[right_key]),
                "left_examples": support_edges[left_key][:6],
                "right_examples": support_edges[right_key][:6],
            })

        row = {
            "state": state,
            "shell_bit": b,
            "rank_bit": rank,
            "step": step,
            "from_c": src,
            "to_c": dst,
            "mediator_count": len(mediators),
            "mediators": mediators,
            "relay_records": relay_records,
            "all_relays_are_two_hop": len(mediators) > 0,
        }
        unsupported_rows.append(row)

        for rec in relay_records:
            rows.append({
                "state": state,
                "shell_bit": b,
                "rank_bit": rank,
                "step": step,
                "from_c": src,
                "mediator": rec["mediator"],
                "to_c": dst,
                "left_support_count": rec["left_support_count"],
                "right_support_count": rec["right_support_count"],
                "path": [src, rec["mediator"], dst],
            })

    mediator_counter = Counter()
    mediator_by_state = {}
    mediator_by_shell_rank_step = {}

    for row in unsupported_rows:
        for m in row["mediators"]:
            mediator_counter[m] += 1
        mediator_by_state[row["state"] + "_step" + str(row["step"])] = row["mediators"]
        key = "b" + str(row["shell_bit"]) + "_r" + str(row["rank_bit"]) + "_s" + str(row["step"])
        mediator_by_shell_rank_step[key] = row["mediators"]

    checks = {
        "residue_support_004_checks_pass": bool(a004.get("all_checks_pass")),
        "residue_distance_005_checks_pass": bool(a005.get("all_checks_pass")),
        "bit_law_006_theorem_pass": bool(a006.get("theorem_pass")),
        "unsupported_row_count_is_6": len(unsupported_rows) == 6,
        "all_unsupported_have_two_hop_relay": all(x["mediator_count"] > 0 for x in unsupported_rows),
        "all_unsupported_have_distance_2_in_005": all(
            x.get("residue_distance") == 2
            for x in a006["rows"]
            if not x["observed_direct_residue_support"]
        ),
    }

    result = {
        "status": "native_g60_c_path_residue_two_hop_relay_recorded",
        "audit_id": "007",
        "inputs": {
            "residue_support_004": str(IN_004),
            "residue_distance_005": str(IN_005),
            "bit_law_006": str(IN_006),
            "g60_edges": str(G60_EDGES),
        },
        "unsupported_row_count": len(unsupported_rows),
        "relay_row_count": len(rows),
        "unsupported_rows": unsupported_rows,
        "relay_rows": rows,
        "mediator_counts": dict(sorted(mediator_counter.items())),
        "mediator_by_state_step": mediator_by_state,
        "mediator_by_shell_rank_step": mediator_by_shell_rank_step,
        "checks": checks,
        "theorem_pass": all(checks.values()),
        "interpretation": (
            "The six C transitions not directly supported in the mod15 residue quotient are tested for two-hop relay support. "
            "If every unsupported transition has a residue mediator, then the missing half of the bit-law support pattern is not absence; "
            "it is a two-hop relay layer in the quotient graph."
        ),
        "boundary": (
            "This is only a two-hop relay audit in the simple mod15 residue quotient. It does not derive the C paths, "
            "does not derive the local cell from native G60 provenance, does not test station fields or lifted masks, "
            "does not derive the full role-labeled shared_B edge universe, and does not close Gap A."
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
            "mediator",
            "to_c",
            "left_support_count",
            "right_support_count",
            "path",
        ])
        for r in rows:
            w.writerow([
                r["state"],
                r["shell_bit"],
                r["rank_bit"],
                r["step"],
                r["from_c"],
                r["mediator"],
                r["to_c"],
                r["left_support_count"],
                r["right_support_count"],
                " ".join(str(x) for x in r["path"]),
            ])

    lines = []
    lines.append("# Native G60 C path residue two-hop relay 007")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Question")
    lines.append("")
    lines.append("For the six unsupported C transitions from artifact 006, which residue mediators complete the missing two-hop paths?")
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- theorem_pass: `" + str(result["theorem_pass"]) + "`")
    lines.append("- unsupported_row_count: `" + str(len(unsupported_rows)) + "`")
    lines.append("- relay_row_count: `" + str(len(rows)) + "`")
    lines.append("- all_unsupported_have_two_hop_relay: `" + str(checks["all_unsupported_have_two_hop_relay"]) + "`")
    lines.append("- mediator_counts: `" + str(result["mediator_counts"]) + "`")
    lines.append("")
    lines.append("## Unsupported transitions")
    lines.append("")
    for row in unsupported_rows:
        lines.append(
            "- "
            + row["state"]
            + " step "
            + str(row["step"])
            + ": `"
            + str(row["from_c"])
            + " -> "
            + str(row["to_c"])
            + "`, mediators `"
            + str(row["mediators"])
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
    print("unsupported_row_count", len(unsupported_rows))
    print("relay_row_count", len(rows))
    print("all_unsupported_have_two_hop_relay", checks["all_unsupported_have_two_hop_relay"])
    print("mediator_counts", dict(sorted(mediator_counter.items())))


if __name__ == "__main__":
    main()
