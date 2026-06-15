# Upstream station provenance locator 039

Status: upstream_station_provenance_locator_recorded

## Result

- scan_root_count: `7`
- json_files_scanned: `764`
- useful_file_count: `87`
- rich_station_file_count: `57`
- has_slot_or_fiber: `True`
- has_AB_fields: `True`
- has_role_pair_fields: `True`
- has_column_address_fields: `True`
- locator_complete: `True`

## High-value key totals

- source: `14847`
- kind: `14432`
- from_C: `2369`
- to_C: `2307`
- from_slot: `1852`
- from_B: `1847`
- from_A: `1845`
- slot: `1806`
- target: `1694`
- station_role: `1646`
- to_slot: `894`
- to_B: `889`
- to_A: `888`
- role_pair: `843`
- from_fiber: `772`
- lift_q: `699`
- edge_role: `645`
- to_fiber: `631`
- sign: `291`
- fiber: `139`
- C: `128`
- reverse_partner: `96`
- shared_B: `96`
- B: `71`
- A: `68`
- sheet: `35`
- role: `30`
- columns: `8`

## Top rich station files

1. `18-g900-kernel-admission/artifacts/json/wxyzti_station_provenance_law_audit_010.v1.json`
   - score: `150`
   - key_counts: `{'from_A': 48, 'from_B': 48, 'from_C': 48, 'from_fiber': 48, 'from_slot': 48, 'to_A': 48, 'to_B': 48, 'to_C': 48, 'to_fiber': 48, 'to_slot': 48, 'station_role': 30, 'role_pair': 27, 'lift_q': 24, 'source': 24, 'edge_role': 24, 'reverse_partner': 1, 'shared_B': 1}`
   - role_token_counts: `{'shared_B': 27, 'reverse_partner': 27, 'WX': 17, 'YZ': 17, 'TI': 17, 'XY': 17, 'ZT': 17, 'IW': 17}`
   - state_token_counts: `{}`
   - first_example_path: `$`
   - first_example_record: `{'boundary': 'This audits only realized station rows. It does not compare against non-realized candidate rows, does not prove a complete generator, and does not close Gap A.', 'deterministic_test_count': 96, 'exact_deterministic_test_count': 23, 'exact_deterministic_tests_first_40': '[list len 23]', 'input': '/data/data/com.termux/files/home/dev/cori/research/thalean-graph-theory/18-g900-kernel-admission/artifacts/json/wxyzti_station_transition_feature_inspection_009.v1.json', 'interpretation': 'This audits realized WXYZTI station rows for provenance laws. It checks field deltas, same-field constraints, and deterministic maps such as station_role+from_C -> to_C.', 'role_class_counts': '{dict keys 2}', 'role_class_summary': '[list len 2]', 'role_counts': '{dict keys 6}', 'role_pair_counts': '{dict keys 3}', 'role_pair_summary': '[list len 3]', 'rows': '[list len 24]', 'semantic_row_count': 24, 'station_role_summary': '[list len 6]', 'status': 'wxyzti_station_provenance_law_audit_recorded'}`
2. `21-gap-a-answer-pair-generator/source/project18_artifacts/json/wxyzti_station_provenance_law_audit_010.v1.json`
   - score: `150`
   - key_counts: `{'from_A': 48, 'from_B': 48, 'from_C': 48, 'from_fiber': 48, 'from_slot': 48, 'to_A': 48, 'to_B': 48, 'to_C': 48, 'to_fiber': 48, 'to_slot': 48, 'station_role': 30, 'role_pair': 27, 'lift_q': 24, 'source': 24, 'edge_role': 24, 'reverse_partner': 1, 'shared_B': 1}`
   - role_token_counts: `{'shared_B': 27, 'reverse_partner': 27, 'WX': 17, 'YZ': 17, 'TI': 17, 'XY': 17, 'ZT': 17, 'IW': 17}`
   - state_token_counts: `{}`
   - first_example_path: `$`
   - first_example_record: `{'boundary': 'This audits only realized station rows. It does not compare against non-realized candidate rows, does not prove a complete generator, and does not close Gap A.', 'deterministic_test_count': 96, 'exact_deterministic_test_count': 23, 'exact_deterministic_tests_first_40': '[list len 23]', 'input': '/data/data/com.termux/files/home/dev/cori/research/thalean-graph-theory/18-g900-kernel-admission/artifacts/json/wxyzti_station_transition_feature_inspection_009.v1.json', 'interpretation': 'This audits realized WXYZTI station rows for provenance laws. It checks field deltas, same-field constraints, and deterministic maps such as station_role+from_C -> to_C.', 'role_class_counts': '{dict keys 2}', 'role_class_summary': '[list len 2]', 'role_counts': '{dict keys 6}', 'role_pair_counts': '{dict keys 3}', 'role_pair_summary': '[list len 3]', 'rows': '[list len 24]', 'semantic_row_count': 24, 'station_role_summary': '[list len 6]', 'status': 'wxyzti_station_provenance_law_audit_recorded'}`
