#!/usr/bin/env python3
"""
Complete implementation of Trust Fall experiment parameter.
Makes all necessary changes to predict_conditional_archetype.py
"""

file_path = "src/nba_data/scripts/predict_conditional_archetype.py"

with open(file_path, 'r') as f:
    content = f.read()

# Track changes
changes_made = []

# 1. Add parameter to prepare_features signature
if 'def prepare_features(' in content and 'apply_hard_gates: bool = True' not in content.split('def prepare_features(')[1].split('\n    )')[0]:
    # Find the signature block
    import re
    pattern = r'(def prepare_features\(\s*self,\s*player_data: pd\.Series,\s*usage_level: float,\s*apply_phase3_fixes: bool = True\s*\))'
    replacement = r'def prepare_features(\n        self, \n        player_data: pd.Series, \n        usage_level: float,\n        apply_phase3_fixes: bool = True,\n        apply_hard_gates: bool = True\n    )'
    content = re.sub(pattern, replacement, content)
    changes_made.append("Added apply_hard_gates to prepare_features signature")

# 2. Add docstring parameter
if 'apply_phase3_fixes: Whether to apply Phase 3.5 & 3.6 fixes' in content:
    content = content.replace(
        '            apply_phase3_fixes: Whether to apply Phase 3.5 & 3.6 fixes (default: True)\n        \n        Returns:',
        '            apply_phase3_fixes: Whether to apply Phase 3.5 & 3.6 fixes (default: True)\n            apply_hard_gates: Whether to apply hard-coded gates/taxes (default: True)\n                              Set to False for Trust Fall experiment\n        \n        Returns:'
    )
    changes_made.append("Added apply_hard_gates to prepare_features docstring")

# 3. Add parameter to predict_archetype_at_usage signature  
pattern = r'(def predict_archetype_at_usage\(\s*self,\s*player_data: pd\.Series,\s*usage_level: float,\s*apply_phase3_fixes: bool = True\s*\))'
replacement = r'def predict_archetype_at_usage(\n        self, \n        player_data: pd.Series, \n        usage_level: float,\n        apply_phase3_fixes: bool = True,\n        apply_hard_gates: bool = True\n    )'
if re.search(pattern, content):
    content = re.sub(pattern, replacement, content)
    changes_made.append("Added apply_hard_gates to predict_archetype_at_usage signature")

# 4. Add docstring parameter for predict_archetype_at_usage
if 'apply_phase3_fixes: Whether to apply Phase 3 fixes' in content and 'predict_archetype_at_usage' in content:
    # Find the specific occurrence in predict_archetype_at_usage
    parts = content.split('def predict_archetype_at_usage')
    if len(parts) > 1:
        docstring_part = parts[1].split('Returns:')[0]
        if 'apply_phase3_fixes: Whether to apply Phase 3 fixes' in docstring_part:
            content = content.replace(
                '            apply_phase3_fixes: Whether to apply Phase 3 fixes (default: True)\n        \n        Returns:',
                '            apply_phase3_fixes: Whether to apply Phase 3 fixes (default: True)\n            apply_hard_gates: Whether to apply hard-coded gates/taxes (default: True)\n                              Set to False for Trust Fall experiment\n        \n        Returns:',
                1  # Only replace first occurrence
            )
            changes_made.append("Added apply_hard_gates to predict_archetype_at_usage docstring")

# 5. Update prepare_features call
if 'self.prepare_features(player_data, usage_level, apply_phase3_fixes)' in content:
    content = content.replace(
        'self.prepare_features(player_data, usage_level, apply_phase3_fixes)',
        'self.prepare_features(player_data, usage_level, apply_phase3_fixes, apply_hard_gates)'
    )
    changes_made.append("Updated prepare_features call")

# 6. Update Multi-Signal Tax conditions (2 occurrences)
content = content.replace(
    'if not is_exempt and apply_phase3_fixes:',
    'if not is_exempt and apply_phase3_fixes and apply_hard_gates:'
)
if 'if not is_exempt and apply_phase3_fixes and apply_hard_gates:' in content:
    changes_made.append("Updated Multi-Signal Tax conditions")

# 7. Update all gate conditions
gate_updates = [
    ("if apply_phase3_fixes and 'RS_RIM_APPETITE'", "if apply_phase3_fixes and apply_hard_gates and 'RS_RIM_APPETITE'"),
    ("if apply_phase3_fixes:\n            # Calculate self-created frequency", "if apply_phase3_fixes and apply_hard_gates:\n            # Calculate self-created frequency"),
    ("if apply_phase3_fixes:\n            leverage_usg = player_data.get('LEVERAGE_USG_DELTA'", "if apply_phase3_fixes and apply_hard_gates:\n            leverage_usg = player_data.get('LEVERAGE_USG_DELTA'"),
    ("if apply_phase3_fixes:\n            creation_tax = player_data.get('CREATION_TAX'", "if apply_phase3_fixes and apply_hard_gates:\n            creation_tax = player_data.get('CREATION_TAX'"),
    ("if apply_phase3_fixes:\n            critical_features = [", "if apply_phase3_fixes and apply_hard_gates:\n            critical_features = ["),
    ("if apply_phase3_fixes:\n            # Check pressure shots", "if apply_phase3_fixes and apply_hard_gates:\n            # Check pressure shots"),
]

for old, new in gate_updates:
    if old in content:
        content = content.replace(old, new)
        changes_made.append(f"Updated gate condition: {old[:50]}...")

# Write back
with open(file_path, 'w') as f:
    f.write(content)

print("✅ Trust Fall implementation complete!")
print(f"Changes made: {len(changes_made)}")
for change in changes_made:
    print(f"  - {change}")

# Verify syntax
import subprocess
result = subprocess.run(['python', '-m', 'py_compile', file_path], 
                       capture_output=True, text=True)
if result.returncode == 0:
    print("✅ Syntax check passed")
else:
    print("❌ Syntax error:")
    print(result.stderr)
    print("\n⚠️  File may need manual fixes")

