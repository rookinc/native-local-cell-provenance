# Local anchor residue derivation chain 033

Status: local_anchor_residue_derivation_chain_recorded

## Result

- theorem_candidate_pass: `True`

## Chain

- state bits determine expected C-overlap and scalar free-block targets
- artifact 011 supplies same-state relay blocks
- artifact 032 selects the unique free block
- relay block union selected free block generates the anchor residue set
- generated anchor residue set matches the anchor residue set used by artifact 020
- artifact 023 then conditionally selects the observed anchor path from that generated residue set

## Per state

- O0:
  - relay_block: `[4, 5, 7]`
  - selected_free_block: `[8, 9, 12]`
  - generated_anchor_residue_set: `[4, 5, 7, 8, 9, 12]`
  - observed_anchor_residue_set: `[4, 5, 7, 8, 9, 12]`
  - generated_matches_observed_anchor_set: `True`
- O1:
  - relay_block: `[2, 4, 9]`
  - selected_free_block: `[0, 13, 14]`
  - generated_anchor_residue_set: `[0, 2, 4, 9, 13, 14]`
  - observed_anchor_residue_set: `[0, 2, 4, 9, 13, 14]`
  - generated_matches_observed_anchor_set: `True`
- B0:
  - relay_block: `[4, 8]`
  - selected_free_block: `[0, 2, 3]`
  - generated_anchor_residue_set: `[0, 2, 3, 4, 8]`
  - observed_anchor_residue_set: `[0, 2, 3, 4, 8]`
  - generated_matches_observed_anchor_set: `True`
- B1:
  - relay_block: `[8, 10, 13]`
  - selected_free_block: `[2, 3, 7]`
  - generated_anchor_residue_set: `[2, 3, 7, 8, 10, 13]`
  - observed_anchor_residue_set: `[2, 3, 7, 8, 10, 13]`
  - generated_matches_observed_anchor_set: `True`

## Checks

- unlifted_relay_cover_011_theorem_pass: `True`
- candidate_census_020_theorem_pass: `True`
- rank_selector_023_theorem_pass: `True`
- free_block_scalar_032_theorem_candidate_pass: `True`
- all_states_select_one_free_block: `True`
- all_generated_anchor_sets_match_observed: `True`

## Interpretation

This composes the relay layer and free-block scalar selector into a generated anchor residue set. The generated anchor residue set matches the residue set required by the existing anchor path rank selector in all four states.

## Boundary

This is a local anchor residue derivation chain, not full Gap A closure. The relay blocks still come from the unlifted relay cover rather than uniquely selected relay mediators, the scalar laws still need native/provenance interpretation, and the full role-labeled shared_B universe is not derived.
