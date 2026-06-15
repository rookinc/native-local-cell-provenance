# Header source audit 047

Status: header_source_audit_recorded

## Result

- audit_pass: `True`
- verdict: `header_source_remains_open_small_bit_header_only`
- station_extract_041_pass: `True`
- shared_header_045_pass: `True`
- checkpoint_046_pass: `True`
- all_join_checks: `True`
- remaining_header_target_count: `3`
- remaining_headers_are_free_sum_relay_max_relay_sum: `True`
- all_headers_small: `True`
- station_header_source_found_for_all: `False`
- shared_near_station_family_exists: `False`
- small_integer_relation_found: `False`

## Header targets

- free_sum:
  - base_feature: `op__q0__A_delta__cpath_minus__sum`
  - residual: `{'O0': 2, 'O1': 3, 'B0': 0, 'B1': 1}`
  - residual_bit_law: `{'formula': 'p0 + pb*b + pr*r + pbr*b*r', 'coefficients': {'p0': 2, 'pb': -2, 'pr': 1, 'pbr': 0}, 'predictions': {'O0': 2, 'O1': 3, 'B0': 0, 'B1': 1}, 'coefficient_l1': 5, 'max_abs_coeff': 2, 'nonzero_terms': ['p0', 'pb', 'pr']}`
  - exact_station_source_count: `0`
  - station_source_found: `False`
  - nearest_source_class_counts_top20: `{'station_role_feature': 6, 'role_pair_feature': 4, 'other_station_feature': 3, 'q0_station_feature': 3, 'shared_B_feature': 2, 'reverse_partner_feature': 2}`
  - exact_station_sources_first_5: `[]`
  - nearest_station_sources_first_5: `[{'feature': 'op__all__C_delta__union_cpath__range', 'source_class': 'other_station_feature', 'family': 'op__all__C_delta__union_cpath', 'a': 1, 'c': -10, 'feature_values': {'O0': 12, 'O1': 12, 'B0': 10, 'B1': 11}, 'predicted_residual': {'O0': 2, 'O1': 2, 'B0': 0, 'B1': 1}, 'l1_error': 1, 'complexity': 1011.036}, {'feature': 'op__shared__C_delta__union_cpath__range', 'source_class': 'shared_B_feature', 'family': 'op__shared__C_delta__union_cpath', 'a': 1, 'c': -10, 'feature_values': {'O0': 12, 'O1': 12, 'B0': 10, 'B1': 11}, 'predicted_residual': {'O0': 2, 'O1': 2, 'B0': 0, 'B1': 1}, 'l1_error': 1, 'complexity': 1011.039}, {'feature': 'op__reverse__C_delta__union_cpath__range', 'source_class': 'reverse_partner_feature', 'family': 'op__reverse__C_delta__union_cpath', 'a': 1, 'c': -10, 'feature_values': {'O0': 12, 'O1': 12, 'B0': 10, 'B1': 11}, 'predicted_residual': {'O0': 2, 'O1': 2, 'B0': 0, 'B1': 1}, 'l1_error': 1, 'complexity': 1011.04}, {'feature': 'op__station_XY__to_A__union_cpath__range', 'source_class': 'station_role_feature', 'family': 'op__station_XY__to_A__union_cpath', 'a': 1, 'c': -10, 'feature_values': {'O0': 12, 'O1': 13, 'B0': 10, 'B1': 10}, 'predicted_residual': {'O0': 2, 'O1': 3, 'B0': 0, 'B1': 0}, 'l1_error': 1, 'complexity': 1011.04}, {'feature': 'op__station_YZ__to_A__union_cpath__range', 'source_class': 'station_role_feature', 'family': 'op__station_YZ__to_A__union_cpath', 'a': 1, 'c': -10, 'feature_values': {'O0': 12, 'O1': 13, 'B0': 10, 'B1': 10}, 'predicted_residual': {'O0': 2, 'O1': 3, 'B0': 0, 'B1': 0}, 'l1_error': 1, 'complexity': 1011.04}]`
