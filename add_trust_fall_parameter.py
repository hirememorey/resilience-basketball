#!/usr/bin/env python3
"""
Script to add apply_hard_gates parameter to predict_conditional_archetype.py
for Trust Fall experiment.
"""

import re
from pathlib import Path

file_path = Path("src/nba_data/scripts/predict_conditional_archetype.py")

with open(file_path, 'r') as f:
    content = f.read()

# 1. Add parameter to prepare_features signature
content = re.sub(
    r'def prepare_features\(\s*self,\s*player_data: pd\.Series,\s*usage_level: float,\s*apply_phase3_fixes: bool = True\s*\)',
    'def prepare_features(\n        self, \n        player_data: pd.Series, \n        usage_level: float,\n        apply_phase3_fixes: bool = True,\n        apply_hard_gates: bool = True\n    )',
    content
)

# 2. Add parameter description in docstring
content = re.sub(
    r'(apply_phase3_fixes: Whether to apply Phase 3\.5 & 3\.6 fixes \(default: True\))',
    r'\1\n            apply_hard_gates: Whether to apply hard-coded gates/taxes (default: True)\n                              Set to False for Trust Fall experiment',
    content
)

# 3. Update Multi-Signal Tax conditions
content = re.sub(
    r'if not is_exempt and apply_phase3_fixes:',
    r'if not is_exempt and apply_phase3_fixes and apply_hard_gates:',
    content
)

# 4. Add parameter to predict_archetype_at_usage signature
content = re.sub(
    r'def predict_archetype_at_usage\(\s*self,\s*player_data: pd\.Series,\s*usage_level: float,\s*apply_phase3_fixes: bool = True\s*\)',
    'def predict_archetype_at_usage(\n        self, \n        player_data: pd.Series, \n        usage_level: float,\n        apply_phase3_fixes: bool = True,\n        apply_hard_gates: bool = True\n    )',
    content
)

# 5. Update predict_archetype_at_usage docstring
content = re.sub(
    r'(apply_phase3_fixes: Whether to apply Phase 3 fixes \(default: True\))',
    r'\1\n            apply_hard_gates: Whether to apply hard-coded gates/taxes (default: True)\n                              Set to False for Trust Fall experiment',
    content
)

# 6. Update prepare_features call
content = re.sub(
    r'features, phase3_metadata = self\.prepare_features\(player_data, usage_level, apply_phase3_fixes\)',
    'features, phase3_metadata = self.prepare_features(player_data, usage_level, apply_phase3_fixes, apply_hard_gates)',
    content
)

# 7. Wrap all gate conditions
gate_patterns = [
    (r'if apply_phase3_fixes and \'RS_RIM_APPETITE\'', r'if apply_phase3_fixes and apply_hard_gates and \'RS_RIM_APPETITE\''),
    (r'if apply_phase3_fixes:\s+# Calculate self-created frequency', r'if apply_phase3_fixes and apply_hard_gates:\n            # Calculate self-created frequency'),
    (r'if apply_phase3_fixes:\s+# Check if missing leverage data', r'if apply_phase3_fixes and apply_hard_gates:\n            # Check if missing leverage data'),
    (r'if apply_phase3_fixes:\s+# Penalize players with multiple negative signals', r'if apply_phase3_fixes and apply_hard_gates:\n            # Penalize players with multiple negative signals'),
    (r'if apply_phase3_fixes:\s+# Require at least 4 of 6 critical features', r'if apply_phase3_fixes and apply_hard_gates:\n            # Require at least 4 of 6 critical features'),
    (r'if apply_phase3_fixes:\s+# Check for minimum sample sizes', r'if apply_phase3_fixes and apply_hard_gates:\n            # Check for minimum sample sizes'),
]

for pattern, replacement in gate_patterns:
    content = re.sub(pattern, replacement, content)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ Successfully added apply_hard_gates parameter to predict_conditional_archetype.py")

