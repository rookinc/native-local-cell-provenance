# Local anchor payload pipeline 036

Status: local_anchor_payload_pipeline_recorded

## Result

- theorem_candidate_pass: `True`
- source_caveat_count: `1`

## Pipeline

- artifact 007 supplies native two-hop C-transition mediator geometry
- artifact 035 selects relay blocks from mediator geometry
- artifact 032 selects free blocks from state-bit scalar laws
- artifact 033 unions relay blocks and free blocks to generate anchor residue sets
- artifact 023 selects anchor paths inside the generated residue-set candidate universe
- artifact 034 verifies node-path residues and lift masks via node-sheet rule

## Per state

- O0:
  - mediator_union_035: `[0, 1, 2, 3, 4, 5, 7, 8]`
  - relay_block_from_035: `[4, 5, 7]`
  - free_block_from_032: `[8, 9, 12]`
  - anchor_from_relay_union_free: `[4, 5, 7, 8, 9, 12]`
  - anchor_node_residues_034: `[4, 5, 7, 8, 9, 12]`
  - lift_mask_from_034: `[1, 1, 0, 0, 0, 0, 1, 1]`
  - state_pipeline_pass: `True`
- O1:
  - mediator_union_035: `[1, 2, 4, 6, 7, 9]`
  - relay_block_from_035: `[2, 4, 9]`
  - free_block_from_032: `[0, 13, 14]`
  - anchor_from_relay_union_free: `[0, 2, 4, 9, 13, 14]`
  - anchor_node_residues_034: `[0, 2, 4, 9, 13, 14]`
  - lift_mask_from_034: `[1, 1, 0, 0, 0, 0, 1, 1]`
  - state_pipeline_pass: `True`
- B0:
  - mediator_union_035: `[1, 4, 8, 11, 14]`
  - relay_block_from_035: `[4, 8]`
  - free_block_from_032: `[0, 2, 3]`
  - anchor_from_relay_union_free: `[0, 2, 3, 4, 8]`
  - anchor_node_residues_034: `[0, 2, 3, 4, 8]`
  - lift_mask_from_034: `[0, 0, 0, 1, 0, 1, 0, 0]`
  - state_pipeline_pass: `True`
- B1:
  - mediator_union_035: `[0, 8, 10, 11, 13, 14]`
  - relay_block_from_035: `[8, 10, 13]`
  - free_block_from_032: `[2, 3, 7]`
  - anchor_from_relay_union_free: `[2, 3, 7, 8, 10, 13]`
  - anchor_node_residues_034: `[2, 3, 7, 8, 10, 13]`
  - lift_mask_from_034: `[0, 0, 0, 1, 0, 1, 0, 0]`
  - state_pipeline_pass: `True`

## Checks

- two_hop_relay_007_theorem_pass: `True`
- lift_mask_sheet_018_theorem_pass: `True`
- anchor_rank_selector_023_theorem_pass: `True`
- free_block_scalar_032_theorem_candidate_pass: `True`
- anchor_residue_chain_033_theorem_candidate_pass: `True`
- anchor_path_chain_034_theorem_candidate_pass: `True`
- relay_selector_035_theorem_candidate_pass: `True`
- mediator_source_is_artifact_007_parsed: `True`
- relay_target_source_is_artifact_011_rows: `True`
- all_relay_blocks_match_between_035_and_033: `True`
- all_free_blocks_match_between_032_and_033: `True`
- all_anchor_unions_match_033: `True`
- all_anchor_sets_match_034_node_residues: `True`
- all_state_pipelines_pass: `True`

## Source caveats

- Artifact 034 used known Project22 anchor node paths as fallback rather than auto-extracting them from Project22 artifact 012.

## Interpretation

This composes the current local anchor payload provenance pipeline. The anchor payload is now generated from native two-hop mediator geometry plus compact state-bit scalar selectors, then matched through anchor residues, anchor paths, and lift masks.

## Boundary

This is not full Gap A closure. The scalar laws still need native/provenance interpretation, artifact 034 has a source-binding caveat if it used fallback anchor paths, and the full role-labeled shared_B universe is not yet derived.
