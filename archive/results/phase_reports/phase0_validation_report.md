# Phase 0 Validation Report: Test Case Analysis

## Executive Summary

This report validates 14 test cases against the current detection system.

---

## Test Cases Found in Dataset

| Case ID | Name | Season | Type | Found | Age | USG% | Leverage TS Δ | Scalability | Creation Ratio |
|---------|------|--------|------|-------|-----|------|---------------|-------------|----------------|
| Haliburton_2020-21 | Tyrese Haliburton | 2020-21 | breakout | ✅ | 21.0 | 0.2% | 0.178 | 0.912 | 0.582 |
| Brunson_2020-21 | Jalen Brunson | 2020-21 | breakout | ✅ | 24.0 | 0.2% | -0.060 | 0.647 | 0.692 |
| Siakam_2017-18 | Pascal Siakam | 2017-18 | breakout | ✅ | 24.0 | 0.2% | 0.339 | 0.891 | 0.203 |
| Siakam_2018-19 | Pascal Siakam | 2018-19 | breakout | ✅ | 25.0 | 0.2% | 0.119 | 0.932 | 0.463 |
| Maxey_2020-21 | Tyrese Maxey | 2020-21 | breakout | ✅ | 20.0 | 0.2% | nan | 0.727 | 0.746 |
| Edwards_2020-21 | Anthony Edwards | 2020-21 | breakout | ✅ | 19.0 | 0.3% | -0.057 | 0.719 | 0.610 |
| Turner_2015-16 | Evan Turner | 2015-16 | non_breakout | ✅ | 27.0 | 0.2% | -0.016 | 0.715 | 0.721 |
| Turner_2016-17 | Evan Turner | 2016-17 | non_breakout | ✅ | 28.0 | 0.2% | -0.017 | 0.652 | 0.656 |
| McConnell_2020-21 | T.J. McConnell | 2020-21 | non_breakout | ✅ | 29.0 | 0.1% | 0.180 | 0.872 | 0.816 |
| Simmons_2017-18 | Ben Simmons | 2017-18 | fragility | ✅ | 21.0 | 0.2% | 0.093 | 0.903 | 0.769 |
| Simmons_2018-19 | Ben Simmons | 2018-19 | fragility | ✅ | 22.0 | 0.2% | 0.007 | 0.872 | 0.650 |
| KAT_2015-16 | Karl-Anthony Towns | 2015-16 | fragility | ✅ | 20.0 | 0.2% | 0.028 | 0.956 | 0.088 |
| KAT_2016-17 | Karl-Anthony Towns | 2016-17 | fragility | ✅ | 21.0 | 0.3% | -0.052 | 0.854 | 0.136 |
| KAT_2017-18 | Karl-Anthony Towns | 2017-18 | fragility | ✅ | 22.0 | 0.2% | -0.132 | 0.755 | 0.109 |

---

## Filter Analysis

### Known Breakouts (Should Be Identified)

### Tyrese Haliburton (2020-21)

- **Age Filter**: ✅ PASS (Age: 21.0)
- **Usage Filter**: ✅ PASS (USG%: 0.2%)
- **Leverage Data**: ✅ AVAILABLE (Value: 0.178)
- **Scalability**: ✅ HIGH (Value: 0.912)
- **Creation Ratio**: ✅ HIGH (Value: 0.582)
- **Pressure Data**: ❌ MISSING (Value: nan)

### Jalen Brunson (2020-21)

- **Age Filter**: ✅ PASS (Age: 24.0)
- **Usage Filter**: ✅ PASS (USG%: 0.2%)
- **Leverage Data**: ✅ AVAILABLE (Value: -0.060)
- **Scalability**: ✅ HIGH (Value: 0.647)
- **Creation Ratio**: ✅ HIGH (Value: 0.692)
- **Pressure Data**: ✅ AVAILABLE (Value: 0.661)

### Pascal Siakam (2017-18)

- **Age Filter**: ✅ PASS (Age: 24.0)
- **Usage Filter**: ✅ PASS (USG%: 0.2%)
- **Leverage Data**: ✅ AVAILABLE (Value: 0.339)
- **Scalability**: ✅ HIGH (Value: 0.891)
- **Creation Ratio**: ✅ HIGH (Value: 0.203)
- **Pressure Data**: ✅ AVAILABLE (Value: 0.464)

### Pascal Siakam (2018-19)

- **Age Filter**: ❌ REMOVED (Age: 25.0)
- **Usage Filter**: ❌ REMOVED (USG%: 0.2%)
- **Leverage Data**: ✅ AVAILABLE (Value: 0.119)
- **Scalability**: ✅ HIGH (Value: 0.932)
- **Creation Ratio**: ✅ HIGH (Value: 0.463)
- **Pressure Data**: ✅ AVAILABLE (Value: 0.552)

### Tyrese Maxey (2020-21)

- **Age Filter**: ✅ PASS (Age: 20.0)
- **Usage Filter**: ❌ REMOVED (USG%: 0.2%)
- **Leverage Data**: ❌ MISSING (Value: nan)
- **Scalability**: ✅ HIGH (Value: 0.727)
- **Creation Ratio**: ✅ HIGH (Value: 0.746)
- **Pressure Data**: ✅ AVAILABLE (Value: 0.531)

### Anthony Edwards (2020-21)

- **Age Filter**: ✅ PASS (Age: 19.0)
- **Usage Filter**: ❌ REMOVED (USG%: 0.3%)
- **Leverage Data**: ✅ AVAILABLE (Value: -0.057)
- **Scalability**: ✅ HIGH (Value: 0.719)
- **Creation Ratio**: ✅ HIGH (Value: 0.610)
- **Pressure Data**: ❌ MISSING (Value: nan)

---

## Key Findings

### Data Availability

- **Found in Dataset**: 14 / 14 (100.0%)
- **Known Breakouts Found**: 6 / 6 (100.0%)