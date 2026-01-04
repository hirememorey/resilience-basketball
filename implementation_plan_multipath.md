# Multi-Path Framework Implementation Plan
## NBA Playoff Resilience Engine — Component 1 Refactor

**Version:** 1.1
**Date:** January 3, 2026
**Status:** 🚧 **In Progress - Phase 3 (Principled Adjustments)**

---

## Executive Summary

### The Problem

The current Self-Created Shot Score (Component 1, 30% of CII) measures only ISO creation ability. This causes systematic misclassification of elite players whose creation manifests through other modes:

| Player | Season | Current CII | Expected | Root Cause |
|--------|--------|-------------|----------|------------|
| LeBron James | 2015-16 | 68.8 | 78+ | Drive-and-kick creation not captured |
| Stephen Curry | 2016-17 | 68.7 | 78+ | Off-ball gravity not captured |
| Giannis Antetokounmpo | 2020-21 | 56.5 | 78+ | Rim pressure/drive creation not captured |

### The Solution

Refactor Component 1 to evaluate players across multiple creation pathways. Take the maximum score across all pathways, with bonuses for multi-modal creation ability.

### Expected Outcome

After implementation, all sanity check players should classify correctly:
- LeBron 2016: CII 78+ (Franchise Engine)
- Curry 2017: CII 78+ (Franchise Engine)
- Giannis 2021: CII 78+ (Franchise Engine)
- Existing correct classifications (Jokić, Kawhi, Simmons) should remain correct

---

## Progress Tracker

### Phase 0: Preparation ✅
- [x] Create clean branch `refactor/principled-multipath`
- [x] Document current state parameters (`docs/CURRENT_STATE_AUDIT.md`)
- [x] Run baseline decomposition (`scripts/decompose_scores.py`)

### Phase 1: Strip to Core ✅
- [x] Create bare path modules (ISO, Drive-Kick, Post Hub, Gravity)
- [x] Create bare CII calculator (no gates)
- [x] Run bare validation (`scripts/run_bare_validation.py`)
- [x] **Result**: 41.7% pass rate (baseline established)

### Phase 2: Diagnostic Analysis ✅
- [x] Diagnose failures for LeBron, Curry, Giannis, Jokić, Durant, Ja, Mitchell
- [x] Create diagnosis documents in `docs/failure_diagnosis/`
- [x] Categorize failures (`docs/failure_diagnosis/CATEGORIZATION_SUMMARY.md`)
- [x] **Key Findings**: 
    - Jokić fails C3 (Difficulty) because it lacks Hub path logic.
    - Drive-Kick path formula underestimates volume/outcomes.
    - Gravity path requires better proxies than raw screen assists.
    - Missing data for Ja Morant/Mitchell (2021-22).

### Phase 3: Principled Adjustments 🚧 (Current)
- [ ] **Fix 3.1 (Critical)**: Refactor C3 (Difficulty Embrace) to include Hub path logic (Fixes Jokić).
- [ ] **Fix 3.2 (High)**: Revise Drive-Kick path formula weights/thresholds (Fixes LeBron, Giannis).
- [ ] **Fix 3.3 (High)**: Revise Gravity path formula and data inputs (Fixes Curry, Giannis).
- [ ] **Fix 3.4 (Low)**: Fine-tune ISO path thresholds (Fixes Durant).
- [ ] **Fix 3.5 (Medium)**: Investigate data pipeline for missing 2021-22 tracking data.

### Phase 4: Gates (If Necessary)
- [ ] Only implement categorically justified gates (e.g., Simmons Aggression Gate).

### Phase 5: Final Validation
- [ ] Run full validation suite.
- [ ] Document final model specification.

---

## Architecture Overview

### Current Architecture

```
CII = (Self-Created × 0.30) + (Pressure × 0.25) + (Difficulty × 0.20) + (Defense × 0.15) + (Force × 0.10)
```

**Component 1 (Self-Created Shot Score)** currently uses a single-path calculation based on:
- `pct_uast_fgm` (unassisted field goal percentage)
- `pull_up_fga` (pull-up field goal attempts)
- True Shooting percentage
- Weighted touch production

This single path rewards ISO creation but penalizes drive-and-kick engines (LeBron) and gravity engines (Curry).

### New Architecture

**Component 1 (Self-Created Shot Score)** will evaluate four pathways and take the maximum:

```
Self-Created Score = max(Path_A, Path_B, Path_C, Path_D) + Multi-Modal Bonus
```

| Path | Name | Primary Archetype | Example Players |
|------|------|-------------------|-----------------|
| Path A | ISO Creator | Isolation scorers | Harden, Trae, Dame, Luka |
| Path B | Drive-and-Kick Engine | Penetration + passing | LeBron, Giannis, Westbrook |
| Path C | Post Hub | Post-up + passing | Jokić, Embiid, Sabonis |
| Path D | Gravity Engine | Off-ball movement | Curry, Klay (future phase) |

**Components 2-5 remain unchanged in Phase 1.**

---

## Data Requirements

### Required Data Sources

