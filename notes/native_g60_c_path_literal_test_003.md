# Native G60 C path literal test 003

Status: native_g60_c_path_literal_test_recorded

## Question

Do the Project 22 C paths appear as literal paths in the copied canonical G60 local edge payload?

## Result

- g60_edge_count: `120`
- g60_vertex_count: `60`
- total_tested_c_path_edges: `12`
- total_literal_g60_edges: `0`
- literal_c_paths_all_pass: `False`
- literal_c_paths_any_support: `False`

## Per state

- B0: path `[2, 5, 0, 2]`, literal_flags `[False, False, False]`, all_edges_literal `False`
- B1: path `[4, 5, 2, 4]`, literal_flags `[False, False, False]`, all_edges_literal `False`
- O0: path `[11, 2, 14, 11]`, literal_flags `[False, False, False]`, all_edges_literal `False`
- O1: path `[13, 1, 10, 13]`, literal_flags `[False, False, False]`, all_edges_literal `False`

## Interpretation

This tests whether the Project 22 C paths are literal paths in the copied canonical G60 local edge payload. A failure here does not refute the local cell; it means the C paths are likely quotient-visible, transition-overlay, or provenance-field paths rather than literal G60 adjacency paths.

## Boundary

This is only a literal-edge test against the copied G60 local edge payload. It does not test quotient paths, station provenance paths, lifted masks, or the full role-labeled shared_B universe, and it does not close Gap A.
