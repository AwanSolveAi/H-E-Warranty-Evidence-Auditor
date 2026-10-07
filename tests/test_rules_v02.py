
from pathlib import Path
from src.models import ClaimEvidence, SourceValue
from src.rules import evaluate, overall_status
from src.auditor import audit_claim_folder

def sv(v, f="x.pdf", p=1):
    return SourceValue(v, f, p)

def base_claim():
    c=ClaimEvidence()
    c.files=["claim.pdf","work.pdf","diag.pdf","parts.pdf"]
    c.model=[sv("M1")]
    c.serial=[sv("S1")]
    c.operating_hours=[sv("100")]
    c.complaint=sv("Machine loses power under rated load.")
    c.cause=sv("Fuel restriction caused by collapsed hose.")
    c.claimed_part=[sv("P1")]
    c.labor_hours=[sv("2.0")]
    c.diagnostic_test=sv("Fuel pressure test")
    c.diagnostic_reading=sv("210 kPa")
    c.verification=sv("Operational test PASS")
    c.repair_close_date=sv("2026-08-10")
    c.verification_date=sv("2026-08-10")
    return c

def status_map(c, profile="general_heavy_equipment"):
    return {r.rule_id:r.status for r in evaluate(c,profile)}

def test_rule_serial_missing():
    c=base_claim(); c.serial=[]
    assert status_map(c)["R001"]=="MISSING_EVIDENCE"

def test_rule_serial_conflict():
    c=base_claim(); c.serial=[sv("S1","a.pdf"),sv("S2","b.pdf")]
    assert status_map(c)["R001"]=="INCONSISTENT"

def test_rule_usage_missing():
    c=base_claim(); c.operating_hours=[sv("NOT RECORDED")]
    assert status_map(c)["R002"]=="MISSING_EVIDENCE"

def test_rule_usage_conflict():
    c=base_claim(); c.operating_hours=[sv("100","a.pdf"),sv("120","b.pdf")]
    assert status_map(c)["R007"]=="INCONSISTENT"

def test_rule_weak_cause():
    c=base_claim(); c.cause=sv("Possible sensor issue; cause not confirmed.")
    assert status_map(c)["R004"]=="WEAK_EVIDENCE"

def test_rule_missing_measurement():
    c=base_claim(); c.diagnostic_reading=sv("NOT RECORDED")
    assert status_map(c)["R005"]=="MISSING_EVIDENCE"

def test_rule_part_conflict():
    c=base_claim(); c.claimed_part=[sv("P1","a.pdf"),sv("P2","b.pdf")]
    assert status_map(c)["R006"]=="INCONSISTENT"

def test_rule_labor_conflict():
    c=base_claim(); c.labor_hours=[sv("2.0","a.pdf"),sv("3.0","b.pdf")]
    assert status_map(c)["R009"]=="INCONSISTENT"

def test_rule_missing_verification():
    c=base_claim(); c.verification=sv("NOT DOCUMENTED")
    assert status_map(c)["R013"]=="MISSING_EVIDENCE"

def test_rule_bad_chronology():
    c=base_claim(); c.verification_date=sv("2026-08-09"); c.repair_close_date=sv("2026-08-10")
    assert status_map(c)["R008"]=="INCONSISTENT"

def test_rule_boundary_routes_to_review():
    c=base_claim(); c.files=["quote.pdf"]
    rules=evaluate(c)
    assert overall_status(rules)=="REVIEW_REQUIRED"

def test_generator_profile_all_present():
    c=base_claim()
    c.battery_voltage=sv("25.2 V"); c.output_voltage=sv("400 V")
    c.frequency=sv("50.0 Hz"); c.load_test=sv("75% rated load - PASS")
    m=status_map(c,"generator")
    assert all(m[x]=="PASS" for x in ("G001","G002","G003","G004"))

def test_generator_missing_load_test():
    c=base_claim()
    c.battery_voltage=sv("25.2 V"); c.output_voltage=sv("400 V")
    c.frequency=sv("50.0 Hz"); c.load_test=sv("NOT DOCUMENTED")
    assert status_map(c,"generator")["G004"]=="MISSING_EVIDENCE"

def test_rule_citations_present_for_conflict():
    c=base_claim(); c.serial=[sv("S1","claim.pdf",1),sv("S2","diag.pdf",2)]
    r=next(x for x in evaluate(c) if x.rule_id=="R001")
    assert r.citations==["claim.pdf p.1","diag.pdf p.2"]

def test_multipage_integration_citation():
    root=Path(__file__).resolve().parents[1]
    r=audit_claim_folder(root/"evaluation"/"holdout"/"A-020")
    assert r.claim.diagnostic_reading.source_page==2
    assert r.claim.diagnostic_reading.citation=="diagnostic_record.pdf p.2"
