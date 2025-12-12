#!/usr/bin/env python3
"""
Run the NBA Resilience Streamlit App

Usage:
    python scripts/run_streamlit_app.py [--port PORT] [--host HOST]

This script launches the interactive web application for visualizing
the 2D Risk Matrix and Stress Vectors.
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Run NBA Resilience Streamlit App")
    parser.add_argument("--port", type=int, default=8501, help="Port to run the app on")
    parser.add_argument("--host", type=str, default="localhost", help="Host to bind to")
    parser.add_argument("--browser", action="store_true", help="Open browser automatically")

    args = parser.parse_args()

    # Path to the main app file
    app_path = Path(__file__).parent.parent / "src" / "streamlit_app" / "main.py"

    if not app_path.exists():
        print(f"❌ Error: App file not found at {app_path}")
        sys.exit(1)

    # Build command with proper Python path
    project_root = Path(__file__).parent.parent
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)

    cmd = [
        sys.executable, "-m", "streamlit", "run", str(app_path),
        "--server.port", str(args.port),
        "--server.address", args.host
    ]

    if args.browser:
        cmd.append("--server.headless=true")
        cmd.append("--server.runOnSave=false")

    print(f"🚀 Starting NBA Resilience Streamlit App on http://{args.host}:{args.port}")
    print(f"📁 App location: {app_path}")
    print(f"📂 Project root: {project_root}")

    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\n👋 App stopped")
    except Exception as e:
        print(f"❌ Error running app: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
