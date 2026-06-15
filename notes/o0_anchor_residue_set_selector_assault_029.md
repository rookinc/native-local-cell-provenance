# O0 anchor residue-set selector assault 029

Status: o0_anchor_residue_set_selector_assault_recorded

## Result

- all_checks_pass: `True`
- candidate_count: `4081`
- observed_found: `True`
- observed_candidate_index: `3705`
- exact_selector_count: `1`

## Observed set

- observed_residue_set: `[4, 5, 7, 8, 9, 12]`
- relay_hits: `[4, 5, 7]`
- c_values: `[2, 11, 14]`
- observed_features: `{'sum_residues': 45, 'sum_mod15': 0, 'gap_signature': '1,1,1,2,3,7', 'ordered_gap_signature': '1,2,1,1,3,7', 'relay_block_signature': '4,5,7', 'relay_block_count': 3, 'free_block_signature': '8,9,12', 'free_block_count': 3, 'c_overlap_signature': '', 'c_overlap_count': 0, 'no_c_overlap': True, 'internal_supported_pair_count': 8, 'internal_support_weight': 14, 'internal_missing_pair_count': 7, 'boundary_supported_pair_count': 31, 'boundary_support_weight': 62, 'c_cut_supported_pair_count': 10, 'c_cut_weight': 22, 'free_to_c_supported_pair_count': 4, 'free_to_c_weight': 10, 'relay_to_free_supported_pair_count': 3, 'relay_to_free_weight': 5, 'nearest_c_distance_signature': '1,2,2,3,3,4', 'sum_nearest_c_distance': 15, 'min_nearest_c_distance': 1, 'max_nearest_c_distance': 4, 'all_c_distance_signature': '1,2,2,2,3,3,4,5,5,5,5,6,6,6,6,7,7,7'}`

## Exact selectors first 50

- `{'features': ['free_block_signature'], 'observed_values': ['8,9,12'], 'width': 1}`

## Checks

- unlifted_relay_cover_011_theorem_pass: `True`
- candidate_census_020_theorem_pass: `True`
- residue_selector_audit_028_recorded: `True`
- g60_edge_count_is_120: `True`
- observed_o0_residue_set_found: `True`
- exact_o0_selector_found: `True`

## Interpretation

Artifact 028 showed that simple scalar residue-set features did not select O0. This assault adds relational features: relay/free decomposition, C-distance profiles, gap signatures, and quotient support cuts. If an exact selector appears, O0 may be reachable without station fields. If no exact selector appears, the next layer is almost certainly station/provenance structure.

## Boundary

This is an O0-only selector assault. Any exact selector found here is a candidate direction, not a native theorem until independently justified and generalized. This does not close Gap A.