| Source | Data Type | Access Method | Priority |
|--------|-----------|---------------|----------|
| NBA.com/stats | Player tracking data | API or scraping | Critical |
| Basketball-Reference | Traditional stats | API (sportsipy) or scraping | Critical |
| Existing dataset | `predictive_dataset_with_friction.csv` | Local file | Critical |

### New Fields Required (Phase 1: Drive-and-Kick)

These fields must be added to the player-season dataset:

| Field Name | Description | Source | Units |
|------------|-------------|--------|-------|
| `drives_per_game` | Average drives per game | NBA.com tracking | count |
| `drive_pts` | Points scored on drives | NBA.com tracking | count |
| `drive_ast` | Assists from drives | NBA.com tracking | count |
| `drive_fga` | Field goal attempts on drives | NBA.com tracking | count |
| `drive_fgm` | Field goals made on drives | NBA.com tracking | count |
| `drive_tov` | Turnovers on drives | NBA.com tracking | count |
| `drive_pf` | Fouls drawn on drives | NBA.com tracking | count |
| `potential_ast` | Passes leading to shots (made or missed) | NBA.com tracking | count |
| `ast_adj` | Adjusted assists (assist opportunities created) | NBA.com tracking | count |
| `passes_made` | Total passes made | NBA.com tracking | count |
| `touches` | Total touches | NBA.com tracking | count |
| `time_of_poss` | Time of possession (seconds) | NBA.com tracking | seconds |
| `pts_created` | Points created (own points + assisted points) | Calculated | count |

### New Fields Required (Phase 2: Gravity)

| Field Name | Description | Source | Units |
|------------|-------------|--------|-------|
| `screen_ast` | Screen assists per game | NBA.com tracking | count |
| `screen_ast_pts` | Points from screen assists | NBA.com tracking | count |
| `deflections` | Deflections per game | NBA.com tracking | count |
| `contested_shots` | Contested shots per game | NBA.com tracking | count |
| `off_ball_touches` | Touches without dribble | NBA.com tracking | count |
| `catch_shoot_fga` | Catch-and-shoot attempts | NBA.com tracking | count |
| `catch_shoot_fg3a` | Catch-and-shoot 3PT attempts | NBA.com tracking | count |
| `catch_shoot_fg_pct` | Catch-and-shoot FG% | NBA.com tracking | percentage |
| `pull_up_pts` | Points from pull-up shots | NBA.com tracking | count |
| `paint_touches` | Touches in the paint | NBA.com tracking | count |

### Data Collection Script Structure

```
src/nba_data/scripts/
├── collect_tracking_data.py      # NEW: Fetch NBA.com tracking data
├── merge_tracking_features.py    # NEW: Merge tracking data with existing dataset
└── validate_tracking_data.py     # NEW: Validate data quality
```

**API Endpoint for NBA.com Tracking Data:**
```
https://stats.nba.com/stats/leaguedashptstats
Parameters:
  - Season: "2015-16" through "2024-25"
  - SeasonType: "Regular Season"
  - PerMode: "PerGame"
  - PlayerOrTeam: "Player"
  - PtMeasureType: "Drives" | "Passing" | "Touches" | "CatchShoot" | "PullUpShot"
```

---

## Path Implementations

### Path A: ISO Creator (EXISTING — Minor Refactor)

**Location:** `src/nba_data/phase2_creation_independence/index/self_created.py`

**Current Implementation:**
The existing `calculate_self_created_score()` function serves as Path A.

**Required Changes:**
1. Rename function to `calculate_iso_path_score()`
2. Ensure it returns a 0-100 score
3. Expose as standalone function for multi-path integration

**Pseudocode:**

```python
def calculate_iso_path_score(player_data: dict) -> float:
    """
    Calculate ISO Creator path score.
    
    Measures ability to create isolation scoring opportunities:
    - Unassisted field goal percentage (self-generated shots)
    - Pull-up shooting volume (creation off the dribble)
    - True shooting efficiency on self-created shots
    
    Args:
        player_data: Dictionary containing player-season statistics
        
    Returns:
        Score from 0-100, where:
        - 80+ = Elite ISO creator (Harden, Trae, Luka)
        - 60-80 = Good ISO scorer (Mitchell, Booker)
        - 40-60 = Average (role players with some ISO ability)
        - <40 = Limited ISO creation (catch-and-shoot players)
    """
    
    # Component 1: Unassisted FG% (0-100)
    # Measures what percentage of made FGs were unassisted
    uast_pct = player_data.get('pct_uast_fgm', 0)
    uast_score = min(uast_pct * 100, 100)
    
    # Component 2: Pull-up volume (0-100)
    # Normalize to elite threshold of 10 pull-up FGA per game
    pull_up_fga = player_data.get('pull_up_fga', 0)
    pull_up_score = min((pull_up_fga / 10.0) * 100, 100)
    
    # Component 3: ISO efficiency (0-100)
    # Use TS% as proxy, normalize to 55% baseline
    ts_pct = player_data.get('ts_pct', 0.55)
    efficiency_score = min(((ts_pct - 0.45) / 0.25) * 100, 100)
    efficiency_score = max(efficiency_score, 0)
    
    # Component 4: Usage in ISO-heavy situations (0-100)
    # High usage + high unassisted = true ISO creator
    usg_pct = player_data.get('usg_pct', 0.20)
    usage_score = min((usg_pct / 0.30) * 100, 100)
    
    # Weighted combination
    iso_score = (
        uast_score * 0.35 +
        pull_up_score * 0.30 +
        efficiency_score * 0.20 +
        usage_score * 0.15
    )
    
    return round(iso_score, 1)
```

