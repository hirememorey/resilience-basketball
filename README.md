# NBA Extended Playoff Resilience Analytics

A comprehensive data science project analyzing NBA player performance under playoff pressure through multiple resilience pathways. This project builds an advanced predictive model to identify all factors that make players "playoff resilient" - maintaining or exceeding regular-season production in postseason games.

## 🎯 Project Vision

**Core Question:** What are the measurable, observable factors in a player's regular-season performance that predict their ability to maintain or exceed production in the postseason?

**Ultimate Goal:** Create a comprehensive "Extended Playoff Resilience Score" that helps basketball decision-makers make championship-focused investments by understanding all pathways to playoff adaptability.

## 📊 Current Status: PHASE 5 COMPLETE - Unified Framework Operational ✅

**BREAKTHROUGH ACHIEVEMENT:** We have successfully implemented and validated the **Five-Pathway Resilience Framework**. The model now generates a single "Unified Resilience Score" that integrates five distinct dimensions of basketball adaptability, validated against 10 years of historical data (2015-2025).

### The 5 Resilience Pathways
1.  **Versatility Resilience**: Diversity of scoring methods (Spatial, Play-Type, Creation).
2.  **Specialization Mastery**: Elite efficiency in a primary method (The "Shaq" Pathway).
3.  **Role Scalability**: Ability to maintain efficiency under increased usage (The "Jimmy Butler" Pathway).
4.  **Dominance Resilience**: Ability to make high-difficulty shots (The "Shot Quality" Pathway).
5.  **Longitudinal Evolution**: The "Neuroplasticity Coefficient" - rate of new skill acquisition over time.

### Key Findings (Trend Analysis)
*   **Nikola Jokic** is the "Resilience Gold Standard" with elite scores in Specialization, Scalability, *and* Evolution.
*   **James Harden's** decline was predicted by the model years in advance due to a critically low **Evolution Score (18.4)**.
*   **Resilience is Dynamic:** Players shift archetypes over their careers (e.g., KD shifting from Versatility to Specialization).

## 🚀 Quick Start

### Prerequisites
```bash
pip install pandas requests tqdm tenacity pydantic matplotlib
```

### Initialize Database
```bash
python src/nba_data/db/schema.py
```

### Run Unified Analysis
Generate resilience scores for key archetypes:
```bash
python src/nba_data/scripts/calculate_unified_resilience.py
```

### Run Trend Analysis (Pre-Mortem)
Analyze career trajectories across 10 seasons:
```bash
python src/nba_data/scripts/analyze_resilience_trends.py
```

## 📁 Project Structure

```
resilience-basketball/
├── src/
│   └── nba_data/
│       ├── scripts/
│       │   ├── calculate_unified_resilience.py    # MAIN ENGINE: Combines all 5 pathways
│       │   ├── calculate_longitudinal_evolution.py # Neuroplasticity/Growth logic
│       │   ├── calculate_role_scalability.py      # Usage vs Efficiency logic
│       │   ├── calculate_dominance_score.py       # Shot Quality (SQAV) logic
│       │   ├── analyze_resilience_trends.py       # Multi-season trend analysis
│       │   └── ... (Data population scripts)
│       ├── db/               # Database schema
│       └── api/              # NBA Stats API clients
├── data/                     # SQLite database (nba_stats.db) and CSV results
├── extended_resilience_framework.md # Detailed methodology documentation
└── README.md
```

## 🏗️ Architecture
*   **Data Source:** NBA Stats API (Cached locally).
*   **Storage:** SQLite (`nba_stats.db`).
*   **Logic:** Python-based modular calculators for each pathway.
*   **Validation:** "Historical Processing Mode" ensures all metrics are reproducible across 10 seasons.

## 🤝 Contributing
This project is research-grade code. If you are picking this up:
1.  **Start with `extended_resilience_framework.md`** to understand the theory.
2.  **Run `analyze_resilience_trends.py`** to see the model in action.
3.  **Focus on the "Dominance" Normalization:** This is the next area for refinement (see TODOs).

## ⚖️ License
Research and educational purposes. Data sourced from NBA Stats API.
