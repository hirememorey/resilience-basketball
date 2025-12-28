# Telescope Model Validation Summary

**Pass Rate**: 21/35 (60.0%)

## Detailed Test Results

| Player Name | Season | Subsidy | Potential | Predicted | Expected | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Shai Gilgeous-Alexander | 2018-19 | 0.578 | 1.91 | Sniper | Bulldozer | ❌ FAIL |
| Victor Oladipo | 2016-17 | 0.729 | 0.60 | Victim | Bulldozer | ❌ FAIL |
| Jalen Brunson | 2020-21 | 0.522 | 8.09 | King | Bulldozer | ✅ PASS |
| Tyrese Maxey | 2021-22 | 0.356 | 4.88 | King | Bulldozer | ✅ PASS |
| Pascal Siakam | 2018-19 | 0.687 | 0.84 | Victim | Bulldozer | ❌ FAIL |
| Jayson Tatum | 2017-18 | 0.800 | 4.92 | King | Bulldozer | ✅ PASS |
| Mikal Bridges | 2021-22 | 0.813 | 0.65 | Victim | Bulldozer | ❌ FAIL |
| Desmond Bane | 2021-22 | 0.698 | 0.80 | Victim | Bulldozer | ❌ FAIL |
| Nikola Jokić | 2015-16 | 0.609 | 1.61 | Sniper | King | ❌ FAIL |
| Nikola Jokić | 2016-17 | 0.409 | 3.63 | Bulldozer | King | ✅ PASS |
| Nikola Jokić | 2017-18 | 0.364 | 3.93 | Bulldozer | King | ✅ PASS |
| Nikola Jokić | 2018-19 | 0.198 | 3.51 | Bulldozer | King | ✅ PASS |
| Anthony Davis | 2015-16 | 0.260 | 0.02 | Victim | Bulldozer | ❌ FAIL |
| Anthony Davis | 2016-17 | 0.130 | 5.20 | King | Bulldozer | ✅ PASS |
| Joel Embiid | 2016-17 | 0.310 | 2.71 | Bulldozer | King | ✅ PASS |
| Joel Embiid | 2017-18 | 0.000 | 3.73 | Bulldozer | Bulldozer | ✅ PASS |
| Jordan Poole | 2021-22 | 0.522 | 2.40 | Sniper | Victim | ✅ PASS |
| Talen Horton-Tucker | 2020-21 | - | - | - | - | ⚠️ MISSING |
| Christian Wood | 2020-21 | 0.610 | 3.07 | Bulldozer | Victim | ❌ FAIL |
| D'Angelo Russell | 2018-19 | 0.129 | 1.88 | Sniper | Victim | ✅ PASS |
| Julius Randle | 2020-21 | 0.402 | 3.36 | Bulldozer | Victim | ❌ FAIL |
| Ben Simmons | 2017-18 | 0.196 | 1.88 | Sniper | Victim | ✅ PASS |
| Ben Simmons | 2018-19 | 0.242 | 2.48 | Sniper | Victim | ✅ PASS |
| Ben Simmons | 2020-21 | 0.316 | 2.28 | Sniper | Victim | ✅ PASS |
| Tyus Jones | 2021-22 | 0.367 | 0.48 | Victim | Sniper | ✅ PASS |
| Domantas Sabonis | 2021-22 | 0.410 | 2.28 | Sniper | Victim | ✅ PASS |
| Tyrese Haliburton | 2021-22 | 0.256 | 3.46 | Bulldozer | Bulldozer | ✅ PASS |
| Karl-Anthony Towns | 2015-16 | 0.380 | 1.23 | Sniper | Victim | ✅ PASS |
| Karl-Anthony Towns | 2016-17 | 0.090 | 3.71 | Bulldozer | Victim | ❌ FAIL |
| Karl-Anthony Towns | 2017-18 | 0.340 | 2.44 | Sniper | Victim | ✅ PASS |
| Karl-Anthony Towns | 2018-19 | 0.090 | 3.59 | Bulldozer | Victim | ❌ FAIL |
| Karl-Anthony Towns | 2019-20 | 0.400 | 2.82 | Bulldozer | Victim | ❌ FAIL |
| Karl-Anthony Towns | 2020-21 | 0.420 | 2.95 | Bulldozer | Victim | ❌ FAIL |
| Markelle Fultz | 2017-18 | - | - | - | - | ⚠️ MISSING |
| Markelle Fultz | 2018-19 | - | - | - | - | ⚠️ MISSING |
| Markelle Fultz | 2019-20 | 0.378 | 1.93 | Sniper | Victim | ✅ PASS |
| Markelle Fultz | 2020-21 | - | - | - | - | ⚠️ MISSING |
| Markelle Fultz | 2021-22 | - | - | - | - | ⚠️ MISSING |
| Markelle Fultz | 2022-23 | 0.356 | 4.11 | King | Victim | ❌ FAIL |
| Markelle Fultz | 2023-24 | 0.569 | 1.10 | Sniper | Victim | ✅ PASS |

## Identified Failures

- **Shai Gilgeous-Alexander (2018-19)**: Expected Bulldozer, but model predicted Sniper. (Potential: 1.91, Subsidy: 0.578)
- **Victor Oladipo (2016-17)**: Expected Bulldozer, but model predicted Victim. (Potential: 0.60, Subsidy: 0.729)
- **Pascal Siakam (2018-19)**: Expected Bulldozer, but model predicted Victim. (Potential: 0.84, Subsidy: 0.687)
- **Mikal Bridges (2021-22)**: Expected Bulldozer, but model predicted Victim. (Potential: 0.65, Subsidy: 0.813)
- **Desmond Bane (2021-22)**: Expected Bulldozer, but model predicted Victim. (Potential: 0.80, Subsidy: 0.698)
- **Nikola Jokić (2015-16)**: Expected King, but model predicted Sniper. (Potential: 1.61, Subsidy: 0.609)
- **Anthony Davis (2015-16)**: Expected Bulldozer, but model predicted Victim. (Potential: 0.02, Subsidy: 0.260)
- **Christian Wood (2020-21)**: Expected Victim, but model predicted Bulldozer. (Potential: 3.07, Subsidy: 0.610)
- **Julius Randle (2020-21)**: Expected Victim, but model predicted Bulldozer. (Potential: 3.36, Subsidy: 0.402)
- **Karl-Anthony Towns (2016-17)**: Expected Victim, but model predicted Bulldozer. (Potential: 3.71, Subsidy: 0.090)
- **Karl-Anthony Towns (2018-19)**: Expected Victim, but model predicted Bulldozer. (Potential: 3.59, Subsidy: 0.090)
- **Karl-Anthony Towns (2019-20)**: Expected Victim, but model predicted Bulldozer. (Potential: 2.82, Subsidy: 0.400)
- **Karl-Anthony Towns (2020-21)**: Expected Victim, but model predicted Bulldozer. (Potential: 2.95, Subsidy: 0.420)
- **Markelle Fultz (2022-23)**: Expected Victim, but model predicted King. (Potential: 4.11, Subsidy: 0.356)
