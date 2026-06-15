# Anchor free-block law search 030

Status: anchor_free_block_law_search_recorded

## Result

- all_checks_pass: `True`
- exact_law_hit_count_reported: `0`

## Blocks

- O0:
  - bits: `(0, 0)`
  - observed_set: `[4, 5, 7, 8, 9, 12]`
  - relay_block: `[4, 5, 7]`
  - free_block: `[8, 9, 12]`
  - c_values: `[2, 11, 14]`
  - c_overlap_free: `[]`
  - offset_summary: `{'relay_to_free_offsets': [], 'c_to_free_offsets': []}`
- O1:
  - bits: `(0, 1)`
  - observed_set: `[0, 2, 4, 9, 13, 14]`
  - relay_block: `[2, 4, 9]`
  - free_block: `[0, 13, 14]`
  - c_values: `[1, 10, 13]`
  - c_overlap_free: `[13]`
  - offset_summary: `{'relay_to_free_offsets': [], 'c_to_free_offsets': []}`
- B0:
  - bits: `(1, 0)`
  - observed_set: `[0, 2, 3, 4, 8]`
  - relay_block: `[4, 8]`
  - free_block: `[0, 2, 3]`
  - c_values: `[0, 2, 5]`
  - c_overlap_free: `[0, 2]`
  - offset_summary: `{'relay_to_free_offsets': [], 'c_to_free_offsets': []}`
- B1:
  - bits: `(1, 1)`
  - observed_set: `[2, 3, 7, 8, 10, 13]`
  - relay_block: `[8, 10, 13]`
  - free_block: `[2, 3, 7]`
  - c_values: `[2, 4, 5]`
  - c_overlap_free: `[2]`
  - offset_summary: `{'relay_to_free_offsets': [], 'c_to_free_offsets': []}`

## Exact law hits first 50

- none

## Checks

- unlifted_relay_cover_011_theorem_pass: `True`
- candidate_census_020_theorem_pass: `True`
- o0_selector_029_checks_pass: `True`
- all_free_blocks_nonempty: `True`
- o0_free_block_is_8_9_12: `True`

## Interpretation

This searches for a common law generating the free block from relay hits or C values. If no common transform appears, the free block likely requires station/provenance context or a richer relational law.

## Boundary

This is a law search over observed free blocks. It does not prove native provenance, does not select relay mediators, does not derive the full shared_B universe, and does not close Gap A.
