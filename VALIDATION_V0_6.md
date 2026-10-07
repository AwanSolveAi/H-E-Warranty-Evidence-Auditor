# AwanSolveAi Heavy-Equipment Warranty Claim Evidence Auditor
## V0.6 Validation Report

### V0.6 changes
Generic parser hardening based on External Set C:
- anchored and expanded model-label handling
- anchored and expanded repair/correction labels
- broader labor-hour labels

### Regression results
- Development corpus: 30/30 = 100%
- Earlier holdout + adversarial: 50/50 = 100%
- Robustness suite: 12/12 = 100%
- Automated tests: 34/34 PASS
- External Set C regression: 15/15 = 100%

### Independent external release gate
External Set D was created only after V0.6 was frozen.

Set D families:
- Coaire compressor warranty claim terminology
- Show-Me Shortline agricultural warranty terminology
- Mi-T-M dealer warranty terminology
- Rightline attachment reimbursement terminology
- Industrial Gold compressor warranty terminology

Blind first-pass results:
- Overall status accuracy: 15/15 = 100%
- Field extraction accuracy: 165/165 = 100%
- Critical false READY: 0

### Interpretation
V0.6 passes the current independent external synthetic-real-format release gate.
The result demonstrates generalization across several public warranty-form vocabularies not used
to tune V0.6.

### Remaining limitations
- Validation documents contain synthetic claim facts, not real customer warranty records.
- PDF text extraction only; image-only/scanned PDFs route to review rather than OCR.
- General Heavy Equipment and Generator profiles only.
- No OEM-specific warranty-eligibility/coverage logic.
- The system audits documentation completeness and internal consistency; it does not approve claims.

### Current verdict
V0.6: PASS on current automated, regression, robustness, and independent external-format gates.
Recommended status: DEMO CANDIDATE, subject to one final live Windows UI smoke test of V0.6.
