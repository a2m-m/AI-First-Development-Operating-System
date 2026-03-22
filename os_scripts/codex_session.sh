#!/usr/bin/env bash

# =============================================================================
# os_scripts/codex_session.sh
# =============================================================================
# Description: Codex CLI 双方向セッション管理スクリプト。
#   Claude がコンテキストを渡し、Codex が主導して応答する双方向フローを実現する。
#
# Usage:
#   codex_session.sh start  <session_id> <context_file>
#   codex_session.sh reply  <session_id> "<message>"
#   codex_session.sh end    <session_id>
#
# Session log: os_scripts/codex_sessions/<session_id>.log
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# 定数
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SESSIONS_DIR="${SCRIPT_DIR}/codex_sessions"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
AGENTS_MD="${REPO_ROOT}/AGENTS.md"

# ---------------------------------------------------------------------------
# ヘルパー
# ---------------------------------------------------------------------------

usage() {
    echo "Usage:"
    echo "  $(basename "$0") [--no-inject] start <session_id> <context_file>"
    echo "  $(basename "$0") reply <session_id> \"<message>\""
    echo "  $(basename "$0") end   <session_id>"
    echo ""
    echo "Options:"
    echo "  --no-inject  AGENTS.md を system prompt に注入しない（CLI 自動参照時の二重注入防止）"
    exit 1
}

check_codex() {
    if ! command -v codex >/dev/null 2>&1; then
        echo "Error: 'codex' CLI が見つかりません。" >&2
        echo "  インストール方法: npm install -g @openai/codex" >&2
        exit 1
    fi
}

validate_session_id() {
    local session_id="$1"
    if [[ -z "${session_id}" ]]; then
        echo "Error: session_id が空です。" >&2
        exit 1
    fi
    # パストラバーサル防止: スラッシュや .. を禁止
    if [[ "${session_id}" =~ [/\\] ]] || [[ "${session_id}" == *".."* ]]; then
        echo "Error: session_id に無効な文字が含まれています: '${session_id}'" >&2
        exit 1
    fi
}

run_codex() {
    local prompt="$1"
    local response
    if ! response="$(echo "${prompt}" | codex -q 2>&1)"; then
        echo "Error: Codex の実行に失敗しました。" >&2
        echo "  詳細: ${response}" >&2
        exit 1
    fi
    echo "${response}"
}

session_log() {
    local session_id="$1"
    echo "${SESSIONS_DIR}/${session_id}.log"
}

require_session() {
    local log_file
    log_file="$(session_log "$1")"
    if [[ ! -f "${log_file}" ]]; then
        echo "Error: セッション '$1' が存在しません。先に 'start' を実行してください。" >&2
        exit 1
    fi
    echo "${log_file}"
}

load_agents_md() {
    if [[ -f "${AGENTS_MD}" ]]; then
        cat "${AGENTS_MD}"
    fi
}

append_log() {
    local log_file="$1"
    local role="$2"   # "Claude" or "Codex"
    local content="$3"
    {
        echo ""
        echo "## ${role}"
        echo ""
        echo "${content}"
    } >> "${log_file}"
}

build_prompt() {
    local log_file="$1"
    local new_message="$2"

    cat "${log_file}"
    echo ""
    echo "## Claude"
    echo ""
    echo "${new_message}"
    echo ""
    echo "---"
    echo ""
    echo "上記の会話履歴を踏まえて、Codex として応答してください。"
}

# ---------------------------------------------------------------------------
# サブコマンド
# ---------------------------------------------------------------------------

cmd_start() {
    local session_id="$1"
    local context_file="$2"
    local inject_agents="${3:-true}"

    validate_session_id "${session_id}"

    if [[ ! -f "${context_file}" ]]; then
        echo "Error: コンテキストファイル '${context_file}' が見つかりません。" >&2
        exit 1
    fi

    local log_file
    log_file="$(session_log "${session_id}")"

    if [[ -f "${log_file}" ]]; then
        echo "Error: セッション '${session_id}' は既に存在します。別の session_id を使うか 'end' で終了してください。" >&2
        exit 1
    fi

    mkdir -p "${SESSIONS_DIR}"

    # ログ初期化
    {
        echo "# Codex セッション: ${session_id}"
        echo ""
        echo "開始日時: $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
        echo "---"
        echo ""
        echo "## コンテキスト"
        echo ""
        cat "${context_file}"
        echo ""
        echo "---"
    } > "${log_file}"

    # 初回プロンプト生成（AGENTS.md を先頭に注入）
    local agents_content=""
    if [[ "${inject_agents}" == "true" ]]; then
        agents_content="$(load_agents_md)"
    fi

    local prompt
    if [[ -n "${agents_content}" ]]; then
        prompt="${agents_content}"$'\n\n'"---"$'\n\n'"$(cat "${context_file}")"$'\n\n'"上記のコンテキストを読んで、Codex としてレビュー・質問・調査の観点を示してください。"
    else
        prompt="$(cat "${context_file}")"$'\n\n'"上記のコンテキストを読んで、Codex としてレビュー・質問・調査の観点を示してください。"
    fi

    echo "--- Codex 初回応答 (session: ${session_id}) ---"
    local response
    response="$(run_codex "${prompt}")"
    echo "${response}"
    echo "---"

    # 応答をログに追記
    append_log "${log_file}" "Codex" "${response}"

    echo ""
    echo "セッション開始: ${log_file}"
}

cmd_reply() {
    local session_id="$1"
    local message="$2"

    validate_session_id "${session_id}"

    local log_file
    log_file="$(require_session "${session_id}")"

    # 会話履歴 + 今回のメッセージからプロンプトを構築
    local prompt
    prompt="$(build_prompt "${log_file}" "${message}")"

    echo "--- Codex 応答 (session: ${session_id}) ---"
    local response
    response="$(run_codex "${prompt}")"
    echo "${response}"
    echo "---"

    # Claude の発言とCodex の応答をログに追記
    append_log "${log_file}" "Claude" "${message}"
    append_log "${log_file}" "Codex" "${response}"
}

cmd_end() {
    local session_id="$1"

    validate_session_id "${session_id}"

    local log_file
    log_file="$(require_session "${session_id}")"

    {
        echo ""
        echo "---"
        echo ""
        echo "終了日時: $(date '+%Y-%m-%d %H:%M:%S')"
    } >> "${log_file}"

    echo "セッション終了: ${log_file}"
}

# ---------------------------------------------------------------------------
# エントリーポイント
# ---------------------------------------------------------------------------

if [[ $# -lt 1 ]]; then
    usage
fi

# --no-inject フラグの解析
INJECT_AGENTS="true"
if [[ "$1" == "--no-inject" ]]; then
    INJECT_AGENTS="false"
    shift
fi

if [[ $# -lt 1 ]]; then
    usage
fi

SUBCOMMAND="$1"
shift

check_codex

case "${SUBCOMMAND}" in
    start)
        if [[ $# -lt 2 ]]; then
            echo "Error: 'start' には session_id と context_file が必要です。" >&2
            usage
        fi
        cmd_start "$1" "$2" "${INJECT_AGENTS}"
        ;;
    reply)
        if [[ $# -lt 2 ]]; then
            echo "Error: 'reply' には session_id と message が必要です。" >&2
            usage
        fi
        cmd_reply "$1" "$2"
        ;;
    end)
        if [[ $# -lt 1 ]]; then
            echo "Error: 'end' には session_id が必要です。" >&2
            usage
        fi
        cmd_end "$1"
        ;;
    *)
        echo "Error: 不明なサブコマンド '${SUBCOMMAND}'" >&2
        usage
        ;;
esac
