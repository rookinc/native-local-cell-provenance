# Native G60 C path residue distance 005

Status: native_g60_c_path_residue_distance_recorded

## Question

When a Project 22 C-path transition is not a direct mod15 residue edge, is it still nearby in the residue quotient graph?

## Result

- target_step_count: `12`
- distance_counts: `{'1': 6, '2': 6}`
- max_finite_distance: `2`
- all_target_residue_steps_reachable: `True`

## Per state

- B0:
  - path: `[2, 5, 0, 2]`
  - distances: `[2, 2, 1]`
  - shortest_paths: `[[2, 8, 5], [5, 1, 0], [0, 2]]`
- B1:
  - path: `[4, 5, 2, 4]`
  - distances: `[1, 2, 2]`
  - shortest_paths: `[[4, 5], [5, 8, 2], [2, 0, 4]]`
- O0:
  - path: `[11, 2, 14, 11]`
  - distances: `[1, 1, 2]`
  - shortest_paths: `[[11, 2], [2, 14], [14, 0, 11]]`
- O1:
  - path: `[13, 1, 10, 13]`
  - distances: `[1, 1, 2]`
  - shortest_paths: `[[13, 1], [1, 10], [10, 1, 13]]`

## Interpretation

This tests whether C-path transitions that are not direct mod15 residue edges are nevertheless nearby in the residue quotient graph induced by canonical G60 edges. If all target transitions have small quotient distance, the C paths may be quotient-walk or closure paths rather than literal edges. If distances are large or unreachable, the mod15 residue quotient is probably the wrong native support layer.

## Boundary

This is only a shortest-path audit in the simple vertex mod15 residue quotient. It does not derive native local-cell provenance, does not test station provenance fields, lifted masks, or alternate quotient maps, and does not close Gap A.
