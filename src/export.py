
from pathlib import Path
import pandas as pd

def export_audit_xlsx(result, path):
    rows = []
    for r in result.rules:
        rows.append({
            "Rule ID": r.rule_id,
            "Check": r.name,
            "Status": r.status,
            "Severity": r.severity,
            "Reason": r.reason,
            "Evidence": "; ".join(f"{k}={v}" for k,v in r.evidence.items()),
            "Source / Page": "; ".join(r.citations)
        })
    df = pd.DataFrame(rows)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(path, index=False)
    return path