**Validation Targets:**

| Player | Season | Expected ISO Path Score |
|--------|--------|------------------------|
| James Harden | 2018-19 | 90+ |
| Trae Young | 2019-20 | 85+ |
| Damian Lillard | 2019-20 | 85+ |
| Zach LaVine | 2021-22 | 65-75 |
| Ben Simmons | 2020-21 | <40 |

---

### Path B: Drive-and-Kick Engine (NEW — Phase 1 Priority)

**Location:** `src/nba_data/phase2_creation_independence/index/self_created.py`

**Purpose:**
Capture creation value from players who generate offense through penetration and passing, rather than isolation scoring.

**Key Insight:**
Drive-and-kick players like LeBron create massive value that doesn't show up in "unassisted FG%" because:
1. Their own scores are often "assisted" (after a teammate probes first)
2. Their primary value is creating shots for others
3. Rim pressure forces defensive rotations that create open shots

**Pseudocode:**

```python
def calculate_drive_kick_path_score(player_data: dict) -> float:
    """
    Calculate Drive-and-Kick Engine path score.
    
    Measures ability to create offense through penetration and passing:
    - Drive volume (how often they attack)
    - Drive outcomes (points + assists per drive)
    - Assist creation (potential assists, not just converted)
    - Rim pressure (drives that force defensive rotations)
    
    Args:
        player_data: Dictionary containing player-season statistics
        
    Returns:
        Score from 0-100, where:
        - 80+ = Elite drive-and-kick engine (LeBron, Giannis)
        - 60-80 = Good penetrator (Ja Morant, De'Aaron Fox)
        - 40-60 = Average driver
        - <40 = Limited penetration ability
    """
    
    # =====================
    # Component 1: Drive Volume (0-100)
    # =====================
    # How often does this player attack the paint?
    # Elite threshold: 15 drives per game (LeBron, Giannis peak)
    # Good threshold: 10 drives per game
    # Average: 5 drives per game
    
    drives_per_game = player_data.get('drives_per_game', 0)
    drive_volume_score = min((drives_per_game / 15.0) * 100, 100)
    
    # =====================
    # Component 2: Drive Outcome Efficiency (0-100)
    # =====================
    # Points + Assists generated per drive
    # Elite threshold: 1.5 points created per drive
    # This captures both scoring AND passing value from drives
    
    drive_pts = player_data.get('drive_pts', 0)
    drive_ast = player_data.get('drive_ast', 0)
    drives_total = player_data.get('drives_per_game', 0.01) * 82  # Approximate total drives
    
    # Points created per drive (own points + estimated assisted points)
    # Assume each assist = ~2.5 points
    if drives_per_game > 0:
        pts_created_per_drive = (drive_pts + (drive_ast * 2.5)) / (drives_per_game * 82) * 82
        # Simplify to per-game
        pts_created_per_drive = (drive_pts + (drive_ast * 2.5)) / max(drives_per_game, 0.1)
    else:
        pts_created_per_drive = 0
    
    drive_efficiency_score = min((pts_created_per_drive / 1.5) * 100, 100)
    
    # =====================
    # Component 3: Assist Creation Rate (0-100)
    # =====================
    # Potential assists / touches = creation rate
    # This measures how often their passes lead to shot opportunities
    # (regardless of whether teammate converts)
    
    potential_ast = player_data.get('potential_ast', 0)
    touches = player_data.get('touches', 1)
    
    assist_creation_rate = potential_ast / max(touches, 1)
    # Elite threshold: 25% of touches lead to potential assists (LeBron, Jokic, CP3)
    assist_creation_score = min((assist_creation_rate / 0.25) * 100, 100)
    
    # =====================
    # Component 4: Rim Pressure (0-100)
    # =====================
    # Drives that result in shots at rim OR passes (forcing help defense)
    # This captures "gravity" from driving
    
    drive_fga = player_data.get('drive_fga', 0)
    drive_tov = player_data.get('drive_tov', 0)
    drive_pf = player_data.get('drive_pf', 0)  # Fouls drawn
    
    # Successful drive outcomes: FGA + AST + Fouls Drawn
    # Failed outcomes: TOV
    if drives_per_game > 0:
        successful_drive_rate = (drive_fga + drive_ast + drive_pf) / (drives_per_game + 0.01)
        # Normalize: elite is ~0.9 (90% of drives lead to good outcome)
        rim_pressure_score = min((successful_drive_rate / 0.90) * 100, 100)
    else:
        rim_pressure_score = 0
    
    # =====================
    # Component 5: Creation Independence (0-100)
    # =====================
    # Time of possession relative to touches
    # High time = they're creating, not just catching and passing
    
    time_of_poss = player_data.get('time_of_poss', 0)
    touches = player_data.get('touches', 1)
    
    time_per_touch = time_of_poss / max(touches, 1)
    # Elite threshold: 4+ seconds per touch (ball in hands, creating)
    creation_independence_score = min((time_per_touch / 4.0) * 100, 100)
    
    # =====================
    # Final Score: Weighted Combination
    # =====================
    drive_kick_score = (
        drive_volume_score * 0.25 +          # Volume matters
        drive_efficiency_score * 0.25 +       # Outcomes matter
        assist_creation_score * 0.25 +        # Passing creation matters
        rim_pressure_score * 0.15 +           # Forcing help matters
        creation_independence_score * 0.10    # Time on ball matters
    )
    
    return round(drive_kick_score, 1)
```

