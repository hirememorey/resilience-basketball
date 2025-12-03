# Latent Star Detection Report: Sleeping Giants

## Executive Summary

This report identifies **5** players with high stress vector profiles
who may be undervalued or underutilized. These 'Sleeping Giants' have the stress
profile of playoff stars but may not have been given the opportunity yet.

---

## Methodology (Phase 2 - Updated)

**Criteria for Latent Stars:**

1. **Age < 25 years old**: Filter FIRST - latent stars must be young
2. **Low Usage (< 25% USG)**: Identifies players with low opportunity
3. **LEVERAGE_USG_DELTA ≥ -0.05**: Abdication Detector - must scale up in clutch (filters out passivity)
4. **Predicted Archetype (King/Bulldozer)**: Model predicts actual playoff performance, not just skills
5. **Primary Score Ranking**: Ranked by Stress Vector Composite (weighted by model feature importance)
6. **Confidence Score**: Flags data quality (missing data = lower confidence, no proxies)

**Key Principles:**
- **Filter FIRST (Reference Class)**: Define candidate pool before ranking
- **Normalize within Candidate Pool**: All ranking relative to filtered subset, not entire league
- **Use Validated Stress Vectors**: Model feature importance weights (not arbitrary)
- **No Proxies**: Flag missing data with confidence scores (correlation = 0.0047 invalidates Isolation EFG proxy)

**Key Stress Vectors Analyzed (from validated model):**
- LEVERAGE_USG_DELTA (9.2%): Clutch usage scaling (Abdication Detector)
- CREATION_VOLUME_RATIO (6.2%): Self-creation ability
- RS_PRESSURE_APPETITE (4.5%): Dominance signal
- EFG_ISO_WEIGHTED (4.1%): Isolation efficiency
- RS_LATE_CLOCK_PRESSURE_RESILIENCE (4.8%): Late-clock bailout ability
- Plus 10+ other validated stress vector features

---

## Top Latent Star Candidates

| Rank | Player | Season | Age | RS USG% | Z-Score | Predicted Archetype | King Prob | Key Strengths |
|------|--------|--------|-----|---------|---------|---------------------|-----------|---------------|
| 1 | Shai Gilgeous-Alexander | 2018-19 | 20.0 | 18.2% | 0.00 | Bulldozer (Fragile Star) | 0.36 | High Creation, Pressure Resilient |
| 2 | Bam Adebayo | 2019-20 | 22.0 | 21.2% | 0.00 | King (Resilient Star) | 0.28 | Pressure Resilient |
| 3 | Anfernee Simons | 2021-22 | 23.0 | 24.4% | 0.00 | Bulldozer (Fragile Star) | 0.50 | High Creation, Clutch Scaling |
| 4 | Tyrese Haliburton | 2022-23 | 23.0 | 23.8% | 0.00 | Bulldozer (Fragile Star) | 0.50 | High Creation, Clutch Scaling |
| 5 | Vít Krejčí | 2023-24 | 24.0 | 9.8% | 0.00 | Bulldozer (Fragile Star) | 0.61 | Clutch Scaling |

---

## Insights

### What Makes a Latent Star?

These players share common characteristics:

1. **Self-Creation Ability**: High Creation Volume Ratio indicates they can
   generate their own offense, critical for playoff success.

2. **Pressure Resilience**: Ability to make tough shots (high Pressure Resilience)
   suggests they won't shrink in playoff moments.

3. **Late-Clock Ability**: Players with high Late-Clock Pressure Resilience
   can bail out broken plays, a valuable playoff skill.

### Why They're Undervalued

These players may be undervalued because:

- **Low Usage**: They haven't been given high-usage roles in regular season
- **Role Player Perception**: They're seen as complementary pieces, not stars
- **Small Sample Size**: Limited opportunity to show their stress profile

### The "Next Jalen Brunson" Test

Jalen Brunson in 2021 (DAL) had a high stress profile but was a backup.
When given opportunity in NYK, he became a star. These candidates may follow
a similar path.

---

## Full Results

See `results/latent_stars.csv` for complete list of candidates.
