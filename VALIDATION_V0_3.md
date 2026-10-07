# AwanSolveAi Heavy-Equipment Warranty Claim Evidence Auditor
## V0.3 Validation Report

### Scope
Claim_Evidence_Audit_Core V0.3 - robustness hardening release.

### Automated release results
- Python syntax compilation: PASS
- Automated tests: 34/34 PASS
- Development corpus overall-status accuracy: 30/30 (100%)
- Unseen holdout overall-status accuracy: 25/25 (100%)
- Adversarial overall-status accuracy: 25/25 (100%)
- Combined holdout + adversarial: 50/50 (100%)
- Robustness cases: 12/12 (100%)
- Development field extraction exact-set coverage: 342/342 (100%)
- Supported holdout identity-field coverage: 96/96 (100%)
- Unsupported/minimum-boundary holdout cases are scored by rejection accuracy, not field extraction.
- Benchmark/claim-ID leakage in `src/` and `app/`: 0 hits
- Critical false PASS in included deterministic benchmark: 0

### V0.3 hardening
- Corrupt PDF detection: PASS
- Blank / effectively unreadable PDF detection: PASS
- Image-only/scanned PDF detection: PASS -> REVIEW_REQUIRED
- No-supported-PDF package handling: PASS -> REVIEW_REQUIRED
- Document/prompt-injection resistance: PASS -> REVIEW_REQUIRED
- Spoofed/conflicting asset identity detection: PASS
- Duplicate evidence detection: PASS
- Critical unitless numeric measurement handling: PASS -> REVIEW_REQUIRED
- Generator missing-load-test handling: PASS
- Page-level source citations: PASS
- PDF audit report export: PASS
- PDF audit report visual render inspection: PASS

### Performance
Sequential audit of 80 text-PDF claims:
- Mean: 0.0087 s/claim
- Maximum: 0.0109 s/claim

### UI startup
- Streamlit startup: NOT VERIFIED - Streamlit unavailable in this offline runtime
- Installation was attempted, but this execution environment has no outbound package access.
- `streamlit>=1.40` remains declared in requirements.txt.
- The UI module passes Python syntax compilation.

### Important limitations
- OCR is NOT yet performed. Image-only/scanned PDFs are detected and routed to human review rather than guessed.
- Claim input remains PDF-only in V0.3.
- General Heavy Equipment and Generator profiles are implemented.
- No OEM-specific warranty eligibility, reimbursement, authorization, or approval logic.
- All benchmark claim packages are synthetic.
- The 100% benchmark results apply only to the included controlled datasets and do not imply 100% accuracy on unknown real dealer documents.

### V0.3 verdict
ROBUSTNESS CORE: PASS on included automated gates.
FULL DEMO-READY GOLD STANDARD: NOT YET CLAIMED.

Remaining high-value gates:
1. Real Streamlit startup on the target Windows environment after installing requirements.
2. Small external/anonymized real-world warranty-document evaluation.
3. Optional OCR pipeline for scanned claims, with separate OCR accuracy gates.
4. Broader malformed/noisy real PDF corpus.
5. Real-client/OEM rule-pack validation before any OEM-specific compliance statement.
