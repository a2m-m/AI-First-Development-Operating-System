#!/usr/bin/env python3
import sys
import os
import re

def load_config(filepath):
    """
    Parses a simple two-level YAML file (os-template.yml) natively.
    Returns a dictionary of dictionaries: {section: {key: value}}
    Also handles lists if formatted simply like `["a", "b"]`.
    """
    config = {}
    current_section = None
    
    if not os.path.exists(filepath):
        return config

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            original_line = line
            line = line.strip()
            
            # Skip empty lines or pure comments
            if not line or line.startswith('#'):
                continue
            
            # Remove inline comments (naive approach, handles most cases in this template)
            # Find the first '#' that is not inside quotes
            in_single_quote = False
            in_double_quote = False
            comment_idx = -1
            
            for i, char in enumerate(original_line):
                if char == "'" and not in_double_quote:
                    in_single_quote = not in_single_quote
                elif char == '"' and not in_single_quote:
                    in_double_quote = not in_double_quote
                elif char == '#' and not in_single_quote and not in_double_quote:
                    comment_idx = i
                    break
                    
            if comment_idx != -1:
                line = original_line[:comment_idx].strip()
                if not line:
                    continue
            
            # Check for top-level section (e.g., "project:")
            section_match = re.match(r'^([a-zA-Z0-9_-]+):$', line)
            if section_match and not original_line.startswith(' ') and not original_line.startswith('\t'):
                current_section = section_match.group(1)
                config[current_section] = {}
                continue
                
            # Check for key-value pair under a section
            if current_section and ':' in line:
                # Find the first colon
                colon_idx = line.find(':')
                key = line[:colon_idx].strip()
                val = line[colon_idx+1:].strip()
                
                # Strip quotes if present
                if val.startswith('"') and val.endswith('"'):
                    val = val[1:-1]
                elif val.startswith("'") and val.endswith("'"):
                    val = val[1:-1]
                    
                # Handle boolean-like strings
                if val.lower() == 'true':
                    val = True
                elif val.lower() == 'false':
                    val = False
                elif val.isdigit():
                    val = int(val)
                elif val.startswith('[') and val.endswith(']'):
                    # Extremely simple list parsing for single-line lists like ["a", "b"]
                    inner = val[1:-1].strip()
                    if inner:
                         # Split by comma, but be careful with quotes
                         # A naive split by comma is enough for our use cases (e.g., host_setup_steps)
                         parts = [p.strip() for p in inner.split(',')]
                         # Clean quotes from parts
                         val_list = []
                         for p in parts:
                             if p.startswith('"') and p.endswith('"'):
                                 val_list.append(p[1:-1])
                             elif p.startswith("'") and p.endswith("'"):
                                 val_list.append(p[1:-1])
                             else:
                                 val_list.append(p)
                         val = val_list
                    else:
                         val = []

                config[current_section][key] = val

    return config

def get_value(filepath, key_path):
    """
    Get a value by path like 'runtime.mode'
    """
    config = load_config(filepath)
    parts = key_path.split('.')
    
    current = config
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
            
    return current

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 config.py <path_to_yaml> <key_path>", file=sys.stderr)
        sys.exit(1)
        
    filepath = sys.argv[1]
    key_path = sys.argv[2]
    
    val = get_value(filepath, key_path)
    
    if val is None:
        print("", end="")
    elif isinstance(val, bool):
        print("true" if val else "false")
    elif isinstance(val, list):
         # Print as a JSON-like array string which is often parsed safely or eval'd by bash
         # Alternatively, just space separated. Let's stick to bash friendly or eval friendly.
         # Actually os-template.yml host_setup_steps is used in bash. If we print the raw array, it might be hard to parse.
         # For simplicity in Bash scripts, we can join them with newlines or spaces. 
         # But in scripts/run, host_setup_steps is only checked for not empty.
         # Let's just output a string representation that bash can check if it's "[]" or not.
         if not val:
             print("[]")
         else:
             import json
             print(json.dumps(val))
    else:
        print(str(val))
