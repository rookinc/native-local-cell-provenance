# Gap A direct anchor selector assault 027

Status: gap_a_direct_anchor_selector_assault_recorded

## Result

- closure_candidate_pass: `False`
- uses_observed_anchor_residue_sets_for_generation: `False`
- uses_observed_anchor_paths_for_generation: `False`

## Generation rules

- residue_count_law: `6 - b*(1-r)`
- size_profile_law: `[2, 2 - b*(1-r), 2]`
- relay_obligation_rule: `candidate residue set must intersect every same-state unlifted relay-hit set from artifact 011`
- quotient_support_rule: `every cycle step must have native G60 mod15 residue-pair support`
- rank_selector_law: `rank = 2 + 7*b + 2*r - b*r`

## Per state

- O0:
  - target_rank: `2`
  - residue_count_law: `6`
  - size_profile_law: `[2, 2, 2]`
  - residue_set_after_relay_count: `4081`
  - canonical_candidate_count: `56688`
  - observed_found: `True`
  - observed_rank: `34232`
  - selected_candidate_index: `1`
  - selected_rank: `2`
  - selected_matches_observed: `False`
  - selected_residue_set: `[0, 2, 5, 8, 11, 14]`
- O1:
  - target_rank: `4`
  - residue_count_law: `6`
  - size_profile_law: `[2, 2, 2]`
  - residue_set_after_relay_count: `4081`
  - canonical_candidate_count: `57049`
  - observed_found: `True`
  - observed_rank: `8982`
  - selected_candidate_index: `3`
  - selected_rank: `4`
  - selected_matches_observed: `False`
  - selected_residue_set: `[1, 3, 4, 7, 12, 13]`
- B0:
  - target_rank: `9`
  - residue_count_law: `5`
  - size_profile_law: `[2, 1, 2]`
  - residue_set_after_relay_count: `1001`
  - canonical_candidate_count: `10232`
  - observed_found: `True`
  - observed_rank: `7068`
  - selected_candidate_index: `8`
  - selected_rank: `9`
  - selected_matches_observed: `False`
  - selected_residue_set: `[2, 5, 8, 11, 14]`
- B1:
  - target_rank: `10`
  - residue_count_law: `6`
  - size_profile_law: `[2, 2, 2]`
  - residue_set_after_relay_count: `2002`
  - canonical_candidate_count: `28032`
  - observed_found: `True`
  - observed_rank: `23159`
  - selected_candidate_index: `9`
  - selected_rank: `10`
  - selected_matches_observed: `False`
  - selected_residue_set: `[1, 2, 5, 8, 11, 14]`

## Checks

- unlifted_relay_cover_011_theorem_pass: `True`
- prior_census_020_theorem_pass: `True`
- rank_law_022_theorem_pass: `True`
- frontier_checkpoint_024_pass: `True`
- g60_edge_count_is_120: `True`
- all_observed_cycles_found_in_direct_universe: `True`
- all_states_select_one_candidate_by_rank_law: `True`
- all_selected_candidates_match_observed: `False`

## Interpretation

This is a direct Gap A assault on the anchor selector. It stops assuming the observed anchor residue sets and instead generates candidates from state bits, C-relay obligations, native mod15 G60 quotient support, and the rank law. If the selected candidates match the observed anchor paths in all four states, the anchor-selector subproblem moves from observed residue-set assumption to a native/provenance candidate law.

## Boundary

Even if this passes, it is not full Gap A closure by itself. The rank law and size-profile law still require independent native/provenance justification, relay mediators are not uniquely selected, station fields are not tested, and the full role-labeled shared_B universe is not yet derived.