3. `18-g900-kernel-admission/artifacts/json/wxyzti_g30_shadow_sheet_audit_011.v1.json`
   - score: `150`
   - key_counts: `{'from_A': 48, 'from_B': 48, 'from_C': 48, 'from_fiber': 48, 'from_slot': 48, 'to_A': 48, 'to_B': 48, 'to_C': 48, 'to_fiber': 48, 'to_slot': 48, 'station_role': 30, 'role_pair': 27, 'lift_q': 26, 'source': 24, 'edge_role': 24}`
   - role_token_counts: `{'shared_B': 24, 'reverse_partner': 24, 'WX': 15, 'YZ': 15, 'TI': 15, 'XY': 15, 'ZT': 15, 'IW': 15}`
   - state_token_counts: `{}`
   - first_example_path: `$`
   - first_example_record: `{'all_fiber_mod15_delta_equals_C_delta': True, 'all_fiber_sheet15_delta_equals_lift_q': False, 'all_from_fiber_mod15_equals_from_C': True, 'all_q3_sheet30_rule': False, 'all_to_fiber_mod15_equals_to_C': True, 'boundary': 'This is a coordinate-shadow audit over realized WXYZTI rows only. It does not prove a complete generator, does not derive G60-native structure, and does not close Gap A.', 'exact_deterministic_test_count': 50, 'exact_deterministic_tests_first_50': '[list len 50]', 'from_fiber_sheet15_summary': '[list len 1]', 'from_fiber_sheet30_summary': '[list len 1]', 'input': '/data/data/com.termux/files/home/dev/cori/research/thalean-graph-theory/18-g900-kernel-admission/artifacts/json/wxyzti_station_provenance_law_audit_010.v1.json', 'interpretation': 'This tests whether the WXYZTI realized rows expose a G30 two-sheet shadow or a cleaner four-sheet G15 lift inside the G60 fiber coordinates.', 'lift_q_summary': '[list len 2]', 'role_pair_summary': '[list len 3]', 'row_count': 24, 'rows': '[list len 24]'}`
4. `21-gap-a-answer-pair-generator/source/project18_artifacts/json/wxyzti_g30_shadow_sheet_audit_011.v1.json`
   - score: `150`
   - key_counts: `{'from_A': 48, 'from_B': 48, 'from_C': 48, 'from_fiber': 48, 'from_slot': 48, 'to_A': 48, 'to_B': 48, 'to_C': 48, 'to_fiber': 48, 'to_slot': 48, 'station_role': 30, 'role_pair': 27, 'lift_q': 26, 'source': 24, 'edge_role': 24}`
   - role_token_counts: `{'shared_B': 24, 'reverse_partner': 24, 'WX': 15, 'YZ': 15, 'TI': 15, 'XY': 15, 'ZT': 15, 'IW': 15}`
   - state_token_counts: `{}`
   - first_example_path: `$`
   - first_example_record: `{'all_fiber_mod15_delta_equals_C_delta': True, 'all_fiber_sheet15_delta_equals_lift_q': False, 'all_from_fiber_mod15_equals_from_C': True, 'all_q3_sheet30_rule': False, 'all_to_fiber_mod15_equals_to_C': True, 'boundary': 'This is a coordinate-shadow audit over realized WXYZTI rows only. It does not prove a complete generator, does not derive G60-native structure, and does not close Gap A.', 'exact_deterministic_test_count': 50, 'exact_deterministic_tests_first_50': '[list len 50]', 'from_fiber_sheet15_summary': '[list len 1]', 'from_fiber_sheet30_summary': '[list len 1]', 'input': '/data/data/com.termux/files/home/dev/cori/research/thalean-graph-theory/18-g900-kernel-admission/artifacts/json/wxyzti_station_provenance_law_audit_010.v1.json', 'interpretation': 'This tests whether the WXYZTI realized rows expose a G30 two-sheet shadow or a cleaner four-sheet G15 lift inside the G60 fiber coordinates.', 'lift_q_summary': '[list len 2]', 'role_pair_summary': '[list len 3]', 'row_count': 24, 'rows': '[list len 24]'}`
