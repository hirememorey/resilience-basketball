# Risk Category Analysis for Failing Test Cases

## Summary

The 2D Risk Matrix is **working correctly** - risk categories are being assigned properly based on the actual Performance and Dependence scores. However, **gate capping is changing the risk categories** from what the test cases expect.

## Risk Categorization Logic

From `predict_conditional_archetype.py`:
- **Franchise Cornerstone**: Performance ≥70% + Low Dependence (<0.3570)
- **Luxury Component**: Performance ≥70% + High Dependence (≥0.4482)
- **Moderate Performance, High Dependence**: Performance 30-70% + High Dependence (≥0.4482)
- **Moderate Performance, Low Dependence**: Performance 30-70% + Low Dependence (<0.3570)
- **Depth**: Performance <30% + Low Dependence (<0.3570)
- **Avoid**: Performance <30% + High Dependence (≥0.4482)

## Cases with Expected Risk Categories

### ✅ Jordan Poole (2021-22) - CORRECT
- **Expected**: "Luxury Component"
- **Got**: "Luxury Component" ✅
- **Performance**: 87.62% (High ≥70%)
- **Dependence**: 46.11% (Moderate, between 0.3570-0.4482)
- **Analysis**: High performance + moderate dependence = "Luxury Component" (correct)

### ❌ Domantas Sabonis (2021-22) - CORRECT for Capped Performance
- **Expected**: "Luxury Component"
- **Got**: "Moderate Performance, High Dependence"
- **Performance**: 30.00% (Gates capped from higher value)
- **Dependence**: 60.37% (High ≥0.4482)
- **Analysis**: 
  - **Risk category is CORRECT** for the capped performance (30% = Moderate, not High)
  - **Issue**: Gates are capping performance, preventing "Luxury Component" classification
  - **Root Cause**: Gates should not cap Sabonis, or test expectation should account for gate capping

### ❌ Tyrese Haliburton (2021-22) - CORRECT for Capped Performance
- **Expected**: "Franchise Cornerstone"
- **Got**: "Moderate Performance, Low Dependence"
- **Performance**: 30.00% (Gates capped from higher value)
- **Dependence**: 28.55% (Low <0.3570)
- **Analysis**:
  - **Risk category is CORRECT** for the capped performance (30% = Moderate, not High)
  - **Issue**: Gates are capping performance, preventing "Franchise Cornerstone" classification
  - **Root Cause**: Gates should not cap Haliburton (he's a true positive), or test expectation should account for gate capping

## Cases Without Expected Risk Categories

### KAT Seasons (2016-17, 2018-19, 2019-20, 2020-21)
- **Got**: "Luxury Component" (when performance is 73-85%)
- **Performance**: 73.57-85.02% (High ≥70%)
- **Dependence**: 59.27-62.40% (High ≥0.4482)
- **Analysis**: **Risk category is CORRECT** - High performance + High dependence = "Luxury Component"
- **Issue**: These are false positives (model thinks KAT is good when he's not)

### Fultz Later Seasons (2019-20, 2022-23)
- **Got**: "Franchise Cornerstone" (when performance is 73-75%)
- **Performance**: 73.04-74.87% (High ≥70%)
- **Dependence**: 27.19-27.25% (Low <0.3570)
- **Analysis**: **Risk category is CORRECT** - High performance + Low dependence = "Franchise Cornerstone"
- **Issue**: These are false positives (model thinks Fultz is good when he's not)

### Fultz 2023-24
- **Got**: "Moderate Performance, Low Dependence"
- **Performance**: 66.08% (Moderate, 30-70%)
- **Dependence**: 26.60% (Low <0.3570)
- **Analysis**: **Risk category is CORRECT** - Moderate performance + Low dependence = "Moderate Performance, Low Dependence"
- **Issue**: False positive (model thinks Fultz is good when he's not)

## Key Findings

1. **Risk Categories Are Correct**: All risk categories match the 2D Risk Matrix logic based on actual Performance and Dependence scores.

2. **Gate Capping Issue**: 
   - Sabonis and Haliburton have correct risk categories **for their capped performance**
   - The problem is that gates are capping them at 30%, which prevents "Luxury Component" and "Franchise Cornerstone" classifications
   - These cases need gate logic fixes, not risk category fixes

3. **False Positive Issue**:
   - KAT and Fultz later seasons have correct risk categories **for their predicted performance**
   - The problem is that the model is predicting high performance when it shouldn't
   - These cases need model/feature improvements, not risk category fixes

## Recommendations

1. **For Sabonis/Haliburton**: Fix gate logic to not cap these players (they're legitimate cases)
2. **For KAT/Fultz**: These are model prediction issues, not risk categorization issues
3. **For Test Expectations**: Update test expectations to account for gate capping when gates are expected to apply

## Conclusion

**The 2D Risk Matrix is working correctly.** All risk categories are properly assigned based on the Performance and Dependence scores. The failures are due to:
- Gate logic capping performance (Sabonis, Haliburton)
- Model predicting high performance when it shouldn't (KAT, Fultz later seasons)

The risk categorization itself is not the problem.

