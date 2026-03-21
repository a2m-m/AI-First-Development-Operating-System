#!/usr/bin/env python3
import sys
import os
import json

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    
def load_config(filepath):
    """
    Loads and returns the parsed contents of a YAML file as a dict.
    """
    config = {}
    
    if not HAS_YAML:
        return config
    
    if not os.path.exists(filepath):
        return config

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            parsed = yaml.safe_load(f)
            if parsed:
                config = parsed
    except Exception as e:
        print(f"Error parsing YAML file {filepath}: {e}", file=sys.stderr)

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
    if not HAS_YAML:
        print("Warning: pyyaml is not installed. Run 'pip install pyyaml' or check requirements.txt.", file=sys.stderr)
        print("")
        sys.exit(0)

    if len(sys.argv) != 3:
        print("Usage: python3 config.py <path_to_yaml> <key_path>", file=sys.stderr)
        sys.exit(1)
        
    filepath = sys.argv[1]
    key_path = sys.argv[2]
    
    val = get_value(filepath, key_path)
    
    if val is None:
        print("")
    elif isinstance(val, bool):
        print("true" if val else "false")
    elif isinstance(val, list):
        # 空リストは '[]'、非空は JSON 配列文字列として出力
        if not val:
            print("[]")
        else:
            print(json.dumps(val))
    else:
        print(str(val))