5. `18-g900-kernel-admission/artifacts/json/wxyzti_same_sheet_wrap_carry_audit_012.v1.json`
   - score: `150`
   - key_counts: `{'from_A': 48, 'from_B': 48, 'from_C': 48, 'from_fiber': 48, 'from_slot': 48, 'to_A': 48, 'to_B': 48, 'to_C': 48, 'to_fiber': 48, 'to_slot': 48, 'station_role': 30, 'role_pair': 27, 'lift_q': 24, 'source': 24, 'edge_role': 24}`
   - role_token_counts: `{'shared_B': 24, 'reverse_partner': 24, 'WX': 15, 'YZ': 15, 'TI': 15, 'XY': 15, 'ZT': 15, 'IW': 15}`
   - state_token_counts: `{}`
   - first_example_path: `$`
   - first_example_record: `{'all_predicted_fiber_delta_matches': True, 'all_predicted_lift_q_matches': True, 'all_same_sheet15': True, 'all_same_sheet30': True, 'boundary': 'This is an exact law over realized WXYZTI station rows. It does not generate the allowed transitions from a larger candidate universe, does not derive G60-native structure, and does not close Gap A.', 'input': '/data/data/com.termux/files/home/dev/cori/research/thalean-graph-theory/18-g900-kernel-admission/artifacts/json/wxyzti_g30_shadow_sheet_audit_011.v1.json', 'integer_C_delta_counts': '{dict keys 9}', 'law': 'For realized WXYZTI rows, endpoints preserve the same 15-sheet and 30-sheet. The lift q is determined by ordinary integer C wrap: q=0 when to_C-from_C >= 0, q=3 when to_C-from_C < 0. The fiber delta is (to_C-from_C) mod 60.', 'lift_q_counts': '{dict keys 2}', 'role_pair_summary': '[list len 3]', 'row_count': 24, 'rows': '[list len 24]', 'station_role_summary': '[list len 6]', 'status': 'wxyzti_same_sheet_wrap_carry_audit_recorded', 'wrap_flag_counts': '{dict keys 2}'}`
6. `21-gap-a-answer-pair-generator/source/project18_artifacts/json/wxyzti_same_sheet_wrap_carry_audit_012.v1.json`
   - score: `150`
   - key_counts: `{'from_A': 48, 'from_B': 48, 'from_C': 48, 'from_fiber': 48, 'from_slot': 48, 'to_A': 48, 'to_B': 48, 'to_C': 48, 'to_fiber': 48, 'to_slot': 48, 'station_role': 30, 'role_pair': 27, 'lift_q': 24, 'source': 24, 'edge_role': 24}`
   - role_token_counts: `{'shared_B': 24, 'reverse_partner': 24, 'WX': 15, 'YZ': 15, 'TI': 15, 'XY': 15, 'ZT': 15, 'IW': 15}`
   - state_token_counts: `{}`
   - first_example_path: `$`
   - first_example_record: `{'all_predicted_fiber_delta_matches': True, 'all_predicted_lift_q_matches': True, 'all_same_sheet15': True, 'all_same_sheet30': True, 'boundary': 'This is an exact law over realized WXYZTI station rows. It does not generate the allowed transitions from a larger candidate universe, does not derive G60-native structure, and does not close Gap A.', 'input': '/data/data/com.termux/files/home/dev/cori/research/thalean-graph-theory/18-g900-kernel-admission/artifacts/json/wxyzti_g30_shadow_sheet_audit_011.v1.json', 'integer_C_delta_counts': '{dict keys 9}', 'law': 'For realized WXYZTI rows, endpoints preserve the same 15-sheet and 30-sheet. The lift q is determined by ordinary integer C wrap: q=0 when to_C-from_C >= 0, q=3 when to_C-from_C < 0. The fiber delta is (to_C-from_C) mod 60.', 'lift_q_counts': '{dict keys 2}', 'role_pair_summary': '[list len 3]', 'row_count': 24, 'rows': '[list len 24]', 'station_role_summary': '[list len 6]', 'status': 'wxyzti_same_sheet_wrap_carry_audit_recorded', 'wrap_flag_counts': '{dict keys 2}'}`
7. `21-gap-a-answer-pair-generator/source/project18_artifacts/json/wxyzti_role_class_invariant_audit_018.v1.json`
   - score: `145`
   - key_counts: `{'from_A': 72, 'from_B': 72, 'from_C': 72, 'from_fiber': 72, 'from_slot': 72, 'lift_q': 72, 'role_pair': 72, 'station_role': 72, 'to_A': 72, 'to_B': 72, 'to_C': 72, 'to_fiber': 72, 'to_slot': 72}`
   - role_token_counts: `{'shared_B': 44, 'reverse_partner': 44, 'WX': 38, 'YZ': 38, 'TI': 38, 'XY': 38, 'ZT': 38, 'IW': 38}`
   - state_token_counts: `{}`
   - first_example_path: `$`
   - first_example_record: `{'boundary': 'This is an invariant audit over realized station rows only. It does not generate the allowed transitions from a non-realized candidate universe and does not close Gap A.', 'input': '/Users/scottcave/dev/cori/research/thalean-graph-theory/18-g900-kernel-admission/artifacts/json/wxyzti_same_sheet_wrap_carry_audit_012.v1.json', 'interpretation': 'This audits preservation and equality invariants for reverse_partner and shared_B WXYZTI station rows. It tests whether reverse_partner and shared_B are distinguished by preserving A vs B/slot.', 'reverse_partner_summary': '{dict keys 12}', 'role_pair_summaries': '[list len 3]', 'row_count': 24, 'shared_B_summary': '{dict keys 12}', 'station_summaries': '[list len 6]', 'status': 'wxyzti_role_class_invariant_audit_recorded'}`
