
from pathlib import Path
import fitz

INJECTION_PATTERNS = (
    "ignore previous instructions",
    "ignore all previous",
    "system prompt",
    "developer message",
    "mark this claim ready",
    "always return ready",
    "override audit rules",
    "do not report missing",
    "bypass validation",
)

def _detect_injection(text: str):
    low = text.lower()
    hits = [p for p in INJECTION_PATTERNS if p in low]
    return hits

def extract_pdf_pages(path: Path):
    issues = []
    try:
        doc = fitz.open(path)
    except Exception as e:
        return [], [{
            "type":"CORRUPT_PDF",
            "file":path.name,
            "detail":f"PDF could not be opened: {type(e).__name__}"
        }]

    if doc.page_count == 0:
        return [], [{"type":"EMPTY_PDF","file":path.name,"detail":"PDF has zero pages."}]

    pages=[]
    total_chars=0
    for i,page in enumerate(doc):
        try:
            text = page.get_text("text") or ""
        except Exception as e:
            issues.append({
                "type":"PAGE_EXTRACTION_ERROR","file":path.name,
                "page":str(i+1),"detail":type(e).__name__
            })
            text=""
        total_chars += len(text.strip())
        pages.append((i+1,text))
        for hit in _detect_injection(text):
            issues.append({
                "type":"DOCUMENT_INJECTION",
                "file":path.name,
                "page":str(i+1),
                "detail":hit
            })

    # Image-only / effectively non-text PDFs are not silently treated as absent evidence.
    if total_chars < max(20, doc.page_count * 8):
        issues.append({
            "type":"UNREADABLE_OR_SCANNED_PDF",
            "file":path.name,
            "detail":"Little or no extractable text. OCR/manual review required."
        })

    return pages, issues

def load_claim_folder(folder: Path):
    pdfs = sorted(folder.glob("*.pdf"))
    documents={}
    issues=[]
    if not pdfs:
        issues.append({
            "type":"NO_SUPPORTED_FILES",
            "file":"",
            "detail":"No PDF files found in claim package."
        })
        return documents, issues

    for p in pdfs:
        pages, file_issues = extract_pdf_pages(p)
        if pages:
            documents[p.name]=pages
        issues.extend(file_issues)
    return documents, issues