**Validation Targets:**

| Player | Season | Expected Drive-Kick Score | Notes |
|--------|--------|---------------------------|-------|
| LeBron James | 2015-16 | 85+ | Elite drives + elite assist creation |
| Giannis Antetokounmpo | 2020-21 | 85+ | Elite drives + rim pressure |
| Russell Westbrook | 2016-17 | 80+ | High volume drives + assists |
| Ja Morant | 2021-22 | 75-85 | High drives, good assist creation |
| De'Aaron Fox | 2020-21 | 70-80 | High drives, moderate assist creation |
| James Harden | 2018-19 | 75-85 | Also elite here (multi-modal) |
| Ben Simmons | 2020-21 | 50-65 | Drives but limited outcomes |
| Zach LaVine | 2021-22 | 40-55 | Moderate drives, low assist creation |

---

### Path C: Post Hub (EXISTING — Minor Refactor)

**Location:** `src/nba_data/phase2_creation_independence/index/self_created.py`

**Current Implementation:**
The existing "Hub Path" in `calculate_self_created_score()` handles this.

**Required Changes:**
1. Extract Hub Path logic into standalone function `calculate_post_hub_path_score()`
2. Ensure it returns 0-100 score
3. Expose for multi-path integration

**Pseudocode:**

```python
def calculate_post_hub_path_score(player_data: dict) -> float:
    """
    Calculate Post Hub path score.
    
    Measures ability to create offense from post position through:
    - Post touch volume
    - Efficiency from post
    - Passing out of post (assist creation)
    - Defensive attention drawn in post
    
    Args:
        player_data: Dictionary containing player-season statistics
        
    Returns:
        Score from 0-100, where:
        - 80+ = Elite post hub (Jokić, peak Embiid)
        - 60-80 = Good post player (Sabonis, Bam)
        - 40-60 = Average post player
        - <40 = Limited post game
    """
    
    # Component 1: Post touch volume (0-100)
    # Elite threshold: 8+ touches in post per game
    post_touches = player_data.get('post_touches', player_data.get('touches', 0) * 0.3)
    post_volume_score = min((post_touches / 8.0) * 100, 100)
    
    # Component 2: Post efficiency (0-100)
    # Use TS% as proxy, with higher threshold for post players
    ts_pct = player_data.get('ts_pct', 0.55)
    # Post players need 60%+ TS to be elite creators
    efficiency_score = min(((ts_pct - 0.50) / 0.20) * 100, 100)
    efficiency_score = max(efficiency_score, 0)
    
    # Component 3: Assist rate (0-100)
    # Post hubs create through passing
    ast_pct = player_data.get('ast_pct', 0.15)
    # Elite threshold: 30% assist rate (Jokić level)
    assist_score = min((ast_pct / 0.30) * 100, 100)
    
    # Component 4: Usage from post (0-100)
    # High usage + high efficiency = true hub
    usg_pct = player_data.get('usg_pct', 0.20)
    usage_score = min((usg_pct / 0.28) * 100, 100)
    
    # Gate: Must have minimum efficiency to qualify
    # This prevents inefficient post players from scoring high
    if ts_pct < 0.55:
        efficiency_gate = ts_pct / 0.55
    else:
        efficiency_gate = 1.0
    
    # Weighted combination with efficiency gate
    post_hub_score = (
        post_volume_score * 0.25 +
        efficiency_score * 0.30 +
        assist_score * 0.30 +
        usage_score * 0.15
    ) * efficiency_gate
    
    return round(post_hub_score, 1)
```

**Validation Targets:**

| Player | Season | Expected Post Hub Score |
|--------|--------|------------------------|
| Nikola Jokić | 2022-23 | 90+ |
| Joel Embiid | 2022-23 | 80-90 |
| Domantas Sabonis | 2022-23 | 70-80 |
| Bam Adebayo | 2022-23 | 60-75 |
| Karl-Anthony Towns | 2019-20 | 55-70 |

---

### Path D: Gravity Engine (NEW — Phase 2)

