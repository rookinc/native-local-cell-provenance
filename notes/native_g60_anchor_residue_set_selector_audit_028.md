# Native G60 anchor residue-set selector audit 028

Status: native_g60_anchor_residue_set_selector_audit_recorded

## Question

Can simple residue-set features select the observed anchor residue sets before cycle ranking?

## Result

- all_checks_pass: `False`
- uses_observed_anchor_residue_sets_for_generation: `False`
- uses_observed_anchor_residue_sets_for_validation: `True`

## Per state

- O0:
  - residue_count_law: `6`
  - observed_anchor_residue_set: `[4, 5, 7, 8, 9, 12]`
  - c_values: `[2, 11, 14]`
  - expected_c_overlap: `[]`
  - relay_hits: `[4, 5, 7]`
  - unique_relay_hits: `[]`
  - candidate_count_after_relay_obligations: `4081`
  - observed_found: `True`
  - observed_candidate_index: `3705`
  - exact_feature_selector_count: `0`
  - exact_feature_selectors_first_30: `[]`
- O1:
  - residue_count_law: `6`
  - observed_anchor_residue_set: `[0, 2, 4, 9, 13, 14]`
  - c_values: `[1, 10, 13]`
  - expected_c_overlap: `[13]`
  - relay_hits: `[2, 4, 9]`
  - unique_relay_hits: `[]`
  - candidate_count_after_relay_obligations: `4081`
  - observed_found: `True`
  - observed_candidate_index: `779`
  - exact_feature_selector_count: `70`
  - exact_feature_selectors_first_30: `[{'features': ['contains_all_relay_hits', 'boundary_supported_pair_count', 'complement_support_weight'], 'observed_values': [True, 29, 41], 'width': 3}, {'features': ['contains_all_relay_hits', 'internal_missing_pair_count', 'boundary_support_weight'], 'observed_values': [True, 4, 56], 'width': 3}, {'features': ['contains_all_relay_hits', 'internal_missing_pair_count', 'complement_support_weight'], 'observed_values': [True, 4, 41], 'width': 3}, {'features': ['contains_all_relay_hits', 'internal_support_weight', 'internal_missing_pair_count'], 'observed_values': [True, 19, 4], 'width': 3}, {'features': ['contains_all_relay_hits', 'internal_supported_pair_count', 'boundary_support_weight'], 'observed_values': [True, 11, 56], 'width': 3}, {'features': ['contains_all_relay_hits', 'internal_supported_pair_count', 'complement_support_weight'], 'observed_values': [True, 11, 41], 'width': 3}, {'features': ['contains_all_relay_hits', 'internal_supported_pair_count', 'internal_support_weight'], 'observed_values': [True, 11, 19], 'width': 3}, {'features': ['relay_hit_overlap_count', 'boundary_supported_pair_count', 'complement_support_weight'], 'observed_values': [3, 29, 41], 'width': 3}, {'features': ['relay_hit_overlap_count', 'internal_missing_pair_count', 'boundary_support_weight'], 'observed_values': [3, 4, 56], 'width': 3}, {'features': ['relay_hit_overlap_count', 'internal_missing_pair_count', 'complement_support_weight'], 'observed_values': [3, 4, 41], 'width': 3}, {'features': ['relay_hit_overlap_count', 'internal_support_weight', 'internal_missing_pair_count'], 'observed_values': [3, 19, 4], 'width': 3}, {'features': ['relay_hit_overlap_count', 'internal_supported_pair_count', 'boundary_support_weight'], 'observed_values': [3, 11, 56], 'width': 3}, {'features': ['relay_hit_overlap_count', 'internal_supported_pair_count', 'complement_support_weight'], 'observed_values': [3, 11, 41], 'width': 3}, {'features': ['relay_hit_overlap_count', 'internal_supported_pair_count', 'internal_support_weight'], 'observed_values': [3, 11, 19], 'width': 3}, {'features': ['relay_hit_overlap_signature', 'boundary_supported_pair_count', 'complement_support_weight'], 'observed_values': ['2,4,9', 29, 41], 'width': 3}, {'features': ['relay_hit_overlap_signature', 'internal_missing_pair_count', 'boundary_support_weight'], 'observed_values': ['2,4,9', 4, 56], 'width': 3}, {'features': ['relay_hit_overlap_signature', 'internal_missing_pair_count', 'complement_support_weight'], 'observed_values': ['2,4,9', 4, 41], 'width': 3}, {'features': ['relay_hit_overlap_signature', 'internal_support_weight', 'internal_missing_pair_count'], 'observed_values': ['2,4,9', 19, 4], 'width': 3}, {'features': ['relay_hit_overlap_signature', 'internal_supported_pair_count', 'boundary_support_weight'], 'observed_values': ['2,4,9', 11, 56], 'width': 3}, {'features': ['relay_hit_overlap_signature', 'internal_supported_pair_count', 'complement_support_weight'], 'observed_values': ['2,4,9', 11, 41], 'width': 3}, {'features': ['relay_hit_overlap_signature', 'internal_supported_pair_count', 'internal_support_weight'], 'observed_values': ['2,4,9', 11, 19], 'width': 3}, {'features': ['span', 'c_overlap_signature', 'contains_all_relay_hits'], 'observed_values': [14, '13', True], 'width': 3}, {'features': ['span', 'c_overlap_signature', 'relay_hit_overlap_count'], 'observed_values': [14, '13', 3], 'width': 3}, {'features': ['span', 'c_overlap_signature', 'relay_hit_overlap_signature'], 'observed_values': [14, '13', '2,4,9'], 'width': 3}, {'features': ['span', 'contains_all_relay_hits', 'complement_support_weight'], 'observed_values': [14, True, 41], 'width': 3}, {'features': ['span', 'contains_all_relay_hits', 'internal_support_weight'], 'observed_values': [14, True, 19], 'width': 3}, {'features': ['span', 'expected_c_overlap_exact', 'contains_all_relay_hits'], 'observed_values': [14, True, True], 'width': 3}, {'features': ['span', 'expected_c_overlap_exact', 'relay_hit_overlap_count'], 'observed_values': [14, True, 3], 'width': 3}, {'features': ['span', 'expected_c_overlap_exact', 'relay_hit_overlap_signature'], 'observed_values': [14, True, '2,4,9'], 'width': 3}, {'features': ['span', 'relay_hit_overlap_count', 'complement_support_weight'], 'observed_values': [14, 3, 41], 'width': 3}]`
