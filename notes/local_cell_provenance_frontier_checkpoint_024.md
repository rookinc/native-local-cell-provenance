# Local cell provenance frontier checkpoint 024

Status: local_cell_provenance_frontier_checkpoint_recorded

## Checkpoint result

- checkpoint_pass: `True`

## Closed results

- 012: Every Project22 C-path step is covered by direct mod15 G60 residue support or same-state unlifted anchor-path relay support.
  - status: `closed intermediate theorem`
- 017: Every Project22 closed anchor node-path step is supported after projection to mod15 residue pairs.
  - status: `closed intermediate theorem`
- 018: Project22 anchor lift masks are exactly recovered by node-sheet selector node >= 15 on the inherited anchor paths.
  - status: `closed intermediate theorem`
- 023: Given observed anchor residue sets, observed pair-size profiles, corrected quotient candidate census, and the rank law, the observed anchor paths are selected exactly.
  - status: `conditional selector theorem`

## Open frontier

- Derive the anchor residue sets natively rather than inheriting them from Project22.
- Derive the pair-size profiles natively rather than inheriting them from observed anchor paths.
- Validate or derive the rank law rank = 2 + 7*b + 2*r - b*r from native/provenance fields rather than fitting it to four observed states.
- Test station/provenance fields if available.
- Select unique relay mediators rather than only covering relay transitions.
- Derive the full role-labeled shared_B edge universe.
- Only then reconsider Gap A closure.

## Checks

- c_path_cover_012_theorem_pass: `True`
- paper_boundary_014_pass: `True`
- anchor_literal_015_checks_pass: `True`
- anchor_literal_015_not_full_support: `True`
- anchor_residue_016_full_support: `True`
- anchor_quotient_017_theorem_pass: `True`
- lift_mask_sheet_018_theorem_pass: `True`
- candidate_census_020_theorem_pass: `True`
- candidate_census_020_not_unique: `True`
- feature_audit_021_checks_pass: `True`
- rank_law_022_theorem_pass: `True`
- rank_selector_023_theorem_pass: `True`

## Summary

Project24 has moved the local-cell provenance frontier. The C-path side is covered by quotient-anchor support; the anchor side is quotient-pair supported; lift masks are native sheet labels; and the observed anchor paths are conditionally selected by a compact bit-rank law inside the candidate universe. The remaining upstream problem is no longer generic support. It is provenance selection: native derivation of anchor residue sets, pair-size profiles, and the rank law.

## Boundary

This checkpoint does not close Gap A. It records the current frontier and explicitly preserves the remaining native-provenance obligations.