**Location:** `src/nba_data/phase2_creation_independence/index/self_created.py`

**Purpose:**
Capture creation value from players who generate offense through off-ball movement and spacing, even when their shots are "assisted."

**Key Insight:**
Gravity players like Curry create massive value that doesn't show up in traditional creation metrics because:
1. Their movement forces defensive rotations before they touch the ball
2. Their shots are often "assisted" (catch-and-shoot) but the space was self-created through movement
3. Screen assists and off-ball actions generate value for teammates

**Data Challenge:**
True gravity measurement requires Second Spectrum tracking data (defender distance, off-ball movement tracking) which is proprietary and expensive. We use proxy metrics.

**Pseudocode:**

```python
def calculate_gravity_path_score(player_data: dict) -> float:
    """
    Calculate Gravity Engine path score.
    
    Measures ability to create offense through off-ball movement and spacing:
    - Screen assist volume and quality
    - Catch-and-shoot efficiency (suggests good movement to get open)
    - Off-ball touch efficiency
    - Spacing impact (proxy through on/off metrics if available)
    
    Args:
        player_data: Dictionary containing player-season statistics
        
    Returns:
        Score from 0-100, where:
        - 80+ = Elite gravity player (Curry, prime Klay)
        - 60-80 = Good off-ball threat (Duncan Robinson, Korver)
        - 40-60 = Average movement
        - <40 = Limited off-ball value
    """
    
    # =====================
    # Component 1: Screen Assist Value (0-100)
    # =====================
    # Points generated through screen assists
    # Elite threshold: 4+ screen assists per game (Curry, Draymond)
    
    screen_ast = player_data.get('screen_ast', 0)
    screen_ast_pts = player_data.get('screen_ast_pts', screen_ast * 2.5)
    
    screen_value_score = min((screen_ast / 4.0) * 100, 100)
    
    # =====================
    # Component 2: Catch-and-Shoot Efficiency (0-100)
    # =====================
    # High efficiency on assisted shots suggests good movement to get open
    # Elite: 42%+ on catch-and-shoot 3s
    
    catch_shoot_fg3_pct = player_data.get('catch_shoot_fg3_pct', 0.36)
    catch_shoot_efficiency = min(((catch_shoot_fg3_pct - 0.30) / 0.15) * 100, 100)
    catch_shoot_efficiency = max(catch_shoot_efficiency, 0)
    
    # =====================
    # Component 3: Off-Ball Volume (0-100)
    # =====================
    # Catch-and-shoot attempts as percentage of total FGA
    # High = player moves well, gets open looks
    
    catch_shoot_fga = player_data.get('catch_shoot_fga', 0)
    total_fga = player_data.get('fga', 1)
    
    offball_rate = catch_shoot_fga / max(total_fga, 1)
    # For gravity players, 50%+ of shots are catch-and-shoot
    offball_volume_score = min((offball_rate / 0.50) * 100, 100)
    
    # =====================
    # Component 4: Pull-Up Threat (0-100)
    # =====================
    # Gravity requires BOTH off-ball AND on-ball threat
    # Without pull-up ability, defense doesn't respect you off screens
    
    pull_up_pts = player_data.get('pull_up_pts', 0)
    pull_up_fga = player_data.get('pull_up_fga', 0)
    
    if pull_up_fga > 0:
        pull_up_efficiency = pull_up_pts / pull_up_fga
        pull_up_threat_score = min((pull_up_efficiency / 1.2) * 100, 100)
    else:
        pull_up_threat_score = 0
    
    # =====================
    # Component 5: Movement Proxy (0-100)
    # =====================
    # Distance traveled per game (if available) or proxy through paint touches
    # More movement = more gravity
    
    # If we have distance data:
    dist_miles = player_data.get('dist_miles', None)
    if dist_miles is not None:
        movement_score = min((dist_miles / 2.8) * 100, 100)  # Elite: 2.8+ miles/game
    else:
        # Proxy: cuts per game (if available)
        cuts = player_data.get('cuts', 0)
        movement_score = min((cuts / 4.0) * 100, 100)  # Elite: 4+ cuts/game
    
    # =====================
    # Gate: Must have shooting threat
    # =====================
    # Gravity only works if defense respects your shot
    ts_pct = player_data.get('ts_pct', 0.55)
    three_pt_rate = player_data.get('fg3a_rate', 0.30)
    
    if ts_pct < 0.55 or three_pt_rate < 0.25:
        shooting_gate = 0.5  # Penalize non-shooters
    else:
        shooting_gate = 1.0
    
    # =====================
    # Final Score: Weighted Combination
    # =====================
    gravity_score = (
        screen_value_score * 0.20 +
        catch_shoot_efficiency * 0.25 +
        offball_volume_score * 0.20 +
        pull_up_threat_score * 0.20 +
        movement_score * 0.15
    ) * shooting_gate
    
    return round(gravity_score, 1)
```

**Validation Targets:**

