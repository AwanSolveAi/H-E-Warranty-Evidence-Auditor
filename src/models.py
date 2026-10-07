
from dataclasses import dataclass, field
from typing import Optional, List, Dict

@dataclass
class SourceValue:
    value: Optional[str]
    source_file: Optional[str] = None
    source_page: Optional[int] = None
    raw_text: Optional[str] = None

    @property
    def citation(self) -> str:
        if not self.source_file:
            return ""
        return f"{self.source_file} p.{self.source_page}" if self.source_page else self.source_file

@dataclass
class ClaimEvidence:
    claim_id: SourceValue = field(default_factory=lambda: SourceValue(None))
    equipment: SourceValue = field(default_factory=lambda: SourceValue(None))
    model: List[SourceValue] = field(default_factory=list)
    serial: List[SourceValue] = field(default_factory=list)
    operating_hours: List[SourceValue] = field(default_factory=list)
    complaint: SourceValue = field(default_factory=lambda: SourceValue(None))
    fault_code: SourceValue = field(default_factory=lambda: SourceValue(None))
    cause: SourceValue = field(default_factory=lambda: SourceValue(None))
    correction: SourceValue = field(default_factory=lambda: SourceValue(None))
    claimed_part: List[SourceValue] = field(default_factory=list)
    labor_hours: List[SourceValue] = field(default_factory=list)
    diagnostic_test: SourceValue = field(default_factory=lambda: SourceValue(None))
    diagnostic_reading: SourceValue = field(default_factory=lambda: SourceValue(None))
    verification: SourceValue = field(default_factory=lambda: SourceValue(None))
    verification_date: SourceValue = field(default_factory=lambda: SourceValue(None))
    repair_close_date: SourceValue = field(default_factory=lambda: SourceValue(None))

    # Generator profile fields
    battery_voltage: SourceValue = field(default_factory=lambda: SourceValue(None))
    output_voltage: SourceValue = field(default_factory=lambda: SourceValue(None))
    frequency: SourceValue = field(default_factory=lambda: SourceValue(None))
    load_test: SourceValue = field(default_factory=lambda: SourceValue(None))

    files: List[str] = field(default_factory=list)
    input_issues: List[Dict[str, str]] = field(default_factory=list)

@dataclass
class RuleResult:
    rule_id: str
    name: str
    status: str
    severity: str
    reason: str
    evidence: Dict[str, str] = field(default_factory=dict)
    citations: List[str] = field(default_factory=list)

@dataclass
class AuditResult:
    overall_status: str
    profile: str
    claim: ClaimEvidence
    rules: List[RuleResult]
