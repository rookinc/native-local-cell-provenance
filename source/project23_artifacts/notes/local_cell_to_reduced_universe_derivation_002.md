# Local cell to reduced universe derivation 002

Status: local_cell_to_reduced_universe_derivation_recorded

## Claim

The Project 22 local answer-cell kernel generates the reduced 16-candidate universe as the product of two readouts. The C readout orders states O0,O1,B0,B1. The anchor readout orders the same states B0,O0,O1,B1. Their product contains candidates 0..15, and the hidden identity diagonal selects exactly [1,6,8,15], appearing visibly as [1,2,0,3].

## Readouts

- C readout order: `['O0', 'O1', 'B0', 'B1']`
- anchor readout order: `['B0', 'O0', 'O1', 'B1']`

## Derived universe

- candidate_count: `16`
- candidate_indices: `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]`
- visible_permutation: `[1, 2, 0, 3]`
- diagonal_indices: `[1, 6, 8, 15]`

## Candidate table

| candidate | C state | anchor state | diagonal | overlap |
|---:|---|---|---:|---|
| 0 | O0 | B0 | 0 | 2 |
| 1 | O0 | O0 | 1 | none |
| 2 | O0 | O1 | 0 | 2 14 |
| 3 | O0 | B1 | 0 | 2 |
| 4 | O1 | B0 | 0 | none |
| 5 | O1 | O0 | 0 | none |
| 6 | O1 | O1 | 1 | 13 |
| 7 | O1 | B1 | 0 | 10 13 |
| 8 | B0 | B0 | 1 | 0 2 |
| 9 | B0 | O0 | 0 | 5 |
| 10 | B0 | O1 | 0 | 0 2 |
| 11 | B0 | B1 | 0 | 2 |
| 12 | B1 | B0 | 0 | 2 4 |
| 13 | B1 | O0 | 0 | 4 5 |
| 14 | B1 | O1 | 0 | 2 4 |
| 15 | B1 | B1 | 1 | 2 |

## Checks

- project22_011_theorem_pass: `True`
- project22_014_boundary_pass: `True`
- c_order_matches_project22_003: `True`
- anchor_order_matches_project22_003: `True`
- derived_c_order_matches_project22_004: `True`
- derived_anchor_order_matches_project22_004: `True`
- candidate_count_is_16: `True`
- candidate_indices_are_0_to_15: `True`
- diagonal_indices_match_expected: `True`
- visible_permutation_matches_expected: `True`
- project22_003_diagonal_matches: `True`
- project22_003_actual_selected_matches: `True`
- theorem_pass: `True`

## Boundary

This derives the reduced 16-candidate universe from the copied Project 22 local-cell kernel. It does not derive that local-cell kernel from native G60 provenance, does not derive the full role-labeled shared_B edge universe, and does not close Gap A.
