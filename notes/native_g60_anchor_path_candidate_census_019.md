# Native G60 anchor path candidate census 019

Status: native_g60_anchor_path_candidate_census_recorded

## Question

Given each state's anchor residue set and native mod15 quotient-pair support, how many closed three-step residue-pair paths exist?

## Result

- theorem_pass: `False`
- total_candidate_count: `48`
- observed_unique_in_all_states: `False`

## Per state

- O0:
  - anchor_residue_set: `[4, 5, 7, 8, 9, 12]`
  - pair_sizes: `[2, 2, 2]`
  - observed_residue_cycle: `[[4, 5], [7, 12], [8, 9]]`
  - candidate_count: `14`
  - observed_found: `True`
  - observed_support_sum: `13`
  - observed_rank_by_support_sum_desc: `2`
- O1:
  - anchor_residue_set: `[0, 2, 4, 9, 13, 14]`
  - pair_sizes: `[2, 2, 2]`
  - observed_residue_cycle: `[[0, 2], [4, 9], [13, 14]]`
  - candidate_count: `15`
  - observed_found: `True`
  - observed_support_sum: `16`
  - observed_rank_by_support_sum_desc: `4`
- B0:
  - anchor_residue_set: `[0, 2, 3, 4, 8]`
  - pair_sizes: `[2, 1, 2]`
  - observed_residue_cycle: `[[0, 4], [2], [3, 8]]`
  - candidate_count: `6`
  - observed_found: `False`
  - observed_support_sum: `None`
  - observed_rank_by_support_sum_desc: `None`
- B1:
  - anchor_residue_set: `[2, 3, 7, 8, 10, 13]`
  - pair_sizes: `[2, 2, 2]`
  - observed_residue_cycle: `[[2, 13], [3, 8], [7, 10]]`
  - candidate_count: `13`
  - observed_found: `True`
  - observed_support_sum: `11`
  - observed_rank_by_support_sum_desc: `7`

## Checks

- project22_012_theorem_pass: `True`
- anchor_quotient_pair_017_theorem_pass: `True`
- lift_mask_sheet_018_theorem_pass: `True`
- g60_edge_count_is_120: `True`
- all_observed_cycles_found: `False`
- all_states_have_at_least_one_candidate: `True`

## Interpretation

This enumerates closed three-step residue-pair cycles using each state's observed anchor residue set and pair-size profile, keeping only cycles supported by native mod15 G60 residue-pair edges. If the observed cycle is unique, residue-pair support already selects the anchor path. If not, another selector layer is needed.

## Boundary

This is a candidate census over observed anchor residue sets and observed pair-size profiles. It does not derive the anchor residue sets themselves, does not derive the full local cell from native G60 provenance, does not test station fields, does not select unique relay mediators, does not derive the full role-labeled shared_B universe, and does not close Gap A.
