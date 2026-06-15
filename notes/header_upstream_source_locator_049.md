# Header upstream source locator 049

Status: header_upstream_source_locator_recorded

## Result

- audit_pass: `True`
- verdict: `upstream_header_source_not_found_in_imported_sources`
- shared_header_045_pass: `True`
- header_source_047_pass: `True`
- frontier_048_pass: `True`
- source_root_exists: `True`
- json_file_count: `25`
- candidate_count: `10690`
- remaining_header_target_count: `3`
- remaining_headers_are_free_sum_relay_max_relay_sum: `True`
- upstream_source_found_for_all: `False`
- shared_exact_upstream_family_exists: `False`
- shared_near_upstream_family_exists: `False`

## Header targets

- free_sum:
  - base_feature: `op__q0__A_delta__cpath_minus__sum`
  - residual: `{'O0': 2, 'O1': 3, 'B0': 0, 'B1': 1}`
  - exact_upstream_source_count: `0`
  - upstream_source_found: `False`
  - exact_family_counts: `{}`
  - near_family_counts: `{'row_group_field::lift_q__max': 4, 'row_group_field::lift_q__min': 3, 'row_group_field::lift_q__sum': 3}`
  - exact_upstream_sources_first_5: `[]`
  - nearest_upstream_sources_first_5: `[{'source_file': 'source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/c_transition_role_channel_grammar_audit_004.v1.json', 'source_path': 'role_pair_rows/1/transitions', 'kind': 'row_group_field', 'feature': 'lift_q__max', 'family': 'row_group_field::lift_q__max', 'values': {'O0': 3, 'O1': 3, 'B0': 0, 'B1': 0}, 'match_kind': 'direct', 'a': 1, 'c': 0, 'l1_error': 2, 'predicted': {'O0': 3, 'O1': 3, 'B0': 0, 'B1': 0}, 'complexity': 2000.011}, {'source_file': 'source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/c_transition_role_channel_grammar_audit_004.v1.json', 'source_path': 'role_pair_rows/1/transitions', 'kind': 'row_group_field', 'feature': 'lift_q__min', 'family': 'row_group_field::lift_q__min', 'values': {'O0': 3, 'O1': 3, 'B0': 0, 'B1': 0}, 'match_kind': 'direct', 'a': 1, 'c': 0, 'l1_error': 2, 'predicted': {'O0': 3, 'O1': 3, 'B0': 0, 'B1': 0}, 'complexity': 2000.011}, {'source_file': 'source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/c_transition_role_channel_grammar_audit_004.v1.json', 'source_path': 'role_pair_rows/1/transitions', 'kind': 'row_group_field', 'feature': 'lift_q__sum', 'family': 'row_group_field::lift_q__sum', 'values': {'O0': 3, 'O1': 3, 'B0': 0, 'B1': 0}, 'match_kind': 'direct', 'a': 1, 'c': 0, 'l1_error': 2, 'predicted': {'O0': 3, 'O1': 3, 'B0': 0, 'B1': 0}, 'complexity': 2000.011}, {'source_file': 'source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/wxyzti_reverse_partner_vs_sharedB_audit_016.v1.json', 'source_path': 'station_summaries/1/rows', 'kind': 'row_group_field', 'feature': 'lift_q__max', 'family': 'row_group_field::lift_q__max', 'values': {'O0': 3, 'O1': 3, 'B0': 0, 'B1': 0}, 'match_kind': 'direct', 'a': 1, 'c': 0, 'l1_error': 2, 'predicted': {'O0': 3, 'O1': 3, 'B0': 0, 'B1': 0}, 'complexity': 2000.011}, {'source_file': 'source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/wxyzti_reverse_partner_vs_sharedB_audit_016.v1.json', 'source_path': 'station_summaries/1/rows', 'kind': 'row_group_field', 'feature': 'lift_q__min', 'family': 'row_group_field::lift_q__min', 'values': {'O0': 3, 'O1': 3, 'B0': 0, 'B1': 0}, 'match_kind': 'direct', 'a': 1, 'c': 0, 'l1_error': 2, 'predicted': {'O0': 3, 'O1': 3, 'B0': 0, 'B1': 0}, 'complexity': 2000.011}]`
