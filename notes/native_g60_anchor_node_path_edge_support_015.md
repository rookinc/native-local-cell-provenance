# Native G60 anchor node path edge support 015

Status: native_g60_anchor_node_path_edge_support_recorded

## Question

Are the Project 22 closed anchor node paths literal pair-walks in canonical G60?

## Result

- all_checks_pass: `True`
- total_anchor_path_step_count: `12`
- supported_anchor_path_step_count: `1`
- unsupported_anchor_path_step_count: `11`
- all_anchor_pair_steps_supported: `False`

## Per state

- O0:
  - closed_path: `[[23, 24], [7, 12], [4, 5], [23, 24]]`
  - supported_step_count: `1/3`
  - internal_supported_count: `0/4`
  - step 0 `[23, 24] -> [7, 12]`: cross_edge_count `1`, edges `[[24, 12]]`
  - step 1 `[7, 12] -> [4, 5]`: cross_edge_count `0`, edges `[]`
  - step 2 `[4, 5] -> [23, 24]`: cross_edge_count `0`, edges `[]`
- O1:
  - closed_path: `[[28, 29], [0, 2], [4, 9], [28, 29]]`
  - supported_step_count: `0/3`
  - internal_supported_count: `0/4`
  - step 0 `[28, 29] -> [0, 2]`: cross_edge_count `0`, edges `[]`
  - step 1 `[0, 2] -> [4, 9]`: cross_edge_count `0`, edges `[]`
  - step 2 `[4, 9] -> [28, 29]`: cross_edge_count `0`, edges `[]`
- B0:
  - closed_path: `[[0, 4], [2, 17], [8, 18], [0, 4]]`
  - supported_step_count: `0/3`
  - internal_supported_count: `0/4`
  - step 0 `[0, 4] -> [2, 17]`: cross_edge_count `0`, edges `[]`
  - step 1 `[2, 17] -> [8, 18]`: cross_edge_count `0`, edges `[]`
  - step 2 `[8, 18] -> [0, 4]`: cross_edge_count `0`, edges `[]`
- B1:
  - closed_path: `[[7, 10], [8, 18], [13, 17], [7, 10]]`
  - supported_step_count: `0/3`
  - internal_supported_count: `1/4`
  - step 0 `[7, 10] -> [8, 18]`: cross_edge_count `0`, edges `[]`
  - step 1 `[8, 18] -> [13, 17]`: cross_edge_count `0`, edges `[]`
  - step 2 `[13, 17] -> [7, 10]`: cross_edge_count `0`, edges `[]`

## Checks

- project22_012_theorem_pass: `True`
- paper_boundary_014_pass: `True`
- g60_edge_count_is_120: `True`
- state_count_is_4: `True`
- total_anchor_path_step_count_is_12: `True`
- all_states_have_three_anchor_steps: `True`

## Interpretation

This tests whether the inherited Project 22 closed anchor node paths are literal pair-walks in canonical G60. A supported pair step means at least one native G60 edge crosses between consecutive node pairs. If support is partial or absent, the anchor paths are likely not simple native G60 pair-walks and require a different provenance layer such as station fields, lifted masks, or quotient-pair geometry.

## Boundary

This is only a literal G60 edge-support audit for inherited anchor node paths. It does not derive anchor paths or lift masks from native provenance, does not select unique relay mediators, does not derive the full role-labeled shared_B universe, and does not close Gap A.