| Player | Season | Expected Gravity Score |
|--------|--------|----------------------|
| Stephen Curry | 2016-17 | 85+ |
| Klay Thompson | 2018-19 | 80+ |
| Duncan Robinson | 2019-20 | 70-80 |
| Kyle Korver | 2014-15 | 65-75 |
| JJ Redick | 2017-18 | 65-75 |
| LeBron James | 2015-16 | 40-55 (not his mode) |
| Ben Simmons | 2020-21 | <30 (no shooting threat) |

---

## Multi-Path Integration

### Combined Self-Created Score

**Location:** `src/nba_data/phase2_creation_independence/index/self_created.py`

**New Main Function:**

```python
def calculate_self_created_score(player_data: dict, debug: bool = False) -> dict:
    """
    Calculate multi-path Self-Created Shot Score.
    
    Evaluates player across all creation pathways and returns:
    - Maximum path score (primary creation mode)
    - Multi-modal bonus (for players elite at multiple modes)
    - Final composite score
    
    Args:
        player_data: Dictionary containing player-season statistics
        debug: If True, return detailed breakdown
        
    Returns:
        Dictionary containing:
        - 'self_created_score': Final 0-100 score for CII calculation
        - 'iso_path': ISO Creator path score
        - 'drive_kick_path': Drive-and-Kick path score
        - 'post_hub_path': Post Hub path score
        - 'gravity_path': Gravity Engine path score
        - 'primary_mode': String indicating dominant creation mode
        - 'multi_modal_bonus': Bonus points for multiple elite paths
    """
    
    # Calculate all path scores
    iso_score = calculate_iso_path_score(player_data)
    drive_kick_score = calculate_drive_kick_path_score(player_data)
    post_hub_score = calculate_post_hub_path_score(player_data)
    gravity_score = calculate_gravity_path_score(player_data)
    
    # Collect all scores
    path_scores = {
        'iso': iso_score,
        'drive_kick': drive_kick_score,
        'post_hub': post_hub_score,
        'gravity': gravity_score
    }
    
    # Find maximum (primary creation mode)
    primary_mode = max(path_scores, key=path_scores.get)
    base_score = path_scores[primary_mode]
    
    # Calculate multi-modal bonus
    # Elite threshold: 75+ on a path
    elite_threshold = 75.0
    elite_paths = [name for name, score in path_scores.items() if score >= elite_threshold]
    
    if len(elite_paths) >= 3:
        multi_modal_bonus = 15.0  # Rare: elite at 3+ modes (prime LeBron)
    elif len(elite_paths) == 2:
        multi_modal_bonus = 8.0   # Very good: elite at 2 modes (Harden, Luka)
    elif len(elite_paths) == 1:
        multi_modal_bonus = 0.0   # Standard: elite at 1 mode
    else:
        multi_modal_bonus = 0.0   # No elite paths
    
    # Secondary mode bonus (for players good but not elite at second mode)
    # Good threshold: 60+ on a path
    good_threshold = 60.0
    sorted_scores = sorted(path_scores.values(), reverse=True)
    if len(sorted_scores) >= 2 and sorted_scores[1] >= good_threshold:
        secondary_bonus = 3.0
    else:
        secondary_bonus = 0.0
    
    # Calculate final score
    final_score = min(base_score + multi_modal_bonus + secondary_bonus, 100.0)
    
    result = {
        'self_created_score': round(final_score, 1),
        'iso_path': round(iso_score, 1),
        'drive_kick_path': round(drive_kick_score, 1),
        'post_hub_path': round(post_hub_score, 1),
        'gravity_path': round(gravity_score, 1),
        'primary_mode': primary_mode,
        'multi_modal_bonus': round(multi_modal_bonus + secondary_bonus, 1),
        'elite_paths': elite_paths
    }
    
    if debug:
        print(f"\n=== Self-Created Score Breakdown ===")
        print(f"ISO Path:        {iso_score:.1f}")
        print(f"Drive-Kick Path: {drive_kick_score:.1f}")
        print(f"Post Hub Path:   {post_hub_score:.1f}")
        print(f"Gravity Path:    {gravity_score:.1f}")
        print(f"Primary Mode:    {primary_mode} ({base_score:.1f})")
        print(f"Multi-Modal Bonus: +{multi_modal_bonus + secondary_bonus:.1f}")
        print(f"FINAL SCORE:     {final_score:.1f}")
        print(f"Elite Paths:     {elite_paths}")
    
    return result
```

### CII Integration

**Location:** `src/nba_data/phase2_creation_independence/index/composite.py`

**Required Changes:**

The existing CII calculator uses `calculate_self_created_score()` for Component 1. With the refactor:

1. The function signature remains the same
2. The function now returns a dictionary instead of a float
3. Update CII calculator to extract the score:

```python
# Before:
self_created_score = calculate_self_created_score(player_data)

# After:
self_created_result = calculate_self_created_score(player_data)
self_created_score = self_created_result['self_created_score']

# Optionally store path breakdown for diagnostics:
player_creation_breakdown = {
    'primary_mode': self_created_result['primary_mode'],
    'iso_path': self_created_result['iso_path'],
    'drive_kick_path': self_created_result['drive_kick_path'],
    'post_hub_path': self_created_result['post_hub_path'],
    'gravity_path': self_created_result['gravity_path'],
    'multi_modal_bonus': self_created_result['multi_modal_bonus']
}
```

