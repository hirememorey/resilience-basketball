# Telescope Model Validation Summary

**Pass Rate**: 22/40 (55.0%)

## Detailed Test Results

| Player Name | Season | Subsidy | Potential | Predicted | Expected | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Shai Gilgeous-Alexander | 2018-19 | 0.578 | 4.60 | King | Bulldozer | ✅ PASS |
| Victor Oladipo | 2016-17 | 0.729 | 1.28 | Sniper | Bulldozer | ❌ FAIL |
| Jalen Brunson | 2020-21 | 0.522 | 6.56 | King | Bulldozer | ✅ PASS |
| Tyrese Maxey | 2021-22 | 0.356 | 4.96 | King | Bulldozer | ✅ PASS |
| Pascal Siakam | 2018-19 | 0.687 | 2.21 | Sniper | Bulldozer | ❌ FAIL |
| Jayson Tatum | 2017-18 | 0.800 | 1.65 | Sniper | Bulldozer | ❌ FAIL |
| Mikal Bridges | 2021-22 | 0.813 | 0.55 | Victim | Bulldozer | ❌ FAIL |
| Desmond Bane | 2021-22 | 0.698 | 0.89 | Victim | Bulldozer | ❌ FAIL |
| Nikola Jokić | 2015-16 | 0.609 | 1.02 | Sniper | King | ❌ FAIL |
| Nikola Jokić | 2016-17 | 0.409 | 2.00 | Sniper | King | ❌ FAIL |
| Nikola Jokić | 2017-18 | 0.364 | 2.52 | Bulldozer | King | ✅ PASS |
| Nikola Jokić | 2018-19 | 0.198 | 7.54 | King | King | ✅ PASS |
| Anthony Davis | 2015-16 | 0.260 | 4.23 | King | Bulldozer | ✅ PASS |
| Anthony Davis | 2016-17 | 0.130 | 4.83 | King | Bulldozer | ✅ PASS |
| Joel Embiid | 2016-17 | 0.310 | 0.52 | Victim | King | ❌ FAIL |
| Joel Embiid | 2017-18 | 0.000 | 5.78 | King | Bulldozer | ✅ PASS |
| Jordan Poole | 2021-22 | 0.522 | 1.31 | Sniper | Victim | ✅ PASS |
| Talen Horton-Tucker | 2020-21 | 0.536 | 2.57 | Bulldozer | Victim | ❌ FAIL |
| Christian Wood | 2020-21 | 0.610 | 1.32 | Sniper | Victim | ✅ PASS |
| D'Angelo Russell | 2018-19 | 0.129 | 6.25 | King | Victim | ❌ FAIL |
| Julius Randle | 2020-21 | 0.402 | 2.29 | Sniper | Victim | ✅ PASS |
| Ben Simmons | 2017-18 | 0.196 | 6.17 | King | Victim | ❌ FAIL |
| Ben Simmons | 2018-19 | 0.242 | 6.95 | King | Victim | ❌ FAIL |
| Ben Simmons | 2020-21 | 0.316 | 3.67 | Bulldozer | Victim | ❌ FAIL |
| Tyus Jones | 2021-22 | 0.367 | 2.07 | Sniper | Sniper | ✅ PASS |
| Domantas Sabonis | 2021-22 | 0.410 | 2.50 | Bulldozer | Victim | ✅ PASS |
| Tyrese Haliburton | 2021-22 | 0.256 | 7.00 | King | Bulldozer | ✅ PASS |
| Karl-Anthony Towns | 2015-16 | 0.380 | 1.76 | Sniper | Victim | ✅ PASS |
| Karl-Anthony Towns | 2016-17 | 0.090 | 5.98 | King | Victim | ❌ FAIL |
| Karl-Anthony Towns | 2017-18 | 0.340 | 1.30 | Sniper | Victim | ✅ PASS |
| Karl-Anthony Towns | 2018-19 | 0.090 | 7.01 | King | Victim | ❌ FAIL |
| Karl-Anthony Towns | 2019-20 | 0.400 | 0.46 | Victim | Victim | ✅ PASS |
| Karl-Anthony Towns | 2020-21 | 0.420 | 2.24 | Sniper | Victim | ✅ PASS |
| Markelle Fultz | 2017-18 | 0.347 | 3.37 | Bulldozer | Victim | ❌ FAIL |
| Markelle Fultz | 2018-19 | 0.529 | 2.95 | Bulldozer | Victim | ❌ FAIL |
| Markelle Fultz | 2019-20 | 0.378 | 2.94 | Bulldozer | Victim | ❌ FAIL |
| Markelle Fultz | 2020-21 | 0.322 | 2.29 | Sniper | Victim | ✅ PASS |
| Markelle Fultz | 2021-22 | 0.004 | 2.31 | Sniper | Victim | ✅ PASS |
| Markelle Fultz | 2022-23 | 0.356 | 2.22 | Sniper | Victim | ✅ PASS |
| Markelle Fultz | 2023-24 | 0.569 | 2.13 | Sniper | Victim | ✅ PASS |

## Identified Failures

- **Victor Oladipo (2016-17)**: Expected Bulldozer, but model predicted Sniper. (Potential: 1.28, Subsidy: 0.729)
- **Pascal Siakam (2018-19)**: Expected Bulldozer, but model predicted Sniper. (Potential: 2.21, Subsidy: 0.687)
- **Jayson Tatum (2017-18)**: Expected Bulldozer, but model predicted Sniper. (Potential: 1.65, Subsidy: 0.800)
- **Mikal Bridges (2021-22)**: Expected Bulldozer, but model predicted Victim. (Potential: 0.55, Subsidy: 0.813)
- **Desmond Bane (2021-22)**: Expected Bulldozer, but model predicted Victim. (Potential: 0.89, Subsidy: 0.698)
- **Nikola Jokić (2015-16)**: Expected King, but model predicted Sniper. (Potential: 1.02, Subsidy: 0.609)
- **Nikola Jokić (2016-17)**: Expected King, but model predicted Sniper. (Potential: 2.00, Subsidy: 0.409)
- **Joel Embiid (2016-17)**: Expected King, but model predicted Victim. (Potential: 0.52, Subsidy: 0.310)
- **Talen Horton-Tucker (2020-21)**: Expected Victim, but model predicted Bulldozer. (Potential: 2.57, Subsidy: 0.536)
- **D'Angelo Russell (2018-19)**: Expected Victim, but model predicted King. (Potential: 6.25, Subsidy: 0.129)
- **Ben Simmons (2017-18)**: Expected Victim, but model predicted King. (Potential: 6.17, Subsidy: 0.196)
- **Ben Simmons (2018-19)**: Expected Victim, but model predicted King. (Potential: 6.95, Subsidy: 0.242)
- **Ben Simmons (2020-21)**: Expected Victim, but model predicted Bulldozer. (Potential: 3.67, Subsidy: 0.316)
- **Karl-Anthony Towns (2016-17)**: Expected Victim, but model predicted King. (Potential: 5.98, Subsidy: 0.090)
- **Karl-Anthony Towns (2018-19)**: Expected Victim, but model predicted King. (Potential: 7.01, Subsidy: 0.090)
- **Markelle Fultz (2017-18)**: Expected Victim, but model predicted Bulldozer. (Potential: 3.37, Subsidy: 0.347)
- **Markelle Fultz (2018-19)**: Expected Victim, but model predicted Bulldozer. (Potential: 2.95, Subsidy: 0.529)
- **Markelle Fultz (2019-20)**: Expected Victim, but model predicted Bulldozer. (Potential: 2.94, Subsidy: 0.378)
