# Lift & Twist local answer-cell bit law 007

Status: lift_twist_local_answer_cell_bit_law_recorded

## Claim

The 006 local answer-cell target has an exact two-bit header law. With shell bit b (ordinary=0, branch=1) and rank bit r, the formulas c_row=2*b+r, anchor_col=1+r+b*(2*r-1), selected=4*c_row+anchor_col, c_key=11+6*b+2*r mod 15, and anchor_key=4*b+12*r+12*b*r mod 15 recover all observed C rows, anchor columns, selected candidate indices, C keys, and anchor keys.

## Bit encoding

- ordinary shell: `b=0`
- branch shell: `b=1`
- rank: `r=0 or r=1`

## Laws

- c_row: `2*b + r`
- anchor_col: `1 + r + b*(2*r - 1)`
- selected_candidate_index: `4*c_row + anchor_col`
- c_key_mod15: `11 + 6*b + 2*r mod 15`
- anchor_key_mod15: `4*b + 12*r + 12*b*r mod 15`

## Table

| state | b | r | C row | anchor col | selected | C key | anchor key | match |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| O0 | 0 | 0 | 0 | 1 | 1 | 11 | 0 | 1 |
| O1 | 0 | 1 | 1 | 2 | 6 | 13 | 12 | 1 |
| B0 | 1 | 0 | 2 | 0 | 8 | 2 | 4 | 1 |
| B1 | 1 | 1 | 3 | 3 | 15 | 4 | 13 | 1 |

## Checks

- all_c_rows_match: `True`
- all_anchor_cols_match: `True`
- all_selected_candidates_match: `True`
- all_c_keys_match: `True`
- all_anchor_keys_match: `True`
- all_header_matches: `True`
- project22_006_theorem_pass: `True`
- theorem_pass: `True`

## Boundary

This derives the local answer-cell header from a two-bit state law. It does not derive the full C payload paths, anchor residue sets, or the reduced 16-candidate universe from native provenance. It is not Gap A closure.
