# Lift & Twist local answer-cell target 006

Status: lift_twist_local_answer_cell_target_recorded

## Claim

The Project 22 reduced Lift & Twist data can be consolidated into one four-state local answer-cell target. Each hidden state has one C readout payload, one anchor readout payload, and one selected diagonal candidate. This target table is the object a stronger native generator must derive.

## Target table

| state | shell | rank | selected | C row | anchor col | C key | anchor key | overlap |
|---|---|---:|---:|---:|---:|---:|---:|---|
| O0 | ordinary | 0 | 1 | 0 | 1 | 11 | 0 | none |
| O1 | ordinary | 1 | 6 | 1 | 2 | 13 | 12 | 13 |
| B0 | branch | 0 | 8 | 2 | 0 | 2 | 4 | 0 2 |
| B1 | branch | 1 | 15 | 3 | 3 | 4 | 13 | 2 |

## Checks

- state_order_matches_expected: `True`
- selected_indices_match_expected: `True`
- c_rows_match_expected: `True`
- anchor_cols_match_expected: `True`
- ordinary_states_match_expected: `True`
- branch_states_match_expected: `True`
- project22_003_theorem_pass: `True`
- project22_005_theorem_pass: `True`
- theorem_pass: `True`

## Interpretation

This artifact turns the Lift & Twist representation into a concrete generator target.
The next problem is no longer to name the four states. The next problem is to derive their payloads.

## Boundary

This is a target-table construction, not a native derivation. It organizes the payloads that must be generated from one local answer cell, but it does not yet derive those payloads or close Gap A.
