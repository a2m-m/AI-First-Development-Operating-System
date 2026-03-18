#!/usr/bin/env python3
import sys
import json
import re
import os
import fnmatch

# デフォルトの機密ファイル遮断パターン（os-template.yml 未設定時のフォールバック）
_DEFAULT_BLOCKED_PATTERNS = [
    ".env",
    ".env.*",
    "**/.env",
    "**/.env.*",
    "credentials*",
    "**/secret*",
]

def _load_blocked_patterns():
    """os-template.yml から security.blocked_file_patterns を読み込む。
    未設定・読み込み失敗時はデフォルトパターンを返す。"""
    try:
        hooks_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(hooks_dir)
        scripts_lib = os.path.join(repo_root, "scripts", "lib")
        os_template = os.path.join(repo_root, "os-template.yml")

        sys.path.insert(0, scripts_lib)
        from config import get_value
        patterns = get_value(os_template, "security.blocked_file_patterns")
        if patterns and isinstance(patterns, list) and len(patterns) > 0:
            return patterns
    except Exception:
        pass
    return _DEFAULT_BLOCKED_PATTERNS

def _is_blocked(path, patterns):
    """path が patterns のいずれかにマッチすれば True を返す。"""
    name = os.path.basename(str(path))
    full = str(path)
    for p in patterns:
        # ファイル名マッチ（glob プレフィックスを除いた末尾パターンで照合）
        basename_pattern = p.lstrip("**/").lstrip("/")
        if fnmatch.fnmatch(name, basename_pattern):
            return True
        # フルパスマッチ
        if fnmatch.fnmatch(full, p):
            return True
    return False

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

        blocked_patterns = _load_blocked_patterns()

        is_secret = False
        if target_path:
            is_secret = _is_blocked(target_path, blocked_patterns)

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
    try:
        main()
    except Exception:
        sys.exit(0)  # 最終安全網: 想定外のクラッシュでも fail-open
