
from pathlib import Path
from src.auditor import audit_claim_folder

ROOT=Path(__file__).resolve().parents[1]

def audit(case, profile="general_heavy_equipment"):
    return audit_claim_folder(ROOT/"evaluation"/"robustness"/case,profile=profile)

def test_good_control_ready():
    assert audit("RBT-001").overall_status=="READY"

def test_corrupt_pdf_routes_review():
    r=audit("RBT-002")
    assert r.overall_status=="REVIEW_REQUIRED"
    assert any(i["type"]=="CORRUPT_PDF" for i in r.claim.input_issues)

def test_scanned_pdf_routes_review():
    r=audit("RBT-003")
    assert r.overall_status=="REVIEW_REQUIRED"
    assert any(i["type"]=="UNREADABLE_OR_SCANNED_PDF" for i in r.claim.input_issues)

def test_document_injection_routes_review():
    r=audit("RBT-004")
    assert r.overall_status=="REVIEW_REQUIRED"
    assert any(x.rule_id=="R901" and x.status=="REVIEW_REQUIRED" for x in r.rules)

def test_system_prompt_spoof_routes_review():
    assert audit("RBT-005").overall_status=="REVIEW_REQUIRED"

def test_unitless_measurement_routes_review():
    r=audit("RBT-006")
    assert r.overall_status=="REVIEW_REQUIRED"
    assert any(x.rule_id=="R019" and x.status=="REVIEW_REQUIRED" for x in r.rules)

def test_no_supported_pdf_routes_review():
    assert audit("RBT-007").overall_status=="REVIEW_REQUIRED"

def test_duplicate_evidence_is_inconsistent():
    assert audit("RBT-008").overall_status=="INCONSISTENT"

def test_identity_conflict_is_inconsistent():
    assert audit("RBT-009").overall_status=="INCONSISTENT"

def test_generator_missing_load_test():
    r=audit("RBT-010","generator")
    assert r.overall_status=="MISSING_EVIDENCE"
    assert any(x.rule_id=="G004" and x.status=="MISSING_EVIDENCE" for x in r.rules)

def test_blank_attachment_routes_review():
    assert audit("RBT-011").overall_status=="REVIEW_REQUIRED"

def test_unreadable_attachment_not_silently_ignored():
    assert audit("RBT-012").overall_status=="REVIEW_REQUIRED"
