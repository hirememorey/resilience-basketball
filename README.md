# NBA Extended Playoff Resilience Analytics

A data science project to identify the factors that make NBA players "playoff resilient."

## 🎯 Project Vision

**Core Question:** What are the measurable, observable factors in a player's regular-season performance that predict their ability to maintain or exceed production in the postseason?

**Ultimate Goal:** Create a comprehensive "Extended Playoff Resilience Score" that moves beyond traditional stats to capture the underlying drivers of playoff adaptability.

## ❗ Crucial Context for New Developers

This project has recently undergone a **major data integrity overhaul and a philosophical pivot.**

1.  **Data Integrity:** The foundational database was rebuilt to fix critical schema and data population errors. The database is now **fully populated with clean data for 10 seasons (2015-16 to 2024-25).**
2.  **Philosophical Pivot:** We have shifted from viewing resilience as an "intrinsic trait" to a "conditional probability."
3.  **Recent Progress (Nov 2025):** The "Data Bridge" is complete with combinatorial shot dashboard data. Friction Score calculation is now working. Next: Crucible Baseline and Dominance Score implementations.

**Before you begin, you MUST read the new "Project Pivot" and "Data Integrity Post-Mortem" sections at the top of `extended_resilience_framework.md`.** This document contains the new roadmap and essential context.

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Initialize Database
This will create the database file with the correct, updated schema.
```bash
python src/nba_data/db/schema.py
```

### Database Status: ✅ POPULATED
The database is fully populated with 10 seasons of historical data. The main population script (`populate_historical_data.py`) can be re-run if necessary, but is not required for initial setup.

```bash
# Optional: Example for re-populating one season
python populate_historical_data.py --seasons 2023-24
```

### Validate Data Integrity
After any new data ingestion, **always** run the validation script.
```bash
python src/nba_data/scripts/validate_integrity.py
```

## 📁 Project Structure

```
resilience-basketball/
├── src/
│   └── nba_data/
│       ├── scripts/
│       │   ├── populate_historical_data.py # MAIN SCRIPT for data ingestion
│       │   ├── validate_integrity.py       # CRITICAL validation script
│       │   ├── calculate_...               # Analysis scripts (REQUIRE UPDATES)
│       │   └── ...
│       ├── db/               # Database schema
│       └── api/              # NBA Stats API clients
├── data/                     # SQLite database (nba_stats.db)
├── extended_resilience_framework.md # ✅ START HERE: Detailed methodology & new roadmap
└── README.md
```

## Next Steps
1.  **Start with `extended_resilience_framework.md`** to understand the new project direction.
2.  **Continue Logic Bridge:** Implement remaining metrics:
   - ✅ Friction Score (`calculate_friction.py`) - **COMPLETE**
   - 🔄 Crucible Baseline (`calculate_crucible_baseline.py`) - **IN PROGRESS**
   - ⏳ Dominance Score (`calculate_dominance_score.py`) - **NEXT**
   - ⏳ Unified Resilience (`calculate_unified_resilience.py`) - **FINAL**

## Current Working Features
- **Friction Score Calculation:** Working for 2023-24 season. Measures scoring efficiency relative to ball-handling time.
- **Data Foundation:** Shot dashboard (13K+ rows), tracking stats, team ratings, and player metadata all populated.
