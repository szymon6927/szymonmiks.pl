from dataclasses import dataclass


@dataclass(frozen=True)
class AnalysisParameters:
    has_cf_correction: bool
    has_batch_correction: bool
