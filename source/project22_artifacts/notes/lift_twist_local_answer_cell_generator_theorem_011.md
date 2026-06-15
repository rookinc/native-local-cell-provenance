# Lift & Twist local answer-cell generator theorem 011

Status: lift_twist_local_answer_cell_generator_theorem_recorded

## Claim

The four-state local answer-cell target from 006 is generated from the two bits b,r by the consolidated Lift & Twist laws from 007-010. The generator reproduces the C row, anchor column, selected candidate, C key, anchor key, C path values, anchor residue set, and overlap markers for O0,O1,B0,B1.

## Generated table

| state | b | r | C row | anchor col | selected | C key | anchor key | C path | C values | anchor residues | overlap | match |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|---:|
| O0 | 0 | 0 | 0 | 1 | 1 | 11 | 0 | 11 2 14 11 | 2 11 14 | 4 5 7 8 9 12 | none | 1 |
| O1 | 0 | 1 | 1 | 2 | 6 | 13 | 12 | 13 1 10 13 | 1 10 13 | 0 2 4 9 13 14 | 13 | 1 |
| B0 | 1 | 0 | 2 | 0 | 8 | 2 | 4 | 2 5 0 2 | 0 2 5 | 0 2 3 4 8 | 0 2 | 1 |
| B1 | 1 | 1 | 3 | 3 | 15 | 4 | 13 | 4 5 2 4 | 2 4 5 | 2 3 7 8 10 13 | 2 | 1 |

## Checks

- all_generated_rows_match_006_target: `True`
- selected_candidates_match_expected: `True`
- c_rows_match_expected: `True`
- anchor_cols_match_expected: `True`
- overlap_signatures_match_expected: `True`
- project22_006_theorem_pass: `True`
- project22_007_theorem_pass: `True`
- project22_008_theorem_pass: `True`
- project22_009_theorem_pass: `True`
- project22_010_theorem_pass: `True`
- theorem_pass: `True`

## Interpretation

This consolidates artifacts 007-010 into one local answer-cell generator theorem.
The four-state target is now generated from the two bits b,r, except for the still-open anchor node path geometry.

## Boundary

This is a theorem for the four-state local answer-cell target. It still does not derive the anchor node paths themselves, does not derive the full reduced 16-candidate universe from native G60 provenance, and does not close Gap A.
