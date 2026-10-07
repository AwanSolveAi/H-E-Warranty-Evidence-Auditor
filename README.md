
# AwanSolveAi Claim Evidence Audit Core V0.2

Validation-hardened core for the Heavy-Equipment Warranty Claim Evidence Auditor.

## V0.2 capabilities
- PDF-only input
- General Heavy Equipment profile
- Generator-specific profile
- Page-level source citations
- Deterministic field extraction and cross-document rules
- Excel audit export with Source / Page column
- Streamlit demo UI
- 30-claim development corpus
- 25-claim unseen holdout corpus
- 25-claim adversarial corpus
- Rule-isolation regression tests

## Run
`pytest -q`

`python evaluate_corpus.py`

`python evaluate_v02.py`

`python run_audit.py evaluation/holdout/A-020 --xlsx outputs/holdout_A020.xlsx`

Generator:
`python run_audit.py evaluation/holdout/A-006 --profile generator`

UI:
`streamlit run app/streamlit_app.py`

## Product boundary
This software audits the completeness and internal consistency of supplied warranty-claim evidence.
It does not determine OEM warranty eligibility, approve claims, calculate reimbursement, authorize repairs,
or replace manufacturer warranty policy or warranty-administrator review.


## V0.3 additions
- corrupt/unreadable/scanned-PDF fail-safe detection
- document-injection resistance
- critical numeric/unit validation
- PDF audit report export
- 12-case robustness suite
- field-level extraction scoring

See `VALIDATION_V0_3.md` for the current release verdict.


## V0.5
Generic parser hardening after External Set B. See `VALIDATION_V0_5.md`.


## V0.6
External-format hardening and independent Set D release-gate PASS. See `VALIDATION_V0_6.md`.
