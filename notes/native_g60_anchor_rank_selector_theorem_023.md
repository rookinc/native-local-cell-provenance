# Native G60 anchor rank selector theorem 023

Status: native_g60_anchor_rank_selector_theorem_recorded

## Claim

Given the corrected candidate census from artifact 020 and the rank law from artifact 022, the selected support-rank candidate in each state exactly recovers the observed Project 22 anchor path.

## Result

- theorem_pass: `True`
- rank_law: `rank = 2 + 7*b + 2*r - b*r`

## Per state

- O0:
  - bits: `(0, 0)`
  - target_rank: `2`
  - candidate_count: `14`
  - selected_candidate_index: `1`
  - observed_candidate_index: `1`
  - selected_matches_observed: `True`
- O1:
  - bits: `(0, 1)`
  - target_rank: `4`
  - candidate_count: `15`
  - selected_candidate_index: `3`
  - observed_candidate_index: `3`
  - selected_matches_observed: `True`
- B0:
  - bits: `(1, 0)`
  - target_rank: `9`
  - candidate_count: `11`
  - selected_candidate_index: `8`
  - observed_candidate_index: `8`
  - selected_matches_observed: `True`
- B1:
  - bits: `(1, 1)`
  - target_rank: `10`
  - candidate_count: `13`
  - selected_candidate_index: `9`
  - observed_candidate_index: `9`
  - selected_matches_observed: `True`

## Checks

- candidate_census_020_theorem_pass: `True`
- rank_fingerprint_022_theorem_pass: `True`
- state_count_is_4: `True`
- all_states_select_one_candidate: `True`
- all_selected_candidates_match_observed: `True`
- target_rank_profile_matches_022: `True`

## Interpretation

This combines the candidate census and rank fingerprint into a bounded selector theorem. It shows that the observed anchor paths are exactly recoverable from state bits plus support-rank order inside the quotient-pair candidate universe. The remaining question is whether the rank law itself has native provenance rather than being inferred from the observed four-state target.

## Boundary

This is conditional on the observed anchor residue sets, observed pair-size profiles, and the rank law from artifact 022. It does not prove the rank law is native, does not derive anchor residue sets, does not test station fields, does not select unique relay mediators, does not derive the full role-labeled shared_B universe, and does not close Gap A.
