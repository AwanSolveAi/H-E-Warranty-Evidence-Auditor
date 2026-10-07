from pathlib import Path
import sys
import tempfile
import shutil

# Ensure the repository root is importable both locally and on Streamlit Community Cloud.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from src.auditor import audit_claim_folder
from src.export import export_audit_xlsx
from src.pdf_report import export_audit_pdf


st.set_page_config(
    page_title="AwanSolveAi Warranty Evidence Auditor",
    layout="wide",
)

st.title("AwanSolveAi Heavy-Equipment Warranty Claim Evidence Auditor")

st.caption(
    "Documentation pre-audit only. V0.6 supports PDF claim packages, "
    "page-level evidence traces, robustness checks, General Heavy Equipment, "
    "and Generator profiles."
)

profile_label = st.selectbox(
    "Audit profile",
    ["General Heavy Equipment", "Generator"],
)

profile = (
    "generator"
    if profile_label == "Generator"
    else "general_heavy_equipment"
)

uploads = st.file_uploader(
    "Upload warranty claim package",
    type=["pdf"],
    accept_multiple_files=True,
)

if st.button("Analyze Claim", type="primary"):
    if not uploads:
        st.error("Upload at least one PDF.")
    else:
        tmp = Path(tempfile.mkdtemp())

        try:
            for uploaded_file in uploads:
                safe_name = Path(uploaded_file.name).name
                (tmp / safe_name).write_bytes(uploaded_file.getvalue())

            result = audit_claim_folder(
                tmp,
                profile=profile,
            )

            st.subheader(
                f"Claim readiness: {result.overall_status}"
            )

            cols = st.columns(4)

            cols[0].metric(
                "Documents",
                len(result.claim.files),
            )

            cols[1].metric(
                "Checks",
                len(result.rules),
            )

            cols[2].metric(
                "Passed",
                sum(
                    rule.status == "PASS"
                    for rule in result.rules
                ),
            )

            cols[3].metric(
                "Issues",
                sum(
                    rule.status != "PASS"
                    for rule in result.rules
                ),
            )

            rows = [
                {
                    "Rule": rule.rule_id,
                    "Check": rule.name,
                    "Status": rule.status,
                    "Severity": rule.severity,
                    "Reason": rule.reason,
                    "Evidence": "; ".join(
                        f"{key}={value}"
                        for key, value in rule.evidence.items()
                    ),
                    "Source / Page": "; ".join(
                        rule.citations
                    ),
                }
                for rule in result.rules
            ]

            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True,
            )

            excel_output = tmp / "audit_report.xlsx"

            export_audit_xlsx(
                result,
                excel_output,
            )

            st.download_button(
                "Download Excel Audit",
                data=excel_output.read_bytes(),
                file_name="warranty_claim_audit.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
            )

            pdf_output = tmp / "audit_report.pdf"

            export_audit_pdf(
                result,
                pdf_output,
            )

            st.download_button(
                "Download PDF Audit",
                data=pdf_output.read_bytes(),
                file_name="warranty_claim_audit.pdf",
                mime="application/pdf",
            )

        except Exception as exc:
            st.error(
                "The uploaded claim package could not be audited."
            )
            st.exception(exc)

        finally:
            shutil.rmtree(
                tmp,
                ignore_errors=True,
            )

st.info(
    "This system evaluates documentation completeness and internal consistency. "
    "It does not approve warranty coverage, determine OEM liability, authorize "
    "repairs, or replace manufacturer warranty policy or warranty-administrator review."
)
