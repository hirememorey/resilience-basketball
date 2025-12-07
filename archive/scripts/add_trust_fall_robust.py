#!/usr/bin/env python3
"""
Robust script to add apply_hard_gates parameter - reads line by line to avoid corruption.
"""

file_path = "src/nba_data/scripts/predict_conditional_archetype.py"

with open(file_path, 'r') as f:
    lines = f.readlines()

output_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # 1. Update prepare_features signature
    if 'def prepare_features(' in line and 'apply_hard_gates' not in ''.join(lines[i:i+10]):
        # Find the closing parenthesis
        sig_lines = [line]
        j = i + 1
        paren_count = line.count('(') - line.count(')')
        while j < len(lines) and paren_count > 0:
            sig_lines.append(lines[j])
            paren_count += lines[j].count('(') - lines[j].count(')')
            j += 1
        
        # Reconstruct signature with new parameter
        sig_text = ''.join(sig_lines)
        if 'apply_hard_gates' not in sig_text:
            # Insert parameter before closing paren
            sig_text = sig_text.rstrip()
            if sig_text.endswith(')'):
                sig_text = sig_text[:-1] + ',\n        apply_hard_gates: bool = True\n    )'
            output_lines.append(sig_text)
            i = j
            continue
    
    # 2. Update prepare_features docstring
    if 'apply_phase3_fixes: Whether to apply Phase 3.5 & 3.6 fixes' in line:
        output_lines.append(line)
        # Add next line for parameter description
        indent = len(line) - len(line.lstrip())
        output_lines.append(' ' * indent + 'apply_hard_gates: Whether to apply hard-coded gates/taxes (default: True)\n')
        output_lines.append(' ' * indent + '                              Set to False for Trust Fall experiment\n')
        i += 1
        continue
    
    # 3. Update predict_archetype_at_usage signature
    if 'def predict_archetype_at_usage(' in line and 'apply_hard_gates' not in ''.join(lines[i:i+10]):
        sig_lines = [line]
        j = i + 1
        paren_count = line.count('(') - line.count(')')
        while j < len(lines) and paren_count > 0:
            sig_lines.append(lines[j])
            paren_count += lines[j].count('(') - lines[j].count(')')
            j += 1
        
        sig_text = ''.join(sig_lines)
        if 'apply_hard_gates' not in sig_text:
            sig_text = sig_text.rstrip()
            if sig_text.endswith(')'):
                sig_text = sig_text[:-1] + ',\n        apply_hard_gates: bool = True\n    )'
            output_lines.append(sig_text)
            i = j
            continue
    
    # 4. Update predict_archetype_at_usage docstring
    if 'apply_phase3_fixes: Whether to apply Phase 3 fixes' in line and 'predict_archetype_at_usage' in ''.join(lines[max(0,i-20):i]):
        output_lines.append(line)
        indent = len(line) - len(line.lstrip())
        output_lines.append(' ' * indent + 'apply_hard_gates: Whether to apply hard-coded gates/taxes (default: True)\n')
        output_lines.append(' ' * indent + '                              Set to False for Trust Fall experiment\n')
        i += 1
        continue
    
    # 5. Update prepare_features call
    if 'features, phase3_metadata = self.prepare_features(player_data, usage_level, apply_phase3_fixes)' in line:
        output_lines.append(line.replace(
            'self.prepare_features(player_data, usage_level, apply_phase3_fixes)',
            'self.prepare_features(player_data, usage_level, apply_phase3_fixes, apply_hard_gates)'
        ))
        i += 1
        continue
    
    # 6. Update gate conditions - look for specific patterns
    if 'if apply_phase3_fixes:' in line:
        # Check if this is a gate condition (not Flash Multiplier or other non-gate logic)
        context = ''.join(lines[max(0,i-2):min(len(lines),i+5)])
        is_gate = any(keyword in context for keyword in [
            'Fragility Gate',
            'Bag Check Gate',
            'Missing Leverage Data',
            'Negative Signal Gate',
            'Data Completeness Gate',
            'Minimum Sample Size Gate',
            'Multi-Signal Tax',
            'is_exempt and apply_phase3_fixes'
        ])
        
        if is_gate and 'apply_hard_gates' not in line:
            # Add apply_hard_gates condition
            line = line.replace('if apply_phase3_fixes:', 'if apply_phase3_fixes and apply_hard_gates:')
    
    output_lines.append(line)
    i += 1

with open(file_path, 'w') as f:
    f.writelines(output_lines)

print("✅ Successfully added apply_hard_gates parameter")


