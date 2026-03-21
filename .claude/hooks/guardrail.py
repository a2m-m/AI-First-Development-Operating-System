#!/usr/bin/env python3
import sys
import json
import os
import fnmatch
import shlex
import re
from functools import lru_cache

# デフォルトの機密ファイル遮断パターン（project_config.yml 未設定時のフォールバック）
_DEFAULT_BLOCKED_PATTERNS = [
    ".env",
    ".env.*",
    "**/.env",
    "**/.env.*",
    "credentials*",
    "**/credentials*",
    "secret*",
    "**/secret*",
    "**/.secret*",
    "**/secrets.json",
    "**/secrets.yaml",
]

_SHELL_OPERATORS = {
    "|",
    "||",
    "&&",
    ";",
    "&",
    "(",
    ")",
    "<",
    "<<",
    ">",
    ">>",
    "1>",
    "1>>",
    "2>",
    "2>>",
    "&>",
}

def _normalize_match_path(value):
    return str(value or "").replace("\\", "/")

@lru_cache(maxsize=32)
def _compile_blocked_patterns(patterns):
    compiled = []
    for raw_pattern in patterns:
        pattern = _normalize_match_path(raw_pattern)
        compiled.append(("full", re.compile(fnmatch.translate(pattern))))

        if "/" not in pattern:
            compiled.append(("basename", re.compile(fnmatch.translate(pattern))))
        elif pattern.startswith("**/"):
            compiled.append(("basename", re.compile(fnmatch.translate(pattern[3:]))))

    return compiled


def _load_blocked_patterns():
    """project_config.yml から security.blocked_file_patterns を読み込む。
    未設定・読み込み失敗時はデフォルトパターンを返す。"""
    try:
        hooks_dir = os.path.dirname(os.path.abspath(__file__))
        claude_dir = os.path.dirname(hooks_dir)
        repo_root = os.path.dirname(claude_dir)
        scripts_lib = os.path.join(repo_root, "os_scripts", "lib")
        os_template = os.path.join(repo_root, "project_config.yml")

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
    full = _normalize_match_path(path)
    name = full.rsplit("/", 1)[-1]
    for scope, pattern in _compile_blocked_patterns(tuple(patterns)):
        target = full if scope == "full" else name
        if pattern.match(target):
            return True
    return False

def _iter_bash_candidates(command):
    """Split a Bash command and yield path-like candidates for secret checks."""
    text = str(command or "")

    try:
        tokens = shlex.split(text, posix=True)
    except ValueError:
        tokens = text.split()

    for token in tokens:
        candidate = token.strip().strip("'\"")
        if not candidate or candidate in _SHELL_OPERATORS:
            continue

        yield candidate

        if "=" in candidate:
            _, rhs = candidate.split("=", 1)
            rhs = rhs.strip().strip("'\"")
            if rhs:
                yield rhs

def _find_blocked_bash_reference(command, patterns):
    for candidate in _iter_bash_candidates(command):
        if _is_blocked(candidate, patterns):
            return candidate
    return None

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
            print(f"SECURITY BLOCK: Access to secret file '{target_path}' is strictly prohibited by the template security policy.", file=sys.stderr)
            sys.exit(2)

        if tool_name == "Bash":
            command = tool_input.get("command", "")
            blocked_ref = _find_blocked_bash_reference(command, blocked_patterns)
            if blocked_ref:
                print(f"SECURITY BLOCK: Bash command references a secret file '{blocked_ref}'. Command blocked.", file=sys.stderr)
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
