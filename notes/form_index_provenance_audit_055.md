# Form index provenance audit 055

Status: form_index_provenance_audit_recorded

## Result

- audit_pass: `True`
- verdict: `form_index_has_candidates_but_order_label_leakage_risk`
- probe_054_pass: `True`
- source_json_exists: `True`
- edge_records_found: `True`
- rows_with_form_index_count: `24`
- form_indices_are_0_1_2_3: `True`
- form_index_group_count_is_4: `True`
- form_index_group_sizes: `{'0': 6, '1': 6, '2': 6, '3': 6}`
- form_index_equals_first_occurrence_order: `True`
- form_index_blocks_are_contiguous: `True`
- label_like_field_count: `2`
- non_label_field_count: `27`
- native_like_field_count: `26`
- non_label_group_feature_count: `240`
- independent_exact_form_index_hit_count: `0`
- independent_order_hit_count: `12`
- unique_native_signatures_by_form: `True`
- candidate_source_found: `True`
- native_provenance_confirmed: `False`
- answer_label_leakage_ruled_out: `False`
- required_phrases_present: `True`
- forbidden_phrases_absent: `True`

## Source under audit

- source_json: `source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/g60_native_overlay_generator_family_search_001.v1.json`
- edge_records_path: `['edge_records']`

## Record-order leakage checks

- first_occurrence_order: `[0, 1, 2, 3]`
- contiguous_blocks: `[0, 1, 2, 3]`
- first_40_form_index_sequence: `[0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3]`

## Candidate source checks

- independent_exact_form_index_hit_count: `0`
- independent_order_hit_count: `12`
- unique_native_signatures_by_form: `True`
- native_provenance_confirmed: `False`
- answer_label_leakage_ruled_out: `False`

## Exact form-index hits, first 10

`[]`

## Order-source hits, first 10

`[{'feature': 'slot_delta_mod15__max', 'native_like': True, 'label_like': False, 'order_kind': 'ascending_rank_matches_form_index', 'ordered_form_indices': [0, 1, 2, 3], 'feature_values': {0: 9, 1: 12, 2: 13, 3: 14}}, {'feature': 'fiber_delta_mod60__min', 'native_like': True, 'label_like': False, 'order_kind': 'descending_rank_matches_form_index', 'ordered_form_indices': [0, 1, 2, 3], 'feature_values': {0: 12, 1: 3, 2: 2, 3: 1}}, {'feature': 'slot_delta_mod15__range', 'native_like': True, 'label_like': False, 'order_kind': 'ascending_rank_matches_form_index', 'ordered_form_indices': [0, 1, 2, 3], 'feature_values': {0: 9, 1: 12, 2: 13, 3: 14}}, {'feature': '_record_index__unique_max', 'native_like': True, 'label_like': False, 'order_kind': 'ascending_rank_matches_form_index', 'ordered_form_indices': [0, 1, 2, 3], 'feature_values': {0: 5, 1: 11, 2: 17, 3: 23}}, {'feature': '_record_index__unique_min', 'native_like': True, 'label_like': False, 'order_kind': 'ascending_rank_matches_form_index', 'ordered_form_indices': [0, 1, 2, 3], 'feature_values': {0: 0, 1: 6, 2: 12, 3: 18}}, {'feature': '_record_index__unique_sum', 'native_like': True, 'label_like': False, 'order_kind': 'ascending_rank_matches_form_index', 'ordered_form_indices': [0, 1, 2, 3], 'feature_values': {0: 15, 1: 51, 2: 87, 3: 123}}, {'feature': 'slot_delta_mod15__unique_max', 'native_like': True, 'label_like': False, 'order_kind': 'ascending_rank_matches_form_index', 'ordered_form_indices': [0, 1, 2, 3], 'feature_values': {0: 9, 1: 12, 2: 13, 3: 14}}, {'feature': 'fiber_delta_mod60__unique_min', 'native_like': True, 'label_like': False, 'order_kind': 'descending_rank_matches_form_index', 'ordered_form_indices': [0, 1, 2, 3], 'feature_values': {0: 12, 1: 3, 2: 2, 3: 1}}, {'feature': 'slot_delta_mod15__unique_range', 'native_like': True, 'label_like': False, 'order_kind': 'ascending_rank_matches_form_index', 'ordered_form_indices': [0, 1, 2, 3], 'feature_values': {0: 9, 1: 12, 2: 13, 3: 14}}, {'feature': '_record_index__max', 'native_like': False, 'label_like': False, 'order_kind': 'ascending_rank_matches_form_index', 'ordered_form_indices': [0, 1, 2, 3], 'feature_values': {0: 5, 1: 11, 2: 17, 3: 23}}]`

## Interpretation

Artifact 054 found form_index as a candidate source for c_row and completion_level. Artifact 055 audits whether that field has independent support or whether it may be an answer-order label. Because answer-label leakage is not ruled out here, form_index remains a candidate source, not native provenance closure.

## Boundary

This audit may find a candidate source, but it is not native closure. It does not prove form_index is native, does not rule out answer-label leakage, is not full role-labeled shared_B universe derivation, and is not Gap A closure.
