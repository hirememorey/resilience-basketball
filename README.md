# NBA Extended Playoff Resilience Analytics

A data science project to identify the factors that make NBA players "playoff resilient."

## 🎯 Project Vision

**Core Question:** What are the measurable, observable factors in a player's regular-season performance that predict their ability to maintain or exceed production in the postseason?

**Ultimate Goal:** Create a comprehensive "Extended Playoff Resilience Score" that moves beyond traditional stats to capture the underlying drivers of playoff adaptability.

## ❗ Crucial Context for New Developers

This project has undergone a **major data integrity overhaul and philosophical pivot.**

1.  **Data Integrity Crisis (RESOLVED):** A critical data integrity issue was discovered and fixed - 27,931 orphaned game references in player_game_logs. Root cause: 2024-25 season game logs were populated before games table data. **Issue resolved** by running historical population for 2024-25 season.
2.  **Philosophical Pivot:** We have shifted from viewing resilience as an "intrinsic trait" to a "conditional probability."
3.  **Complete Historical Coverage:** The database now contains comprehensive historical data for 10 seasons (2015-16 to 2024-25) with both Regular Season and Playoff data.

**Before you begin, you MUST read the "Project Pivot" and "Data Integrity Post-Mortem" sections at the top of `extended_resilience_framework.md`.** This document contains the methodology and essential context.

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

### Database Status: ✅ FULLY POPULATED & INTEGRITY VERIFIED
The database contains comprehensive historical data across all critical tables:

- **Players:** 1,437 players with complete metadata
- **Seasons:** 10 full seasons (2015-16 to 2024-25) with both Regular Season and Playoff data
- **Games:** 12,813 complete game records
- **Game Logs:** 271,183 game-by-game records for granular analysis
- **Tracking Stats:** 7,516 possession metrics for friction analysis
- **Shot Dashboard:** 135,738 combinatorial shot records for dominance analysis
- **Team Ratings:** Complete defensive ratings for crucible baseline calculations

**Data Integrity:** ✅ All referential integrity checks pass. No orphaned records.

The historical data surge is complete. Individual season re-population is available if needed:

```bash
# Optional: Re-populate specific seasons
python src/nba_data/scripts/populate_game_logs.py --season 2023-24
python src/nba_data/scripts/populate_shot_dashboard_data.py --season 2023-24
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
1.  **Start with `extended_resilience_framework.md`** to understand the philosophical pivot and methodology.
2.  **Execute Resilience Calculations:** The five-pathway framework is now ready for implementation:
    ```bash
    # Run the unified resilience calculator (integrates all 5 pathways)
    python src/nba_data/scripts/calculate_unified_resilience.py

    # Or run individual pathway calculators:
    python src/nba_data/scripts/calculate_friction.py           # Process independence
    python src/nba_data/scripts/calculate_crucible_baseline.py  # Top-10 defense performance
    python src/nba_data/scripts/calculate_dominance_score.py     # Shot quality under pressure
    python src/nba_data/scripts/calculate_longitudinal_evolution.py # Multi-season adaptability
    python src/nba_data/scripts/calculate_extended_resilience.py   # Versatility/diversification
    ```
3.  **Validate Results:** Compare resilience scores against known playoff performers (e.g., Jimmy Butler vs. Anthony Edwards)
4.  **Visualize:** Generate career arc charts and correlation analysis
5.  **Iterate:** Refine weighting and methodology based on empirical results

## Current Working Features

### ✅ Data Foundation (Complete & Verified)
- **Comprehensive Historical Coverage:** 10 seasons (2015-16 to 2024-25) with both Regular Season and Playoff data
- **Player Universe:** 1,437 players with complete metadata and historical tracking
- **Game-Level Granularity:** 271,183 game logs enabling crucible baseline calculations
- **Possession Metrics:** 7,516 tracking records with friction analysis data
- **Shot Quality Data:** 135,738 combinatorial shot dashboard records for dominance scoring
- **Team Defense Ratings:** Complete ratings for all seasons enabling Top-10 defense filtering
- **Data Integrity:** All foreign key constraints enforced, no orphaned records

### 🔧 Resilience Framework (Ready for Implementation)
- **Unified Resilience Score:** Framework designed to aggregate 5 pathways using Z-Score normalization
- **Friction Score:** Process independence measurement comparing regular season vs. playoff efficiency
- **Crucible Baseline:** Performance filtering against Top-10 defenses for rigorous benchmarking
- **Dominance Score:** Shot quality analysis under pressure conditions
- **Evolution Score:** Multi-season skill acquisition trajectory analysis
- **Versatility Score:** Skill diversification and dependency-weighted scoring

### 🛠️ Technical Infrastructure
- **Database-First Architecture:** Eliminates brittle CSV dependencies
- **Foreign Key Enforcement:** Data integrity guaranteed at database level
- **Validation Pipeline:** Comprehensive integrity checks for all data operations
- **API Resilience:** Robust error handling for external data sources