8. `18-g900-kernel-admission/artifacts/json/wxyzti_ambiguous_source_split_audit_014.v1.json`
   - score: `145`
   - key_counts: `{'target': 29, 'from_C': 10, 'station_role': 10, 'from_A': 8, 'from_B': 8, 'from_fiber': 8, 'from_slot': 8, 'lift_q': 8, 'role_pair': 8, 'to_A': 8, 'to_B': 8, 'to_C': 8, 'to_fiber': 8, 'to_slot': 8}`
   - role_token_counts: `{'YZ': 19, 'IW': 19, 'shared_B': 7, 'reverse_partner': 7}`
   - state_token_counts: `{}`
   - first_example_path: `$.ambiguous_station_sources[0]`
   - first_example_record: `{'from_C': 5, 'station_role': 'IW'}`
9. `21-gap-a-answer-pair-generator/source/project18_artifacts/json/wxyzti_ambiguous_source_split_audit_014.v1.json`
   - score: `145`
   - key_counts: `{'target': 29, 'from_C': 10, 'station_role': 10, 'from_A': 8, 'from_B': 8, 'from_fiber': 8, 'from_slot': 8, 'lift_q': 8, 'role_pair': 8, 'to_A': 8, 'to_B': 8, 'to_C': 8, 'to_fiber': 8, 'to_slot': 8}`
   - role_token_counts: `{'YZ': 19, 'IW': 19, 'shared_B': 7, 'reverse_partner': 7}`
   - state_token_counts: `{}`
   - first_example_path: `$.ambiguous_station_sources[0]`
   - first_example_record: `{'from_C': 5, 'station_role': 'IW'}`
10. `18-g900-kernel-admission/artifacts/json/wxyzti_reverse_partner_vs_sharedB_audit_016.v1.json`
   - score: `135`
   - key_counts: `{'from_A': 528, 'from_B': 528, 'from_C': 528, 'from_slot': 528, 'station_role': 528, 'to_C': 528, 'lift_q': 48, 'role_pair': 48, 'to_A': 48, 'to_B': 48, 'to_slot': 48}`
   - role_token_counts: `{'WX': 123, 'YZ': 123, 'TI': 123, 'XY': 123, 'ZT': 123, 'IW': 123, 'shared_B': 29, 'reverse_partner': 29}`
   - state_token_counts: `{}`
   - first_example_path: `$`
   - first_example_record: `{'boundary': 'This audits realized rows only. It does not prove selection from non-realized candidates and does not close Gap A.', 'input': '/Users/scottcave/dev/cori/research/thalean-graph-theory/18-g900-kernel-admission/artifacts/json/wxyzti_same_sheet_wrap_carry_audit_012.v1.json', 'interpretation': 'This isolates the clean reverse_partner law from the shared_B residual. It tests simple source-field laws for to_C across role classes and station roles.', 'reverse_partner_summary': '{dict keys 9}', 'row_count': 24, 'shared_B_summary': '{dict keys 9}', 'station_summaries': '[list len 6]', 'status': 'wxyzti_reverse_partner_vs_sharedB_audit_recorded'}`
11. `21-gap-a-answer-pair-generator/source/project18_artifacts/json/wxyzti_reverse_partner_vs_sharedB_audit_016.v1.json`
   - score: `135`
   - key_counts: `{'from_A': 528, 'from_B': 528, 'from_C': 528, 'from_slot': 528, 'station_role': 528, 'to_C': 528, 'lift_q': 48, 'role_pair': 48, 'to_A': 48, 'to_B': 48, 'to_slot': 48}`
   - role_token_counts: `{'WX': 123, 'YZ': 123, 'TI': 123, 'XY': 123, 'ZT': 123, 'IW': 123, 'shared_B': 29, 'reverse_partner': 29}`
   - state_token_counts: `{}`
   - first_example_path: `$`
   - first_example_record: `{'boundary': 'This audits realized rows only. It does not prove selection from non-realized candidates and does not close Gap A.', 'input': '/Users/scottcave/dev/cori/research/thalean-graph-theory/18-g900-kernel-admission/artifacts/json/wxyzti_same_sheet_wrap_carry_audit_012.v1.json', 'interpretation': 'This isolates the clean reverse_partner law from the shared_B residual. It tests simple source-field laws for to_C across role classes and station roles.', 'reverse_partner_summary': '{dict keys 9}', 'row_count': 24, 'shared_B_summary': '{dict keys 9}', 'station_summaries': '[list len 6]', 'status': 'wxyzti_reverse_partner_vs_sharedB_audit_recorded'}`