- relay_max:
  - base_feature: `set__rolepair_IW_YZ__to_A__max`
  - residual: `{'O0': 0, 'O1': 0, 'B0': -2, 'B1': 1}`
  - exact_upstream_source_count: `0`
  - upstream_source_found: `False`
  - exact_family_counts: `{}`
  - near_family_counts: `{'row_group::row_count': 1, 'row_group_field::pred__count': 1, 'row_group_field::to_C__count': 1, 'row_group_field::from_A__count': 1, 'row_group_field::from_B__count': 1, 'row_group_field::from_C__count': 1, 'row_group_field::C_delta__count': 1, 'row_group_field::from_slot__count': 1, 'row_group_field::pred__unique_count': 1, 'row_group_field::to_C__unique_count': 1}`
  - exact_upstream_sources_first_5: `[]`
  - nearest_upstream_sources_first_5: `[{'source_file': 'source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/wxyzti_reverse_partner_vs_sharedB_audit_016.v1.json', 'source_path': 'shared_B_summary/law_scores/2/misses_first_20', 'kind': 'row_group', 'feature': 'row_count', 'family': 'row_group::row_count', 'values': {'O0': 3, 'O1': 3, 'B0': 2, 'B1': 3}, 'match_kind': 'affine', 'a': 2, 'c': -6, 'l1_error': 1, 'predicted': {'O0': 0, 'O1': 0, 'B0': -2, 'B1': 0}, 'complexity': 1008.009}, {'source_file': 'source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/wxyzti_reverse_partner_vs_sharedB_audit_016.v1.json', 'source_path': 'shared_B_summary/law_scores/2/misses_first_20', 'kind': 'row_group_field', 'feature': 'pred__count', 'family': 'row_group_field::pred__count', 'values': {'O0': 3, 'O1': 3, 'B0': 2, 'B1': 3}, 'match_kind': 'affine', 'a': 2, 'c': -6, 'l1_error': 1, 'predicted': {'O0': 0, 'O1': 0, 'B0': -2, 'B1': 0}, 'complexity': 1008.011}, {'source_file': 'source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/wxyzti_reverse_partner_vs_sharedB_audit_016.v1.json', 'source_path': 'shared_B_summary/law_scores/2/misses_first_20', 'kind': 'row_group_field', 'feature': 'to_C__count', 'family': 'row_group_field::to_C__count', 'values': {'O0': 3, 'O1': 3, 'B0': 2, 'B1': 3}, 'match_kind': 'affine', 'a': 2, 'c': -6, 'l1_error': 1, 'predicted': {'O0': 0, 'O1': 0, 'B0': -2, 'B1': 0}, 'complexity': 1008.011}, {'source_file': 'source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/wxyzti_reverse_partner_vs_sharedB_audit_016.v1.json', 'source_path': 'shared_B_summary/law_scores/2/misses_first_20', 'kind': 'row_group_field', 'feature': 'from_A__count', 'family': 'row_group_field::from_A__count', 'values': {'O0': 3, 'O1': 3, 'B0': 2, 'B1': 3}, 'match_kind': 'affine', 'a': 2, 'c': -6, 'l1_error': 1, 'predicted': {'O0': 0, 'O1': 0, 'B0': -2, 'B1': 0}, 'complexity': 1008.013}, {'source_file': 'source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/wxyzti_reverse_partner_vs_sharedB_audit_016.v1.json', 'source_path': 'shared_B_summary/law_scores/2/misses_first_20', 'kind': 'row_group_field', 'feature': 'from_B__count', 'family': 'row_group_field::from_B__count', 'values': {'O0': 3, 'O1': 3, 'B0': 2, 'B1': 3}, 'match_kind': 'affine', 'a': 2, 'c': -6, 'l1_error': 1, 'predicted': {'O0': 0, 'O1': 0, 'B0': -2, 'B1': 0}, 'complexity': 1008.013}]`