---

## Validation Requirements

### Sanity Check Re-Run (After Phase 1)

| Player | Season | Current CII | Target CII | Target Classification |
|--------|--------|-------------|------------|----------------------|
| LeBron James | 2015-16 | 68.8 | 78+ | Franchise Engine |
| Stephen Curry | 2016-17 | 68.7 | 75+ | Franchise Engine (may need Phase 2) |
| Giannis Antetokounmpo | 2020-21 | 56.5 | 78+ | Franchise Engine |
| Kevin Durant | 2018-19 | 71.6 | 78+ | Franchise Engine |
| Nikola Jokić | 2022-23 | 76.5 | 78+ | Franchise Engine (should remain) |
| Kawhi Leonard | 2018-19 | 78.0 | 78+ | Franchise Engine (should remain) |
| Ben Simmons | 2020-21 | 32.9 | <45 | Fragile Star or Role Player |

**Success Criteria (Phase 1):**
- 6/7 sanity checks pass (Curry may require Phase 2)
- LeBron CII increases by 10+ points
- Giannis CII increases by 20+ points
- Jokić CII remains stable (±3 points)
- Simmons CII remains low (<45)

### Discriminant Re-Run (After Phase 1)

| Pair | Current Gap | Target Gap | Expected Outcome |
|------|-------------|------------|------------------|
| Trae vs. Simmons | 56.3 | 50+ | Should remain correct |
| Ja vs. Poole | 24.5 | 25+ | Should remain correct |
| Tatum vs. Brown | 29.2 | 25+ | Should remain correct |
| Mitchell vs. LaVine | 5.8 | 15+ | Should improve separation |
| SGA vs. Fox | 1.0 | 10+ | Should improve separation |
| Edwards vs. Barrett | ~6 | 15+ | Should improve separation |

**Success Criteria (Phase 1):**
- All 4 original wins remain wins
- Mitchell vs. LaVine gap increases (Mitchell higher on ISO, LaVine lower on Drive-Kick)
- SGA vs. Fox gap increases (SGA higher multi-modal)

---

## File Structure

### New Files

```
src/nba_data/
├── scripts/
│   ├── collect_tracking_data.py         # NEW: Fetch NBA.com tracking data
│   ├── merge_tracking_features.py       # NEW: Merge tracking with existing data
│   └── validate_multipath_sanity.py     # NEW: Run sanity checks after implementation
│
├── phase2_creation_independence/
│   ├── index/
│   │   ├── self_created.py              # MODIFIED: Add multi-path logic
│   │   ├── path_iso.py                  # NEW: ISO path calculation
│   │   ├── path_drive_kick.py           # NEW: Drive-and-kick path calculation
│   │   ├── path_post_hub.py             # NEW: Post hub path calculation
│   │   ├── path_gravity.py              # NEW: Gravity path calculation
│   │   └── composite.py                 # MODIFIED: Update to use new self_created
│   │
│   └── MULTIPATH_SPECIFICATION.md       # NEW: This document
│
└── results/
    ├── tracking_data_merged.csv         # NEW: Dataset with tracking features
    └── sanity_check_multipath.csv       # NEW: Validation results
```

### Modified Files

| File | Changes |
|------|---------|
| `self_created.py` | Major refactor to multi-path architecture |
| `composite.py` | Minor update to handle new return format |
| `classify_2d.py` | No changes (uses CII, which is unchanged) |

---

## Testing Protocol

### Unit Tests

Create `tests/test_multipath.py`:

```python
def test_iso_path_harden():
    """Harden 2018-19 should score 90+ on ISO path."""
    player_data = load_player_season("James Harden", "2018-19")
    score = calculate_iso_path_score(player_data)
    assert score >= 90, f"Harden ISO score {score} < 90"

def test_drive_kick_path_lebron():
    """LeBron 2015-16 should score 85+ on drive-kick path."""
    player_data = load_player_season("LeBron James", "2015-16")
    score = calculate_drive_kick_path_score(player_data)
    assert score >= 85, f"LeBron drive-kick score {score} < 85"

def test_post_hub_path_jokic():
    """Jokić 2022-23 should score 90+ on post hub path."""
    player_data = load_player_season("Nikola Jokić", "2022-23")
    score = calculate_post_hub_path_score(player_data)
    assert score >= 90, f"Jokić post hub score {score} < 90"

def test_multimodal_bonus_lebron():
    """LeBron should get multi-modal bonus for elite drive-kick + good post hub."""
    player_data = load_player_season("LeBron James", "2015-16")
    result = calculate_self_created_score(player_data)
    assert result['multi_modal_bonus'] >= 3, "LeBron should get multi-modal bonus"

def test_simmons_remains_low():
    """Simmons should remain low across all paths."""
    player_data = load_player_season("Ben Simmons", "2020-21")
    result = calculate_self_created_score(player_data)
    assert result['self_created_score'] < 50, f"Simmons score {result['self_created_score']} too high"

def test_lavine_no_bonus():
    """LaVine should not get multi-modal bonus (one-dimensional)."""
    player_data = load_player_season("Zach LaVine", "2021-22")
    result = calculate_self_created_score(player_data)
    assert result['multi_modal_bonus'] == 0, "LaVine should not get multi-modal bonus"
```

