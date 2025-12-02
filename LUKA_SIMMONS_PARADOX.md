# The Luka & Simmons Paradox: Problem & Resolution

## 1. The Problem State
As of Dec 2025, the initial "Plasticity" model (which measured resilience as the ability to maintain efficiency in new shot zones) encountered two critical failure modes that threatened its validity.

### Failure Mode A: The "Luka Paradox" (False Negative)
*   **Observation:** Luka Dončić (2023-24) led his team to the NBA Finals but was flagged as "Fragile" by the model.
*   **The Mechanism:**
    1.  **Displacement:** Defenses forced him from the Rim to the "Paint (Non-RA)" zone.
    2.  **Baseline:** He shot **54.7%** in this zone in the Regular Season (unsustainable elite performance).
    3.  **Playoff Reality:** He shot **44.7%** in the Playoffs (still good, but a -10% drop).
    4.  **Model Verdict:** "Efficiency collapsed -> Fragile."
*   **The Reality Gap:** The model ignored that Luka **increased his volume** in this zone by +2.0 shots/game. He "spent" efficiency to "buy" necessary production. He didn't struggle; he carried the load.

### Failure Mode B: The "Simmons Paradox" (False Positive)
*   **Observation:** Ben Simmons (2020-21) had a catastrophic playoff meltdown but his efficiency metrics remained neutral/positive.
*   **The Mechanism:**
    1.  **Passivity:** He stopped shooting. He famously passed up open dunks.
    2.  **Efficiency:** Because he only took the easiest shots, his FG% remained high.
    3.  **Model Verdict:** "Efficiency maintained -> Resilient."
*   **The Reality Gap:** Resilience requires **absorbing responsibility**, not abdicating it. Taking 0 shots and making 0 is not resilience.

---

## 2. First Principles Analysis

### Core Principle 1: Resilience = Efficiency × Volume
Resilience cannot be measured by efficiency alone.
*   **Efficiency** measures *accuracy*.
*   **Volume** measures *responsibility*.
*   **Resilience** is the integral of both: **Production.**

### Core Principle 2: The "Abdication Tax"
A player who plays 40 minutes in the playoffs but attempts fewer shots than they did in 30 minutes of the regular season is failing, regardless of their shooting percentage. The metric must penalize **passivity**.

### Core Principle 3: Baselines are Noisy
Comparing a small-sample Playoff run against an outlier Regular Season performance (like Luka's 55% floater season) creates noise. We need to stabilize expectations.

---

## 3. The Solution: The "Dual-Grade" Archetype System

We resolved these paradoxes by abandoning the search for a single scalar "Resilience Score" in favor of a **Dual-Grade System** that evaluates players on two independent axes.

### The Two Axes
1.  **Resilience Quotient (RQ):** The Y-Axis. Measures **Adaptability**.
    *   Formula: `(Playoff Volume / Regular Season Volume) * (Playoff Efficiency / Regular Season Efficiency)`
    *   This effectively captures "Counter-Punch Efficiency" while penalizing passivity (Volume drop) and rewarding scaling (Volume increase).
2.  **Dominance Score:** The X-Axis. Measures **Absolute Value**.
    *   Formula: `Playoff Points Per 75 Possessions`
    *   We determined that "Delta" metrics (Playoff vs RS) are flawed for Dominance because they reward low-usage players for stability. The true measure of Dominance in the playoffs is **Absolute Magnitude**.

### The Four Archetypes

| Archetype | Description | RQ (Resilience) | Dominance | Example |
| :--- | :--- | :--- | :--- | :--- |
| **King (Resilient Star)** | Elite production maintained under pressure. | High (>0.95) | High (>20) | **Nikola Jokić**, **Giannis '21** |
| **Bulldozer (Fragile Star)** | High production, but inefficient ("Wins Ugly"). | Low (<0.95) | High (>20) | **Luka Dončić**, **LeBron '15** |
| **Sniper (Resilient Role)** | Efficient, but low volume/impact. | High (>0.95) | Low (<20) | **Aaron Gordon**, **Brook Lopez** |
| **Victim (Fragile Role)** | Low production, low efficiency. The "Collapse". | Low (<0.95) | Low (<20) | **Ben Simmons**, **D'Angelo Russell** |

---

## 4. Validation Results (Historical Analysis 2015-2024)

We ran this model against the full 9-year dataset. The results confirmed the solution to the paradoxes.

### Validating the Luka Paradox
*   **Luka Dončić (2020-21 vs LAC):** **King** (RQ: 1.159, Dom: 33.9). *Elite.*
*   **Luka Dončić (2023-24 Run):**
    *   vs MIN: **King** (RQ 0.958, Dom 30.8).
    *   vs LAC/OKC/BOS: **Bulldozer** (RQ ~0.85, Dom >27.0).
    *   **Verdict:** Correctly identified as an offensive engine who carries massive load ("Bulldozer") even when efficiency drops, but hits "King" status when healthy/hot. **Not Fragile.**

### Validating the Simmons Paradox
*   **Ben Simmons (2020-21 vs ATL):** **Victim** (RQ: 0.647, Dom: 10.1).
    *   RQ dropped massively due to Volume abdication. Dominance was non-existent.
    *   **Verdict:** Correctly identified as a collapse. **Not Resilient.**

### Other Key Findings
*   **Nikola Jokić:** The gold standard. **King** in 9 out of 11 career series.
*   **DeMar DeRozan (2015-2018):** Correctly captures his struggles. **Victim** vs IND '16, **Bulldozer** (inefficient volume) vs CLE '16.
*   **James Harden:** Historical validation of his "Bulldozer" status (high volume, significant efficiency drops) in HOU years.

---

## 5. Implementation Status
*   **Script:** `src/nba_data/scripts/calculate_simple_resilience.py`
*   **Dataset:** `results/resilience_archetypes.csv` (Full 2015-2024 History)
*   **Visualization:** `results/resilience_archetypes_plot.png`
