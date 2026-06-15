# Native G60 relay block selector from mediators 035

Status: native_g60_relay_block_selector_from_mediators_recorded

## Result

- theorem_candidate_pass: `True`
- mediator_source: `artifact_007_parsed`
- relay_target_source: `artifact_011_rows`

## Laws

- relay_size: `{'formula': 'p0 + pb*b + pr*r + pbr*b*r', 'coefficients': {'p0': 3, 'pb': -1, 'pr': 0, 'pbr': 1}, 'predictions': {'O0': 3, 'O1': 3, 'B0': 2, 'B1': 3}}`
- relay_sum: `{'formula': 'p0 + pb*b + pr*r + pbr*b*r', 'coefficients': {'p0': 16, 'pb': -4, 'pr': -1, 'pbr': 20}, 'predictions': {'O0': 16, 'O1': 15, 'B0': 12, 'B1': 31}}`
- relay_min: `{'formula': 'p0 + pb*b + pr*r + pbr*b*r', 'coefficients': {'p0': 4, 'pb': 0, 'pr': -2, 'pbr': 6}, 'predictions': {'O0': 4, 'O1': 2, 'B0': 4, 'B1': 8}}`
- relay_max: `{'formula': 'p0 + pb*b + pr*r + pbr*b*r', 'coefficients': {'p0': 7, 'pb': 1, 'pr': 2, 'pbr': 3}, 'predictions': {'O0': 7, 'O1': 9, 'B0': 8, 'B1': 13}}`

## Per state

- O0:
  - mediator_union: `[0, 1, 2, 3, 4, 5, 7, 8]`
  - c_values: `[2, 11, 14]`
  - target_relay_block: `[4, 5, 7]`
  - candidate_count: `35`
  - selected_relay_blocks: `[[4, 5, 7]]`
  - selected_matches_target: `True`
- O1:
  - mediator_union: `[1, 2, 4, 6, 7, 9]`
  - c_values: `[1, 10, 13]`
  - target_relay_block: `[2, 4, 9]`
  - candidate_count: `10`
  - selected_relay_blocks: `[[2, 4, 9]]`
  - selected_matches_target: `True`
- B0:
  - mediator_union: `[1, 4, 8, 11, 14]`
  - c_values: `[0, 2, 5]`
  - target_relay_block: `[4, 8]`
  - candidate_count: `9`
  - selected_relay_blocks: `[[4, 8]]`
  - selected_matches_target: `True`
- B1:
  - mediator_union: `[0, 8, 10, 11, 13, 14]`
  - c_values: `[2, 4, 5]`
  - target_relay_block: `[8, 10, 13]`
  - candidate_count: `19`
  - selected_relay_blocks: `[[8, 10, 13]]`
  - selected_matches_target: `True`

## Checks

- two_hop_relay_007_theorem_pass: `True`
- unlifted_relay_cover_011_theorem_pass: `True`
- anchor_residue_derivation_033_pass: `True`
- anchor_path_derivation_034_pass: `True`
- all_states_have_mediator_rows: `True`
- all_states_select_one_relay_block: `True`
- all_selected_relay_blocks_match_target: `True`

## Interpretation

This attacks the relay block dependency exposed by artifacts 033 and 034. It tests whether relay blocks can be selected from native two-hop C-transition mediator geometry using compact state-bit scalar targets.

## Boundary

This is still a theorem candidate. The scalar relay laws require native/provenance interpretation, and the full role-labeled shared_B universe is not derived. If mediator_source is a fallback, the result also has a source-binding caveat.
