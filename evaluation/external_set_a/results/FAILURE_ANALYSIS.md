# Blind External Validation - Failure Analysis

## Frozen-parser first pass
The V0.3 parser was not modified before or during this external validation run.

### Overall-status result
13/15 correct = 86.7%

### Field extraction result
156/165 correct = 94.5%

## Overall-status failures

### EXT-013 - KTEC-style READY claim
Expected: READY
Actual: INCONSISTENT

Root cause:
The parser interpreted the external field label `Replacement Part Number` incorrectly.
Its broad `Replacement Part` pattern captured the word `Number` as if it were an actual part number.
The real part value `CN-4421` was also found in supporting records, producing a false part conflict:
`CN-4421` versus `Number`.

Classification:
Generic parser-label boundary bug, not a claim-rule failure.

### EXT-014 - KTEC-style missing-diagnostic-evidence claim
Expected: MISSING_EVIDENCE
Actual: INCONSISTENT

The intended missing diagnostic reading was correctly detected.
However, the same false `Replacement Part Number` parsing defect also generated an artificial part conflict.
Because INCONSISTENT has higher result priority than MISSING_EVIDENCE, the final status became INCONSISTENT.

## Field-level failures

Nine field misses occurred, all in the `cause` field:
- ANA-style: EXT-004, EXT-005, EXT-006
- H&S-style: EXT-007, EXT-008, EXT-009
- RockZone-style: EXT-010, EXT-011, EXT-012

Root cause:
The current cause regex is not sufficiently anchored to field labels.
It can match the substring `Cause` inside ordinary narrative text such as `caused unstable control signal`,
then incorrectly extract a fragment such as `d unstable control signal.`

Classification:
Generic anchoring bug. This should be fixed by matching cause labels only at line/field starts.

## What worked well without tuning
- Blue Giant-style: 3/3 correct overall
- ANA generator-style: 3/3 correct overall
- H&S agricultural-style: 3/3 correct overall
- RockZone excavator-style: 3/3 correct overall
- K-Tec-style: conflict case correctly detected; two other cases exposed one generic label-parser defect
- Missing diagnostic evidence: correctly detected
- Serial conflicts: correctly detected
- Generator profile: worked on ANA-style terminology
- Cross-document identity consistency: worked across external layouts

## Correct next step
Do NOT overwrite this first-pass result.

1. Preserve this pack/results as External Set A baseline.
2. Create V0.4 tuning branch.
3. Fix only the two generic parser defects:
   - anchored cause-label extraction
   - exact `Replacement Part Number` handling
4. Re-run Set A as a regression/tuning set.
5. Build a fresh External Set B with unseen field wording/layouts.
6. Use Set B, not Set A, as the new independent release gate.