- relay_sum:
  - base_feature: `op__all__A_delta__minus_cpath__sum`
  - residual: `{'O0': -3, 'O1': 0, 'B0': -1, 'B1': 1}`
  - exact_upstream_source_count: `0`
  - upstream_source_found: `False`
  - exact_family_counts: `{}`
  - near_family_counts: `{'row_group_field::lift_q__max': 4, 'row_group_field::lift_q__min': 3, 'row_group_field::lift_q__sum': 3}`
  - exact_upstream_sources_first_5: `[]`
  - nearest_upstream_sources_first_5: `[{'source_file': 'source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/c_transition_role_channel_grammar_audit_004.v1.json', 'source_path': 'role_pair_rows/2/transitions', 'kind': 'row_group_field', 'feature': 'lift_q__max', 'family': 'row_group_field::lift_q__max', 'values': {'O0': 3, 'O1': 0, 'B0': 0, 'B1': 0}, 'match_kind': 'affine', 'a': -1, 'c': 0, 'l1_error': 2, 'predicted': {'O0': -3, 'O1': 0, 'B0': 0, 'B1': 0}, 'complexity': 2001.011}, {'source_file': 'source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/c_transition_role_channel_grammar_audit_004.v1.json', 'source_path': 'role_pair_rows/2/transitions', 'kind': 'row_group_field', 'feature': 'lift_q__min', 'family': 'row_group_field::lift_q__min', 'values': {'O0': 3, 'O1': 0, 'B0': 0, 'B1': 0}, 'match_kind': 'affine', 'a': -1, 'c': 0, 'l1_error': 2, 'predicted': {'O0': -3, 'O1': 0, 'B0': 0, 'B1': 0}, 'complexity': 2001.011}, {'source_file': 'source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/c_transition_role_channel_grammar_audit_004.v1.json', 'source_path': 'role_pair_rows/2/transitions', 'kind': 'row_group_field', 'feature': 'lift_q__sum', 'family': 'row_group_field::lift_q__sum', 'values': {'O0': 3, 'O1': 0, 'B0': 0, 'B1': 0}, 'match_kind': 'affine', 'a': -1, 'c': 0, 'l1_error': 2, 'predicted': {'O0': -3, 'O1': 0, 'B0': 0, 'B1': 0}, 'complexity': 2001.011}, {'source_file': 'source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/wxyzti_reverse_partner_vs_sharedB_audit_016.v1.json', 'source_path': 'station_summaries/2/rows', 'kind': 'row_group_field', 'feature': 'lift_q__max', 'family': 'row_group_field::lift_q__max', 'values': {'O0': 3, 'O1': 0, 'B0': 0, 'B1': 0}, 'match_kind': 'affine', 'a': -1, 'c': 0, 'l1_error': 2, 'predicted': {'O0': -3, 'O1': 0, 'B0': 0, 'B1': 0}, 'complexity': 2001.011}, {'source_file': 'source/upstream_station_provenance/18-g900-kernel-admission/artifacts/json/wxyzti_reverse_partner_vs_sharedB_audit_016.v1.json', 'source_path': 'station_summaries/2/rows', 'kind': 'row_group_field', 'feature': 'lift_q__min', 'family': 'row_group_field::lift_q__min', 'values': {'O0': 3, 'O1': 0, 'B0': 0, 'B1': 0}, 'match_kind': 'affine', 'a': -1, 'c': 0, 'l1_error': 2, 'predicted': {'O0': -3, 'O1': 0, 'B0': 0, 'B1': 0}, 'complexity': 2001.011}]`

## Shared families

- shared_exact_upstream_families: `[]`
- shared_near_upstream_families: `[]`

## Interpretation

Artifact 047 left the bounded two-bit header as an open provenance target within the tested station-feature family. This locator scans the imported upstream provenance files for state-indexed, transition-indexed, or affine readouts matching the remaining header residuals.

## Boundary

This is an upstream source locator, not a derivation. Exact hits would be candidates requiring independent validation. No hit does not refute the local scalar normal form; it means the header source is not present in the imported source family scanned here. This does not derive the full role-labeled shared_B universe and is not Gap A closure.
