# Native G60 anchor path lift-mask mediator classification 010

Status: native_g60_anchor_path_lift_mask_mediator_class_recorded

## Question

Do the anchor mediator hits from artifact 009 land on lifted, unlifted, or closure positions of the Project 22 anchor paths?

## Result

- theorem_pass: `True`
- total_mediator_hits: `17`
- lifted_hit_count: `2`
- unlifted_hit_count: `15`
- closure_hit_count: `3`

## Lift masks

- O0: `[1, 1, 0, 0, 0, 0, 1, 1]` from `observed_lift_mask`
- O1: `[1, 1, 0, 0, 0, 0, 1, 1]` from `observed_lift_mask`
- B0: `[0, 0, 0, 1, 0, 1, 0, 0]` from `observed_lift_mask`
- B1: `[0, 0, 0, 1, 0, 1, 0, 0]` from `observed_lift_mask`

## Transition profiles

- B0 step 0 `2 -> 5`: hit_count `1`, lifted `0`, unlifted `1`, closure `0`, classes `['unlifted']`
- B0 step 1 `5 -> 0`: hit_count `3`, lifted `0`, unlifted `3`, closure `1`, classes `['unlifted']`
- B1 step 1 `5 -> 2`: hit_count `1`, lifted `0`, unlifted `1`, closure `0`, classes `['unlifted']`
- B1 step 2 `2 -> 4`: hit_count `4`, lifted `0`, unlifted `4`, closure `1`, classes `['unlifted']`
- O0 step 2 `14 -> 11`: hit_count `5`, lifted `2`, unlifted `3`, closure `1`, classes `['lifted', 'unlifted']`
- O1 step 2 `10 -> 13`: hit_count `3`, lifted `0`, unlifted `3`, closure `0`, classes `['unlifted']`

## Checks

- anchor_path_position_009_theorem_pass: `True`
- project22_012_theorem_pass: `True`
- lift_masks_available_for_all_states: `True`
- mediator_hit_count_positive: `True`
- all_mediator_hits_classified: `True`
- all_transitions_have_at_least_one_classified_hit: `True`

## Interpretation

This classifies the anchor-path mediator hits from artifact 009 against the Project 22 anchor lift masks. If the mediator hits concentrate in lifted, unlifted, or closure positions, that may provide the next selector needed to refine anchor mediation toward a native provenance law.

## Boundary

This is a classification audit, not a selector theorem. It does not prove unique mediator selection, does not derive the closed anchor paths or lift masks from native G60 provenance, does not test station fields, does not derive the full role-labeled shared_B edge universe, and does not close Gap A.
