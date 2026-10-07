
from pathlib import Path
import json
from src.auditor import audit_claim_folder

root = Path(__file__).resolve().parent
claims = root/"demo_corpus"/"claims"
truth = json.loads((root/"demo_corpus"/"corpus_ground_truth.json").read_text(encoding="utf-8"))

ok=0
rows=[]
for item in truth:
    cid=item["claim_id"]
    exp=item["expected_status"]
    got=audit_claim_folder(claims/cid).overall_status
    rows.append((cid,exp,got,exp==got))
    ok += exp==got

for r in rows:
    print(f"{r[0]} expected={r[1]:<18} got={r[2]:<18} {'PASS' if r[3] else 'FAIL'}")
print(f"\nExact overall-status accuracy: {ok}/{len(rows)} = {ok/len(rows):.1%}")
