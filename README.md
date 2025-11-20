# NBA Extended Playoff Resilience Analytics

A data science project to identify the factors that make NBA players "playoff resilient."

## 🎯 Project Vision

**Core Question:** What are the measurable, observable factors in a player's regular-season performance that predict their ability to maintain or exceed production in the postseason?

**Ultimate Goal:** Create a comprehensive "Extended Playoff Resilience Score" that moves beyond traditional stats to capture the underlying drivers of playoff adaptability.

## ❗ Crucial Context for New Developers

This project has recently undergone a **major data integrity overhaul and a philosophical pivot.**

1.  **Data Integrity:** The foundational database was rebuilt to fix critical schema and data population errors. **Only the 2024-25 Regular Season data is currently clean and populated.**
2.  **Philosophical Pivot:** We have shifted from viewing resilience as an "intrinsic trait" to a "conditional probability."

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

### (Ongoing) Repopulate Historical Data
The database is currently mostly empty. You will need to run the fixed population scripts for each season and season type.
```bash
# Example for one season
python src/nba_data/scripts/populate_historical_data.py --seasons 2023-24
```

### Validate Data Integrity
After populating any data, **always** run the validation script.
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
2.  **Run the historical data population** to build your dataset.
3.  **Refactor the analysis scripts** in `src/nba_data/scripts/` to implement the new resilience metrics (Friction Score, Crucible Baseline, etc.).