12. `21-gap-a-answer-pair-generator/source/project18_artifacts/json/wxyzti_answer_pair_candidate_universe_audit_022.v1.json`
   - score: `135`
   - key_counts: `{'role_pair': 126, 'from_A': 84, 'from_B': 84, 'from_C': 84, 'from_slot': 84, 'lift_q': 84, 'station_role': 84, 'to_A': 84, 'to_B': 84, 'to_C': 84, 'to_slot': 84}`
   - role_token_counts: `{'shared_B': 85, 'reverse_partner': 85, 'YZ': 55, 'TI': 55, 'XY': 55, 'IW': 55, 'WX': 35, 'ZT': 35}`
   - state_token_counts: `{}`
   - first_example_path: `$`
   - first_example_record: `{'accepted_strict_pairs': '[list len 12]', 'boundary': 'This is still a row-pair candidate universe built from realized WXYZTI rows. It is stronger than a realized-pair audit, but it is not a native G60 generator and does not close Gap A.', 'candidate_count': 48, 'candidate_role_pair_counts': '{dict keys 3}', 'candidate_universe': 'All shared_B rows crossed with all reverse_partner rows having the same role_pair.', 'exact_selectors': ['reciprocal_answer_pair', 'strict_pair_grammar'], 'expected_pair_count': 12, 'expected_role_pair_counts': '{dict keys 3}', 'input_pairs': '/Users/scottcave/dev/cori/research/thalean-graph-theory/18-g900-kernel-admission/artifacts/json/wxyzti_shared_reverse_pair_coupling_audit_021.v1.json', 'input_rows': '/Users/scottcave/dev/cori/research/thalean-graph-theory/18-g900-kernel-admission/artifacts/json/wxyzti_same_sheet_wrap_carry_audit_012.v1.json', 'interpretation': 'The candidate universe is broader than the realized reciprocal pairs: every shared_B row is crossed with every reverse_partner row in the same role_pair. The strict pair grammar tests whether reciprocal answer coupling selects exactly the 12 realized pairs.', 'rejected_strict_pairs_first_30': '[list len 30]', 'reverse_row_count': 12, 'selector_scores': '[list len 12]', 'shared_row_count': 12, 'status': 'wxyzti_answer_pair_candidate_universe_audit_recorded'}`
13. `21-gap-a-answer-pair-generator/artifacts/json/synthetic_pair_skeleton_universe_003.v1.json`
   - score: `135`
   - key_counts: `{'from_A': 48, 'from_B': 48, 'from_C': 48, 'from_slot': 48, 'lift_q': 48, 'role_pair': 48, 'station_role': 48, 'to_A': 48, 'to_B': 48, 'to_C': 48, 'to_slot': 48}`
   - role_token_counts: `{'shared_B': 61, 'reverse_partner': 61, 'WX': 29, 'YZ': 29, 'TI': 29, 'XY': 29, 'ZT': 29, 'IW': 29}`
   - state_token_counts: `{}`
   - first_example_path: `$`
   - first_example_record: `{'audit_id': '003', 'boundary': 'This is not Gap A closure. It uses selected transition keys from 002, and it uses realized rows only for evaluation. It does not yet generate the transition support or the A/B assignments natively.', 'free_variable_count_per_key': 4, 'input_realized_rows_for_evaluation_only': '/data/data/com.termux/files/home/dev/cori/research/thalean-graph-theory/21-gap-a-answer-pair-generator/source/project18_artifacts/json/wxyzti_same_sheet_wrap_carry_audit_012.v1.json', 'input_selector_002': '/data/data/com.termux/files/home/dev/cori/research/thalean-graph-theory/21-gap-a-answer-pair-generator/artifacts/json/admission_blind_row_pair_selector_002.v1.json', 'interpretation': 'Given the selected transition key and reciprocal station roles, the pair grammar still leaves four mod-15 degrees of freedom: S.from_A, S.B/slot, S.to_A, and R.from_A. The synthetic skeleton universe therefore overgenerates heavily. This identifies the next native-generator problem: select the missing A/B assignments without using realized rows.', 'matched_examples_first_20': '[list len 12]', 'overgeneration_factor_per_realized_pair': 50625, 'per_key': '[list len 12]', 'realized_pair_signature_count': 12, 'selected_key_count': 12, 'status': 'synthetic_pair_skeleton_universe_recorded', 'synthetic_candidate_count_per_key': 50625, 'total_realized_match_count': 12, 'total_synthetic_candidate_count': 607500, 'uses_project18_expected_pair_records': False}`
