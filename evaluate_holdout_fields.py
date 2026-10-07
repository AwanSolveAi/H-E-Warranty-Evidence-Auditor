
from pathlib import Path
import json, csv, re
from src.auditor import audit_claim_folder

ROOT=Path(__file__).resolve().parent

def norm(v):
    if v is None: return None
    return re.sub(r"\s+"," ",str(v)).strip().lower()

truth=json.loads((ROOT/"evaluation"/"holdout_ground_truth.json").read_text(encoding="utf-8"))
rows=[]
for item in truth:
    # Unsupported/minimum-boundary cases are evaluated by rejection accuracy,
    # not by field extraction because the expected fields are intentionally absent.
    if item["defect"]=="unsupported":
        continue
    r=audit_claim_folder(ROOT/"evaluation"/"holdout"/item["claim_id"],profile=item["profile"])
    checks={
        "claim_id": (norm(item["claim_id"]), norm(r.claim.claim_id.value)),
        "model": (norm(item["model"]), {norm(x.value) for x in r.claim.model if x.value}),
        "serial": (norm(item["serial"]), {norm(x.value) for x in r.claim.serial if x.value}),
    }
    # Hours are intentionally absent in hours_missing cases.
    actual_hours={norm(x.value) for x in r.claim.operating_hours if x.value and norm(x.value) not in {"not recorded","n/a"}}
    if item["defect"]=="hours_missing":
        hour_ok=(len(actual_hours)==0)
        rows.append({"claim_id":item["claim_id"],"field":"hours_absence","pass":hour_ok})
    else:
        rows.append({"claim_id":item["claim_id"],"field":"hours","pass":norm(item["hours"]) in actual_hours})

    rows.append({"claim_id":item["claim_id"],"field":"claim_id","pass":checks["claim_id"][0]==checks["claim_id"][1]})
    rows.append({"claim_id":item["claim_id"],"field":"model","pass":checks["model"][0] in checks["model"][1]})
    rows.append({"claim_id":item["claim_id"],"field":"serial","pass":checks["serial"][0] in checks["serial"][1]})

out=ROOT/"evaluation"/"field_metrics"/"holdout_identity_fields.csv"
with out.open("w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=["claim_id","field","pass"])
    w.writeheader(); w.writerows(rows)
passed=sum(r["pass"] for r in rows)
print(f"Holdout identity-field coverage: {passed}/{len(rows)} = {passed/len(rows):.2%}")
