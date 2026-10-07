# AwanSolveAi Heavy-Equipment Warranty Claim Evidence Auditor
## V0.5 Validation Report

### What changed
V0.5 fixes generic parser gaps exposed by the independent External Set B first-pass run:
1. Serial labels are anchored and longest-form labels are matched first, preventing `Machine Serial Number`
   or `Compressor Serial No.` from producing false values such as `Number` or `No`.
2. Additional external complaint labels are recognized as actual field labels, including:
   - Description of the failure, condition found
   - Detailed information of the problem found
   - Problem Reported
   - Warranty Concern
   - Problem Description
3. Diagnostic measurement extraction is anchored and recognizes `Measured Value`.

### Preserved blind result
Before V0.5 tuning, External Set B produced:
- Overall status: 8/15 = 53.3%
- Field extraction: 135/165 = 81.8%

That result remains the honest independent first-pass baseline for V0.4.

### V0.5 regression/tuning result
After the three generic parser changes:
- External Set B overall: 15/15 = 100%
- External Set B fields: 165/165 = 100%
- Development corpus: 30/30 = 100%
- Earlier holdout + adversarial: 50/50 = 100%
- Robustness suite: 12/12 = 100%
- Automated tests: 34/34 PASS

### Release interpretation
External Set B is now a tuning/regression set and can no longer serve as independent proof for V0.5.

### Next release gate
Create External Set C using new public terminology/layout families not used in:
- internal development corpus,
- External Set A, or
- External Set B.

Run V0.5 unchanged against Set C before any further parser changes.

### Current verdict
V0.5 regression state: PASS
Independent external release gate for V0.5: PENDING SET C
