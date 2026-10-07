# V0.2 Validation Report

## Scope
AwanSolveAi Heavy-Equipment Warranty Claim Evidence Auditor - Claim_Evidence_Audit_Core V0.2

## Automated results
- Unit/integration tests: 21/21 PASS
- Development corpus: 30/30 exact overall-status matches (100%)
- Unseen holdout corpus: 25/25 exact overall-status matches (100%)
- Adversarial corpus: 25/25 exact overall-status matches (100%)
- Combined independent validation: 50/50 (100%)
- Benchmark/claim-ID leakage scan in `src/` and `app/`: 0 hits
- Python syntax compilation: PASS

## Citation validation
- Source file + page are attached to extracted evidence.
- Multi-page integration test confirms diagnostic evidence can resolve to page 2.
- Representative smoke result: `diagnostic_record.pdf p.2`.

## Generator profile
Additional deterministic checks:
- G001 Battery voltage evidence
- G002 Generator output voltage evidence
- G003 Frequency evidence
- G004 Load-test evidence

## Performance
50 independent validation claims processed sequentially.
- Mean audit time: 0.0080 seconds
- Maximum audit time: 0.0116 seconds

## PDF visual verification
A representative two-page holdout diagnostic PDF was rendered and visually inspected.
No clipping, overlap, broken glyphs, or unreadable table content was observed.

## Startup gate
NOT YET VERIFIED in this runtime.
Reason: Streamlit is not installed in the execution environment. The UI source passes Python syntax compilation, and `streamlit` remains declared in requirements.txt. A real startup smoke test must be run after installing project requirements.

## Current boundary / limitations
- Text-based PDFs only; OCR/scanned documents are not yet supported.
- DOCX/XLSX/images are not yet supported as claim inputs.
- General Heavy Equipment and Generator profiles only.
- No OEM-specific warranty eligibility logic.
- No reimbursement calculation or claim approval.
- Validation corpora are synthetic, not historical dealer claims.
- Current 100% results apply only to the controlled deterministic corpora included in this project and must not be generalized to unknown real dealer documents.

## Next recommended gate
1. Run Streamlit startup after requirements installation.
2. Add scanned/noisy PDF tests.
3. Add document-injection/spoofed-label cases.
4. Add field-level extraction scoring, not only final-status scoring.
5. Add PDF audit report export.
6. Then evaluate on anonymized real-world claim samples when available.
