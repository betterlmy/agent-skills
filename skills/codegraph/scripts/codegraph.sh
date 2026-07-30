#!/usr/bin/env bash
set -euo pipefail

verified_codegraph_version="1.4.1"

usage() {
  cat <<'EOF'
CodeGraph CLI wrapper

用法:
  codegraph.sh check
  codegraph.sh raw <codegraph-args...>
  codegraph.sh init <project> [--verbose]
  codegraph.sh uninit <project> [--force]
  codegraph.sh index <project> [--force] [--quiet] [--verbose]
  codegraph.sh sync <project> [--quiet]
  codegraph.sh status <project> [--no-json]
  codegraph.sh explore <project> <query...> [--max-files N]
  codegraph.sh node <project> [name] [--file FILE] [--offset N] [--limit N] [--symbols-only]
  codegraph.sh query <project> <search> [--limit N] [--kind KIND] [--no-json]
  codegraph.sh files <project> [--filter DIR] [--pattern GLOB] [--format tree|flat|grouped] [--max-depth N] [--no-metadata] [--no-json]
  codegraph.sh callers <project> <symbol> [--limit N] [--no-json]
  codegraph.sh callees <project> <symbol> [--limit N] [--no-json]
  codegraph.sh impact <project> <symbol> [--depth N] [--no-json]
  codegraph.sh affected <project> [files...] [--stdin] [--depth N] [--filter GLOB] [--quiet] [--no-json]
  codegraph.sh unlock <project>
  codegraph.sh upgrade [version] [--check] [--force]

环境变量:
  CODEGRAPH_BIN  指定 codegraph 可执行文件，默认从 PATH 查找。

说明:
  查询类命令默认输出 JSON；需要原始可读输出时加 --no-json。
EOF
}

fail() {
    printf '错误: %s\n' "$*" >&2
    exit 1
}

codegraph_bin() {
    if [[ -n "${CODEGRAPH_BIN:-}" ]]; then
        printf '%s\n' "$CODEGRAPH_BIN"
        return
    fi
    command -v codegraph || fail "找不到 codegraph。请先获得用户同意后安装 CLI，或设置 CODEGRAPH_BIN。"
}

require_project() {
    local project="${1:-}"
    [[ -n "$project" ]] || fail "缺少 project 参数。"
    printf '%s\n' "$project"
}

ensure_index_ignored() {
    local project="$1"
    command -v git >/dev/null 2>&1 || return 0
    git -C "$project" rev-parse --is-inside-work-tree >/dev/null 2>&1 || return 0

    local probe
    probe="$(cd "$project" && pwd -P)/.codegraph/.ignore-check"
    if ! git -C "$project" check-ignore -q --no-index -- "$probe"; then
        fail "项目未忽略 .codegraph/。请先获得用户同意并在适用的 .gitignore 中加入 .codegraph/ 或 **/.codegraph/。"
    fi
}

cmd="${1:-help}"
if [[ "$cmd" == "-h" || "$cmd" == "--help" || "$cmd" == "help" ]]; then
    usage
    exit 0
fi
shift || true

bin="$(codegraph_bin)"

if [[ "$cmd" != "raw" && ( "${1:-}" == "-h" || "${1:-}" == "--help" ) ]]; then
    exec "$bin" "$cmd" --help
fi

