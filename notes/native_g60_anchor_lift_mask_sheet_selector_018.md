# Native G60 anchor lift-mask sheet selector 018

Status: native_g60_anchor_lift_mask_sheet_selector_recorded

## Claim

The inherited Project 22 anchor lift masks are exactly recovered on the closed anchor paths by the native sheet selector node//15 = 1, equivalently node >= 15.

## Result

- theorem_pass: `True`
- row_count: `32`
- lifted_count: `12`
- unlifted_count: `20`
- exact_selectors: `['node_ge_15', 'node_sheet_eq_1', 'ordinary_pair0_or_branch_sheet1_node1']`
- expected_sheet_selector_exact: `True`

## Path profiles

- O0:
  - closed_path: `[[23, 24], [7, 12], [4, 5], [23, 24]]`
  - flat_nodes: `[23, 24, 7, 12, 4, 5, 23, 24]`
  - lift_mask: `[1, 1, 0, 0, 0, 0, 1, 1]`
- O1:
  - closed_path: `[[28, 29], [0, 2], [4, 9], [28, 29]]`
  - flat_nodes: `[28, 29, 0, 2, 4, 9, 28, 29]`
  - lift_mask: `[1, 1, 0, 0, 0, 0, 1, 1]`
- B0:
  - closed_path: `[[0, 4], [2, 17], [8, 18], [0, 4]]`
  - flat_nodes: `[0, 4, 2, 17, 8, 18, 0, 4]`
  - lift_mask: `[0, 0, 0, 1, 0, 1, 0, 0]`
- B1:
  - closed_path: `[[7, 10], [8, 18], [13, 17], [7, 10]]`
  - flat_nodes: `[7, 10, 8, 18, 13, 17, 7, 10]`
  - lift_mask: `[0, 0, 0, 1, 0, 1, 0, 0]`

## Selector results

- branch_rank0_node_index1: exact `False`, mismatch_count `12`
- branch_rank1_node_index1: exact `False`, mismatch_count `12`
- branch_sheet1_node_index1: exact `False`, mismatch_count `8`
- node_ge_15: exact `True`, mismatch_count `0`
- node_index1: exact `False`, mismatch_count `12`
- node_sheet_eq_1: exact `True`, mismatch_count `0`
- ordinary_base_pair0: exact `False`, mismatch_count `4`
- ordinary_pair0_or_branch_sheet1_node1: exact `True`, mismatch_count `0`
- ordinary_pair0_or_closure: exact `False`, mismatch_count `4`
- pair0_or_closure: exact `False`, mismatch_count `12`
- residue_ge_8: exact `False`, mismatch_count `11`

## Checks

- project22_012_theorem_pass: `True`
- anchor_quotient_pair_017_theorem_pass: `True`
- row_count_is_32: `True`
- all_states_have_lift_masks: `True`
- expected_sheet_selector_exact: `True`
- at_least_one_exact_selector_found: `True`

## Interpretation

The lift mask is not arbitrary relative to the anchor node paths. On the closed Project 22 anchor paths, lifted positions are exactly the upper-sheet node labels 15..29. This identifies a simple native node-sheet reading of the inherited lift mask.

## Boundary

This recovers the inherited lift masks from node-sheet labels on the inherited anchor paths. It does not derive why those exact anchor paths are selected, does not derive the full local cell from native G60 provenance, does not test station fields, does not select unique relay mediators, does not derive the full role-labeled shared_B universe, and does not close Gap A.
