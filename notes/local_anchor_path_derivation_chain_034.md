# Local anchor path derivation chain 034

Status: local_anchor_path_derivation_chain_recorded

## Result

- theorem_candidate_pass: `True`
- path_source: `known_project22_anchor_node_paths_fallback`

## Chain

- artifact 033 generates the anchor residue set from relay block plus scalar-selected free block
- artifact 023 selects the anchor path from that generated residue-set candidate universe
- the Project22 anchor node path has exactly the generated residue set under mod15 projection
- artifact 018 generates the lift mask by the native sheet rule node >= 15

## Per state

- O0:
  - relay_block: `[4, 5, 7]`
  - selected_free_block: `[8, 9, 12]`
  - generated_anchor_residue_set: `[4, 5, 7, 8, 9, 12]`
  - anchor_node_path: `[[23, 24], [7, 12], [4, 5], [23, 24]]`
  - anchor_node_path_residue_set: `[4, 5, 7, 8, 9, 12]`
  - node_path_residues_match_generated_anchor: `True`
  - sheet_mask_by_node_ge_15: `[1, 1, 0, 0, 0, 0, 1, 1]`
- O1:
  - relay_block: `[2, 4, 9]`
  - selected_free_block: `[0, 13, 14]`
  - generated_anchor_residue_set: `[0, 2, 4, 9, 13, 14]`
  - anchor_node_path: `[[28, 29], [0, 2], [4, 9], [28, 29]]`
  - anchor_node_path_residue_set: `[0, 2, 4, 9, 13, 14]`
  - node_path_residues_match_generated_anchor: `True`
  - sheet_mask_by_node_ge_15: `[1, 1, 0, 0, 0, 0, 1, 1]`
- B0:
  - relay_block: `[4, 8]`
  - selected_free_block: `[0, 2, 3]`
  - generated_anchor_residue_set: `[0, 2, 3, 4, 8]`
  - anchor_node_path: `[[0, 4], [2, 17], [8, 18], [0, 4]]`
  - anchor_node_path_residue_set: `[0, 2, 3, 4, 8]`
  - node_path_residues_match_generated_anchor: `True`
  - sheet_mask_by_node_ge_15: `[0, 0, 0, 1, 0, 1, 0, 0]`
- B1:
  - relay_block: `[8, 10, 13]`
  - selected_free_block: `[2, 3, 7]`
  - generated_anchor_residue_set: `[2, 3, 7, 8, 10, 13]`
  - anchor_node_path: `[[7, 10], [8, 18], [13, 17], [7, 10]]`
  - anchor_node_path_residue_set: `[2, 3, 7, 8, 10, 13]`
  - node_path_residues_match_generated_anchor: `True`
  - sheet_mask_by_node_ge_15: `[0, 0, 0, 1, 0, 1, 0, 0]`

## Checks

- lift_mask_sheet_selector_018_theorem_pass: `True`
- candidate_census_020_theorem_pass: `True`
- rank_selector_023_theorem_pass: `True`
- free_block_scalar_032_theorem_candidate_pass: `True`
- anchor_residue_derivation_033_theorem_candidate_pass: `True`
- all_generated_anchor_sets_match_020: `True`
- all_node_path_residue_sets_match_generated_anchor: `True`
- all_sheet_masks_generated_by_node_ge_15: `True`

## Interpretation

This composes the local anchor side: generated anchor residue sets match the residue sets required by the rank-selected anchor paths, and the node paths carry the lift mask by node sheet. This is the first full local anchor payload derivation chain.

## Boundary

This is still not full Gap A closure. Relay blocks are supplied by the unlifted relay cover rather than uniquely generated from station/provenance fields; the scalar laws require native interpretation; and the full role-labeled shared_B universe is not yet derived.
