# Shared residual correction grammar 045

Status: shared_residual_correction_grammar_recorded

## Result

- input_044_audit_pass: `True`
- nontrivial_target_count: `6`
- corrected_or_zero_count: `3`
- remaining_small_header_count: `3`
- all_residuals_small_header: `True`
- all_residuals_compress_target_bit_law: `True`
- max_residual_coeff_l1: `9`
- max_residual_abs_coeff: `3`
- shared_header_grammar_pass: `True`

## Classification

- exact_station_register_correction: `['free_min', 'relay_min']`
- small_header_residual_remaining: `['free_sum', 'relay_max', 'relay_sum']`
- station_base_exact_zero_residual: `['relay_size']`

## Grammar candidate

- name: `bounded two-bit residual header`
- basis: `['1', 'b', 'r', 'b*r']`
- law: `residual = p0 + pb*b + pr*r + pbr*b*r`
- bound: `max_abs_coeff <= 3 and coefficient_l1 <= 9`

## Target rows

- free_min:
  - classification: `exact_station_register_correction`
  - base_feature: `set__q3__to_C__range`
  - target_values: `{'O0': 8, 'O1': 0, 'B0': 0, 'B1': 2}`
  - base_values: `{'O0': 9, 'O1': 0, 'B0': 0, 'B1': 0}`
  - residual: `{'O0': -1, 'O1': 0, 'B0': 0, 'B1': 2}`
  - target_coeff_l1: `34`
  - residual_coeff_l1: `4`
  - residual_bit_law: `{'formula': 'p0 + pb*b + pr*r + pbr*b*r', 'coefficients': {'p0': -1, 'pb': 1, 'pr': 1, 'pbr': 1}, 'predictions': {'O0': -1, 'O1': 0, 'B0': 0, 'B1': 2}, 'coefficient_l1': 4, 'max_abs_coeff': 1, 'nonzero_terms': ['p0', 'pb', 'pr', 'pbr']}`
  - exact_non_bit_correction_count_first_saved: `1`
- free_sum:
  - classification: `small_header_residual_remaining`
  - base_feature: `op__q0__A_delta__cpath_minus__sum`
  - target_values: `{'O0': 29, 'O1': 27, 'B0': 5, 'B1': 12}`
  - base_values: `{'O0': 27, 'O1': 24, 'B0': 5, 'B1': 11}`
  - residual: `{'O0': 2, 'O1': 3, 'B0': 0, 'B1': 1}`
  - target_coeff_l1: `64`
  - residual_coeff_l1: `5`
  - residual_bit_law: `{'formula': 'p0 + pb*b + pr*r + pbr*b*r', 'coefficients': {'p0': 2, 'pb': -2, 'pr': 1, 'pbr': 0}, 'predictions': {'O0': 2, 'O1': 3, 'B0': 0, 'B1': 1}, 'coefficient_l1': 5, 'max_abs_coeff': 2, 'nonzero_terms': ['p0', 'pb', 'pr']}`
  - exact_non_bit_correction_count_first_saved: `0`
- relay_max:
  - classification: `small_header_residual_remaining`
  - base_feature: `set__rolepair_IW_YZ__to_A__max`
  - target_values: `{'O0': 7, 'O1': 9, 'B0': 8, 'B1': 13}`
  - base_values: `{'O0': 7, 'O1': 9, 'B0': 10, 'B1': 12}`
  - residual: `{'O0': 0, 'O1': 0, 'B0': -2, 'B1': 1}`
  - target_coeff_l1: `13`
  - residual_coeff_l1: `5`
  - residual_bit_law: `{'formula': 'p0 + pb*b + pr*r + pbr*b*r', 'coefficients': {'p0': 0, 'pb': -2, 'pr': 0, 'pbr': 3}, 'predictions': {'O0': 0, 'O1': 0, 'B0': -2, 'B1': 1}, 'coefficient_l1': 5, 'max_abs_coeff': 3, 'nonzero_terms': ['pb', 'pbr']}`
  - exact_non_bit_correction_count_first_saved: `0`
- relay_min:
  - classification: `exact_station_register_correction`
  - base_feature: `op__shared__A_delta__minus_cpath__min`
  - target_values: `{'O0': 4, 'O1': 2, 'B0': 4, 'B1': 8}`
  - base_values: `{'O0': 6, 'O1': 2, 'B0': 4, 'B1': 8}`
  - residual: `{'O0': -2, 'O1': 0, 'B0': 0, 'B1': 0}`
  - target_coeff_l1: `12`
  - residual_coeff_l1: `8`
  - residual_bit_law: `{'formula': 'p0 + pb*b + pr*r + pbr*b*r', 'coefficients': {'p0': -2, 'pb': 2, 'pr': 2, 'pbr': -2}, 'predictions': {'O0': -2, 'O1': 0, 'B0': 0, 'B1': 0}, 'coefficient_l1': 8, 'max_abs_coeff': 2, 'nonzero_terms': ['p0', 'pb', 'pr', 'pbr']}`
  - exact_non_bit_correction_count_first_saved: `39`
- relay_size:
  - classification: `station_base_exact_zero_residual`
  - base_feature: `op__q0__B_delta__cpath_minus__size`
  - target_values: `{'O0': 3, 'O1': 3, 'B0': 2, 'B1': 3}`
  - base_values: `{'O0': 3, 'O1': 3, 'B0': 2, 'B1': 3}`
  - residual: `{'O0': 0, 'O1': 0, 'B0': 0, 'B1': 0}`
  - target_coeff_l1: `5`
  - residual_coeff_l1: `0`
  - residual_bit_law: `{'formula': 'p0 + pb*b + pr*r + pbr*b*r', 'coefficients': {'p0': 0, 'pb': 0, 'pr': 0, 'pbr': 0}, 'predictions': {'O0': 0, 'O1': 0, 'B0': 0, 'B1': 0}, 'coefficient_l1': 0, 'max_abs_coeff': 0, 'nonzero_terms': []}`
  - exact_non_bit_correction_count_first_saved: `40`
- relay_sum:
  - classification: `small_header_residual_remaining`
  - base_feature: `op__all__A_delta__minus_cpath__sum`
  - target_values: `{'O0': 16, 'O1': 15, 'B0': 12, 'B1': 31}`
  - base_values: `{'O0': 19, 'O1': 15, 'B0': 13, 'B1': 30}`
  - residual: `{'O0': -3, 'O1': 0, 'B0': -1, 'B1': 1}`
  - target_coeff_l1: `41`
  - residual_coeff_l1: `9`
  - residual_bit_law: `{'formula': 'p0 + pb*b + pr*r + pbr*b*r', 'coefficients': {'p0': -3, 'pb': 2, 'pr': 3, 'pbr': -1}, 'predictions': {'O0': -3, 'O1': 0, 'B0': -1, 'B1': 1}, 'coefficient_l1': 9, 'max_abs_coeff': 3, 'nonzero_terms': ['p0', 'pb', 'pr', 'pbr']}`
  - exact_non_bit_correction_count_first_saved: `0`

## Interpretation

Artifact 044 improved the exact scalar correction frontier to 3 of 6 nontrivial targets. This audit does not search for new station features. It checks whether the remaining residuals share a small two-bit header grammar. The result records a constrained grammar candidate rather than a full native derivation.

## Boundary

This proves only a reduced four-state residual compression property. Since any four values can be interpolated by a two-bit polynomial, the load-bearing claim is the small coefficient bound and the station-register complexity reduction. This does not derive the full role-labeled shared_B universe and does not close Gap A.
