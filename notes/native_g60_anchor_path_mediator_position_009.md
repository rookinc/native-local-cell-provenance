# Native G60 anchor path mediator position 009

Status: native_g60_anchor_path_mediator_position_recorded

## Question

Do the same-state anchor mediator hits from artifact 008 sit on the closed Project 22 anchor node paths?

## Result

- theorem_pass: `True`
- all_anchor_hits_on_closed_anchor_path: `True`
- path_residue_matches: `{'B0': True, 'B1': True, 'O0': True, 'O1': True}`

## Closed path profiles

- O0:
  - source_key: `observed_anchor_node_path`
  - closed_path: `[[23, 24], [7, 12], [4, 5], [23, 24]]`
  - residue_set: `[4, 5, 7, 8, 9, 12]`
- O1:
  - source_key: `observed_anchor_node_path`
  - closed_path: `[[28, 29], [0, 2], [4, 9], [28, 29]]`
  - residue_set: `[0, 2, 4, 9, 13, 14]`
- B0:
  - source_key: `observed_anchor_node_path`
  - closed_path: `[[0, 4], [2, 17], [8, 18], [0, 4]]`
  - residue_set: `[0, 2, 3, 4, 8]`
- B1:
  - source_key: `observed_anchor_node_path`
  - closed_path: `[[7, 10], [8, 18], [13, 17], [7, 10]]`
  - residue_set: `[2, 3, 7, 8, 10, 13]`

## Mediator positions

- B0 step 0: `2 -> 5`, anchor hits `[8]`, pair indices `[2]`
- B0 step 1: `5 -> 0`, anchor hits `[4, 8]`, pair indices `[0, 2, 3]`
- B1 step 1: `5 -> 2`, anchor hits `[8]`, pair indices `[1]`
- B1 step 2: `2 -> 4`, anchor hits `[8, 10, 13]`, pair indices `[0, 1, 2, 3]`
- O0 step 2: `14 -> 11`, anchor hits `[4, 5, 7, 8]`, pair indices `[0, 1, 2, 3]`
- O1 step 2: `10 -> 13`, anchor hits `[2, 4, 9]`, pair indices `[1, 2]`

## Checks

- anchor_mediation_008_theorem_pass: `True`
- project22_012_theorem_pass: `True`
- state_anchor_paths_found: `True`
- unsupported_transition_count_is_6: `True`
- all_anchor_hits_on_closed_anchor_path: `True`
- all_closed_path_residue_sets_match_anchor_residue_sets: `True`

## Claim

Every same-state anchor mediator hit from artifact 008 lies on the same state's closed Project 22 anchor node path from artifact 012. The closed path residue sets match the Project 22 anchor residue sets.

## Interpretation

The anchor mediation of missing C relays is not merely set-level anchor overlap. The mediator hits sit on the closed anchor node-path geometry of the same local state. This strengthens the coupling between C-side relay closure and anchor-side path geometry.

## Boundary

This positions mediator hits on known Project 22 closed anchor paths. It does not select a unique mediator in every case, does not derive the closed anchor paths from native G60 provenance, does not test station fields or lifted masks, does not derive the full role-labeled shared_B edge universe, and does not close Gap A.