case "$cmd" in
    check)
        current_version="$("$bin" --version)"
        printf '%s\n' "$current_version"
        if [[ "${current_version#v}" != "$verified_codegraph_version" ]]; then
            printf '警告: 当前 CodeGraph 版本为 %s，本 Skill 本机验证版本为 %s；将继续检查关键能力。\n' \
                "$current_version" "$verified_codegraph_version" >&2
        fi
        for capability in status explore node affected; do
            if ! "$bin" "$capability" --help >/dev/null 2>&1; then
                fail "当前 CodeGraph 缺少必需能力: $capability --help"
            fi
        done
    ;;

    raw)
        [[ "$#" -gt 0 ]] || fail "raw 需要传入 codegraph 原生命令参数。"
        exec "$bin" "$@"
    ;;

    init)
        project="$(require_project "${1:-}")"
        shift || true
        ensure_index_ignored "$project"
        exec "$bin" init "$@" "$project"
    ;;

    uninit)
        project="$(require_project "${1:-}")"
        shift || true
        exec "$bin" uninit "$@" "$project"
    ;;

    index)
        project="$(require_project "${1:-}")"
        shift || true
        exec "$bin" index "$@" "$project"
    ;;

    sync)
        project="$(require_project "${1:-}")"
        shift || true
        exec "$bin" sync "$@" "$project"
    ;;

    status)
        project="$(require_project "${1:-}")"
        shift || true
        no_json=0
        args=()
        while [[ "$#" -gt 0 ]]; do
            case "$1" in
                --no-json) no_json=1 ;;
                *) args+=("$1") ;;
            esac
            shift
        done
        if [[ "$no_json" == "1" ]]; then
            exec "$bin" status ${args[@]+"${args[@]}"} "$project"
        fi
        exec "$bin" status ${args[@]+"${args[@]}"} --json "$project"
    ;;

    explore)
        project="$(require_project "${1:-}")"
        shift || true
        [[ "$#" -gt 0 ]] || fail "explore 缺少 query 参数。"
        exec "$bin" explore --path "$project" "$@"
    ;;

    node)
        project="$(require_project "${1:-}")"
        shift || true
        [[ "$#" -gt 0 ]] || fail "node 需要 symbol、file 或其他查询参数。"
        exec "$bin" node --path "$project" "$@"
    ;;

    query)
        project="$(require_project "${1:-}")"
        shift || true
        search="${1:-}"
        [[ -n "$search" ]] || fail "query 缺少 search 参数。"
        shift || true
        no_json=0
        args=()
        while [[ "$#" -gt 0 ]]; do
            case "$1" in
                --no-json) no_json=1 ;;
                --limit|-l)
                    [[ "${2:-}" ]] || fail "$1 缺少值。"
                    args+=("--limit" "$2")
                    shift
                ;;
                --kind|-k)
                    [[ "${2:-}" ]] || fail "$1 缺少值。"
                    args+=("--kind" "$2")
                    shift
                ;;
                *) args+=("$1") ;;
            esac
            shift
        done
        if [[ "$no_json" == "1" ]]; then
            exec "$bin" query --path "$project" ${args[@]+"${args[@]}"} "$search"
        fi
        exec "$bin" query --path "$project" ${args[@]+"${args[@]}"} --json "$search"
    ;;

    files)
        project="$(require_project "${1:-}")"
        shift || true
        no_json=0
        args=()
        while [[ "$#" -gt 0 ]]; do
            case "$1" in
                --no-json) no_json=1 ;;
                --no-metadata) args+=("--no-metadata") ;;
                --filter|--pattern|--format|--max-depth)
                    [[ "${2:-}" ]] || fail "$1 缺少值。"
                    args+=("$1" "$2")
                    shift
                ;;
                *) args+=("$1") ;;
            esac
            shift
        done
        if [[ "$no_json" == "1" ]]; then
            exec "$bin" files --path "$project" ${args[@]+"${args[@]}"}
        fi
        exec "$bin" files --path "$project" ${args[@]+"${args[@]}"} --json
    ;;

    callers|callees)
        project="$(require_project "${1:-}")"
        shift || true
        symbol="${1:-}"
        [[ -n "$symbol" ]] || fail "$cmd 缺少 symbol 参数。"
        shift || true
        no_json=0
        args=()
        while [[ "$#" -gt 0 ]]; do
            case "$1" in
                --no-json) no_json=1 ;;
                --limit|-l)
                    [[ "${2:-}" ]] || fail "$1 缺少值。"
                    args+=("--limit" "$2")
                    shift
                ;;
                *) args+=("$1") ;;
            esac
            shift
        done
        if [[ "$no_json" == "1" ]]; then
            exec "$bin" "$cmd" --path "$project" ${args[@]+"${args[@]}"} "$symbol"
        fi
        exec "$bin" "$cmd" --path "$project" ${args[@]+"${args[@]}"} --json "$symbol"
    ;;

    impact)
        project="$(require_project "${1:-}")"
        shift || true
        symbol="${1:-}"
        [[ -n "$symbol" ]] || fail "impact 缺少 symbol 参数。"
        shift || true
        no_json=0
        args=()
        while [[ "$#" -gt 0 ]]; do
            case "$1" in
                --no-json) no_json=1 ;;
                --depth|-d)
                    [[ "${2:-}" ]] || fail "$1 缺少值。"
                    args+=("--depth" "$2")
                    shift
                ;;
                *) args+=("$1") ;;
            esac
            shift
        done
        if [[ "$no_json" == "1" ]]; then
            exec "$bin" impact --path "$project" ${args[@]+"${args[@]}"} "$symbol"
        fi
        exec "$bin" impact --path "$project" ${args[@]+"${args[@]}"} --json "$symbol"
    ;;

    affected)
        project="$(require_project "${1:-}")"
        shift || true
        no_json=0
        args=()
        files=()
        while [[ "$#" -gt 0 ]]; do
            case "$1" in
                --no-json) no_json=1 ;;
                --stdin|--quiet|-q) args+=("$1") ;;
                --depth|-d|--filter|-f)
                    [[ "${2:-}" ]] || fail "$1 缺少值。"
                    args+=("$1" "$2")
                    shift
                ;;
                *) files+=("$1") ;;
            esac
            shift
        done
        if [[ "$no_json" == "1" ]]; then
            exec "$bin" affected --path "$project" ${args[@]+"${args[@]}"} ${files[@]+"${files[@]}"}
        fi
        exec "$bin" affected --path "$project" ${args[@]+"${args[@]}"} --json ${files[@]+"${files[@]}"}
    ;;

    unlock)
        project="$(require_project "${1:-}")"
        shift || true
        [[ "$#" -eq 0 ]] || fail "unlock 不接受额外参数。"
        exec "$bin" unlock "$project"
    ;;

    upgrade)
        if "$bin" upgrade --help >/dev/null 2>&1; then
            exec "$bin" upgrade "$@"
        fi

        check=0
        version=""
        while [[ "$#" -gt 0 ]]; do
            case "$1" in
                --check) check=1 ;;
                --force) ;;
                -*)
                    fail "upgrade fallback 不支持参数: $1"
                ;;
                *)
                    version="$1"
                ;;
            esac
            shift
        done

        current="$("$bin" --version 2>/dev/null || printf 'unknown')"
        command -v npm >/dev/null 2>&1 || fail "当前 CodeGraph 不支持原生 upgrade，且找不到 npm；请按官方安装方式重新安装。"
        if [[ "$check" == "1" ]]; then
            latest="$(npm view @colbymchenry/codegraph version)"
            printf 'current=%s\nlatest=%s\n' "$current" "$latest"
            if [[ "$current" == "$latest" ]]; then
                printf 'status=up-to-date\n'
            else
                printf 'status=update-available\n'
            fi
            exit 0
        fi

        if [[ -n "$version" ]]; then
            exec npm i -g "@colbymchenry/codegraph@$version"
        fi
        exec npm i -g @colbymchenry/codegraph
    ;;

    *)
        usage >&2
        fail "未知命令: $cmd"
    ;;
esac
