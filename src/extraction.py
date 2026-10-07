
import re
from .models import ClaimEvidence, SourceValue

def _clean(v):
    if v is None:
        return None
    return re.sub(r"\s+", " ", v).strip(" \n\t:-")

def _find(text, patterns):
    for pat in patterns:
        m = re.search(pat, text, flags=re.I | re.M)
        if m:
            return _clean(m.group(1))
    return None

def _sv(value, source, page, raw=None):
    return SourceValue(value=value, source_file=source, source_page=page, raw_text=raw)

def _append_unique(lst, value, source, page):
    if not value:
        return
    norm = value.strip()
    if not any((x.value or "").strip() == norm and x.source_file == source and x.source_page == page for x in lst):
        lst.append(_sv(norm, source, page))

def _first_into(current, value, source, page):
    return current if current.value or not value else _sv(value, source, page)

def extract_claim(documents):
    claim = ClaimEvidence(files=sorted(documents.keys()))

    for fname, pages in documents.items():
        for page_no, text in pages:
            # IDs and asset identity. Patterns intentionally accept several common labels.
            v = _find(text, [
                r"(?:Claim ID|Claim No\.?|Claim Number|Reference)\s*[:#]?\s*([A-Z0-9\-]+)"
            ])
            claim.claim_id = _first_into(claim.claim_id, v, fname, page_no)

            v = _find(text, [
                r"(?:Equipment Type|Asset Type|Machine Type|Equipment)\s*[:#]?\s*([A-Za-z][A-Za-z /-]+?)(?:\n|Model|Asset Model|Serial|Claim|$)"
            ])
            claim.equipment = _first_into(claim.equipment, v, fname, page_no)

            v = _find(text, [
                r"^(?:Asset Model|Machine Model|Equipment Model|Compressor Model|Model Number|Make & Model|Model)\s*[:#]?\s*\n?([A-Z0-9\-]+)"
            ])
            if v:
                _append_unique(claim.model, v, fname, page_no)

            v = _find(text, [
                r"^(?:Asset Serial Number|Equipment Serial Number|Compressor Serial No\.?|Machine Serial Number|Engine Serial Number|Serial Number|Serial No\.?|Asset Serial|Engine Serial|Machine Serial|Serial)\s*[:#]?\s*\n?([A-Z0-9\-]+)"
            ])
            if v:
                _append_unique(claim.serial, v, fname, page_no)

            v = _find(text, [
                r"(?:Operating Hours|Machine Hours|Engine Hours|Meter Hours|Hour Meter)\s*[:#]?\s*([0-9,.]+|NOT RECORDED|N/?A)"
            ])
            if v:
                _append_unique(claim.operating_hours, v.replace(",", ""), fname, page_no)

            # Narrative fields
            v = _find(text, [
                r"^(?:Customer Complaint|Customer Concern|Reported Complaint|Complaint|Reported Symptom|Description of the failure, condition found|Detailed information of the problem found|Problem Reported|Warranty Concern|Problem Description)\s*[:#]?\s*\n?(.+?)(?=\n(?:Diagnostic|Failure|Fault|Code|Root Cause|Cause|Correction|Corrective Action|Diagnosis|Technician|$))"
            ])
            claim.complaint = _first_into(claim.complaint, v, fname, page_no)

            v = _find(text, [
                r"(?:Failure / Fault Code|Failure Code|Fault Code|Diagnostic Code|DTC)\s*[:#]?\s*([A-Z0-9\-]+)"
            ])
            claim.fault_code = _first_into(claim.fault_code, v, fname, page_no)

            v = _find(text, [
                r"^(?:Claimed Cause|Root Cause|Confirmed Cause|Cause|Mechanic Findings|Technician Diagnosis|Failure Analysis)\s*[:#]?\s*\n?(.+?)(?=\n(?:Correction|Corrective Action|Repair Action|Repair|Repair Performed|Repair Description|Repair Information|Parts Replaced or Repaired|Claimed Part|Installed Part|Final|$))"
            ])
            claim.cause = _first_into(claim.cause, v, fname, page_no)

            v = _find(text, [
                r"^(?:Correction|Corrective Action|Repair Action|Repair Performed|Repairs Completed|Repair Completed|Warranty Service Completed|Solution|Repair)\s*[:#]?\s*\n?(.+?)(?=\n(?:Claimed Part|Installed Part|Part Number|Technician|Final|$))"
            ])
            claim.correction = _first_into(claim.correction, v, fname, page_no)

            for pat in [
                r"^(?:Claimed Part|Installed Part|Part Number|Replacement Part Number|Replacement Part|Blue Giant Part #|ID Number 1|Parts Used for Repair)\s*[:#]?\s*\n?([A-Z0-9\-]+)",
                r"Installed part\s+([A-Z0-9\-]+)"
            ]:
                v = _find(text, [pat])
                if v:
                    _append_unique(claim.claimed_part, v, fname, page_no)

            for pat in [
                r"^(?:Claimed Labor|Labor Claimed|Warranty Labor|Total Labor Hours|Technician Labor Hours|Labor Hrs Claimed|Repair Labor Time|Labor Hours)\s*[:#]?\s*\n?([0-9.]+)\s*(?:h|hr|hrs|hours)?",
                r"^(?:Recorded technician labor|Time Card Total|Labor Recorded)\s*[:#]?\s*\n?([0-9.]+)\s*(?:h|hr|hrs|hours)?"
            ]:
                v = _find(text, [pat])
                if v:
                    _append_unique(claim.labor_hours, v, fname, page_no)

            # Test and verification fields
            v = _find(text, [
                r"^(?:Diagnostic Test|Test Performed|Diagnostic Procedure)\s*[:#]?\s*\n?([^\n]+)",
                r"^Diagnosis\s*[:#]?\s*(?:Performed\s+)?([^\n]+)"
            ])
            claim.diagnostic_test = _first_into(claim.diagnostic_test, v, fname, page_no)

            v = _find(text, [
                r"^(?:Measured Result|Diagnostic Measurement|Test Reading|Measured Value|Reading)\s*[:#]?\s*\n?(.+?)(?=\n(?:Fault|Code|Post-Repair|Final Test|Operational Verification|$))"
            ])
            claim.diagnostic_reading = _first_into(claim.diagnostic_reading, v, fname, page_no)

            v = _find(text, [
                r"^(?:Post-Repair Verification|Final Test Result|Final Verification|Operational Verification)\s*[:#]?\s*\n?([^\n]+)"
            ])
            claim.verification = _first_into(claim.verification, v, fname, page_no)

            v = _find(text, [
                r"(?:Verification Date|Final Test Date)\s*[:#]?\s*([0-9]{4}-[0-9]{2}-[0-9]{2})"
            ])
            claim.verification_date = _first_into(claim.verification_date, v, fname, page_no)

            v = _find(text, [
                r"(?:Closed|Repair Closed|Repair Completion Date|Repair Completed)\s*[:#]?\s*([0-9]{4}-[0-9]{2}-[0-9]{2})"
            ])
            claim.repair_close_date = _first_into(claim.repair_close_date, v, fname, page_no)

            # Generator profile
            v = _find(text, [r"(?:Battery Voltage|Cranking Battery Voltage)\s*[:#]?\s*([0-9.]+\s*V)"])
            claim.battery_voltage = _first_into(claim.battery_voltage, v, fname, page_no)

            v = _find(text, [r"(?:Generator Output Voltage|Output Voltage|AC Voltage)\s*[:#]?\s*([0-9.]+\s*V)"])
            claim.output_voltage = _first_into(claim.output_voltage, v, fname, page_no)

            v = _find(text, [r"(?:Frequency|Output Frequency)\s*[:#]?\s*([0-9.]+\s*Hz)"])
            claim.frequency = _first_into(claim.frequency, v, fname, page_no)

            v = _find(text, [
                r"(?:Load Test|Load Bank Test)\s*[:#]?\s*(.+?)(?=\n|$)"
            ])
            claim.load_test = _first_into(claim.load_test, v, fname, page_no)

    return claim