14. `21-gap-a-answer-pair-generator/source/project18_artifacts/json/wxyzti_station_transform_map_audit_019.v1.json`
   - score: `135`
   - key_counts: `{'station_role': 60, 'role_pair': 48, 'from_A': 24, 'from_B': 24, 'from_C': 24, 'from_slot': 24, 'lift_q': 24, 'to_A': 24, 'to_B': 24, 'to_C': 24, 'to_slot': 24}`
   - role_token_counts: `{'shared_B': 28, 'WX': 22, 'YZ': 22, 'TI': 22, 'XY': 19, 'ZT': 19, 'IW': 19, 'reverse_partner': 1}`
   - state_token_counts: `{}`
   - first_example_path: `$`
   - first_example_record: `{'boundary': 'This audits realized station rows only. It does not generate shared_B from a non-realized candidate universe and does not close Gap A.', 'input': '/Users/scottcave/dev/cori/research/thalean-graph-theory/18-g900-kernel-admission/artifacts/json/wxyzti_same_sheet_wrap_carry_audit_012.v1.json', 'interpretation': 'This writes the reverse_partner side as an explicit station transform and profiles the remaining shared_B transform by station role. reverse_partner should be exactly (A,B,C)->(A,C,B). shared_B preserves B/slot but has residual A/C motion.', 'name': 'all_rows', 'reverse_partner_matches': '[list len 12]', 'reverse_partner_misses': [], 'reverse_partner_row_count': 12, 'reverse_partner_swap_BC_exact': True, 'reverse_partner_swap_BC_match_count': 12, 'reverse_partner_swap_BC_miss_count': 0, 'row_count': 24, 'shared_B_by_role': '{dict keys 3}', 'shared_B_delta_counts': '{dict keys 12}', 'shared_B_items': '[list len 12]', 'shared_B_row_count': 12, 'status': 'wxyzti_station_transform_map_audit_recorded'}`
15. `21-gap-a-answer-pair-generator/artifacts/json/triangle_frame_assignment_audit_006.v1.json`
   - score: `135`
   - key_counts: `{'role_pair': 48, 'from_A': 24, 'from_B': 24, 'from_C': 24, 'from_slot': 24, 'lift_q': 24, 'station_role': 24, 'to_A': 24, 'to_B': 24, 'to_C': 24, 'to_slot': 24}`
   - role_token_counts: `{'shared_B': 37, 'reverse_partner': 37, 'WX': 18, 'YZ': 18, 'TI': 18, 'XY': 18, 'ZT': 18, 'IW': 18}`
   - state_token_counts: `{}`
   - first_example_path: `$`
   - first_example_record: `{'audit_id': '006', 'boundary': 'This is an exploratory frame audit over realized WXYZTI rows. It does not generate the C-transition support or the A/B assignments natively. It is not Gap A closure.', 'candidate_count': 48, 'candidate_universe': 'All shared_B rows crossed with all reverse_partner rows having the same role_pair.', 'input_rows': '/data/data/com.termux/files/home/dev/cori/research/thalean-graph-theory/21-gap-a-answer-pair-generator/source/project18_artifacts/json/wxyzti_same_sheet_wrap_carry_audit_012.v1.json', 'interpretation': 'The triangle-frame predicate selects the same 12-style structure from the 48 row-pair candidate universe, but phrases the selector geometrically: fixed B face plus fixed A answer face, joined by forward and return C seams.', 'selected_C_tracks': '[list len 12]', 'selected_count': 12, 'selected_frames': '[list len 12]', 'selected_role_pair_counts': '{dict keys 3}', 'sketch_reading': 'The hand sketch is interpreted as one ABC triangle with two complementary readings. The shared_B reading fixes B and lets A/C move. The reverse_partner reading fixes A and swaps B/C. A selected answer-pair is where both readings close on the same C-track.', 'status': 'triangle_frame_assignment_audit_recorded'}`
