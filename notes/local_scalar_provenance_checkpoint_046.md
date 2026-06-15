# Local scalar provenance checkpoint 046

Status: local_scalar_provenance_checkpoint_recorded

## Result

- checkpoint_pass: `True`
- station_extract_041_pass: `True`
- station_scalar_join_042_pass: `True`
- coupled_register_043_pass: `True`
- residual_correction_044_pass: `True`
- shared_header_045_pass: `True`
- canonical_24_row_station_register: `True`
- clean_state_to_station_join: `True`
- direct_station_derivation_not_claimed: `True`
- nontrivial_target_count_is_6: `True`
- corrected_or_zero_count_is_3: `True`
- remaining_small_header_count_is_3: `True`
- all_residuals_small_header: `True`
- all_residuals_compress_target_bit_law: `True`
- max_residual_coeff_l1_at_most_9: `True`
- max_residual_abs_coeff_at_most_3: `True`
- required_closed_phrases_present: `True`
- required_boundary_phrases_present: `True`
- forbidden_phrases_absent: `True`

## Closed statement

Given the reduced four-state Lift/Twist local-cell target and the imported canonical 24-row station register, Project 24 now records a local scalar-provenance normal form. The station register gives a clean state-to-station join. Each scalar target is represented as a station-register base readout, plus an exact station-register correction where available, plus a bounded two-bit residual header over basis [1,b,r,b*r].

## Result statement

The six nontrivial scalar targets split as follows: relay_size has station-base exact zero residual; free_min and relay_min have exact station-register corrections; free_sum, relay_max, and relay_sum remain as small bounded two-bit header residuals.

## Normal form

```text
scalar target = station-register base readout + exact station correction where available + bounded two-bit residual header
```

- header_basis: `['1', 'b', 'r', 'b*r']`
- header_bound: `max_abs_coeff <= 3 and coefficient_l1 <= 9`

## Target classification

- exact_station_register_correction: `['free_min', 'relay_min']`
- small_header_residual_remaining: `['free_sum', 'relay_max', 'relay_sum']`
- station_base_exact_zero_residual: `['relay_size']`

## Target rows

- free_min:
  - classification: `exact_station_register_correction`
  - base_feature: `set__q3__to_C__range`
  - target_values: `{'B0': 0, 'B1': 2, 'O0': 8, 'O1': 0}`
  - base_values: `{'B0': 0, 'B1': 0, 'O0': 9, 'O1': 0}`
  - residual: `{'B0': 0, 'B1': 2, 'O0': -1, 'O1': 0}`
  - target_coeff_l1: `34`
  - residual_coeff_l1: `4`
  - residual_max_abs_coeff: `1`
- free_sum:
  - classification: `small_header_residual_remaining`
  - base_feature: `op__q0__A_delta__cpath_minus__sum`
  - target_values: `{'B0': 5, 'B1': 12, 'O0': 29, 'O1': 27}`
  - base_values: `{'B0': 5, 'B1': 11, 'O0': 27, 'O1': 24}`
  - residual: `{'B0': 0, 'B1': 1, 'O0': 2, 'O1': 3}`
  - target_coeff_l1: `64`
  - residual_coeff_l1: `5`
  - residual_max_abs_coeff: `2`
- relay_max:
  - classification: `small_header_residual_remaining`
  - base_feature: `set__rolepair_IW_YZ__to_A__max`
  - target_values: `{'B0': 8, 'B1': 13, 'O0': 7, 'O1': 9}`
  - base_values: `{'B0': 10, 'B1': 12, 'O0': 7, 'O1': 9}`
  - residual: `{'B0': -2, 'B1': 1, 'O0': 0, 'O1': 0}`
  - target_coeff_l1: `13`
  - residual_coeff_l1: `5`
  - residual_max_abs_coeff: `3`
- relay_min:
  - classification: `exact_station_register_correction`
  - base_feature: `op__shared__A_delta__minus_cpath__min`
  - target_values: `{'B0': 4, 'B1': 8, 'O0': 4, 'O1': 2}`
  - base_values: `{'B0': 4, 'B1': 8, 'O0': 6, 'O1': 2}`
  - residual: `{'B0': 0, 'B1': 0, 'O0': -2, 'O1': 0}`
  - target_coeff_l1: `12`
  - residual_coeff_l1: `8`
  - residual_max_abs_coeff: `2`
- relay_size:
  - classification: `station_base_exact_zero_residual`
  - base_feature: `op__q0__B_delta__cpath_minus__size`
  - target_values: `{'B0': 2, 'B1': 3, 'O0': 3, 'O1': 3}`
  - base_values: `{'B0': 2, 'B1': 3, 'O0': 3, 'O1': 3}`
  - residual: `{'B0': 0, 'B1': 0, 'O0': 0, 'O1': 0}`
  - target_coeff_l1: `5`
  - residual_coeff_l1: `0`
  - residual_max_abs_coeff: `0`
- relay_sum:
  - classification: `small_header_residual_remaining`
  - base_feature: `op__all__A_delta__minus_cpath__sum`
  - target_values: `{'B0': 12, 'B1': 31, 'O0': 16, 'O1': 15}`
  - base_values: `{'B0': 13, 'B1': 30, 'O0': 19, 'O1': 15}`
  - residual: `{'B0': -1, 'B1': 1, 'O0': -3, 'O1': 0}`
  - target_coeff_l1: `41`
  - residual_coeff_l1: `9`
  - residual_max_abs_coeff: `3`

## Boundary

This is a reduced four-state local normal form, not native closure. It does not derive the bounded header from native G60 structure, does not derive the full role-labeled shared_B universe, and is not Gap A closure.

## Interpretation

This checkpoint packages artifacts 041 through 045 into one bounded local result. The scalar-provenance problem is compressed into a station-register normal form with a small residual header, but it is not closed.
