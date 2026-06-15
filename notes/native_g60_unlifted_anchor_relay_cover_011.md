# Native G60 unlifted anchor relay cover 011

Status: native_g60_unlifted_anchor_relay_cover_recorded

## Question

Does the unlifted anchor-path layer cover every missing C relay?

## Result

- theorem_pass: `True`
- transition_count: `6`
- covered_count: `6`
- uncovered_count: `0`
- unique_unlifted_count: `2`
- total_unlifted_hits: `15`
- total_lifted_hits: `2`
- total_closure_hits: `3`

## Transition cover

- B0 step 0 `2 -> 5`: unlifted hits `[[8, 2, 0, 8]]`, unique `True`
- B0 step 1 `5 -> 0`: unlifted hits `[[4, 0, 1, 4], [4, 3, 1, 4], [8, 2, 0, 8]]`, unique `False`
- B1 step 1 `5 -> 2`: unlifted hits `[[8, 1, 0, 8]]`, unique `True`
- B1 step 2 `2 -> 4`: unlifted hits `[[8, 1, 0, 8], [10, 0, 1, 10], [10, 3, 1, 10], [13, 2, 0, 13]]`, unique `False`
- O0 step 2 `14 -> 11`: unlifted hits `[[4, 2, 0, 4], [5, 2, 1, 5], [7, 1, 0, 7]]`, unique `False`
- O1 step 2 `10 -> 13`: unlifted hits `[[2, 1, 1, 2], [4, 2, 0, 4], [9, 2, 1, 9]]`, unique `False`

## Checks

- lift_mask_class_010_theorem_pass: `True`
- unsupported_transition_count_is_6: `True`
- all_transitions_have_unlifted_anchor_cover: `True`
- uncovered_count_is_0: `True`
- unlifted_hit_count_matches_010: `True`
- lifted_hit_count_matches_010: `True`

## Claim

Every unsupported C transition is covered by at least one same-state unlifted anchor-path mediator. The unlifted anchor-path layer repairs all six missing direct C-residue transitions.

## Interpretation

Artifact 010 showed that most anchor-path mediator hits are unlifted. Artifact 011 sharpens this: unlifted anchor-path positions are sufficient to cover every missing C relay. This suggests the missing C-side closure is carried by the unlifted anchor layer, while lifted positions may be secondary or exceptional.

## Boundary

This is a cover theorem, not a unique selector theorem. It does not select a unique mediator for every transition, does not derive the anchor paths or lift masks from native G60 provenance, does not test station fields, does not derive the full role-labeled shared_B edge universe, and does not close Gap A.
