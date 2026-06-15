# Lift & Twist payload overlap marker law 008

Status: lift_twist_payload_overlap_marker_law_recorded

## Claim

The local answer-cell payload overlap markers obey an exact two-bit law. With shell bit b and rank bit r, the overlap count is r+2*b-2*b*r. Marker 13 appears exactly for ordinary rank 1; marker 2 appears exactly for branch states; marker 0 appears exactly for branch rank 0. This recovers the observed overlaps: O0 none, O1 {13}, B0 {0,2}, B1 {2}.

## Laws

- overlap_count: `r + 2*b - 2*b*r`
- marker_13: `present iff (1-b)*r = 1`
- marker_2: `present iff b = 1`
- marker_0: `present iff b*(1-r) = 1`

## Table

| state | b | r | observed overlap | predicted overlap | count | match |
|---|---:|---:|---|---|---:|---:|
| O0 | 0 | 0 | none | none | 0 | 1 |
| O1 | 0 | 1 | 13 | 13 | 1 | 1 |
| B0 | 1 | 0 | 0 2 | 0 2 | 2 | 1 |
| B1 | 1 | 1 | 2 | 2 | 1 | 1 |

## Checks

- all_overlap_sets_match: `True`
- all_overlap_counts_match: `True`
- all_overlap_matches: `True`
- project22_006_theorem_pass: `True`
- project22_007_theorem_pass: `True`
- theorem_pass: `True`

## Interpretation

This is the first payload-coupling law. It derives the overlap signature of each local state from the two state bits.

## Boundary

This derives the overlap markers between C payload values and anchor residues for the 006 target table. It does not derive the full C payload paths, full anchor residue sets, the reduced 16-candidate universe, or Gap A closure.
