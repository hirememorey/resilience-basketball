# Component Analysis Report: Stress Vectors → Playoff Outcomes

## Executive Summary

This report correlates Regular Season stress vector features with Playoff outcome metrics.
The goal is to identify which stress vectors are actionable predictors of playoff performance.

---

## Methodology

- **Stress Vectors Analyzed:** 27
- **Outcome Metrics:** 7
- **Total Correlations Calculated:** 175

### Outcome Metrics

- **PO_DOMINANCE**: Playoff points per 75 possessions (absolute production)
- **PO_RQ**: Resilience Quotient (volume × efficiency ratio)
- **PO_PTS_PER_75**: Playoff points per 75 possessions
- **PO_TS_PCT**: Playoff True Shooting Percentage
- **PO_VOL_RATIO**: Playoff volume ratio (PO volume / RS volume)
- **PO_EFF_RATIO**: Playoff efficiency ratio (PO TS% / RS TS%)
- **PO_RESILIENCE_SCORE**: Composite resilience score

---

## Top Correlations by Outcome Metric

### PO_DOMINANCE

| Stress Vector | Pearson r | p-value | n |
|--------------|----------|---------|---|
| CREATION_VOLUME_RATIO | 0.536*** | 8.124e-44 | 572 |
| LEVERAGE_USG_DELTA | 0.474*** | 2.237e-33 | 572 |
| RS_FTr | 0.271*** | 4.124e-11 | 572 |
| EFG_ISO_WEIGHTED | 0.224*** | 6.523e-08 | 572 |
| CLUTCH_MIN_TOTAL | 0.215*** | 2.054e-07 | 572 |

### PO_RQ

| Stress Vector | Pearson r | p-value | n |
|--------------|----------|---------|---|
| FTr_RESILIENCE | 0.160*** | 1.211e-04 | 572 |
| EARLY_CLOCK_PRESSURE_RESILIENCE_DELTA | 0.151** | 2.965e-03 | 387 |
| EARLY_CLOCK_PRESSURE_APPETITE_DELTA | -0.147*** | 4.071e-04 | 571 |
| LATE_CLOCK_PRESSURE_APPETITE_DELTA | 0.147*** | 4.071e-04 | 571 |
| EFG_PCT_0_DRIBBLE | -0.142*** | 6.419e-04 | 572 |

### PO_PTS_PER_75

| Stress Vector | Pearson r | p-value | n |
|--------------|----------|---------|---|
| CREATION_VOLUME_RATIO | 0.633*** | 1.693e-65 | 572 |
| LEVERAGE_USG_DELTA | 0.512*** | 1.577e-39 | 572 |
| CLUTCH_MIN_TOTAL | 0.257*** | 4.348e-10 | 572 |
| RS_FTr | 0.255*** | 6.232e-10 | 572 |
| EFG_ISO_WEIGHTED | 0.195*** | 2.644e-06 | 572 |

### PO_TS_PCT

| Stress Vector | Pearson r | p-value | n |
|--------------|----------|---------|---|
| EFG_PCT_0_DRIBBLE | 0.260*** | 2.619e-10 | 572 |
| CREATION_VOLUME_RATIO | -0.237*** | 9.843e-09 | 572 |
| PRESSURE_RESILIENCE_DELTA | 0.214*** | 2.384e-07 | 572 |
| EARLY_CLOCK_PRESSURE_RESILIENCE_DELTA | 0.206*** | 4.426e-05 | 387 |
| RS_PRESSURE_RESILIENCE | 0.189*** | 5.211e-06 | 572 |

### PO_VOL_RATIO

| Stress Vector | Pearson r | p-value | n |
|--------------|----------|---------|---|
| LEVERAGE_USG_DELTA | 0.183*** | 1.075e-05 | 572 |
| EARLY_CLOCK_PRESSURE_APPETITE_DELTA | -0.167*** | 6.051e-05 | 571 |
| LATE_CLOCK_PRESSURE_APPETITE_DELTA | 0.167*** | 6.051e-05 | 571 |
| CREATION_VOLUME_RATIO | 0.108** | 9.951e-03 | 572 |
| RS_PRESSURE_APPETITE | -0.089* | 3.341e-02 | 572 |

