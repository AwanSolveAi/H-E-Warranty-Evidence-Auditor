
from pathlib import Path
import argparse
from src.auditor import audit_claim_folder
from src.export import export_audit_xlsx

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("claim_folder")
    ap.add_argument("--profile", default="general_heavy_equipment",
                    choices=["general_heavy_equipment","generator"])
    ap.add_argument("--xlsx")
    args = ap.parse_args()

    result = audit_claim_folder(Path(args.claim_folder), profile=args.profile)
    print(f"Profile: {result.profile}")
    print(f"Overall status: {result.overall_status}")
    for r in result.rules:
        cites = f" [{'; '.join(r.citations)}]" if r.citations else ""
        print(f"{r.rule_id:>4}  {r.status:<18} {r.name}: {r.reason}{cites}")

    if args.xlsx:
        export_audit_xlsx(result, args.xlsx)
        print(f"Exported: {args.xlsx}")

if __name__ == "__main__":
    main()