- B0:
  - residue_count_law: `5`
  - observed_anchor_residue_set: `[0, 2, 3, 4, 8]`
  - c_values: `[0, 2, 5]`
  - expected_c_overlap: `[0, 2]`
  - relay_hits: `[4, 8]`
  - unique_relay_hits: `[8]`
  - candidate_count_after_relay_obligations: `1001`
  - observed_found: `True`
  - observed_candidate_index: `66`
  - exact_feature_selector_count: `322`
  - exact_feature_selectors_first_30: `[{'features': ['sum_mod15', 'complement_supported_pair_count'], 'observed_values': [2, 23], 'width': 2}, {'features': ['sum_residues', 'boundary_supported_pair_count'], 'observed_values': [17, 33], 'width': 2}, {'features': ['sum_residues', 'complement_support_weight'], 'observed_values': [17, 47], 'width': 2}, {'features': ['sum_residues', 'complement_supported_pair_count'], 'observed_values': [17, 23], 'width': 2}, {'features': ['sum_residues', 'contains_all_relay_hits'], 'observed_values': [17, True], 'width': 2}, {'features': ['sum_residues', 'internal_missing_pair_count'], 'observed_values': [17, 4], 'width': 2}, {'features': ['sum_residues', 'internal_support_weight'], 'observed_values': [17, 11], 'width': 2}, {'features': ['sum_residues', 'internal_supported_pair_count'], 'observed_values': [17, 6], 'width': 2}, {'features': ['sum_residues', 'relay_hit_overlap_count'], 'observed_values': [17, 2], 'width': 2}, {'features': ['sum_residues', 'relay_hit_overlap_signature'], 'observed_values': [17, '4,8'], 'width': 2}, {'features': ['boundary_supported_pair_count', 'boundary_support_weight', 'complement_supported_pair_count'], 'observed_values': [33, 58, 23], 'width': 3}, {'features': ['boundary_supported_pair_count', 'complement_supported_pair_count', 'complement_support_weight'], 'observed_values': [33, 23, 47], 'width': 3}, {'features': ['c_overlap_count', 'boundary_support_weight', 'complement_supported_pair_count'], 'observed_values': [2, 58, 23], 'width': 3}, {'features': ['c_overlap_count', 'boundary_supported_pair_count', 'boundary_support_weight'], 'observed_values': [2, 33, 58], 'width': 3}, {'features': ['c_overlap_count', 'boundary_supported_pair_count', 'complement_support_weight'], 'observed_values': [2, 33, 47], 'width': 3}, {'features': ['c_overlap_count', 'complement_supported_pair_count', 'complement_support_weight'], 'observed_values': [2, 23, 47], 'width': 3}, {'features': ['c_overlap_count', 'contains_all_relay_hits', 'boundary_supported_pair_count'], 'observed_values': [2, True, 33], 'width': 3}, {'features': ['c_overlap_count', 'contains_all_relay_hits', 'complement_support_weight'], 'observed_values': [2, True, 47], 'width': 3}, {'features': ['c_overlap_count', 'contains_all_relay_hits', 'complement_supported_pair_count'], 'observed_values': [2, True, 23], 'width': 3}, {'features': ['c_overlap_count', 'internal_support_weight', 'boundary_supported_pair_count'], 'observed_values': [2, 11, 33], 'width': 3}, {'features': ['c_overlap_count', 'internal_support_weight', 'complement_supported_pair_count'], 'observed_values': [2, 11, 23], 'width': 3}, {'features': ['c_overlap_count', 'relay_hit_overlap_count', 'boundary_supported_pair_count'], 'observed_values': [2, 2, 33], 'width': 3}, {'features': ['c_overlap_count', 'relay_hit_overlap_count', 'complement_support_weight'], 'observed_values': [2, 2, 47], 'width': 3}, {'features': ['c_overlap_count', 'relay_hit_overlap_count', 'complement_supported_pair_count'], 'observed_values': [2, 2, 23], 'width': 3}, {'features': ['c_overlap_count', 'relay_hit_overlap_signature', 'boundary_supported_pair_count'], 'observed_values': [2, '4,8', 33], 'width': 3}, {'features': ['c_overlap_count', 'relay_hit_overlap_signature', 'complement_support_weight'], 'observed_values': [2, '4,8', 47], 'width': 3}, {'features': ['c_overlap_count', 'relay_hit_overlap_signature', 'complement_supported_pair_count'], 'observed_values': [2, '4,8', 23], 'width': 3}, {'features': ['c_overlap_signature', 'boundary_support_weight', 'complement_supported_pair_count'], 'observed_values': ['0,2', 58, 23], 'width': 3}, {'features': ['c_overlap_signature', 'boundary_supported_pair_count', 'boundary_support_weight'], 'observed_values': ['0,2', 33, 58], 'width': 3}, {'features': ['c_overlap_signature', 'boundary_supported_pair_count', 'complement_support_weight'], 'observed_values': ['0,2', 33, 47], 'width': 3}]`