16. `21-gap-a-answer-pair-generator/source/project18_artifacts/json/wxyzti_shared_reverse_pair_coupling_audit_021.v1.json`
   - score: `135`
   - key_counts: `{'from_A': 24, 'from_B': 24, 'from_C': 24, 'from_slot': 24, 'lift_q': 24, 'role_pair': 24, 'station_role': 24, 'to_A': 24, 'to_B': 24, 'to_C': 24, 'to_slot': 24}`
   - role_token_counts: `{'shared_B': 25, 'reverse_partner': 25, 'WX': 14, 'YZ': 14, 'TI': 14, 'XY': 14, 'ZT': 14, 'IW': 14}`
   - state_token_counts: `{}`
   - first_example_path: `$`
   - first_example_record: `{'bad_bucket_count': 0, 'bad_buckets': [], 'boundary': 'This audits realized reciprocal pairs only. It does not generate the pair set from a non-realized candidate universe and does not close Gap A.', 'exact_true_flag_count': 16, 'exact_true_flags': '[list len 16]', 'flag_counts': '{dict keys 16}', 'input': '/Users/scottcave/dev/cori/research/thalean-graph-theory/18-g900-kernel-admission/artifacts/json/wxyzti_same_sheet_wrap_carry_audit_012.v1.json', 'interpretation': "This pairs each shared_B row with its reciprocal reverse_partner row using (role_pair, from_C, to_C). It tests whether shared_B's target is coupled to the neighboring reverse_partner row rather than explained by a standalone formula.", 'pair_count': 12, 'pair_records': '[list len 12]', 'partial_flags': '{dict keys 0}', 'reverse_role_counts': '{dict keys 3}', 'shared_role_counts': '{dict keys 3}', 'status': 'wxyzti_shared_reverse_pair_coupling_audit_recorded'}`
17. `21-gap-a-answer-pair-generator/source/project18_artifacts/json/wxyzti_sharedB_residual_law_search_017.v1.json`
   - score: `135`
   - key_counts: `{'station_role': 15, 'from_A': 12, 'from_B': 12, 'from_C': 12, 'from_slot': 12, 'lift_q': 12, 'role_pair': 12, 'to_A': 12, 'to_B': 12, 'to_C': 12, 'to_slot': 12}`
   - role_token_counts: `{'shared_B': 16, 'XY': 7, 'ZT': 7, 'IW': 7, 'WX': 6, 'YZ': 6, 'TI': 6}`
   - state_token_counts: `{}`
   - first_example_path: `$`
   - first_example_record: `{'boundary': 'This is over realized rows only. Role-specific affine laws may be descriptive or overfit; they do not prove selection from non-realized candidates and do not close Gap A.', 'input': '/Users/scottcave/dev/cori/research/thalean-graph-theory/18-g900-kernel-admission/artifacts/json/wxyzti_same_sheet_wrap_carry_audit_012.v1.json', 'interpretation': 'This searches the shared_B residual station roles IW, XY, and ZT for role-specific affine mod-15 laws for to_C. It separates source-side laws from laws that use target-side fields.', 'role_results': '[list len 3]', 'sharedB_named_laws_first_20': '[list len 20]', 'sharedB_row_count': 12, 'source_side_roles_with_exact_law': 1, 'station_role_counts': '{dict keys 3}', 'status': 'wxyzti_sharedB_residual_law_search_recorded'}`
18. `18-g900-kernel-admission/artifacts/json/wxyzti_station_transition_feature_inspection_009.v1.json`
   - score: `131`
   - key_counts: `{'from_C': 48, 'to_C': 48, 'source': 24, 'station_role': 24, 'edge_role': 24, 'from_A': 24, 'from_B': 24, 'from_fiber': 24, 'from_slot': 24, 'to_A': 24, 'to_B': 24, 'to_fiber': 24, 'to_slot': 24}`
   - role_token_counts: `{'shared_B': 14, 'reverse_partner': 14, 'WX': 12, 'YZ': 12, 'TI': 12, 'XY': 12, 'ZT': 12, 'IW': 12}`
   - state_token_counts: `{}`
   - first_example_path: `$`
   - first_example_record: `{'boundary': 'This is a schema/feature inspection. It does not prove a generator and does not close Gap A.', 'expected_pair_role_row_count': 24, 'expected_role_counts': '{dict keys 6}', 'expected_rows_first_40': '[list len 24]', 'feature_keys': '[list len 12]', 'feature_summaries': '[list len 12]', 'interpretation': 'This inspects WXYZTI station-row features to see whether expected directed C-transitions differ from nonexpected role-compatible C-pairs by station/provenance fields.', 'nonexpected_pair_role_row_count': 0, 'nonexpected_role_counts': '{dict keys 0}', 'nonexpected_rows_first_40': [], 'raw_row_count': 72, 'role_counts': '{dict keys 6}', 'scanned_files': ['/data/data/com.termux/files/home/dev/cori/research/thalean-graph-theory/18-g900-kernel-admission/artifacts/json/c_transition_overlay_delta_generator_001.v1.json', '/data/data/com.termux/files/home/dev/cori/research/thalean-graph-theory/18-g900-kernel-admission/artifacts/json/c_transition_delta_lift_decomposition_001.v1.json', '/data/data/com.termux/files/home/dev/cori/research/thalean-graph-theory/18-g900-kernel-admission/artifacts/json/from_c_lift_q_overlay_delta_formula_001.v1.json', '/data/data/com.termux/files/home/dev/cori/research/thalean-graph-theory/18-g900-kernel-admission/artifacts/json/c_transition_station_role_cover_audit_003b.v1.json'], 'semantic_pair_role_row_count': 24, 'status': 'wxyzti_station_transition_feature_inspection_recorded'}`