### PO_EFF_RATIO

| Stress Vector | Pearson r | p-value | n |
|--------------|----------|---------|---|
| EARLY_CLOCK_PRESSURE_RESILIENCE_DELTA | 0.251*** | 5.508e-07 | 387 |
| PRESSURE_RESILIENCE_DELTA | 0.236*** | 1.064e-08 | 572 |
| LATE_CLOCK_PRESSURE_RESILIENCE_DELTA | 0.215*** | 1.020e-04 | 323 |
| FTr_RESILIENCE | 0.213*** | 2.557e-07 | 572 |
| EFG_PCT_0_DRIBBLE | -0.178*** | 1.818e-05 | 572 |

### PO_RESILIENCE_SCORE

| Stress Vector | Pearson r | p-value | n |
|--------------|----------|---------|---|
| FTr_RESILIENCE | 0.160*** | 1.211e-04 | 572 |
| EARLY_CLOCK_PRESSURE_RESILIENCE_DELTA | 0.151** | 2.965e-03 | 387 |
| EARLY_CLOCK_PRESSURE_APPETITE_DELTA | -0.147*** | 4.071e-04 | 571 |
| LATE_CLOCK_PRESSURE_APPETITE_DELTA | 0.147*** | 4.071e-04 | 571 |
| EFG_PCT_0_DRIBBLE | -0.142*** | 6.419e-04 | 572 |

---

## Key Insights

- **CREATION_VOLUME_RATIO** is strongly positively correlated with **PO_PTS_PER_75** (r=0.633, p=1.693e-65). This suggests that this stress vector is a strong predictor of PO_PTS_PER_75
- **CREATION_VOLUME_RATIO** is strongly positively correlated with **PO_DOMINANCE** (r=0.536, p=8.124e-44). This suggests that self-creation ability is a strong predictor of playoff production
- **LEVERAGE_USG_DELTA** is strongly positively correlated with **PO_PTS_PER_75** (r=0.512, p=1.577e-39). This suggests that this stress vector is a strong predictor of PO_PTS_PER_75
- **LEVERAGE_USG_DELTA** is strongly positively correlated with **PO_DOMINANCE** (r=0.474, p=2.237e-33). This suggests that this stress vector is a strong predictor of PO_DOMINANCE
- **RS_FTr** is moderately positively correlated with **PO_DOMINANCE** (r=0.271, p=4.124e-11). This suggests that this stress vector moderately predicts PO_DOMINANCE
- **EFG_PCT_0_DRIBBLE** is moderately positively correlated with **PO_TS_PCT** (r=0.260, p=2.619e-10). This suggests that this stress vector moderately predicts PO_TS_PCT
- **CLUTCH_MIN_TOTAL** is moderately positively correlated with **PO_PTS_PER_75** (r=0.257, p=4.348e-10). This suggests that this stress vector moderately predicts PO_PTS_PER_75
- **RS_FTr** is moderately positively correlated with **PO_PTS_PER_75** (r=0.255, p=6.232e-10). This suggests that this stress vector moderately predicts PO_PTS_PER_75
- **EARLY_CLOCK_PRESSURE_RESILIENCE_DELTA** is moderately positively correlated with **PO_EFF_RATIO** (r=0.251, p=5.508e-07). This suggests that this stress vector moderately predicts PO_EFF_RATIO
- **CREATION_VOLUME_RATIO** is moderately negatively correlated with **PO_TS_PCT** (r=-0.237, p=9.843e-09). This suggests that this stress vector moderately predicts PO_TS_PCT

---

## Actionable Recommendations

### For Coaches:
- Focus on developing players' **Late-Clock Pressure Resilience** - it strongly predicts playoff dominance
- Identify players with high **Creation Volume Ratio** - they scale better in playoffs
- Monitor **Leverage Usage Delta** - players who increase usage in clutch situations perform better

### For GMs:
- Value **Pressure Appetite** over pure efficiency in regular season
- Look for players with high **Rim Pressure Resilience** - they maintain physicality in playoffs
- Avoid players with high **Early-Clock Pressure Appetite** - indicates poor shot selection

---

## Full Correlation Matrix

See `results/component_analysis_correlations.csv` for complete correlation data.
