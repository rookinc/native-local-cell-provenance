# Native G60 C path residue support bit law 006

Status: native_g60_c_path_residue_support_bit_law_recorded

## Candidate law

direct residue support iff (shell_bit=0 and step in {0,1}) or (shell_bit=1 and step=2*(1-rank_bit))

## Result

- theorem_pass: `True`
- bit_step_law_exact: `True`
- supported_count: `6`
- unsupported_count: `6`

## Supported slots

- `['B0', 2, 0, 2]`
- `['B1', 0, 4, 5]`
- `['O0', 0, 11, 2]`
- `['O0', 1, 2, 14]`
- `['O1', 0, 13, 1]`
- `['O1', 1, 1, 10]`

## Unsupported slots

- `['B0', 0, 2, 5, 2]`
- `['B0', 1, 5, 0, 2]`
- `['B1', 1, 5, 2, 2]`
- `['B1', 2, 2, 4, 2]`
- `['O0', 2, 14, 11, 2]`
- `['O1', 2, 10, 13, 2]`

## Checks

- project22_011_theorem_pass: `True`
- residue_support_004_checks_pass: `True`
- residue_distance_005_checks_pass: `True`
- row_count_is_12: `True`
- observed_supported_count_is_6: `True`
- bit_step_law_exact: `True`

## Interpretation

The direct mod15 residue support pattern is generated exactly by a local bit/step law. This does not prove native local-cell provenance, but it shows that the half-supported quotient signal is structured by the same shell/rank bits that generate the local Lift & Twist cell.

## Boundary

This is a support-pattern law over the simple mod15 residue projection only. It does not derive the C paths, does not derive the local cell from native G60 provenance, does not derive the full role-labeled shared_B edge universe, and does not close Gap A.
