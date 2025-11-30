
---

### Phase 6: The API Reality Check (Successful Pivot)

**What:** The initial plan relied on the `playbyplayv2` endpoint for granular playoff data.
**Issue:** "First Principles" diagnostics revealed `playbyplayv2` returns empty responses for historical games, and `leaguedashteamstats` "Defense" measure type lacks key columns.
**Solution:** Pivoted to `playergamelogs` (merged Base + Advanced) for robust per-game data.
**Result:**
- ✅ Successfully collected 100% of playoff data for 2018-19, 2022-23, 2023-24.
- ✅ Verified pipeline end-to-end with "Data Skewer" (Jokic 2023).
- ✅ Models successfully trained (R² > 0.5 for PPG/AST%).
- ✅ Identified small-sample bias (Reggie Jackson 150% TS) as next challenge.

**Lesson:** Validate external dependencies *empirically* before writing full application logic. "Trust but verify" saved hours of debugging.
