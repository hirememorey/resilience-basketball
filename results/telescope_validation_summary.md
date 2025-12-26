# Telescope Model Validation Summary

**Pass Rate**: 22/40 (55.0%)

## Detailed Test Results

| Player Name | Season | Subsidy | Potential | Predicted | Expected | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Shai Gilgeous-Alexander | 2018-19 | 0.578 | 6.27 | King | Bulldozer | ✅ PASS |
| Victor Oladipo | 2016-17 | 0.729 | 1.17 | Sniper | Bulldozer | ❌ FAIL |
| Jalen Brunson | 2020-21 | 0.522 | 6.74 | King | Bulldozer | ✅ PASS |
| Tyrese Maxey | 2021-22 | 0.356 | 5.05 | King | Bulldozer | ✅ PASS |
| Pascal Siakam | 2018-19 | 0.687 | 1.99 | Sniper | Bulldozer | ❌ FAIL |
| Jayson Tatum | 2017-18 | 0.800 | 1.87 | Sniper | Bulldozer | ❌ FAIL |
| Mikal Bridges | 2021-22 | 0.813 | 0.58 | Victim | Bulldozer | ❌ FAIL |
| Desmond Bane | 2021-22 | 0.698 | 2.04 | Sniper | Bulldozer | ❌ FAIL |
| Nikola Jokić | 2015-16 | 0.609 | 3.72 | Bulldozer | King | ✅ PASS |
| Nikola Jokić | 2016-17 | 0.409 | 3.07 | Bulldozer | King | ✅ PASS |
| Nikola Jokić | 2017-18 | 0.364 | 3.23 | Bulldozer | King | ✅ PASS |
| Nikola Jokić | 2018-19 | 0.198 | 7.99 | King | King | ✅ PASS |
| Anthony Davis | 2015-16 | 0.767 | 3.45 | Bulldozer | Bulldozer | ✅ PASS |
| Anthony Davis | 2016-17 | 0.744 | 4.61 | King | Bulldozer | ✅ PASS |
| Joel Embiid | 2016-17 | 0.613 | 3.47 | Bulldozer | King | ✅ PASS |
| Joel Embiid | 2017-18 | 0.596 | 5.04 | King | Bulldozer | ✅ PASS |
| Jordan Poole | 2021-22 | 0.522 | 3.23 | Bulldozer | Victim | ✅ PASS |
| Talen Horton-Tucker | 2020-21 | 0.536 | 3.05 | Bulldozer | Victim | ❌ FAIL |
| Christian Wood | 2020-21 | 0.756 | 2.40 | Sniper | Victim | ✅ PASS |
| D'Angelo Russell | 2018-19 | 0.129 | 3.83 | Bulldozer | Victim | ❌ FAIL |
| Julius Randle | 2020-21 | 0.402 | 2.88 | Bulldozer | Victim | ❌ FAIL |
| Ben Simmons | 2017-18 | 0.196 | 5.05 | King | Victim | ❌ FAIL |
| Ben Simmons | 2018-19 | 0.242 | 4.48 | King | Victim | ❌ FAIL |
| Ben Simmons | 2020-21 | 0.316 | 2.62 | Bulldozer | Victim | ❌ FAIL |
| Tyus Jones | 2021-22 | 0.367 | 2.07 | Sniper | Sniper | ✅ PASS |
| Domantas Sabonis | 2021-22 | 0.469 | 3.13 | Bulldozer | Victim | ✅ PASS |
| Tyrese Haliburton | 2021-22 | 0.256 | 5.38 | King | Bulldozer | ✅ PASS |
| Karl-Anthony Towns | 2015-16 | 0.760 | 0.91 | Victim | Victim | ✅ PASS |
| Karl-Anthony Towns | 2016-17 | 0.718 | 3.49 | Bulldozer | Victim | ❌ FAIL |
| Karl-Anthony Towns | 2017-18 | 0.767 | 1.02 | Sniper | Victim | ✅ PASS |
| Karl-Anthony Towns | 2018-19 | 0.624 | 3.29 | Bulldozer | Victim | ❌ FAIL |
| Karl-Anthony Towns | 2019-20 | 0.533 | 2.27 | Sniper | Victim | ✅ PASS |
| Karl-Anthony Towns | 2020-21 | 0.520 | 2.56 | Bulldozer | Victim | ❌ FAIL |
| Markelle Fultz | 2017-18 | 0.347 | 4.58 | King | Victim | ❌ FAIL |
| Markelle Fultz | 2018-19 | 0.529 | 3.36 | Bulldozer | Victim | ❌ FAIL |
| Markelle Fultz | 2019-20 | 0.378 | 2.59 | Bulldozer | Victim | ❌ FAIL |
| Markelle Fultz | 2020-21 | 0.322 | 1.78 | Sniper | Victim | ✅ PASS |
| Markelle Fultz | 2021-22 | 0.004 | 2.55 | Bulldozer | Victim | ❌ FAIL |
| Markelle Fultz | 2022-23 | 0.356 | 2.31 | Sniper | Victim | ✅ PASS |
| Markelle Fultz | 2023-24 | 0.569 | 2.36 | Sniper | Victim | ✅ PASS |

