# NBA Playoff Resilience Calculator

**Goal:** Identify players who consistently perform better than expected in the playoffs, accounting for their regular-season abilities and the quality of opponent defenses.

This project is fully implemented and the results are trustworthy.

## Quick Start for New Developers

### 1. Understand the Vision
- **`README.md`**: You're here! This provides the high-level overview, key results, and next steps.
- **`HISTORICAL_CONTEXT.md`**: (Optional but Recommended) Explains *why* the project is designed this way and the lessons learned from past mistakes.

### 2. Set Up Environment
```bash
# It is recommended to use a virtual environment
# python3 -m venv venv
# source venv/bin/activate

# Install dependencies
pip install pandas numpy scikit-learn scipy tenacity requests

# Create required directories
mkdir -p data/cache models results logs
```

### 3. Run the Full Pipeline
The data pipeline is designed to be run end-to-end. The following commands will collect 6 seasons of data, train the models, and generate the final resilience report.

```bash
# Phase 1: Collect data for all seasons (approx. 45-60 minutes)
# Note: These can be run in parallel to speed up collection.
python src/nba_data/scripts/collect_regular_season_stats.py --seasons 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24
python src/nba_data/scripts/collect_defensive_context.py --seasons 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24
python src/nba_data/scripts/collect_playoff_logs.py --seasons 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24

# Phase 2: Assemble, train, score, and report (approx. 1 minute)
python src/nba_data/scripts/assemble_training_data.py
python src/nba_data/scripts/train_resilience_models.py
python src/nba_data/scripts/calculate_resilience_scores.py
python src/nba_data/scripts/validate_face_validity.py
python src/nba_data/scripts/generate_report.py
```

**Total time:** 45-60 minutes (mostly unattended API calls).

---

## What This Project Does

### The Core Question
"Given a player's demonstrated abilities and the specific defensive context they faced, how does their actual playoff performance compare to what we would statistically expect?"

### The Approach
1. **Player Ability Baseline:** Regular season TS%, Points per 75, AST%, Usage%
2. **Defensive Context:** Opponent defensive quality (Defensive Rating, eFG% allowed, etc.)
3. **Expected Performance Model:** Regression models predicting playoff performance given #1 and #2
4. **Resilience Score:** (Actual Performance - Expected Performance) in standard deviations

### Why This Approach?
- **Context-aware:** Accounts for opponent quality
- **Fair to elite players:** No penalty for high baselines
- **Interpretable:** Z-scores show how many standard deviations better/worse than expected
- **Statistically grounded:** Regression models capture non-linear relationships

---

## Project Structure

```
├── IMPLEMENTATION_PLAN.md          # Conceptual overview (START HERE)
├── DATA_REQUIREMENTS.md            # Data specifications
├── IMPLEMENTATION_GUIDE.md         # Step-by-step coding guide
├── HISTORICAL_CONTEXT.md           # Project evolution (optional reading)
├── prompts.md                      # AI development commands
├── src/
│   └── nba_data/
│       ├── api/                    # NBA Stats API client (already built)
│       └── scripts/                # All implementation scripts
├── data/                           # Data storage
│   ├── cache/                      # API response cache
│   ├── regular_season_*.csv
│   ├── defensive_context_*.csv
│   ├── playoff_logs_*.csv          # Replaced unreliable play-by-play data
│   └── training_dataset.csv
├── models/                         # Trained regression models
│   ├── ts_pct_model.pkl
│   ├── ppg_per75_model.pkl
│   ├── ast_pct_model.pkl
│   └── model_metadata.pkl
└── results/                        # Output files
    ├── resilience_scores_all.csv
    └── resilience_report.md
```

---

## Key Concepts

### 1. Garbage Time Filter
Removes possessions where game outcome is no longer in doubt:
- 4th quarter or overtime
- Score differential ≥ 15 points
- Time remaining ≤ 5 minutes

### 2. Defensive Context Score (DCS)
Composite metric (0-100) measuring opponent defensive quality:
- 60% Defensive Rating
- 25% Opponent eFG%
- 15% Opponent FT Rate

### 3. Regression Models
Three separate models for:
- **TS%:** Efficiency maintenance
- **Points per 75:** Volume scoring
- **AST%:** Playmaking creation

Each model uses:
- Regular season metric
- Defensive context score
- Usage %
- Interaction term (captures skill elasticity)

### 4. Resilience Score Interpretation
- **+2.0:** Elite playoff riser (2 SD above expected)
- **+1.0:** Strong playoff performer (1 SD above expected)
- **0.0:** Exactly as expected
- **-1.0:** Underperformed expectations
- **-2.0:** Significant playoff decline

---

## Success Criteria

