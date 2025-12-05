# Latent Star Detection Report: Sleeping Giants

## Executive Summary

This report identifies **291** players with high stress vector profiles
who may be undervalued or underutilized. These 'Sleeping Giants' have the stress
profile of playoff stars but may not have been given the opportunity yet.

---

## Methodology (Updated Dec 2025)

**CRITICAL INSIGHT**: Age is the PRIMARY filter. Veterans (25+) have no latent potential.

**Criteria for Latent Stars:**

1. **Age < 26 years old (PRIMARY FILTER)**: Veterans have no latent potential - their game is what it is
2. **Low Usage (< 25% USG)**: Identifies players with low opportunity
3. **Star Potential at 25% Usage ≥ 50%**: Using usage-aware conditional prediction
4. **Quality Filters**: Applied for young players to ensure strong base signals
5. **Ranking**: Ranked by star-level potential at 25% usage (not current performance)

**Key Change**: We predict "What if they had 25% usage?" not "What are they at current usage?"

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

| Rank | Player | Season | Age | RS USG% | Star Potential (25%) | Archetype at 25% | Confidence | Key Strengths |
|------|--------|--------|-----|---------|----------------------|-----------------|------------|---------------|
| 1 | Jamal Murray | 2019-20 | 23.0 | 24.8% | 81.2% | King (Resilient Star) | Low | High Creation, Clutch Scaling |
| 2 | Tyrese Haliburton | 2024-25 | 25.0 | 21.0% | 78.8% | King (Resilient Star) | Low | High Creation, Clutch Scaling |
| 3 | Jamal Murray | 2018-19 | 22.0 | 24.1% | 76.3% | King (Resilient Star) | Low | High Creation, Clutch Scaling |
| 4 | Daishen Nix | 2022-23 | 21.0 | 14.9% | 76.1% | King (Resilient Star) | Low | Clutch Scaling |
| 5 | Mario Hezonja | 2015-16 | 21.0 | 16.6% | 76.0% | King (Resilient Star) | Low | Clutch Scaling |
| 6 | Kevin Porter Jr. | 2020-21 | 21.0 | 24.7% | 75.6% | King (Resilient Star) | Low | High Creation, Clutch Scaling |
| 7 | Aaron Harrison | 2017-18 | 23.0 | 14.7% | 74.1% | King (Resilient Star) | Low | Clutch Scaling |
| 8 | Andrew Nembhard | 2024-25 | 25.0 | 16.3% | 74.0% | King (Resilient Star) | Low | High Creation, Clutch Scaling |
| 9 | Talen Horton-Tucker | 2020-21 | 20.0 | 21.0% | 72.6% | King (Resilient Star) | Low | High Creation, Clutch Scaling |
| 10 | Dalano Banton | 2024-25 | 25.0 | 23.7% | 72.0% | King (Resilient Star) | Low | High Creation, Clutch Scaling |
| 11 | Bub Carrington | 2024-25 | 19.0 | 15.4% | 70.4% | King (Resilient Star) | Low | High Creation, Clutch Scaling |
| 12 | Jerian Grant | 2015-16 | 23.0 | 18.5% | 70.0% | King (Resilient Star) | Low | High Creation, Clutch Scaling |
| 13 | Tyler Ennis | 2017-18 | 23.0 | 16.9% | 69.9% | King (Resilient Star) | Low | High Creation, Clutch Scaling |
| 14 | Austin Reaves | 2021-22 | 24.0 | 12.1% | 69.9% | King (Resilient Star) | Low | Clutch Scaling |
| 15 | Jalen Suggs | 2022-23 | 22.0 | 19.6% | 69.9% | King (Resilient Star) | Low | High Creation, Clutch Scaling |
| 16 | Khem Birch | 2017-18 | 25.0 | 13.1% | 68.8% | King (Resilient Star) | Low | Clutch Scaling |
| 17 | Cam Thomas | 2021-22 | 20.0 | 21.2% | 68.8% | King (Resilient Star) | Low | High Creation, Clutch Scaling |
| 18 | KJ Simpson | 2024-25 | 22.0 | 18.8% | 68.2% | King (Resilient Star) | Low | High Creation, Clutch Scaling |
| 19 | Jaime Jaquez Jr. | 2024-25 | 24.0 | 19.4% | 68.2% | King (Resilient Star) | Low | High Creation, Clutch Scaling |
| 20 | Jalen Brunson | 2020-21 | 24.0 | 19.6% | 68.1% | King (Resilient Star) | Low | High Creation, Clutch Scaling |

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
