
from pathlib import Path
import json, csv
from src.auditor import audit_claim_folder

ROOT=Path(__file__).resolve().parent
truth=json.loads((ROOT/"evaluation"/"robustness_ground_truth.json").read_text(encoding="utf-8"))
rows=[]
for item in truth:
    r=audit_claim_folder(ROOT/"evaluation"/"robustness"/item["case"],profile=item["profile"])
    rows.append({
        "case":item["case"],
        "purpose":item["purpose"],
        "expected":item["expected"],
        "actual":r.overall_status,
        "pass":item["expected"]==r.overall_status
    })

out=ROOT/"evaluation"/"results"/"robustness_results.csv"
with out.open("w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys())
    w.writeheader(); w.writerows(rows)

passed=sum(r["pass"] for r in rows)
for r in rows:
    print(f"{r['case']} expected={r['expected']:<18} actual={r['actual']:<18} {'PASS' if r['pass'] else 'FAIL'}")
print(f"ROBUSTNESS: {passed}/{len(rows)} = {passed/len(rows):.1%}")
