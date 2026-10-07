
from pathlib import Path
import json, csv
from src.auditor import audit_claim_folder

ROOT = Path(__file__).resolve().parent

def evaluate_set(name):
    gt_path = ROOT/"evaluation"/f"{name}_ground_truth.json"
    claims_root = ROOT/"evaluation"/name
    truth = json.loads(gt_path.read_text(encoding="utf-8"))
    rows=[]
    for item in truth:
        result = audit_claim_folder(claims_root/item["claim_id"], profile=item["profile"])
        rows.append({
            "claim_id":item["claim_id"],
            "profile":item["profile"],
            "expected":item["expected_status"],
            "actual":result.overall_status,
            "pass":item["expected_status"]==result.overall_status
        })
    passed=sum(r["pass"] for r in rows)
    print(f"{name.upper()}: {passed}/{len(rows)} = {passed/len(rows):.1%}")
    for r in rows:
        if not r["pass"]:
            print(f"FAIL {r['claim_id']} profile={r['profile']} expected={r['expected']} actual={r['actual']}")
    out=ROOT/"evaluation"/"results"/f"{name}_results.csv"
    with out.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    return rows

if __name__=="__main__":
    h=evaluate_set("holdout")
    a=evaluate_set("adversarial")
    total=h+a
    passed=sum(r["pass"] for r in total)
    print(f"COMBINED: {passed}/{len(total)} = {passed/len(total):.1%}")
