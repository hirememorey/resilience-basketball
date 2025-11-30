# NBA Playoff Resilience Calculator

**Goal:** Identify "16-game players" who perform better than expected in the playoffs given their abilities and defensive context.

## Quick Start for New Developers

### 1. Understand the Approach
Read these documents in order:
1. **`IMPLEMENTATION_PLAN.md`** - High-level conceptual overview (15 min read)
2. **`DATA_REQUIREMENTS.md`** - Data specifications and collection details (10 min read)
3. **`IMPLEMENTATION_GUIDE.md`** - Step-by-step coding instructions (20 min read)

### 2. Set Up Environment
```bash
# Install dependencies
pip install pandas numpy scikit-learn scipy tenacity requests

# Create required directories
mkdir -p data/cache models results
```

### 3. Start Implementation
```bash
# Phase 1: Collect data (4-6 hours, mostly API wait time)
python src/nba_data/scripts/collect_regular_season_stats.py --seasons 2018-19 2022-23 2023-24
python src/nba_data/scripts/collect_defensive_context.py --seasons 2018-19 2022-23 2023-24
python src/nba_data/scripts/collect_playoff_playbyplay.py --seasons 2018-19 2022-23 2023-24

# Phase 2: Assemble and train (10 minutes)
python src/nba_data/scripts/assemble_training_data.py --output data/training_dataset.csv
python src/nba_data/scripts/train_resilience_models.py

# Phase 3: Score and validate (5 minutes)
python src/nba_data/scripts/calculate_resilience_scores.py
python src/nba_data/scripts/validate_face_validity.py
python src/nba_data/scripts/generate_report.py --output results/resilience_report.md
```

**Total time:** 4-7 hours (mostly unattended API calls)

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
│       └── scripts/                # Implementation scripts (to be created)
├── data/                           # Data storage
│   ├── cache/                      # API response cache
│   ├── regular_season_*.csv        # Regular season stats
│   ├── defensive_context_*.csv    # Defensive metrics
│   ├── playoff_playbyplay_*.csv   # Playoff data (garbage time filtered)
│   └── training_dataset.csv       # Assembled training data
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
❌ **Small sample bias** → Set minimum thresholds (50 RS games, 4 playoff games)
❌ **Adding features without validation** → Require proof of improvement
❌ **Ratio metrics without context** → Use expected performance models instead

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

**Q: Why not just use TS% ratios?**
A: Ratio metrics penalize elite players and ignore opponent quality. Expected performance models fix both issues.

**Q: How long does implementation take?**
A: 4-7 hours total, mostly unattended API calls. Actual coding: ~2-3 hours.

**Q: What if I want to understand the project history?**
A: Read `HISTORICAL_CONTEXT.md` (optional). But you can implement without it.

**Q: Can I add more features to the model?**
A: Yes, but require >3% accuracy improvement with statistical significance. Document in validation reports.

**Q: What if face validity fails?**
A: Investigate why. If models systematically miss known cases, revisit feature engineering or model structure.

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
