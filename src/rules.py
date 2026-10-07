
from datetime import datetime
from .models import RuleResult

def _vals(items):
    return [x.value for x in items if x.value]

def _unique(items):
    return sorted(set(_vals(items)))

def _citations(items):
    seen = []
    for x in items:
        c = x.citation
        if c and c not in seen:
            seen.append(c)
    return seen

def _one_citation(value):
    return [value.citation] if value and value.citation else []

def evaluate(claim, profile="general_heavy_equipment"):
    rr = []

    def add(rule_id, name, status, severity, reason, evidence=None, citations=None):
        rr.append(RuleResult(rule_id, name, status, severity, reason, evidence or {}, citations or []))


    # Input-integrity / document-safety gates
    issue_types = [i.get("type","") for i in claim.input_issues]
    if issue_types:
        serious = [i for i in claim.input_issues if i.get("type") in {
            "CORRUPT_PDF","EMPTY_PDF","UNREADABLE_OR_SCANNED_PDF",
            "PAGE_EXTRACTION_ERROR","NO_SUPPORTED_FILES"
        }]
        injections = [i for i in claim.input_issues if i.get("type")=="DOCUMENT_INJECTION"]

        if serious:
            add("R900","Input readability / integrity","REVIEW_REQUIRED","critical",
                "One or more uploaded files could not be safely interpreted.",
                {"issues": "; ".join(f"{i.get('type')}:{i.get('file')}" for i in serious)})
        else:
            add("R900","Input readability / integrity","PASS","critical",
                "No corrupt or unreadable input condition detected.")

        if injections:
            add("R901","Document-injection resistance","REVIEW_REQUIRED","critical",
                "Suspicious instruction-like text was found inside uploaded evidence. It was ignored for audit decisions.",
                {"hits": "; ".join(f"{i.get('file')} p.{i.get('page','?')}: {i.get('detail')}" for i in injections)})
        else:
            add("R901","Document-injection resistance","PASS","critical",
                "No suspicious instruction-like text detected.")
    else:
        add("R900","Input readability / integrity","PASS","critical",
            "No corrupt or unreadable input condition detected.")
        add("R901","Document-injection resistance","PASS","critical",
            "No suspicious instruction-like text detected.")

    # Package boundary
    if len(claim.files) <= 2:
        add("R020","Minimum claim-package boundary","REVIEW_REQUIRED","critical",
            "Too few supporting documents were supplied for a normal claim package.",
            {"file_count": str(len(claim.files))})
    else:
        add("R020","Minimum claim-package boundary","PASS","critical","Sufficient package structure detected.")

    serials = _unique(claim.serial)
    if not serials:
        add("R001","Asset serial number","MISSING_EVIDENCE","critical","No asset serial number located.")
    elif len(serials) > 1:
        add("R001","Asset serial number","INCONSISTENT","critical","Conflicting serial numbers found.",
            {"values": ", ".join(serials)}, _citations(claim.serial))
    else:
        add("R001","Asset serial number","PASS","critical","Serial number located.",
            {"value": serials[0]}, _citations(claim.serial))

    models = _unique(claim.model)
    if len(models) > 1:
        add("R011","Model consistency","INCONSISTENT","critical","Conflicting equipment models found.",
            {"values": ", ".join(models)}, _citations(claim.model))
    elif models:
        add("R011","Model consistency","PASS","critical","No model conflict detected.",
            {"value": models[0]}, _citations(claim.model))
    else:
        add("R011","Model consistency","REVIEW_REQUIRED","major","Equipment model was not located.")

    hours = _unique(claim.operating_hours)
    real_hours = [h for h in hours if h.upper() not in {"NOT RECORDED","N/A","NA"}]
    if not hours or not real_hours:
        add("R002","Usage evidence","MISSING_EVIDENCE","critical","Operating hours/mileage evidence missing.",
            citations=_citations(claim.operating_hours))
    elif len(real_hours) > 1:
        add("R007","Usage consistency","INCONSISTENT","critical","Conflicting operating-hour values found.",
            {"values": ", ".join(real_hours)}, _citations(claim.operating_hours))
    else:
        add("R002","Usage evidence","PASS","critical","Usage evidence located.",
            {"value": real_hours[0]}, _citations(claim.operating_hours))

    comp = (claim.complaint.value or "").strip()
    if not comp:
        add("R003","Complaint quality","MISSING_EVIDENCE","major","Customer complaint not found.")
    elif len(comp.split()) < 4 or comp.lower().rstrip(".") in {"machine faulty","unit faulty","fixed unit"}:
        add("R003","Complaint quality","WEAK_EVIDENCE","major","Complaint is too vague.",
            {"value": claim.complaint.value or ""}, _one_citation(claim.complaint))
    else:
        add("R003","Complaint quality","PASS","major","Specific complaint located.",
            {"value": claim.complaint.value or ""}, _one_citation(claim.complaint))

    cause = (claim.cause.value or "").strip().lower()
    if not cause:
        add("R004","Cause evidence","MISSING_EVIDENCE","critical","Cause not documented.")
    elif cause.rstrip(".") in {"hydraulic fault","fixed unit","cause not documented","unknown"} or "not confirmed" in cause or "possible " in cause:
        add("R004","Cause evidence","WEAK_EVIDENCE","critical","Cause statement is vague or unconfirmed.",
            {"value": claim.cause.value or ""}, _one_citation(claim.cause))
    else:
        add("R004","Cause evidence","PASS","critical","Cause evidence located.",
            {"value": claim.cause.value or ""}, _one_citation(claim.cause))

    dr = (claim.diagnostic_reading.value or "").strip()
    if dr.upper().startswith("NOT RECORDED") or (claim.diagnostic_test.value and not dr):
        add("R005","Diagnostic reading evidence","MISSING_EVIDENCE","critical",
            "A diagnostic test is referenced but the measured result is missing.",
            citations=_one_citation(claim.diagnostic_test) + _one_citation(claim.diagnostic_reading))
    elif dr:
        add("R005","Diagnostic reading evidence","PASS","critical","Diagnostic measurement located.",
            {"value": dr}, _one_citation(claim.diagnostic_reading))


    # Critical numeric/unit consistency for diagnostic measurements.
    if dr and not dr.upper().startswith("NOT RECORDED"):
        numeric = bool(__import__("re").search(r"[-+]?\d+(?:\.\d+)?", dr))
        unit = bool(__import__("re").search(
            r"\b(?:V|mV|A|mA|Hz|kPa|MPa|Pa|bar|psi|rpm|ohm|Ω|°C|C|°F|F|mm|cm|m|in|%)\b",
            dr, flags=__import__("re").I
        ))
        if numeric and not unit:
            add("R019","Critical measurement units","REVIEW_REQUIRED","critical",
                "A numeric diagnostic reading was found without a recognized unit.",
                {"value": dr}, _one_citation(claim.diagnostic_reading))
        elif numeric and unit:
            add("R019","Critical measurement units","PASS","critical",
                "Diagnostic numeric reading includes a recognized unit.",
                {"value": dr}, _one_citation(claim.diagnostic_reading))

    parts = _unique(claim.claimed_part)
    if len(parts) > 1:
        add("R006","Part consistency","INCONSISTENT","critical","Conflicting part numbers found.",
            {"values": ", ".join(parts)}, _citations(claim.claimed_part))
    elif parts:
        add("R006","Part consistency","PASS","critical","Part evidence is internally consistent.",
            {"value": parts[0]}, _citations(claim.claimed_part))

    labs = _unique(claim.labor_hours)
    if len(labs) > 1:
        add("R009","Labor reconciliation","INCONSISTENT","critical",
            "Claimed and recorded labor hours do not agree.",
            {"values": ", ".join(labs)}, _citations(claim.labor_hours))
    elif labs:
        add("R009","Labor reconciliation","PASS","critical","Labor hours reconcile.",
            {"value": labs[0]}, _citations(claim.labor_hours))

    ver = (claim.verification.value or "").strip()
    if not ver or ver.upper().startswith(("NOT DOCUMENTED","MISSING","NONE")):
        add("R013","Post-repair verification","MISSING_EVIDENCE","critical",
            "Post-repair verification evidence missing.",
            citations=_one_citation(claim.verification))
    else:
        add("R013","Post-repair verification","PASS","critical","Post-repair verification located.",
            {"value": ver}, _one_citation(claim.verification))

    if claim.diagnostic_test.value and not dr:
        add("R016","Diagnostic narrative support","WEAK_EVIDENCE","critical",
            "Diagnostic action is described without supporting measured evidence.",
            citations=_one_citation(claim.diagnostic_test))

    dupes = [f for f in claim.files if "DUPLICATE" in f.upper() or "COPY" in f.upper()]
    if dupes:
        add("R017","Duplicate invoice detection","INCONSISTENT","critical",
            "Potential duplicate supporting document detected.", {"files": ", ".join(dupes)})

    if claim.verification_date.value and claim.repair_close_date.value:
        try:
            vd = datetime.strptime(claim.verification_date.value, "%Y-%m-%d")
            cd = datetime.strptime(claim.repair_close_date.value, "%Y-%m-%d")
            cites = _one_citation(claim.verification_date) + _one_citation(claim.repair_close_date)
            if vd < cd:
                add("R008","Date chronology","INCONSISTENT","critical",
                    "Post-repair verification date precedes repair close date.",
                    {"verification_date": claim.verification_date.value,
                     "repair_close_date": claim.repair_close_date.value}, cites)
            else:
                add("R008","Date chronology","PASS","critical","Verification date is chronologically valid.",
                    citations=cites)
        except ValueError:
            add("R008","Date chronology","REVIEW_REQUIRED","major","Unable to parse one or more dates.")

    # Generator-specific evidence requirements.
    if profile == "generator":
        gen_fields = [
            ("G001","Battery voltage evidence","battery_voltage","Battery voltage evidence is missing."),
            ("G002","Output voltage evidence","output_voltage","Generator output voltage evidence is missing."),
            ("G003","Frequency evidence","frequency","Generator frequency evidence is missing."),
            ("G004","Load-test evidence","load_test","Generator load-test evidence is missing.")
        ]
        for rid, name, attr, missing_reason in gen_fields:
            sv = getattr(claim, attr)
            val = (sv.value or "").strip()
            if not val or val.upper().startswith(("NOT RECORDED","NOT DOCUMENTED","MISSING","NONE")):
                add(rid, name, "MISSING_EVIDENCE","critical", missing_reason, citations=_one_citation(sv))
            else:
                add(rid, name, "PASS","critical", f"{name} located.", {"value": val}, _one_citation(sv))

    return rr

def overall_status(rules):
    safety_review = [r for r in rules if r.rule_id in {"R900","R901"} and r.status=="REVIEW_REQUIRED"]
    if safety_review:
        return "REVIEW_REQUIRED"

    boundary = next((r for r in rules if r.rule_id == "R020"), None)
    if boundary and boundary.status == "REVIEW_REQUIRED":
        return "REVIEW_REQUIRED"

    statuses = [r.status for r in rules]
    if "INCONSISTENT" in statuses:
        return "INCONSISTENT"
    if "MISSING_EVIDENCE" in statuses:
        return "MISSING_EVIDENCE"
    if "WEAK_EVIDENCE" in statuses:
        return "WEAK_EVIDENCE"
    if "REVIEW_REQUIRED" in statuses:
        return "REVIEW_REQUIRED"
    return "READY"
