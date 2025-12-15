#!/usr/bin/env python3
"""
Project Overview Generator for NBA Playoff Resilience Engine

This script creates a comprehensive project overview document by concatenating
key files and including a directory tree structure. The output gives developers
a complete understanding of the project's vision, current state, and future directions.

Usage:
    python scripts/generate_project_overview.py

Output:
    project_overview.txt - Comprehensive project documentation
"""

import os
import sys
from pathlib import Path
from datetime import datetime

class ProjectOverviewGenerator:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.output_file = self.root_dir / "project_overview.txt"

        # Files to include in order
        self.markdown_files = [
            "ACTIVE_CONTEXT.md",
            "CURRENT_STATE.md",
            "IMPLEMENTATION_SUMMARY.md",
            "KEY_INSIGHTS.md",
            "LUKA_SIMMONS_PARADOX.md",
            "NEXT_STEPS.md",
            "README.md"
        ]

        self.python_scripts = [
            "src/nba_data/scripts/evaluate_plasticity_potential.py",
            "src/nba_data/scripts/calculate_physicality_features.py",
            "src/nba_data/scripts/calculate_simple_resilience.py",
            "src/nba_data/scripts/train_rfe_model.py"
        ]

        self.test_files = [
            "tests/validation/test_latent_star_cases.py",
            "tests/validation/test_overall_star_prediction.py"
        ]

        self.diagnostics_files = [
            "results/latent_star_test_cases_diagnostics.csv",
            "results/overall_star_prediction_diagnostics.csv"
        ]

    def generate_tree(self, start_path: Path, prefix: str = "") -> str:
        """Generate a tree-like directory structure, excluding data/ directory."""
        if start_path.name == "data":
            return ""

        lines = []
        try:
            items = sorted(start_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
        except PermissionError:
            return ""

        for i, item in enumerate(items):
            if item.name.startswith('.') or item.name == '__pycache__':
                continue

            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "

            if item.is_dir():
                lines.append(f"{prefix}{connector}{item.name}/")
                extension = "    " if is_last else "│   "
                lines.append(self.generate_tree(item, prefix + extension))
            else:
                lines.append(f"{prefix}{connector}{item.name}")

        return "\n".join(lines)

    def read_file_content(self, file_path: str) -> str:
        """Read file content with error handling."""
        full_path = self.root_dir / file_path
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"FILE NOT FOUND: {file_path}\n"
        except Exception as e:
            return f"ERROR READING {file_path}: {str(e)}\n"

    def write_section_header(self, output, title: str):
        """Write a formatted section header."""
        output.write(f"\n{'='*80}\n")
        output.write(f" {title.upper()}\n")
        output.write(f"{'='*80}\n\n")

    def write_file_section(self, output, file_path: str, section_title: str):
        """Write a file's content with header."""
        output.write(f"\n{'-'*60}\n")
        output.write(f" {section_title}: {file_path}\n")
        output.write(f"{'-'*60}\n\n")
        content = self.read_file_content(file_path)
        output.write(content)
        output.write("\n")

    def generate_overview(self):
        """Generate the complete project overview."""
        print(f"Generating project overview at: {self.output_file}")

        with open(self.output_file, 'w', encoding='utf-8') as output:
            # Header
            output.write("NBA PLAYOFF RESILIENCE ENGINE - PROJECT OVERVIEW\n")
            output.write("=" * 80 + "\n")
            output.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            output.write(f"Project Root: {self.root_dir}\n\n")

            # Project Directory Structure
            self.write_section_header(output, "PROJECT DIRECTORY STRUCTURE")
            output.write(".\n")
            tree_output = self.generate_tree(self.root_dir)
            output.write(tree_output)
            output.write("\n\n")

            # Markdown Documentation Files
            self.write_section_header(output, "PROJECT VISION & DOCUMENTATION")

            for md_file in self.markdown_files:
                if os.path.exists(self.root_dir / md_file):
                    self.write_file_section(output, md_file, "DOCUMENTATION FILE")

            # Core Implementation Scripts
            self.write_section_header(output, "CORE IMPLEMENTATION SCRIPTS")

            for script in self.python_scripts:
                if os.path.exists(self.root_dir / script):
                    self.write_file_section(output, script, "PYTHON SCRIPT")

            # Test Scripts
            self.write_section_header(output, "VALIDATION & TESTING")

            for test_file in self.test_files:
                if os.path.exists(self.root_dir / test_file):
                    self.write_file_section(output, test_file, "TEST SCRIPT")

            # Diagnostics Output
            self.write_section_header(output, "TEST DIAGNOSTICS & RESULTS")

            for diag_file in self.diagnostics_files:
                if os.path.exists(self.root_dir / diag_file):
                    self.write_file_section(output, diag_file, "DIAGNOSTICS CSV")

            # Footer
            output.write(f"\n{'='*80}\n")
            output.write(" END OF PROJECT OVERVIEW\n")
            output.write(f"{'='*80}\n")

        print(f"✓ Project overview generated successfully: {self.output_file}")
        print(f"✓ Total size: {os.path.getsize(self.output_file)} bytes")

def main():
    """Main entry point."""
    # Get the project root directory (parent of scripts/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    generator = ProjectOverviewGenerator(project_root)
    generator.generate_overview()

if __name__ == "__main__":
    main()