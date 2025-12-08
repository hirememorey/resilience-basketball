# Salary Data Collection Strategy


Goal: Efficiently collect historical salary data for 2015-2025 to calculate Alpha Scores.

The "First Principles" Efficiency Approach

Instead of scraping individual player pages (N=5000+ requests), we scrape season-level lists (N=10 requests).

Source Selection

We selected HoopsHype over Spotrac or Basketball Reference for three reasons:

Predictable URLs: https://hoopshype.com/salaries/players/{start_year}-{end_year}/

Clean HTML Tables: Easily parsable by Pandas without complex DOM traversal.

Inflation Adjustment: They provide both nominal and inflation-adjusted values (we use nominal to match historical cap context).

Data Pipeline

Iterate Seasons: 2015-16 to 2024-25.

Fetch: GET request to HoopsHype.

Parse: Extract the main salary table.

Clean:

Convert "$25,000,000" -> 25.0 (Millions)

Normalize names (strip ".", lower case comparison)

Merge: Join with predictive_dataset.csv on normalized names.

Handling Name Mismatches

NBA API and HoopsHype often spell names differently (e.g., "CJ McCollum" vs "C.J. McCollum").
The script includes a normalize_name function to maximize match rates.