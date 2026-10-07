
from pathlib import Path
from .pdf_ingest import load_claim_folder
from .extraction import extract_claim
from .rules import evaluate, overall_status
from .models import AuditResult
from .profiles import validate_profile

def audit_claim_folder(folder, profile="general_heavy_equipment"):
    validate_profile(profile)
    folder = Path(folder)
    documents, issues = load_claim_folder(folder)
    claim = extract_claim(documents)
    claim.files = sorted([p.name for p in folder.glob("*.pdf")])
    claim.input_issues = issues
    rules = evaluate(claim, profile=profile)
    return AuditResult(overall_status=overall_status(rules), profile=profile, claim=claim, rules=rules)
