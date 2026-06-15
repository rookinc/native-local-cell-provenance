# Native G60 C path residue support 004

Status: native_g60_c_path_residue_support_recorded

## Question

Do the Project 22 C-path steps appear as residue-class transitions after projecting native G60 vertices mod 15?

## Result

- total_tested_c_path_steps: `12`
- directed_residue_supported_count: `6`
- undirected_residue_supported_count: `6`
- all_c_paths_directed_residue_supported: `False`
- all_c_paths_undirected_residue_supported: `False`

## Per state

- B0: path `[2, 5, 0, 2]`
  - directed_flags: `[False, False, True]`
  - directed_support_counts: `[0, 0, 1]`
  - undirected_flags: `[False, False, True]`
  - undirected_support_counts: `[0, 0, 1]`
- B1: path `[4, 5, 2, 4]`
  - directed_flags: `[True, False, False]`
  - directed_support_counts: `[1, 0, 0]`
  - undirected_flags: `[True, False, False]`
  - undirected_support_counts: `[1, 0, 0]`
- O0: path `[11, 2, 14, 11]`
  - directed_flags: `[True, True, False]`
  - directed_support_counts: `[2, 2, 0]`
  - undirected_flags: `[True, True, False]`
  - undirected_support_counts: `[2, 2, 0]`
- O1: path `[13, 1, 10, 13]`
  - directed_flags: `[True, True, False]`
  - directed_support_counts: `[2, 2, 0]`
  - undirected_flags: `[True, True, False]`
  - undirected_support_counts: `[2, 2, 0]`

## Interpretation

This tests whether Project 22 C-path transitions are supported after projecting native G60 vertices to residues mod 15. Positive support would suggest the C paths are quotient-visible rather than literal vertex-adjacency paths. Negative support would push the search toward station provenance or transition overlays.

## Boundary

This is only a residue-projection support test using vertex mod 15. It does not prove native local-cell provenance, does not test all possible quotient maps or station fields, does not derive the full role-labeled shared_B universe, and does not close Gap A.
