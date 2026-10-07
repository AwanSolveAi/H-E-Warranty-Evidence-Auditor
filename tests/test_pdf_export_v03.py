
from pathlib import Path
import fitz
from src.auditor import audit_claim_folder
from src.pdf_report import export_audit_pdf

def test_pdf_export_is_readable(tmp_path):
    root=Path(__file__).resolve().parents[1]
    result=audit_claim_folder(root/"evaluation"/"robustness"/"RBT-009")
    out=tmp_path/"report.pdf"
    export_audit_pdf(result,out)
    assert out.exists() and out.stat().st_size>1000
    doc=fitz.open(out)
    text="\n".join(page.get_text("text") for page in doc)
    assert "Warranty Claim Evidence Audit Report" in text
    assert "INCONSISTENT" in text
    assert "Source / Page" in text
