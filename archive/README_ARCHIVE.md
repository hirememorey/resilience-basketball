# Archive Directory - Lessons Learned

This directory contains previous approaches and experiments that were valuable learning experiences but are no longer the recommended path forward.

## 📁 Archived Files

### `data_integrity_remediation_plan.md`
**Status**: Superseded by external data approach
**Lesson**: We discovered that external NBA APIs provide clean, validated data superior to fixing corrupted local data. Attempting to remediate 4+ weeks of corrupted data processing was over-engineering when simple external APIs worked perfectly.

**Key Insight**: Sometimes the "fix" is more complex than using a better source. External validated data beats complex remediation of corrupted data.

**Date Archived**: November 2025
**Replaced By**: `calculate_resilience_external.py` and external API approach

### `complex_framework/`
**Status**: Superseded by simple TS% approach
**Lesson**: Complex 5-pathway resilience framework (Friction, Crucible, Evolution, Dominance, Versatility) added zero predictive value beyond simple TS% ratios.

**Key Insight**: NBA teams have been evaluating playoff resilience correctly for decades using basic stats. Our complex framework was rediscovering simple wisdom with more math but less clarity.

## 🎯 Project Evolution

This project has consistently learned that **simple, validated approaches beat complex solutions**:

1. **Framework**: Simple TS% ratios > Complex 5-pathway models
2. **Data**: External validated APIs > Complex remediation of corrupted data
3. **Philosophy**: Start with what works, not what impresses

## 📚 For Future Reference

When considering complex solutions, ask:
- Does this add real value beyond simpler approaches?
- Have we validated that complexity is necessary?
- Could external sources provide what we need more reliably?

If the answer suggests over-engineering, look for simpler alternatives first.