19. `21-gap-a-answer-pair-generator/source/project18_artifacts/json/wxyzti_station_transition_feature_inspection_009.v1.json`
   - score: `131`
   - key_counts: `{'from_C': 48, 'to_C': 48, 'source': 24, 'station_role': 24, 'edge_role': 24, 'from_A': 24, 'from_B': 24, 'from_fiber': 24, 'from_slot': 24, 'to_A': 24, 'to_B': 24, 'to_fiber': 24, 'to_slot': 24}`
   - role_token_counts: `{'shared_B': 14, 'reverse_partner': 14, 'WX': 12, 'YZ': 12, 'TI': 12, 'XY': 12, 'ZT': 12, 'IW': 12}`
   - state_token_counts: `{}`
   - first_example_path: `$`
   - first_example_record: `{'boundary': 'This is a schema/feature inspection. It does not prove a generator and does not close Gap A.', 'expected_pair_role_row_count': 24, 'expected_role_counts': '{dict keys 6}', 'expected_rows_first_40': '[list len 24]', 'feature_keys': '[list len 12]', 'feature_summaries': '[list len 12]', 'interpretation': 'This inspects WXYZTI station-row features to see whether expected directed C-transitions differ from nonexpected role-compatible C-pairs by station/provenance fields.', 'nonexpected_pair_role_row_count': 0, 'nonexpected_role_counts': '{dict keys 0}', 'nonexpected_rows_first_40': [], 'raw_row_count': 72, 'role_counts': '{dict keys 6}', 'scanned_files': ['/data/data/com.termux/files/home/dev/cori/research/thalean-graph-theory/18-g900-kernel-admission/artifacts/json/c_transition_overlay_delta_generator_001.v1.json', '/data/data/com.termux/files/home/dev/cori/research/thalean-graph-theory/18-g900-kernel-admission/artifacts/json/c_transition_delta_lift_decomposition_001.v1.json', '/data/data/com.termux/files/home/dev/cori/research/thalean-graph-theory/18-g900-kernel-admission/artifacts/json/from_c_lift_q_overlay_delta_formula_001.v1.json', '/data/data/com.termux/files/home/dev/cori/research/thalean-graph-theory/18-g900-kernel-admission/artifacts/json/c_transition_station_role_cover_audit_003b.v1.json'], 'semantic_pair_role_row_count': 24, 'status': 'wxyzti_station_transition_feature_inspection_recorded'}`
20. `18-g900-kernel-admission/artifacts/json/c_transition_overlay_delta_generator_001.v1.json`
   - score: `131`
   - key_counts: `{'edge_role': 48, 'from_fiber': 48, 'from_slot': 24, 'to_slot': 24, 'to_fiber': 24, 'from_A': 24, 'to_A': 24, 'from_B': 24, 'to_B': 24, 'from_C': 24, 'to_C': 24, 'reverse_partner': 2, 'shared_B': 2}`
   - role_token_counts: `{'shared_B': 29, 'reverse_partner': 29, 'WX': 10, 'YZ': 10, 'TI': 10, 'XY': 10, 'ZT': 10, 'IW': 9}`
   - state_token_counts: `{}`
   - first_example_path: `$`
   - first_example_record: `{'schema': 'c_transition_overlay_delta_generator_001.v1', 'status': 'c_transition_overlay_delta_generator_found', 'timestamp_utc': '2026-06-15T14:04:34.598959+00:00', 'purpose': 'Lift the exact context feature set from_C,to_C into an explicit WXYZTI overlay fiber-delta generator table.', 'summary': '{dict keys 14}', 'rule_members': '{dict keys 12}', 'predictions': '[list len 24]', 'checks': '[list len 8]', 'boundary': ['This is an exact overlay delta generator table.', 'The rule is expressed in station provenance terms from_C and to_C.', 'This is not yet a G60-native derivation of C itself.', 'This does not close Gap A.', 'This does not prove full G900.']}`

## Suggested next

- Import the top rich station files into source/upstream_station_provenance.
- Build 040 to join rich station rows to scalar targets from 032 and 035.

## Interpretation

Artifact 038 showed that the current Project24 JSONs do not carry enough rich station/register provenance to explain the scalar laws left open by 037. This locator searches upstream sibling projects for slot, fiber, A/B/C, role-pair, station-role, columns, and address-source fields.

## Boundary

This is a locator only. It identifies candidate provenance sources but does not import them, join them, derive scalar laws, or close Gap A.