- relay_max:
  - base_feature: `set__rolepair_IW_YZ__to_A__max`
  - residual: `{'O0': 0, 'O1': 0, 'B0': -2, 'B1': 1}`
  - residual_bit_law: `{'formula': 'p0 + pb*b + pr*r + pbr*b*r', 'coefficients': {'p0': 0, 'pb': -2, 'pr': 0, 'pbr': 3}, 'predictions': {'O0': 0, 'O1': 0, 'B0': -2, 'B1': 1}, 'coefficient_l1': 5, 'max_abs_coeff': 3, 'nonzero_terms': ['pb', 'pbr']}`
  - exact_station_source_count: `0`
  - station_source_found: `False`
  - nearest_source_class_counts_top20: `{'other_station_feature': 6, 'q0_station_feature': 5, 'q3_station_feature': 4, 'role_pair_feature': 4, 'station_role_feature': 1}`
  - exact_station_sources_first_5: `[]`
  - nearest_station_sources_first_5: `[{'feature': 'op__q0__A_delta__inter_cpath__sum', 'source_class': 'q0_station_feature', 'family': 'op__q0__A_delta__inter_cpath', 'a': -1, 'c': 0, 'feature_values': {'O0': 0, 'O1': 0, 'B0': 2, 'B1': 0}, 'predicted_residual': {'O0': 0, 'O1': 0, 'B0': -2, 'B1': 0}, 'l1_error': 1, 'complexity': 1001.033}, {'feature': 'op__q0__A_delta__inter_cpath__size', 'source_class': 'q0_station_feature', 'family': 'op__q0__A_delta__inter_cpath', 'a': -1, 'c': 0, 'feature_values': {'O0': 0, 'O1': 0, 'B0': 2, 'B1': 0}, 'predicted_residual': {'O0': 0, 'O1': 0, 'B0': -2, 'B1': 0}, 'l1_error': 1, 'complexity': 1001.034}, {'feature': 'op__q3__B_delta__inter_cpath__size', 'source_class': 'q3_station_feature', 'family': 'op__q3__B_delta__inter_cpath', 'a': -1, 'c': 0, 'feature_values': {'O0': 0, 'O1': 0, 'B0': 2, 'B1': 0}, 'predicted_residual': {'O0': 0, 'O1': 0, 'B0': -2, 'B1': 0}, 'l1_error': 1, 'complexity': 1001.034}, {'feature': 'op__all__B_delta__inter_cpath__size', 'source_class': 'other_station_feature', 'family': 'op__all__B_delta__inter_cpath', 'a': -1, 'c': 0, 'feature_values': {'O0': 0, 'O1': 0, 'B0': 2, 'B1': 0}, 'predicted_residual': {'O0': 0, 'O1': 0, 'B0': -2, 'B1': 0}, 'l1_error': 1, 'complexity': 1001.035}, {'feature': 'op__q3__slot_delta__inter_cpath__size', 'source_class': 'q3_station_feature', 'family': 'op__q3__slot_delta__inter_cpath', 'a': -1, 'c': 0, 'feature_values': {'O0': 0, 'O1': 0, 'B0': 2, 'B1': 0}, 'predicted_residual': {'O0': 0, 'O1': 0, 'B0': -2, 'B1': 0}, 'l1_error': 1, 'complexity': 1001.037}]`
- relay_sum:
  - base_feature: `op__all__A_delta__minus_cpath__sum`
  - residual: `{'O0': -3, 'O1': 0, 'B0': -1, 'B1': 1}`
  - residual_bit_law: `{'formula': 'p0 + pb*b + pr*r + pbr*b*r', 'coefficients': {'p0': -3, 'pb': 2, 'pr': 3, 'pbr': -1}, 'predictions': {'O0': -3, 'O1': 0, 'B0': -1, 'B1': 1}, 'coefficient_l1': 9, 'max_abs_coeff': 3, 'nonzero_terms': ['p0', 'pb', 'pr', 'pbr']}`
  - exact_station_source_count: `0`
  - station_source_found: `False`
  - nearest_source_class_counts_top20: `{'q3_station_feature': 6, 'q0_station_feature': 6, 'role_pair_feature': 4, 'station_role_feature': 4}`
  - exact_station_sources_first_5: `[]`
  - nearest_station_sources_first_5: `[{'feature': 'set__q3__from_C__range', 'source_class': 'q3_station_feature', 'family': 'set__q3__from_C', 'a': -1, 'c': 0, 'feature_values': {'O0': 3, 'O1': 0, 'B0': 0, 'B1': 0}, 'predicted_residual': {'O0': -3, 'O1': 0, 'B0': 0, 'B1': 0}, 'l1_error': 2, 'complexity': 2001.022}, {'feature': 'set__q3__from_fiber_mod15__range', 'source_class': 'q3_station_feature', 'family': 'set__q3__from_fiber_mod15', 'a': -1, 'c': 0, 'feature_values': {'O0': 3, 'O1': 0, 'B0': 0, 'B1': 0}, 'predicted_residual': {'O0': -3, 'O1': 0, 'B0': 0, 'B1': 0}, 'l1_error': 2, 'complexity': 2001.032}, {'feature': 'op__q0__from_C__cpath_minus__range', 'source_class': 'q0_station_feature', 'family': 'op__q0__from_C__cpath_minus', 'a': -1, 'c': 0, 'feature_values': {'O0': 3, 'O1': 0, 'B0': 0, 'B1': 0}, 'predicted_residual': {'O0': -3, 'O1': 0, 'B0': 0, 'B1': 0}, 'l1_error': 2, 'complexity': 2001.034}, {'feature': 'op__q3__from_C__inter_cpath__range', 'source_class': 'q3_station_feature', 'family': 'op__q3__from_C__inter_cpath', 'a': -1, 'c': 0, 'feature_values': {'O0': 3, 'O1': 0, 'B0': 0, 'B1': 0}, 'predicted_residual': {'O0': -3, 'O1': 0, 'B0': 0, 'B1': 0}, 'l1_error': 2, 'complexity': 2001.034}, {'feature': 'op__q0__from_fiber_mod15__cpath_minus__range', 'source_class': 'q0_station_feature', 'family': 'op__q0__from_fiber_mod15__cpath_minus', 'a': -1, 'c': 0, 'feature_values': {'O0': 3, 'O1': 0, 'B0': 0, 'B1': 0}, 'predicted_residual': {'O0': -3, 'O1': 0, 'B0': 0, 'B1': 0}, 'l1_error': 2, 'complexity': 2001.044}]`

## Shared near families

- shared_near_source_classes: `['q0_station_feature', 'role_pair_feature', 'station_role_feature']`
- shared_near_families: `[]`

## Small integer relations among header residuals

`[]`

## Interpretation

Artifact 046 records a station-register normal form with three remaining small two-bit header residuals. This audit tests whether those residuals have exact station-feature sources or a shared near station family.

## Boundary

This is a header-source audit over the reduced four-state local normal form. Failure to find an exact station source does not refute the normal form; it leaves the bounded header as an open provenance target. This does not derive the full role-labeled shared_B universe and is not Gap A closure.
