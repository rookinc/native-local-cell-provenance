# Native G60 anchor path candidate census fixed 020

Status: native_g60_anchor_path_candidate_census_fixed_recorded

## Question

After fixing unequal-size partition enumeration, are all observed anchor residue cycles found?

## Result

- theorem_pass: `True`
- total_canonical_candidate_count: `53`
- observed_unique_in_all_states: `False`

## Per state

- O0:
  - anchor_residue_set: `[4, 5, 7, 8, 9, 12]`
  - size_profile: `[2, 2, 2]`
  - observed_cycle: `[[4, 5], [7, 12], [8, 9]]`
  - labeled_candidate_count: `90`
  - supported_labeled_candidate_count: `84`
  - canonical_candidate_count: `14`
  - observed_found: `True`
  - observed_rank_by_best_support_sum_desc: `2`
  - observed_support_sum_best_orientation: `13`
- O1:
  - anchor_residue_set: `[0, 2, 4, 9, 13, 14]`
  - size_profile: `[2, 2, 2]`
  - observed_cycle: `[[0, 2], [4, 9], [13, 14]]`
  - labeled_candidate_count: `90`
  - supported_labeled_candidate_count: `90`
  - canonical_candidate_count: `15`
  - observed_found: `True`
  - observed_rank_by_best_support_sum_desc: `4`
  - observed_support_sum_best_orientation: `16`
- B0:
  - anchor_residue_set: `[0, 2, 3, 4, 8]`
  - size_profile: `[2, 1, 2]`
  - observed_cycle: `[[0, 4], [2], [3, 8]]`
  - labeled_candidate_count: `30`
  - supported_labeled_candidate_count: `22`
  - canonical_candidate_count: `11`
  - observed_found: `True`
  - observed_rank_by_best_support_sum_desc: `9`
  - observed_support_sum_best_orientation: `8`
- B1:
  - anchor_residue_set: `[2, 3, 7, 8, 10, 13]`
  - size_profile: `[2, 2, 2]`
  - observed_cycle: `[[2, 13], [3, 8], [7, 10]]`
  - labeled_candidate_count: `90`
  - supported_labeled_candidate_count: `78`
  - canonical_candidate_count: `13`
  - observed_found: `True`
  - observed_rank_by_best_support_sum_desc: `10`
  - observed_support_sum_best_orientation: `11`

## Checks

- anchor_quotient_pair_017_theorem_pass: `True`
- lift_mask_sheet_018_theorem_pass: `True`
- g60_edge_count_is_120: `True`
- all_observed_cycles_found: `True`
- b0_observed_cycle_found: `True`
- all_states_have_candidates: `True`
- old_019_b0_miss_recorded: `True`

## Interpretation

This fixes the anchor-path candidate census by enumerating ordered/labeled partitions with the exact observed size profile before quotienting cycles by rotation and reversal. The prior B0 miss in artifact 019 is treated as a census enumeration issue, because artifact 016 already proved the observed B0 residue-pair steps are supported.

## Boundary

This is still a candidate census over observed anchor residue sets and pair-size profiles. It does not derive the anchor residue sets themselves, does not derive why the exact anchor paths are selected, does not test station fields, does not select unique relay mediators, does not derive the full role-labeled shared_B universe, and does not close Gap A.
