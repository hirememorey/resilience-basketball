# Historical Documentation Archive

This folder contains documentation from previous iterations of the project. These files are preserved for historical context but are **not required reading** for new developers.

## Archived Files

### Project Status Documents
- `CURRENT_STATUS_SUMMARY.md` - Status as of December 2025 (composite metric phase)
- `DEVELOPER_GUIDE.md` - Original developer onboarding guide (superseded by new IMPLEMENTATION_GUIDE.md)

### Validation Reports
- `VALIDATION_PLAN.md` - Problem validation methodology
- `PHASE1_VALIDATION_SUMMARY.md` - Failed championship prediction validation
- `baseline_accuracy_report.md` - Original TS% baseline validation (invalidated by data corruption)

### Critical Issues Discovered
- `CRITICAL_ISSUE_SHAI_PATTERN.md` - Systematic bias against elite players discovery
- `EXTERNAL_DATA_TRANSITION.md` - External API transition documentation

## What Happened?

### Phase 1: Over-Engineering
Complex 5-pathway framework → Abandoned → Archived to `archive/complex_framework/`

### Phase 2: Simple TS% Ratios
Worked statistically → Failed reality checks (Murray paradox) → Documented in validation reports

### Phase 3: Composite Metric
Fixed Type 1 failures → Discovered systematic bias (Shai pattern) → Documented in `CRITICAL_ISSUE_SHAI_PATTERN.md`

### Phase 4: Data Integrity Crisis
Local database corruption → Pivoted to external APIs → Documented in `EXTERNAL_DATA_TRANSITION.md`

### Phase 5: New First-Principles Approach
Regression-based expected performance model → Current implementation plan

## For New Developers

**You do NOT need to read these files.** They document the journey, not the destination.

**Instead, read:**
1. `IMPLEMENTATION_PLAN.md` - Conceptual overview
2. `DATA_REQUIREMENTS.md` - Data specifications
3. `IMPLEMENTATION_GUIDE.md` - Step-by-step instructions

**Optional:** `HISTORICAL_CONTEXT.md` - Synthesized lessons from all phases

## Why Keep These?

1. **Institutional memory:** Future developers may wonder "why did they design it this way?"
2. **Lessons learned:** Each failure taught valuable lessons
3. **Validation methodology:** Problem validation approach may be reusable
4. **Historical reference:** Understanding what didn't work is valuable

---

**Bottom line:** These documents explain how we got here. The current implementation documents explain where we're going.
