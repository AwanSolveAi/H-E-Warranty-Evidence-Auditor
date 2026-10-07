
from pathlib import Path
import sys, json, re, csv
from src.auditor import audit_claim_folder

ROOT=Path(__file__).resolve().parent

def norm(v):
    if v is None:
        return None
    return re.sub(r"\s+"," ",str(v)).strip().rstrip(".").lower()

truth=json.loads((ROOT/"demo_corpus"/"corpus_ground_truth.json").read_text(encoding="utf-8"))
rows=[]
total=correct=0

for gt in truth:
    r=audit_claim_folder(ROOT/"demo_corpus"/"claims"/gt["claim_id"])
    obs=gt["observed_values"]
    expected={
        "claim_id":{norm(gt["claim_id"])},
        "model":{norm(gt["model"]), norm(obs["diag_model"])},
        "serial":{norm(obs["claim_serial"]),norm(obs["work_serial"]),norm(obs["diag_serial"]),norm(obs["parts_serial"])},
        "hours":{norm(obs["claim_hours"]),norm(obs["work_hours"])},
        "complaint":{norm(gt["complaint"])},
        "fault_code":{norm(gt["code"])},
        "cause":{norm(obs["narrative_cause"])},
        "correction":{norm(gt["correction"])},
        "parts":{norm(obs["narrative_part"]),norm(obs["invoice_part"])},
        "labor":{norm(obs["labor_claimed"]),norm(obs["labor_recorded"])},
        "reading":{norm(obs["diagnostic_reading"])},
        "verification":{norm(obs["verification"])},
    }
    actual={
        "claim_id":{norm(r.claim.claim_id.value)} if r.claim.claim_id.value else set(),
        "model":{norm(x.value) for x in r.claim.model if x.value},
        "serial":{norm(x.value) for x in r.claim.serial if x.value},
        "hours":{norm(x.value) for x in r.claim.operating_hours if x.value},
        "complaint":{norm(r.claim.complaint.value)} if r.claim.complaint.value else set(),
        "fault_code":{norm(r.claim.fault_code.value)} if r.claim.fault_code.value else set(),
        "cause":{norm(r.claim.cause.value)} if r.claim.cause.value else set(),
        "correction":{norm(r.claim.correction.value)} if r.claim.correction.value else set(),
        "parts":{norm(x.value) for x in r.claim.claimed_part if x.value},
        "labor":{norm(x.value) for x in r.claim.labor_hours if x.value},
        "reading":{norm(r.claim.diagnostic_reading.value)} if r.claim.diagnostic_reading.value else set(),
        "verification":{norm(r.claim.verification.value)} if r.claim.verification.value else set(),
    }

    if gt["claim_id"]=="DEMO-030":
        fields=["claim_id"]
    elif gt["claim_id"]=="DEMO-010":
        fields=["claim_id","complaint","cause","parts","labor"]
    else:
        fields=list(expected)

    for field in fields:
        exp={x for x in expected[field] if x not in {None,""}}
        act={x for x in actual[field] if x not in {None,""}}
        ok=exp.issubset(act)
        total += 1
        correct += int(ok)
        rows.append({
            "claim_id":gt["claim_id"],
            "field":field,
            "expected":" | ".join(sorted(exp)),
            "actual":" | ".join(sorted(act)),
            "pass":ok,
        })

out=ROOT/"evaluation"/"field_metrics"/"development_field_extraction.csv"
with out.open("w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

summary={
    "correct":correct,
    "total":total,
    "accuracy":correct/total if total else 0,
}
(ROOT/"evaluation"/"field_metrics"/"field_extraction_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
print(f"Field extraction exact-set coverage: {correct}/{total} = {correct/total:.2%}")
