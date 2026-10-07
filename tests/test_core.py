
from pathlib import Path
from src.auditor import audit_claim_folder

BASE = Path(__file__).resolve().parents[1] / "demo_corpus" / "claims"

def test_ready_claim():
    r = audit_claim_folder(BASE / "DEMO-001")
    assert r.overall_status == "READY"

def test_missing_evidence_claim():
    r = audit_claim_folder(BASE / "DEMO-002")
    assert r.overall_status == "MISSING_EVIDENCE"

def test_serial_conflict():
    r = audit_claim_folder(BASE / "DEMO-003")
    assert r.overall_status == "INCONSISTENT"

def test_weak_cause():
    r = audit_claim_folder(BASE / "DEMO-004")
    assert r.overall_status == "WEAK_EVIDENCE"

def test_part_conflict():
    r = audit_claim_folder(BASE / "DEMO-005")
    assert r.overall_status == "INCONSISTENT"

def test_unsupported_package():
    r = audit_claim_folder(BASE / "DEMO-030")
    assert r.overall_status == "REVIEW_REQUIRED"