- B1:
  - residue_count_law: `6`
  - observed_anchor_residue_set: `[2, 3, 7, 8, 10, 13]`
  - c_values: `[2, 4, 5]`
  - expected_c_overlap: `[2]`
  - relay_hits: `[8, 10, 13]`
  - unique_relay_hits: `[8]`
  - candidate_count_after_relay_obligations: `2002`
  - observed_found: `True`
  - observed_candidate_index: `1302`
  - exact_feature_selector_count: `44`
  - exact_feature_selectors_first_30: `[{'features': ['sum_mod15', 'c_overlap_signature', 'boundary_support_weight'], 'observed_values': [13, '2', 66], 'width': 3}, {'features': ['sum_mod15', 'c_overlap_signature', 'boundary_supported_pair_count'], 'observed_values': [13, '2', 36], 'width': 3}, {'features': ['sum_mod15', 'c_overlap_signature', 'complement_support_weight'], 'observed_values': [13, '2', 35], 'width': 3}, {'features': ['sum_mod15', 'c_overlap_signature', 'internal_support_weight'], 'observed_values': [13, '2', 15], 'width': 3}, {'features': ['sum_mod15', 'contains_all_relay_hits', 'complement_support_weight'], 'observed_values': [13, True, 35], 'width': 3}, {'features': ['sum_mod15', 'expected_c_overlap_exact', 'boundary_support_weight'], 'observed_values': [13, True, 66], 'width': 3}, {'features': ['sum_mod15', 'expected_c_overlap_exact', 'boundary_supported_pair_count'], 'observed_values': [13, True, 36], 'width': 3}, {'features': ['sum_mod15', 'expected_c_overlap_exact', 'complement_support_weight'], 'observed_values': [13, True, 35], 'width': 3}, {'features': ['sum_mod15', 'expected_c_overlap_exact', 'internal_support_weight'], 'observed_values': [13, True, 15], 'width': 3}, {'features': ['sum_mod15', 'min_residue', 'boundary_supported_pair_count'], 'observed_values': [13, 2, 36], 'width': 3}, {'features': ['sum_mod15', 'min_residue', 'complement_support_weight'], 'observed_values': [13, 2, 35], 'width': 3}, {'features': ['sum_mod15', 'min_residue', 'complement_supported_pair_count'], 'observed_values': [13, 2, 19], 'width': 3}, {'features': ['sum_mod15', 'relay_hit_overlap_count', 'complement_support_weight'], 'observed_values': [13, 3, 35], 'width': 3}, {'features': ['sum_mod15', 'relay_hit_overlap_signature', 'complement_support_weight'], 'observed_values': [13, '8,10,13', 35], 'width': 3}, {'features': ['sum_residues', 'c_overlap_signature', 'boundary_support_weight'], 'observed_values': [43, '2', 66], 'width': 3}, {'features': ['sum_residues', 'c_overlap_signature', 'boundary_supported_pair_count'], 'observed_values': [43, '2', 36], 'width': 3}, {'features': ['sum_residues', 'c_overlap_signature', 'complement_support_weight'], 'observed_values': [43, '2', 35], 'width': 3}, {'features': ['sum_residues', 'c_overlap_signature', 'complement_supported_pair_count'], 'observed_values': [43, '2', 19], 'width': 3}, {'features': ['sum_residues', 'c_overlap_signature', 'internal_support_weight'], 'observed_values': [43, '2', 15], 'width': 3}, {'features': ['sum_residues', 'contains_all_relay_hits', 'boundary_support_weight'], 'observed_values': [43, True, 66], 'width': 3}, {'features': ['sum_residues', 'contains_all_relay_hits', 'complement_support_weight'], 'observed_values': [43, True, 35], 'width': 3}, {'features': ['sum_residues', 'contains_all_relay_hits', 'internal_support_weight'], 'observed_values': [43, True, 15], 'width': 3}, {'features': ['sum_residues', 'expected_c_overlap_exact', 'boundary_support_weight'], 'observed_values': [43, True, 66], 'width': 3}, {'features': ['sum_residues', 'expected_c_overlap_exact', 'boundary_supported_pair_count'], 'observed_values': [43, True, 36], 'width': 3}, {'features': ['sum_residues', 'expected_c_overlap_exact', 'complement_support_weight'], 'observed_values': [43, True, 35], 'width': 3}, {'features': ['sum_residues', 'expected_c_overlap_exact', 'complement_supported_pair_count'], 'observed_values': [43, True, 19], 'width': 3}, {'features': ['sum_residues', 'expected_c_overlap_exact', 'internal_support_weight'], 'observed_values': [43, True, 15], 'width': 3}, {'features': ['sum_residues', 'internal_missing_pair_count', 'complement_support_weight'], 'observed_values': [43, 8, 35], 'width': 3}, {'features': ['sum_residues', 'internal_support_weight', 'boundary_supported_pair_count'], 'observed_values': [43, 15, 36], 'width': 3}, {'features': ['sum_residues', 'internal_support_weight', 'complement_supported_pair_count'], 'observed_values': [43, 15, 19], 'width': 3}]`

## Checks

- unlifted_relay_cover_011_theorem_pass: `True`
- candidate_census_020_theorem_pass: `True`
- direct_assault_027_recorded: `True`
- g60_edge_count_is_120: `True`
- all_observed_residue_sets_found: `True`
- all_states_have_exact_feature_selector: `False`

## Interpretation

Artifact 027 showed that the global cycle universe is too broad. This audit moves one layer earlier and asks whether simple residue-set features can identify the observed anchor residue sets before cycle ranking. Exact feature selectors here are candidate directions, not final native provenance unless independently justified.

## Boundary

This is a residue-set feature audit. It does not derive a native selector theorem by itself, does not test station fields, does not select unique relay mediators, does not derive the full role-labeled shared_B universe, and does not close Gap A.
