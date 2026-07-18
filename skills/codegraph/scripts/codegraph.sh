#!/usr/bin/env bash
set -euo pipefail

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
    command -v codegraph || fail "找不到 codegraph。请先运行 npm i -g @colbymchenry/codegraph，或设置 CODEGRAPH_BIN。"
}

require_project() {
    local project="${1:-}"
    [[ -n "$project" ]] || fail "缺少 project 参数。"
    printf '%s\n' "$project"
}

cmd="${1:-help}"
if [[ "$cmd" == "-h" || "$cmd" == "--help" || "$cmd" == "help" ]]; then
    usage
    exit 0
fi
shift || true

bin="$(codegraph_bin)"

case "$cmd" in
    check)
        "$bin" --version
    ;;
    
    raw)
        [[ "$#" -gt 0 ]] || fail "raw 需要传入 codegraph 原生命令参数。"
        exec "$bin" "$@"
    ;;
    
    init)
        project="$(require_project "${1:-}")"
        shift || true
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
            exec "$bin" status "${args[@]}" "$project"
        fi
        exec "$bin" status "${args[@]}" --json "$project"
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
            exec "$bin" query --path "$project" "${args[@]}" "$search"
        fi
        exec "$bin" query --path "$project" "${args[@]}" --json "$search"
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
            exec "$bin" files --path "$project" "${args[@]}"
        fi
        exec "$bin" files --path "$project" "${args[@]}" --json
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
            exec "$bin" "$cmd" --path "$project" "${args[@]}" "$symbol"
        fi
        exec "$bin" "$cmd" --path "$project" "${args[@]}" --json "$symbol"
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
            exec "$bin" impact --path "$project" "${args[@]}" "$symbol"
        fi
        exec "$bin" impact --path "$project" "${args[@]}" --json "$symbol"
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
            exec "$bin" affected --path "$project" "${args[@]}" "${files[@]}"
        fi
        exec "$bin" affected --path "$project" "${args[@]}" --json "${files[@]}"
    ;;
    
    unlock)
        project="$(require_project "${1:-}")"
        shift || true
        [[ "$#" -eq 0 ]] || fail "unlock 不接受额外参数。"
        exec "$bin" unlock "$project"
    ;;
    
    upgrade)
        help_text="$("$bin" --help 2>/dev/null || true)"
        if [[ "$help_text" == *"upgrade [version]"* ]]; then
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