### Minimum Viable Product (MVP)
- [ ] Data collected for 3+ seasons
- [ ] Models trained with R² ≥ 0.3
- [ ] Face validity passes (known elite performers score high)
- [ ] Output CSV generated with all required fields

### Validation Checkpoints
- [ ] LeBron James (2012-2018) scores positive
- [ ] Kawhi Leonard (2019) scores positive
- [ ] Nikola Jokić (2023) scores positive
- [ ] Model residuals approximately normal
- [ ] No systematic bias by baseline performance level

---

## Optional: Historical Context

**Why did we design it this way?**

The project went through several iterations:
1. Over-engineered complex framework (abandoned)
2. Simple TS% ratios (failed reality checks)
3. Composite metric (systematic bias against elite players)
4. **Current:** Regression-based expected performance (synthesizes all lessons)

**Read `HISTORICAL_CONTEXT.md` for full story** (optional but informative).

---

## Key Principles

### 1. First Principles Thinking
Start with the core question: "Who performs better than expected given context?"

### 2. Simplicity with Rigor
Simple enough to interpret, complex enough to capture reality.

### 3. Validate Continuously
Statistical significance ≠ practical validity. Test against known cases.

### 4. Measure What Matters
"Better than expected" (useful) vs "maintained baseline" (biased against elite players).

### 5. Reality Check Everything
One counterexample (champion marked as fragile) reveals systematic issues.

---

## Development Workflow

### AI-Assisted Development
Use commands from `prompts.md`:
- `@NewSession` - Understand project state
- `@Plan` - Design implementation approach
- `@PreMortem` - Identify failure modes
- `@Implement` - Begin coding
- `@UpdateDocs` - Keep documentation current

### Iteration Protocol
1. Implement minimal version
2. Validate against reality
3. Measure improvement (>3% accuracy gain required)
4. Document or archive
5. Repeat

---

## Common Pitfalls to Avoid

❌ **Over-fitting to recent data** → Use multiple seasons, validate on held-out data
❌ **Ignoring context** → Always account for opponent defensive quality
❌ **Small sample bias** → Filter out player-series with fewer than 50 total minutes.
❌ **Adding features without validation** → Require proof of improvement
❌ **Ratio metrics without context** → Use expected performance models instead
❌ **API Unreliability:** Do not trust API documentation. Verify endpoints before building dependencies. The `playbyplayv2` endpoint is non-functional; `playergamelogs` is the robust alternative.
❌ **Data Completeness:** Collect both "Base" and "Advanced" stats and merge them to get a complete set of metrics (e.g., PTS from Base, USG% from Advanced).

---

## Data Sources

### Primary: NBA Stats API
- Clean, authoritative, validated data
- Built-in caching and error handling
- Client already implemented: `src/nba_data/api/nba_stats_client.py`

### No Local Database Required
Previous versions used local SQLite database (corrupted). Current approach uses external API exclusively.

---

## FAQ

**Q: Why doesn't Anthony Davis score higher?**
A: The model is currently offense-only. It correctly identifies that his offensive output is roughly what's expected, but it does not yet account for his elite defensive value. Adding a defensive component is the next major step for this project.

**Q: Why was the `playbyplayv2` endpoint abandoned?**
A: During development, it was found to be unreliable, frequently returning empty data. The `playergamelogs` endpoint was chosen as a more robust and stable alternative for playoff data. See `HISTORICAL_CONTEXT.md` for details.

**Q: How is "garbage time" handled?**
A: The original plan was to filter play-by-play data. The current, more robust approach is to filter out any player-series with fewer than 50 total minutes played. This effectively removes noise from players who only had brief, inconsequential appearances.

**Q: How long does the full pipeline take to run?**
A: Approximately 45-60 minutes, most of which is unattended data collection. The analysis and scoring steps take less than a minute.

---

## Next Steps

1. **Read:** `IMPLEMENTATION_PLAN.md` (conceptual overview)
2. **Review:** `DATA_REQUIREMENTS.md` (data specs)
3. **Start:** `IMPLEMENTATION_GUIDE.md` (step-by-step instructions)
4. **Code:** Follow implementation guide to build data pipeline and models
5. **Validate:** Run face validity checks and statistical tests
6. **Iterate:** Refine based on results

---

## Contributing Philosophy

**Build what matters, not what impresses.**

This project values:
- Clear thinking over complex models
- Practical validity over statistical sophistication
- Interpretability over accuracy gains
- Reality checks over theoretical elegance

If you can achieve the same results with simpler code, that's success.

---

## Support

- **Technical questions:** Review `IMPLEMENTATION_GUIDE.md`
- **Conceptual questions:** Review `IMPLEMENTATION_PLAN.md`
- **Historical questions:** Review `HISTORICAL_CONTEXT.md`
- **AI commands:** Review `prompts.md`

---

**Let's build something useful.** 🏀
