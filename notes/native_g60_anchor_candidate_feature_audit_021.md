# Native G60 anchor candidate feature audit 021

Status: native_g60_anchor_candidate_feature_audit_recorded

## Question

Do simple candidate-level features select the observed anchor paths from the corrected census?

## Result

- all_checks_pass: `True`
- total_candidate_count: `53`
- states_with_single_feature_selector: `['O0', 'O1', 'B0', 'B1']`

## Per state

- O0:
  - candidate_count: `14`
  - observed_candidate_index: `1`
  - observed_rank_by_best_support_sum_desc: `2`
  - observed_support_sum: `13`
  - relay_hits: `[4, 5, 7]`
  - unique_relay_hits: `[]`
  - exact_single_feature_selectors: `[{'feature': 'rank_by_best_support_sum_desc', 'observed_value': 2}]`
- O1:
  - candidate_count: `15`
  - observed_candidate_index: `3`
  - observed_rank_by_best_support_sum_desc: `4`
  - observed_support_sum: `16`
  - relay_hits: `[2, 4, 9]`
  - unique_relay_hits: `[]`
  - exact_single_feature_selectors: `[{'feature': 'rank_by_best_support_sum_desc', 'observed_value': 4}]`
- B0:
  - candidate_count: `11`
  - observed_candidate_index: `8`
  - observed_rank_by_best_support_sum_desc: `9`
  - observed_support_sum: `8`
  - relay_hits: `[4, 8]`
  - unique_relay_hits: `[8]`
  - exact_single_feature_selectors: `[{'feature': 'rank_by_best_support_sum_desc', 'observed_value': 9}]`
- B1:
  - candidate_count: `13`
  - observed_candidate_index: `9`
  - observed_rank_by_best_support_sum_desc: `10`
  - observed_support_sum: `11`
  - relay_hits: `[8, 10, 13]`
  - unique_relay_hits: `[8]`
  - exact_single_feature_selectors: `[{'feature': 'rank_by_best_support_sum_desc', 'observed_value': 10}]`

## Checks

- unlifted_relay_cover_011_theorem_pass: `True`
- anchor_quotient_pair_017_theorem_pass: `True`
- lift_mask_sheet_018_theorem_pass: `True`
- candidate_census_020_theorem_pass: `True`
- total_candidate_count_matches_020: `True`
- all_observed_cycles_found: `True`

## Interpretation

This audits simple candidate-level features after the corrected census. It looks for whether support rank, relay-hit overlap, or unique relay-hit overlap already singles out the observed anchor path. A positive result would suggest a selector direction; a negative result means path selection requires a richer station or provenance feature.

## Boundary

This is a feature audit over candidates from artifact 020. It does not derive anchor residue sets, does not prove a path selector theorem unless exact selector features are found and later validated, does not test station fields, does not select unique relay mediators, does not derive the full role-labeled shared_B universe, and does not close Gap A.