### Integration Tests

```python
def test_sanity_check_suite():
    """All 7 sanity check players should classify correctly."""
    sanity_players = [
        ("LeBron James", "2015-16", "Franchise Engine"),
        ("Stephen Curry", "2016-17", "Franchise Engine"),
        ("Giannis Antetokounmpo", "2020-21", "Franchise Engine"),
        ("Kevin Durant", "2018-19", "Franchise Engine"),
        ("Nikola Jokić", "2022-23", "Franchise Engine"),
        ("Kawhi Leonard", "2018-19", "Franchise Engine"),
        ("Ben Simmons", "2020-21", "Fragile Star"),
    ]
    
    passed = 0
    for name, season, expected in sanity_players:
        result = classify_2d(name, season)
        if result['archetype'] == expected or (expected == "Fragile Star" and result['cii'] < 45):
            passed += 1
        else:
            print(f"FAIL: {name} {season} - Expected {expected}, got {result['archetype']}")
    
    assert passed >= 6, f"Only {passed}/7 sanity checks passed"
```

---

## Rollback Plan

If the multi-path implementation causes unexpected issues:

### Immediate Rollback

```python
# In self_created.py, add feature flag:

USE_MULTIPATH = True  # Set to False to rollback

def calculate_self_created_score(player_data, debug=False):
    if USE_MULTIPATH:
        return calculate_self_created_score_multipath(player_data, debug)
    else:
        return calculate_self_created_score_legacy(player_data, debug)
```

### Preserve Legacy Function

Keep the original `calculate_self_created_score()` function as `calculate_self_created_score_legacy()` until validation is complete.

---

## Appendix A: Data Field Definitions

| Field | Definition | Source |
|-------|------------|--------|
| `drives_per_game` | Touches that start outside the paint and end with a shot attempt, pass, foul, or turnover inside the paint or toward the basket | NBA.com |
| `drive_pts` | Points scored by the player on drives | NBA.com |
| `drive_ast` | Assists by the player resulting from drives | NBA.com |
| `potential_ast` | Passes that lead to a shot attempt (made or missed) | NBA.com |
| `touches` | Number of times player possesses the ball | NBA.com |
| `time_of_poss` | Total time (seconds) player possesses the ball | NBA.com |
| `screen_ast` | Assists where scorer came off screen set by player | NBA.com |
| `catch_shoot_fga` | Shot attempts within 2 seconds of receiving pass with no dribbles | NBA.com |
| `pull_up_fga` | Shot attempts off the dribble (not catch-and-shoot) | NBA.com |

---

## Appendix B: Expected Player Profiles After Implementation

### LeBron James 2015-16 (Expected)

```
=== Self-Created Score Breakdown ===
ISO Path:        52.3
Drive-Kick Path: 88.7   ← PRIMARY MODE
Post Hub Path:   65.2
Gravity Path:    41.0
Primary Mode:    drive_kick (88.7)
Multi-Modal Bonus: +3.0 (good at Post Hub)
FINAL SCORE:     91.7

CII: 78.2 → Franchise Engine ✅
```

### Stephen Curry 2016-17 (Expected, Phase 2)

```
=== Self-Created Score Breakdown ===
ISO Path:        72.4
Drive-Kick Path: 58.1
Post Hub Path:   22.0
Gravity Path:    89.3   ← PRIMARY MODE
Primary Mode:    gravity (89.3)
Multi-Modal Bonus: +3.0 (good at ISO)
FINAL SCORE:     92.3

CII: 79.5 → Franchise Engine ✅
```

### Ben Simmons 2020-21 (Expected, Should Remain Low)

```
=== Self-Created Score Breakdown ===
ISO Path:        18.2
Drive-Kick Path: 52.1   ← PRIMARY MODE (but not elite)
Post Hub Path:   28.4
Gravity Path:    12.0
Primary Mode:    drive_kick (52.1)
Multi-Modal Bonus: +0.0 (no elite paths)
FINAL SCORE:     52.1

CII: 38.5 → Fragile Star ✅
```

### Zach LaVine 2021-22 (Expected, Should Be Lower Than LeBron)

```
=== Self-Created Score Breakdown ===
ISO Path:        68.3   ← PRIMARY MODE
Drive-Kick Path: 42.1
Post Hub Path:   15.2
Gravity Path:    35.8
Primary Mode:    iso (68.3)
Multi-Modal Bonus: +0.0 (one-dimensional)
FINAL SCORE:     68.3

CII: 65.2 → Strong Creator (not Engine) ✅
```

---

*End of Implementation Plan*
