import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from nba_data.scripts.populate_playoff_data import PlayoffDataPopulator
import logging

logging.basicConfig(level=logging.INFO)

SEASONS = [
    "2015-16", "2016-17", "2017-18", "2018-19", "2019-20",
    "2020-21", "2021-22", "2022-23", "2023-24"
]

def main():
    populator = PlayoffDataPopulator()
    for season in SEASONS:
        print(f"Processing {season}...")
        try:
            populator.populate_all_playoff_data(season)
            print(f"✅ Finished {season}")
        except Exception as e:
            print(f"❌ Failed {season}: {e}")

if __name__ == "__main__":
    main()
