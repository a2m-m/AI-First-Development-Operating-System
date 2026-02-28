#!/usr/bin/env python3
import sys
import json
import re

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data.strip():
            sys.exit(0)
            
        payload = json.loads(input_data)
        tool_name = payload.get("tool_name", "")
        tool_input = payload.get("tool_input", {})
        
        # We care about tools that could modify or read files, or execute commands
        file_tools = {"Read", "Write", "Edit", "Glob", "LS", "ViewDocument"}
        
        # Tools that access files uses either file_path, path, file, or pattern
        target_path = tool_input.get("file_path", "") or tool_input.get("path", "") or tool_input.get("pattern", "") or tool_input.get("file", "")
        
        # Detect any occurrences of typical secret file names
        secret_patterns = [
            r'^\.env$',          # exactly .env
            r'^\.env\..*$',      # .env.local, .env.test, etc
            r'/\.env$',          # path/.env
            r'/\.env\..*$',      # path/.env.test
            r'credentials.*',    # credentials.json, etc
            r'.*secret.*'        # dummy_secret.txt, etc
        ]
        
        is_secret = False
        if target_path:
            is_secret = any(re.search(p, str(target_path), re.IGNORECASE) for p in secret_patterns)
        
        if tool_name in file_tools and is_secret:
            print(f"SECURITY BLOCK: Access to secret file '{target_path}' is strictly prohibited by AI-First-Development-Operating-System rules.", file=sys.stderr)
            sys.exit(2)
            
        if tool_name == "Bash":
            command = tool_input.get("command", "")
            # Check for secrets passing in command
            if any(re.search(r'\b' + p + r'\b', str(command), re.IGNORECASE) for p in ["\.env", "credentials"]):
                print(f"SECURITY BLOCK: Bash command references a secret file. Command blocked.", file=sys.stderr)
                sys.exit(2)
                
            # Check for external URLs via bash
            url_tools = ["curl", "wget"]
            if any(tool in str(command) for tool in url_tools):
                print(f"SECURITY WARNING: External network request detected in Bash command. Proceed with caution.", file=sys.stderr)
                
        if tool_name == "Fetch":
            print(f"SECURITY WARNING: External network request (Fetch tool) detected. Proceed with caution.", file=sys.stderr)
            
        sys.exit(0)
        
    except Exception as e:
        # If the hook fails for any reason, don't crash Claude Code
        print(f"Hook Execution Warning: {e}", file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()
