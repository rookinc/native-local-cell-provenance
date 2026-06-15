# Native two-bit header mechanism 051

Status: native_two_bit_header_mechanism_recorded

## Result

- theorem_candidate_pass: `True`
- shared_header_045_pass: `True`
- frontier_050_pass: `True`
- target_set_is_free_sum_relay_max_relay_sum: `True`
- all_state_rows_match: `True`
- all_target_formulas_match: `True`
- free_sum_is_c_row_phase_shift: `True`
- relay_max_is_branch_only_hinge: `True`
- relay_sum_is_rank_release_plus_branch_relief: `True`
- required_phrases_present: `True`
- forbidden_phrases_absent: `True`

## Closed statement

Within the reduced four-state Lift/Twist local-cell coordinate system, the remaining bounded header is exactly recovered by a two-bit coordinate mechanism: free_sum is a C-row phase shift, relay_max is a branch-only hinge, and relay_sum is rank release plus branch relief.

## Mechanism

- free_sum:
  - claim: free_sum header is the C-row phase shifted by two
  - formula: `H_free_sum = (c_row + 2) mod 4`
  - interpretation: The free-sum residual is not an arbitrary four-state table; it is the four-step C-row clock read from the opposite half-cycle.
- relay_max:
  - claim: relay_max header is a branch-only hinge
  - formula: `H_relay_max = b * (3*r - 2)`
  - interpretation: The relay-max residual vanishes in the ordinary shell and appears only when the branch shell is active.
- relay_sum:
  - claim: relay_sum header is rank release plus branch relief
  - formula: `H_relay_sum = -3 + 3*r + b*(2-r)`
  - interpretation: The relay-sum residual has an ordinary rank release from -3 to 0, then branch relief shifts B0 and B1 differently.

## State table

- O0: b=0, r=0, c_row=0, anchor_col=1, selected=1, headers=(2,0,-3), match=True
- O1: b=0, r=1, c_row=1, anchor_col=2, selected=6, headers=(3,0,0), match=True
- B0: b=1, r=0, c_row=2, anchor_col=0, selected=8, headers=(0,-2,-1), match=True
- B1: b=1, r=1, c_row=3, anchor_col=3, selected=15, headers=(1,1,1), match=True

## Target results

- free_sum:
  - observed_residual: `{'O0': 2, 'O1': 3, 'B0': 0, 'B1': 1}`
  - predicted_residual: `{'O0': 2, 'O1': 3, 'B0': 0, 'B1': 1}`
  - exact_match: `True`
  - predicted_bit_coefficients: `{'coefficients': {'p0': 2, 'pb': -2, 'pr': 1, 'pbr': 0}, 'predictions': {'O0': 2, 'O1': 3, 'B0': 0, 'B1': 1}, 'coefficient_l1': 5, 'max_abs_coeff': 2, 'nonzero_terms': ['p0', 'pb', 'pr']}`
- relay_max:
  - observed_residual: `{'O0': 0, 'O1': 0, 'B0': -2, 'B1': 1}`
  - predicted_residual: `{'O0': 0, 'O1': 0, 'B0': -2, 'B1': 1}`
  - exact_match: `True`
  - predicted_bit_coefficients: `{'coefficients': {'p0': 0, 'pb': -2, 'pr': 0, 'pbr': 3}, 'predictions': {'O0': 0, 'O1': 0, 'B0': -2, 'B1': 1}, 'coefficient_l1': 5, 'max_abs_coeff': 3, 'nonzero_terms': ['pb', 'pbr']}`
- relay_sum:
  - observed_residual: `{'O0': -3, 'O1': 0, 'B0': -1, 'B1': 1}`
  - predicted_residual: `{'O0': -3, 'O1': 0, 'B0': -1, 'B1': 1}`
  - exact_match: `True`
  - predicted_bit_coefficients: `{'coefficients': {'p0': -3, 'pb': 2, 'pr': 3, 'pbr': -1}, 'predictions': {'O0': -3, 'O1': 0, 'B0': -1, 'B1': 1}, 'coefficient_l1': 9, 'max_abs_coeff': 3, 'nonzero_terms': ['p0', 'pb', 'pr', 'pbr']}`

## Interpretation

Artifacts 047 and 049 failed to source the bounded header as a station or imported-upstream feature. Artifact 051 turns the direction around: it treats the header as a reduced local-cell coordinate mechanism and verifies exact recovery from b, r, and c_row.

## Boundary

This is a coordinate-mechanism derivation candidate, not native closure. It derives the remaining header from the reduced two-bit local-cell coordinates, but it does not derive those coordinates from the full native G60/shared_B universe and is not Gap A closure.
