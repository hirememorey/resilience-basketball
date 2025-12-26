# Telescope Model Validation Summary

**Pass Rate**: 20/35 (57.1%)

## Detailed Test Results

| Player Name | Season | Subsidy | Potential | Predicted | Expected | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Shai Gilgeous-Alexander | 2018-19 | 0.578 | 4.09 | King | Bulldozer | ✅ PASS |
| Victor Oladipo | 2016-17 | 0.729 | 1.21 | Sniper | Bulldozer | ❌ FAIL |
| Jalen Brunson | 2020-21 | 0.522 | 6.82 | King | Bulldozer | ✅ PASS |
| Tyrese Maxey | 2021-22 | 0.356 | 5.61 | King | Bulldozer | ✅ PASS |
| Pascal Siakam | 2018-19 | 0.687 | 2.58 | Bulldozer | Bulldozer | ✅ PASS |
| Jayson Tatum | 2017-18 | 0.800 | 2.52 | Bulldozer | Bulldozer | ✅ PASS |
| Mikal Bridges | 2021-22 | 0.813 | 1.15 | Sniper | Bulldozer | ❌ FAIL |
| Desmond Bane | 2021-22 | 0.698 | 0.69 | Victim | Bulldozer | ❌ FAIL |
| Nikola Jokić | 2015-16 | 0.609 | 0.86 | Victim | King | ❌ FAIL |
| Nikola Jokić | 2016-17 | 0.409 | 2.26 | Sniper | King | ❌ FAIL |
| Nikola Jokić | 2017-18 | 0.364 | 3.90 | Bulldozer | King | ✅ PASS |
| Nikola Jokić | 2018-19 | 0.198 | 4.40 | King | King | ✅ PASS |
| Anthony Davis | 2015-16 | 0.260 | 1.78 | Sniper | Bulldozer | ❌ FAIL |
| Anthony Davis | 2016-17 | 0.130 | 4.98 | King | Bulldozer | ✅ PASS |
| Joel Embiid | 2016-17 | 0.310 | 0.71 | Victim | King | ❌ FAIL |
| Joel Embiid | 2017-18 | 0.000 | 6.13 | King | Bulldozer | ✅ PASS |
| Jordan Poole | 2021-22 | 0.522 | 0.64 | Victim | Victim | ✅ PASS |
| Talen Horton-Tucker | 2020-21 | - | - | - | - | ⚠️ MISSING |
| Christian Wood | 2020-21 | 0.610 | 0.74 | Victim | Victim | ✅ PASS |
| D'Angelo Russell | 2018-19 | 0.129 | 1.43 | Sniper | Victim | ✅ PASS |
| Julius Randle | 2020-21 | 0.402 | 4.46 | King | Victim | ❌ FAIL |
| Ben Simmons | 2017-18 | 0.196 | 4.71 | King | Victim | ❌ FAIL |
| Ben Simmons | 2018-19 | 0.242 | 4.32 | King | Victim | ❌ FAIL |
| Ben Simmons | 2020-21 | 0.316 | 4.43 | King | Victim | ❌ FAIL |
| Tyus Jones | 2021-22 | 0.367 | 2.24 | Sniper | Sniper | ✅ PASS |
| Domantas Sabonis | 2021-22 | 0.410 | 2.26 | Sniper | Victim | ✅ PASS |
| Tyrese Haliburton | 2021-22 | 0.256 | 3.64 | Bulldozer | Bulldozer | ✅ PASS |
| Karl-Anthony Towns | 2015-16 | 0.380 | 2.47 | Sniper | Victim | ✅ PASS |
| Karl-Anthony Towns | 2016-17 | 0.090 | 3.12 | Bulldozer | Victim | ❌ FAIL |
| Karl-Anthony Towns | 2017-18 | 0.340 | 1.83 | Sniper | Victim | ✅ PASS |
| Karl-Anthony Towns | 2018-19 | 0.090 | 4.95 | King | Victim | ❌ FAIL |
| Karl-Anthony Towns | 2019-20 | 0.400 | 1.09 | Sniper | Victim | ✅ PASS |
| Karl-Anthony Towns | 2020-21 | 0.420 | 2.51 | Bulldozer | Victim | ❌ FAIL |
| Markelle Fultz | 2017-18 | - | - | - | - | ⚠️ MISSING |
| Markelle Fultz | 2018-19 | - | - | - | - | ⚠️ MISSING |
| Markelle Fultz | 2019-20 | 0.378 | 3.70 | Bulldozer | Victim | ❌ FAIL |
| Markelle Fultz | 2020-21 | - | - | - | - | ⚠️ MISSING |
| Markelle Fultz | 2021-22 | - | - | - | - | ⚠️ MISSING |
| Markelle Fultz | 2022-23 | 0.356 | 2.43 | Sniper | Victim | ✅ PASS |
| Markelle Fultz | 2023-24 | 0.569 | 1.50 | Sniper | Victim | ✅ PASS |

## Identified Failures

- **Victor Oladipo (2016-17)**: Expected Bulldozer, but model predicted Sniper. (Potential: 1.21, Subsidy: 0.729)
- **Mikal Bridges (2021-22)**: Expected Bulldozer, but model predicted Sniper. (Potential: 1.15, Subsidy: 0.813)
- **Desmond Bane (2021-22)**: Expected Bulldozer, but model predicted Victim. (Potential: 0.69, Subsidy: 0.698)
- **Nikola Jokić (2015-16)**: Expected King, but model predicted Victim. (Potential: 0.86, Subsidy: 0.609)
- **Nikola Jokić (2016-17)**: Expected King, but model predicted Sniper. (Potential: 2.26, Subsidy: 0.409)
- **Anthony Davis (2015-16)**: Expected Bulldozer, but model predicted Sniper. (Potential: 1.78, Subsidy: 0.260)
- **Joel Embiid (2016-17)**: Expected King, but model predicted Victim. (Potential: 0.71, Subsidy: 0.310)
- **Julius Randle (2020-21)**: Expected Victim, but model predicted King. (Potential: 4.46, Subsidy: 0.402)
- **Ben Simmons (2017-18)**: Expected Victim, but model predicted King. (Potential: 4.71, Subsidy: 0.196)
- **Ben Simmons (2018-19)**: Expected Victim, but model predicted King. (Potential: 4.32, Subsidy: 0.242)
- **Ben Simmons (2020-21)**: Expected Victim, but model predicted King. (Potential: 4.43, Subsidy: 0.316)
- **Karl-Anthony Towns (2016-17)**: Expected Victim, but model predicted Bulldozer. (Potential: 3.12, Subsidy: 0.090)
- **Karl-Anthony Towns (2018-19)**: Expected Victim, but model predicted King. (Potential: 4.95, Subsidy: 0.090)
- **Karl-Anthony Towns (2020-21)**: Expected Victim, but model predicted Bulldozer. (Potential: 2.51, Subsidy: 0.420)
- **Markelle Fultz (2019-20)**: Expected Victim, but model predicted Bulldozer. (Potential: 3.70, Subsidy: 0.378)
