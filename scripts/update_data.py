import sys
from pathlib import Path
import subprocess

Add project root to path

project_root = str(Path(file).resolve().parent.parent)
sys.path.insert(0, project_root)

def run_defensive_features():
print("Running defensive feature generation...")
try:
subprocess.run([sys.executable, "src/nba_data/scripts/calculate_defensive_features.py"], check=True)
print("✅ Defensive features generated successfully.")
except subprocess.CalledProcessError as e:
print(f"❌ Error generating defensive features: {e}")
sys.exit(1)

if name == "main":
run_defensive_features()