## Identified Failures

- **Victor Oladipo (2016-17)**: Expected Bulldozer, but model predicted Sniper. (Potential: 1.17, Subsidy: 0.729)
- **Pascal Siakam (2018-19)**: Expected Bulldozer, but model predicted Sniper. (Potential: 1.99, Subsidy: 0.687)
- **Jayson Tatum (2017-18)**: Expected Bulldozer, but model predicted Sniper. (Potential: 1.87, Subsidy: 0.800)
- **Mikal Bridges (2021-22)**: Expected Bulldozer, but model predicted Victim. (Potential: 0.58, Subsidy: 0.813)
- **Desmond Bane (2021-22)**: Expected Bulldozer, but model predicted Sniper. (Potential: 2.04, Subsidy: 0.698)
- **Talen Horton-Tucker (2020-21)**: Expected Victim, but model predicted Bulldozer. (Potential: 3.05, Subsidy: 0.536)
- **D'Angelo Russell (2018-19)**: Expected Victim, but model predicted Bulldozer. (Potential: 3.83, Subsidy: 0.129)
- **Julius Randle (2020-21)**: Expected Victim, but model predicted Bulldozer. (Potential: 2.88, Subsidy: 0.402)
- **Ben Simmons (2017-18)**: Expected Victim, but model predicted King. (Potential: 5.05, Subsidy: 0.196)
- **Ben Simmons (2018-19)**: Expected Victim, but model predicted King. (Potential: 4.48, Subsidy: 0.242)
- **Ben Simmons (2020-21)**: Expected Victim, but model predicted Bulldozer. (Potential: 2.62, Subsidy: 0.316)
- **Karl-Anthony Towns (2016-17)**: Expected Victim, but model predicted Bulldozer. (Potential: 3.49, Subsidy: 0.718)
- **Karl-Anthony Towns (2018-19)**: Expected Victim, but model predicted Bulldozer. (Potential: 3.29, Subsidy: 0.624)
- **Karl-Anthony Towns (2020-21)**: Expected Victim, but model predicted Bulldozer. (Potential: 2.56, Subsidy: 0.520)
- **Markelle Fultz (2017-18)**: Expected Victim, but model predicted King. (Potential: 4.58, Subsidy: 0.347)
- **Markelle Fultz (2018-19)**: Expected Victim, but model predicted Bulldozer. (Potential: 3.36, Subsidy: 0.529)
- **Markelle Fultz (2019-20)**: Expected Victim, but model predicted Bulldozer. (Potential: 2.59, Subsidy: 0.378)
- **Markelle Fultz (2021-22)**: Expected Victim, but model predicted Bulldozer. (Potential: 2.55, Subsidy: 0.004)
