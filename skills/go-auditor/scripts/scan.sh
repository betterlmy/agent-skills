#!/usr/bin/env bash
# Go 代码质量范围基线：执行格式、vet、静态检查、漏洞扫描与构建检查。
# 默认禁止 Go 工具访问网络，并以只读模块模式运行；不会执行测试或安装工具。
set -uo pipefail
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd -P) || {
  echo "错误：无法解析脚本目录" >&2
  exit 2
}

usage() {
  cat <<'EOF'
用法：scan.sh [选项] [repo-or-module-root]

范围选项（可重复；未指定时递归扫描目标根）：
  --target PATH       扫描一个 Go 文件，或递归扫描一个目录。
  --package-dir DIR   只扫描目录直属的 Go 文件，不递归子 package。
  --diff working      扫描未暂存、已暂存和未跟踪的 Go 变更。
  --diff staged       只扫描暂存区中的 Go 变更。
  --diff-range RANGE  扫描指定 Git revision range 中的 Go 变更。

执行选项：
  --strict            任一可选工具缺失时也返回非零。
  --allow-network     允许 Go 工具沿用环境软件源访问网络；使用前应确认授权。
  --test              显式运行范围内的 Go 测试。
  --race              显式运行范围内的竞态测试（同时启用测试）。
  --cover             显式运行范围内的覆盖率测试（同时启用测试）。
  --test-timeout D    设置测试超时，默认 2m。
  --json-output FILE  将同一份扫描结果原子写入 JSON 文件；需要 Python 3。
  --output-dir DIR    将每项工具的完整原始输出保留到已存在目录。
  -h, --help          显示帮助。

Diff 选项与 --target/--package-dir 互斥。文件与 Diff 范围的 Go 工具检查会扩展到所属 package。

退出码：
  0  已执行检查均通过；非 strict 模式允许存在未运行项或范围内没有 Go 文件。
  1  发现代码问题、工具执行失败，或 strict 模式存在未运行项。
  2  参数、目标目录、Git 或 Go 模块预检失败。
EOF
}

strict=0
allow_network=0
run_tests=0
run_race=0
run_cover=0
test_timeout="2m"
json_output=""
result_output_dir=""
repo_arg="."
repo_arg_set=0
target_kinds=()
target_values=()
diff_kind=""
diff_range=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --strict)
      strict=1
      ;;
    --allow-network)
      allow_network=1
      ;;
    --test)
      run_tests=1
      ;;
    --race)
      run_tests=1
      run_race=1
      ;;
    --cover)
      run_tests=1
      run_cover=1
      ;;
    --test-timeout)
      if [ "$#" -lt 2 ]; then
        echo "错误：--test-timeout 需要 Go duration 参数" >&2
        exit 2
      fi
      case "$2" in
        ''|-*) echo "错误：无效的测试超时：$2" >&2; exit 2 ;;
      esac
      test_timeout="$2"
      shift
      ;;
    --json-output)
      if [ "$#" -lt 2 ]; then
        echo "错误：--json-output 需要文件路径" >&2
        exit 2
      fi
      json_output="$2"
      shift
      ;;
    --output-dir)
      if [ "$#" -lt 2 ]; then
        echo "错误：--output-dir 需要目录路径" >&2
        exit 2
      fi
      result_output_dir="$2"
      shift
      ;;
    --target|--package-dir)
      option_name="$1"
      if [ "$#" -lt 2 ]; then
        echo "错误：$option_name 需要路径参数" >&2
        exit 2
      fi
      if [ "$option_name" = "--target" ]; then
        target_kinds+=("target")
      else
        target_kinds+=("package")
      fi
      target_values+=("$2")
      shift
      ;;
    --diff)
      if [ "$#" -lt 2 ]; then
        echo "错误：--diff 需要 working 或 staged" >&2
        exit 2
      fi
      case "$2" in
        working|staged) ;;
        *) echo "错误：--diff 仅支持 working 或 staged" >&2; exit 2 ;;
      esac
      if [ -n "$diff_kind" ]; then
        echo "错误：只能指定一个 Diff 来源" >&2
        exit 2
      fi
      diff_kind="$2"
      shift
      ;;
    --diff-range)
      if [ "$#" -lt 2 ]; then
        echo "错误：--diff-range 需要 revision range" >&2
        exit 2
      fi
      if [ -n "$diff_kind" ]; then
        echo "错误：只能指定一个 Diff 来源" >&2
        exit 2
      fi
      case "$2" in
        -*) echo "错误：revision range 不能以连字符开头" >&2; exit 2 ;;
      esac
      diff_kind="range"
      diff_range="$2"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      if [ "$#" -gt 1 ]; then
        echo "错误：只能指定一个仓库或模块根目录" >&2
        exit 2
      fi
      if [ "$#" -eq 1 ]; then
        repo_arg="$1"
        repo_arg_set=1
      fi
      break
      ;;
    -*)
      echo "错误：未知选项 $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      if [ "$repo_arg_set" -eq 1 ]; then
        echo "错误：只能指定一个仓库或模块根目录" >&2
        exit 2
      fi
      repo_arg="$1"
      repo_arg_set=1
      ;;
  esac
  shift
done

if [ -n "$diff_kind" ] && [ "${#target_values[@]}" -gt 0 ]; then
  echo "错误：Diff 选项不能与 --target 或 --package-dir 同时使用" >&2
  exit 2
fi

if [ ! -d "$repo_arg" ]; then
  echo "错误：目录不存在：$repo_arg" >&2
  exit 2
fi

repo_root=$(cd "$repo_arg" 2>/dev/null && pwd -P) || {
  echo "错误：无法解析目标根目录：$repo_arg" >&2
  exit 2
}

if [ ! -f "$repo_root/go.mod" ] && [ ! -f "$repo_root/go.work" ]; then
  echo "错误：目标根目录没有 go.mod 或 go.work；多模块仓库请从 go.work 根扫描，或逐个模块运行" >&2
  exit 2
fi

cd "$repo_root" || {
  echo "错误：无法进入目标根目录：$repo_root" >&2
  exit 2
}

if [ -n "$json_output" ]; then
  if ! command -v python3 >/dev/null 2>&1; then
    echo "错误：--json-output 需要 Python 3" >&2
    exit 2
  fi
  if [ -L "$json_output" ] || [ -d "$json_output" ]; then
    echo "错误：JSON 输出目标不能是符号链接或目录：$json_output" >&2
    exit 2
  fi
  json_parent=$(dirname "$json_output")
  if [ ! -d "$json_parent" ]; then
    echo "错误：JSON 输出目录不存在：$json_parent" >&2
    exit 2
  fi
  json_parent_abs=$(cd "$json_parent" 2>/dev/null && pwd -P) || {
    echo "错误：无法解析 JSON 输出目录：$json_parent" >&2
    exit 2
  }
  json_output="$json_parent_abs/$(basename "$json_output")"
fi

if [ -n "$result_output_dir" ]; then
  if [ -L "$result_output_dir" ] || [ ! -d "$result_output_dir" ]; then
    echo "错误：--output-dir 必须是已存在的非符号链接目录：$result_output_dir" >&2
    exit 2
  fi
  result_output_dir=$(cd "$result_output_dir" 2>/dev/null && pwd -P) || {
    echo "错误：无法解析原始输出目录：$result_output_dir" >&2
    exit 2
  }
  if find "$result_output_dir" -mindepth 1 -maxdepth 1 -print -quit | grep -q .; then
    echo "错误：--output-dir 必须为空，避免覆盖已有文件：$result_output_dir" >&2
    exit 2
  fi
fi

output_file=$(mktemp "${TMPDIR:-/tmp}/go-auditor.XXXXXX") || {
  echo "错误：无法创建临时文件" >&2
  exit 2
}
error_file=$(mktemp "${TMPDIR:-/tmp}/go-auditor-error.XXXXXX") || {
  rm -f "$output_file"
  echo "错误：无法创建错误输出临时文件" >&2
  exit 2
}
event_file=$(mktemp "${TMPDIR:-/tmp}/go-auditor-events.XXXXXX") || {
  rm -f "$output_file" "$error_file"
  echo "错误：无法创建事件临时文件" >&2
  exit 2
}
command_file=$(mktemp "${TMPDIR:-/tmp}/go-auditor-commands.XXXXXX") || {
  rm -f "$output_file" "$error_file" "$event_file"
  echo "错误：无法创建命令临时文件" >&2
  exit 2
}
metadata_file=$(mktemp "${TMPDIR:-/tmp}/go-auditor-metadata.XXXXXX") || {
  rm -f "$output_file" "$error_file" "$event_file" "$command_file"
  echo "错误：无法创建元数据临时文件" >&2
  exit 2
}
cleanup() {
  rm -f "$output_file" "$error_file" "$event_file" "$command_file" "$metadata_file"
}
trap cleanup EXIT HUP INT TERM

passed=0
issues=0
failed=0
blocked=0
unclassified=0
skipped=0
scan_files=()
package_patterns=()
scope_labels=()
diff_paths=()
diff_deleted=0
reported_tool_versions=()
output_sequence=0

say() {
  printf '\n=== %s ===\n' "$1"
}

have() {
  command -v "$1" >/dev/null 2>&1
}

report_tool_version() {
  tool_name="$1"
  for reported_tool in "${reported_tool_versions[@]}"; do
    [ "$reported_tool" = "$tool_name" ] && return
  done
  reported_tool_versions+=("$tool_name")
  case "$tool_name" in
    go) version_command=(go version) ;;
    staticcheck) version_command=(staticcheck -version) ;;
    golangci-lint) version_command=(golangci-lint version) ;;
    govulncheck) version_command=(govulncheck -version) ;;
    *) return ;;
  esac
  version_output=$("${version_command[@]}" 2>&1)
  version_status=$?
  if [ "$version_status" -eq 0 ] && [ -n "$version_output" ]; then
    printf '工具版本（%s）：%s\n' "$tool_name" "$(printf '%s\n' "$version_output" | sed -n '1p')"
  else
    printf '工具版本（%s）：无法读取（退出码 %s）\n' "$tool_name" "$version_status"
  fi
}

mark_pass() {
  passed=$((passed + 1))
  printf '通过\0%s\0' "$1" >>"$event_file"
  printf '[通过] %s\n' "$1"
}

mark_issue() {
  issues=$((issues + 1))
  printf '发现问题\0%s\0' "$1" >>"$event_file"
  printf '[发现问题] %s\n' "$1"
}

mark_failure() {
  failed=$((failed + 1))
  printf '工具失败\0%s\0' "$1" >>"$event_file"
  printf '[工具失败] %s\n' "$1"
}

mark_blocked() {
  blocked=$((blocked + 1))
  printf '前置条件未满足\0%s\0' "$1" >>"$event_file"
  printf '[前置条件未满足] %s\n' "$1"
}

mark_unclassified() {
  unclassified=$((unclassified + 1))
  printf '未分类失败\0%s\0' "$1" >>"$event_file"
  printf '[未分类失败] %s\n' "$1"
}

mark_skip() {
  skipped=$((skipped + 1))
  printf '未运行\0%s：%s\0' "$1" "$2" >>"$event_file"
  printf '[未运行] %s：%s\n' "$1" "$2"
}

print_output() {
  last_output_truncated=0
  if [ -s "$output_file" ]; then
    sed -n '1,400p' "$output_file"
    line_count=$(wc -l <"$output_file")
    if [ "$line_count" -gt 400 ]; then
      last_output_truncated=1
      printf '输出已截断：共 %s 行，仅显示前 400 行\n' "$line_count"
    fi
  fi
}

preserve_output() {
  output_slug="$1"
  preserved_output=""
  [ -n "$result_output_dir" ] || return
  output_sequence=$((output_sequence + 1))
  printf -v output_number '%03d' "$output_sequence"
  safe_slug=$(printf '%s' "$output_slug" | tr -c 'A-Za-z0-9._-' '-')
  preserved_output="$result_output_dir/$output_number-$safe_slug.log"
  if ! cp "$output_file" "$preserved_output"; then
    preserved_output=""
    mark_failure "完整输出保留失败：$output_slug"
    return
  fi
  printf '完整输出：%s\n' "$preserved_output"
}

add_scan_file() {
  candidate="$1"
  for existing in "${scan_files[@]}"; do
    [ "$existing" = "$candidate" ] && return
  done
  scan_files+=("$candidate")
}

add_package_pattern() {
  candidate="$1"
  for existing in "${package_patterns[@]}"; do
    [ "$existing" = "$candidate" ] && return
  done
  package_patterns+=("$candidate")
}

add_scope_label() {
  scope_labels+=("$1")
}

resolve_scope_path() {
  raw_path="$1"
  case "$raw_path" in
    /*) candidate_path="$raw_path" ;;
    *) candidate_path="$repo_root/$raw_path" ;;
  esac

  if [ -L "$candidate_path" ]; then
    echo "错误：范围路径不能是符号链接：$raw_path" >&2
    exit 2
  fi
  if [ -d "$candidate_path" ]; then
    resolved_abs=$(cd "$candidate_path" 2>/dev/null && pwd -P) || {
      echo "错误：无法解析范围目录：$raw_path" >&2
      exit 2
    }
    resolved_type="directory"
  elif [ -f "$candidate_path" ]; then
    resolved_parent=$(cd "$(dirname "$candidate_path")" 2>/dev/null && pwd -P) || {
      echo "错误：无法解析范围文件：$raw_path" >&2
      exit 2
    }
    resolved_abs="$resolved_parent/$(basename "$candidate_path")"
    resolved_type="file"
  else
    echo "错误：范围路径不存在：$raw_path" >&2
    exit 2
  fi

  case "$resolved_abs" in
    "$repo_root") resolved_rel="." ;;
    "$repo_root"/*) resolved_rel="./${resolved_abs#"$repo_root"/}" ;;
    *) echo "错误：范围路径位于目标根之外：$raw_path" >&2; exit 2 ;;
  esac
}

add_exact_package_for_file() {
  file_path="$1"
  package_dir=$(dirname "$file_path")
  if [ "$package_dir" = "." ]; then
    add_package_pattern "."
  else
    add_package_pattern "$package_dir"
  fi
}

collect_file_target() {
  file_path="$1"
  case "$file_path" in
    *.go) ;;
    *) echo "错误：文件范围必须是 .go 文件：$file_path" >&2; exit 2 ;;
  esac
  add_scan_file "$file_path"
  add_exact_package_for_file "$file_path"
}

collect_recursive_directory() {
  directory_path="$1"
  before_count=${#scan_files[@]}
  if have git && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git_path=${directory_path#./}
    if [ "$git_path" = "." ]; then
      git_pathspec="*.go"
    else
      git_pathspec="$git_path"
    fi
    while IFS= read -r -d '' go_file; do
      case "$go_file" in
        *.go) add_scan_file "./${go_file#./}" ;;
      esac
    done < <(git ls-files -z --cached --others --exclude-standard -- "$git_pathspec")
  else
    while IFS= read -r -d '' go_file; do
      add_scan_file "$go_file"
    done < <(
      find "$directory_path" \
        -type d \( -name .git -o -name vendor \) -prune -o \
        -type f -name '*.go' -print0
    )
  fi
  if [ "${#scan_files[@]}" -gt "$before_count" ]; then
    if [ "$directory_path" = "." ]; then
      add_package_pattern "./..."
    else
      add_package_pattern "$directory_path/..."
    fi
  fi
}

collect_package_directory() {
  directory_path="$1"
  before_count=${#scan_files[@]}
  if have git && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git_path=${directory_path#./}
    while IFS= read -r -d '' go_file; do
      case "$go_file" in
        */*) go_parent=$(dirname "$go_file") ;;
        *) go_parent="." ;;
      esac
      if [ "$go_parent" = "$git_path" ] || { [ "$git_path" = "." ] && [ "$go_parent" = "." ]; }; then
        add_scan_file "./${go_file#./}"
      fi
    done < <(git ls-files -z --cached --others --exclude-standard -- "$git_path")
  else
    for go_file in "$directory_path"/*.go; do
      [ -f "$go_file" ] || continue
      [ -L "$go_file" ] && continue
      add_scan_file "$go_file"
    done
  fi
  if [ "${#scan_files[@]}" -gt "$before_count" ]; then
    add_package_pattern "$directory_path"
  fi
}

add_diff_path() {
  git_path="$1"
  for existing in "${diff_paths[@]}"; do
    [ "$existing" = "$git_path" ] && return
  done
  diff_paths+=("$git_path")

  case "$git_path" in
    *.go) ;;
    *) return ;;
  esac

  current_path="./$git_path"
  if [ -f "$current_path" ] && [ ! -L "$current_path" ]; then
    add_scan_file "$current_path"
  else
    diff_deleted=$((diff_deleted + 1))
  fi

  owner_dir=$(dirname "$current_path")
  if directory_has_buildable_go_file "$owner_dir"; then
    add_package_pattern "$owner_dir"
  fi
}

directory_has_buildable_go_file() {
  directory_path="$1"
  [ -d "$directory_path" ] || return 1
  for go_file in "$directory_path"/*.go; do
    [ -f "$go_file" ] || continue
    [ -L "$go_file" ] && continue
    case "$go_file" in
      *_test.go) continue ;;
    esac
    if have git && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      git_file=${go_file#./}
      if git check-ignore -q -- "$git_file" && ! git ls-files --error-unmatch -- "$git_file" >/dev/null 2>&1; then
        continue
      fi
    fi
    return 0
  done
  return 1
}

read_diff_output() {
  while IFS= read -r -d '' git_path; do
    add_diff_path "$git_path"
  done <"$output_file"
}

run_git_paths() {
  append_mode="$1"
  shift
  if [ "$append_mode" = "replace" ]; then
    : >"$output_file"
  fi
  : >"$error_file"
  "$@" >>"$output_file" 2>"$error_file"
  git_status=$?
  if [ "$git_status" -ne 0 ]; then
    echo "错误：无法读取 Git diff（退出码 $git_status）" >&2
    if [ -s "$error_file" ]; then
      sed -n '1,10p' "$error_file" >&2
    fi
    exit 2
  fi
}

collect_diff_scope() {
  if ! have git || ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "错误：Diff 范围需要目标位于 Git 工作树中" >&2
    exit 2
  fi

  case "$diff_kind" in
    working)
      run_git_paths replace git diff --relative -z --name-only --diff-filter=ACMRD -- '*.go'
      run_git_paths append git diff --cached --relative -z --name-only --diff-filter=ACMRD -- '*.go'
      run_git_paths append git ls-files -z --others --exclude-standard -- '*.go'
      add_scope_label "diff:working"
      ;;
    staged)
      run_git_paths replace git diff --cached --relative -z --name-only --diff-filter=ACMRD -- '*.go'
      add_scope_label "diff:staged"
      ;;
    range)
      run_git_paths replace git diff --relative -z --name-only --diff-filter=ACMRD "$diff_range" -- '*.go'
      add_scope_label "diff-range:$diff_range"
      ;;
  esac
  read_diff_output
}

if [ -n "$diff_kind" ]; then
  collect_diff_scope
elif [ "${#target_values[@]}" -eq 0 ]; then
  collect_recursive_directory "."
  add_scope_label "recursive:."
else
  target_index=0
  while [ "$target_index" -lt "${#target_values[@]}" ]; do
    target_kind="${target_kinds[$target_index]}"
    target_value="${target_values[$target_index]}"
    resolve_scope_path "$target_value"
    if [ "$target_kind" = "package" ]; then
      if [ "$resolved_type" != "directory" ]; then
        echo "错误：--package-dir 只能指定目录：$target_value" >&2
        exit 2
      fi
      collect_package_directory "$resolved_rel"
      add_scope_label "package:$resolved_rel"
    elif [ "$resolved_type" = "file" ]; then
      collect_file_target "$resolved_rel"
      add_scope_label "file:$resolved_rel"
    else
      collect_recursive_directory "$resolved_rel"
      add_scope_label "recursive:$resolved_rel"
    fi
    target_index=$((target_index + 1))
  done
fi

go_env=("GOTOOLCHAIN=local")
if [ "$allow_network" -eq 0 ]; then
  go_env+=("GOPROXY=off")
fi

if [ -f go.work ]; then
  go_env+=("GOWORK=$repo_root/go.work")
else
  go_env+=("GOWORK=off")
fi

module_mode="readonly"
if [ -f vendor/modules.txt ] && [ ! -f go.work ]; then
  module_mode="vendor"
fi

sanitize_goflags() {
  inherited_flags="${GOFLAGS-}"
  safe_flags=()
  inherited_parts=()
  skip_next=0
  if [ -n "$inherited_flags" ]; then
    case "$inherited_flags" in
      *\'*|*\"*|*\\*)
        printf '提示：继承的 GOFLAGS 包含引号或转义，无法安全解析，已忽略并强制模块只读\n'
        inherited_flags=""
        ;;
    esac
  fi
  read -r -a inherited_parts <<<"$inherited_flags"
  for inherited_part in "${inherited_parts[@]}"; do
    if [ "$skip_next" -eq 1 ]; then
      skip_next=0
      continue
    fi
    case "$inherited_part" in
      -C|-exec|-mod|-modfile|-overlay|-toolexec|-vettool)
        skip_next=1
        printf '提示：已过滤继承的 GOFLAGS 参数 %s 及其值\n' "$inherited_part"
        ;;
      -C=*|-exec=*|-mod=*|-modfile=*|-overlay=*|-toolexec=*|-vettool=*)
        printf '提示：已过滤继承的 GOFLAGS 参数 %s\n' "$inherited_part"
        ;;
      *) safe_flags+=("$inherited_part") ;;
    esac
  done
  safe_flags+=("-mod=$module_mode")
  effective_go_flags="${safe_flags[*]}"
}

sanitize_goflags
go_env+=("GOFLAGS=$effective_go_flags")

output_matches_environment_failure() {
  failure_pattern='module lookup disabled by GOPROXY=off|missing go.sum entry|cannot find module providing package|no required module provides package|toolchain upgrade needed|permission denied|no space left on device|connection refused|network is unreachable|i/o timeout|race detector is not supported|-race requires cgo'
  if have rg; then
    rg -qi "$failure_pattern" "$output_file"
  else
    grep -Eqi "$failure_pattern" "$output_file"
  fi
}

package_probe_ok=0
package_count="未知"
package_names=()
probe_packages() {
  if [ "${#package_patterns[@]}" -eq 0 ]; then
    package_count=0
    return
  fi
  if ! have go; then
    return
  fi
  : >"$output_file"
  env "${go_env[@]}" go list -f '{{.ImportPath}}' "${package_patterns[@]}" >"$output_file" 2>&1
  probe_status=$?
  preserve_output "go-list"
  if [ "$probe_status" -ne 0 ]; then
    print_output
    if output_matches_environment_failure; then
      mark_blocked "package 解析失败；后续 Go 语义工具级联跳过（退出码 $probe_status）"
    elif [ ! -s "$output_file" ]; then
      mark_unclassified "package 解析无诊断退出（退出码 $probe_status）"
    else
      mark_unclassified "package 解析失败；后续 Go 语义工具级联跳过（退出码 $probe_status）"
    fi
    return
  fi
  while IFS= read -r package_name; do
    [ -n "$package_name" ] && package_names+=("$package_name")
  done <"$output_file"
  package_count=${#package_names[@]}
  package_probe_ok=1
}

run_command() {
  check_name="$1"
  required_tool="$2"
  command_kind="$3"
  shift 3

  if ! have "$required_tool"; then
    mark_skip "$check_name" "未安装 $required_tool"
    return
  fi

  report_tool_version "$required_tool"
  command_display=""
  for command_part in "$@"; do
    printf -v quoted_part '%q' "$command_part"
    command_display="${command_display}${command_display:+ }$quoted_part"
  done
  printf '工作目录：%s\n' "$repo_root"
  printf '命令：%s\n' "$command_display"
  : >"$output_file"
  command_started=$SECONDS
  "$@" >"$output_file" 2>&1
  command_status=$?
  command_elapsed=$((SECONDS - command_started))
  printf '退出码：%s；耗时：%ss\n' "$command_status" "$command_elapsed"
  print_output
  preserve_output "$required_tool"
  printf '%s\0%s\0%s\0%s\0%s\0%s\0%s\0' \
    "$check_name" "$command_kind" "$command_display" "$command_status" "$command_elapsed" "$last_output_truncated" "$preserved_output" >>"$command_file"
  if [ "$command_status" -eq 0 ]; then
    mark_pass "$check_name"
  elif output_matches_environment_failure; then
    mark_blocked "$check_name（退出码 $command_status）"
  elif [ ! -s "$output_file" ]; then
    mark_unclassified "$check_name 无诊断退出（退出码 $command_status）"
  elif [ "$command_status" -eq 126 ] || [ "$command_status" -eq 127 ]; then
    mark_failure "$check_name（退出码 $command_status）"
  else
    case "$command_kind" in
      analyzer|build|test) mark_issue "$check_name（退出码 $command_status）" ;;
      *) mark_unclassified "$check_name（退出码 $command_status）" ;;
    esac
  fi
}

run_format_check() {
  check_name="$1"
  format_tool="$2"

  if [ "${#scan_files[@]}" -eq 0 ]; then
    mark_skip "$check_name" "范围内没有当前 Go 文件"
    return
  fi
  if ! have "$format_tool"; then
    mark_skip "$check_name" "未安装 $format_tool"
    return
  fi

  : >"$output_file"
  drift_count=0
  error_count=0
  for go_file in "${scan_files[@]}"; do
    format_output=$("$format_tool" -l "$go_file" 2>&1)
    format_status=$?
    if [ "$format_status" -ne 0 ]; then
      error_count=$((error_count + 1))
      printf '%s\n' "$format_output" >>"$output_file"
    elif [ -n "$format_output" ]; then
      drift_count=$((drift_count + 1))
      printf '%s\n' "$format_output" >>"$output_file"
    fi
  done

  print_output
  preserve_output "$format_tool"
  if [ "$error_count" -gt 0 ]; then
    mark_failure "$check_name：$error_count 个文件无法检查"
  elif [ "$drift_count" -gt 0 ]; then
    mark_issue "$check_name：$drift_count/${#scan_files[@]} 个文件存在漂移"
  else
    mark_pass "$check_name：已检查 ${#scan_files[@]} 个文件"
  fi
}

if [ "${#package_patterns[@]}" -eq 1 ]; then
  package_label="${package_patterns[0]}"
else
  package_label="${#package_patterns[@]} 个 package 范围"
fi

say "预检"
printf '目标根：%s\n' "$repo_root"
printf '审计范围：\n'
for scope_label in "${scope_labels[@]}"; do
  printf '  - %s\n' "$scope_label"
done
printf '当前 Go 文件：%s\n' "${#scan_files[@]}"
printf 'Go package pattern 数量：%s\n' "${#package_patterns[@]}"
if [ "${#package_patterns[@]}" -gt 0 ]; then
  printf 'Go package pattern：\n'
  for package_pattern in "${package_patterns[@]}"; do
    printf '  - %s\n' "$package_pattern"
  done
fi
probe_packages
printf '已解析 Go package 数量：%s\n' "$package_count"
if [ "${#package_names[@]}" -gt 0 ]; then
  printf '已解析 Go package：\n'
  for package_name in "${package_names[@]}"; do
    printf '  - %s\n' "$package_name"
  done
fi
if [ -n "$diff_kind" ]; then
  printf 'Diff Go 路径：%s\n' "${#diff_paths[@]}"
  printf '当前不存在或不可扫描的 Diff 路径：%s\n' "$diff_deleted"
fi
printf '模块模式：%s\n' "$module_mode"
printf '最终 GOFLAGS：%s\n' "$effective_go_flags"
if [ -f go.work ]; then
  printf '工作区：%s/go.work\n' "$repo_root"
else
  printf '工作区：关闭，避免继承目标根之外的 go.work\n'
fi
if [ "$allow_network" -eq 0 ]; then
  printf '网络：禁止（GOPROXY=off）\n'
else
  printf '网络：允许，沿用目标环境配置\n'
fi
if have go; then
  go version 2>&1
else
  printf '未找到 go；依赖 go 的检查将跳过\n'
fi

say "格式与导入"
run_format_check "gofmt 格式" "gofmt"
run_format_check "goimports 导入" "goimports"

say "编译器与静态检查"
if [ "${#package_patterns[@]}" -gt 0 ]; then
  if [ "$package_probe_ok" -eq 1 ]; then
    run_command "go vet $package_label" "go" "analyzer" env "${go_env[@]}" go vet "${package_patterns[@]}"
    run_command "go build $package_label" "go" "build" env "${go_env[@]}" go build "${package_patterns[@]}"
    run_command "staticcheck $package_label" "staticcheck" "analyzer" env "${go_env[@]}" staticcheck "${package_patterns[@]}"
    run_command "golangci-lint $package_label" "golangci-lint" "analyzer" env "${go_env[@]}" golangci-lint run "${package_patterns[@]}"
    if [ "$allow_network" -eq 1 ]; then
      run_command "govulncheck $package_label" "govulncheck" "analyzer" env "${go_env[@]}" govulncheck "${package_patterns[@]}"
    else
      mark_skip "govulncheck $package_label" "离线模式不访问漏洞数据库；确认授权后使用 --allow-network"
    fi
  else
    mark_skip "go vet $package_label" "package 前置解析未完成"
    mark_skip "go build $package_label" "package 前置解析未完成"
    mark_skip "staticcheck $package_label" "package 前置解析未完成"
    mark_skip "golangci-lint $package_label" "package 前置解析未完成"
    mark_skip "govulncheck $package_label" "package 前置解析未完成"
  fi
else
  mark_skip "go vet" "范围内没有可检查 package"
  mark_skip "go build" "范围内没有可检查 package"
  mark_skip "staticcheck" "范围内没有可检查 package"
  mark_skip "golangci-lint" "范围内没有可检查 package"
  mark_skip "govulncheck" "范围内没有可检查 package"
fi

say "测试文件统计"
test_count=0
for go_file in "${scan_files[@]}"; do
  case "$go_file" in
    *_test.go) test_count=$((test_count + 1)) ;;
  esac
done
printf '范围内当前 _test.go 文件数：%s\n' "$test_count"
if [ "$test_count" -eq 0 ]; then
  printf '提示：当前范围没有测试文件；所属 package 可能仍有未列入文件范围的测试\n'
fi

say "动态验证"
if [ "$run_tests" -eq 0 ]; then
  printf '测试、竞态与覆盖率默认不执行；应优先使用目标项目既有 Makefile 或 CI 命令，或显式启用对应选项\n'
elif [ "${#package_patterns[@]}" -eq 0 ]; then
  mark_skip "go test" "范围内没有可检查 package"
elif [ "$package_probe_ok" -ne 1 ]; then
  mark_skip "go test $package_label" "package 前置解析未完成"
else
  run_command "go test $package_label" "go" "test" env "${go_env[@]}" go test "-timeout=$test_timeout" "${package_patterns[@]}"
  if [ "$run_race" -eq 1 ]; then
    run_command "go test -race $package_label" "go" "test" env "${go_env[@]}" go test -race "-timeout=$test_timeout" "${package_patterns[@]}"
  fi
  if [ "$run_cover" -eq 1 ]; then
    run_command "go test -cover $package_label" "go" "test" env "${go_env[@]}" go test -cover "-timeout=$test_timeout" "${package_patterns[@]}"
  fi
fi

write_json_result() {
  [ -n "$json_output" ] || return
  : >"$metadata_file"
  for scope_label in "${scope_labels[@]}"; do
    printf 'scope\0%s\0' "$scope_label" >>"$metadata_file"
  done
  for scan_file in "${scan_files[@]}"; do
    printf 'file\0%s\0' "$scan_file" >>"$metadata_file"
  done
  for package_pattern in "${package_patterns[@]}"; do
    printf 'pattern\0%s\0' "$package_pattern" >>"$metadata_file"
  done
  for package_name in "${package_names[@]}"; do
    printf 'package\0%s\0' "$package_name" >>"$metadata_file"
  done
  for diff_path in "${diff_paths[@]}"; do
    printf 'diff\0%s\0' "$diff_path" >>"$metadata_file"
  done
  if [ "$allow_network" -eq 1 ]; then
    json_network="allowed"
  else
    json_network="blocked"
  fi
  python3 "$script_dir/render_scan_json.py" \
    --output "$json_output" \
    --root "$repo_root" \
    --module-mode "$module_mode" \
    "--goflags=$effective_go_flags" \
    --network "$json_network" \
    --package-count "$package_count" \
    --deleted "$diff_deleted" \
    --metadata "$metadata_file" \
    --events "$event_file" \
    --commands "$command_file"
  json_status=$?
  if [ "$json_status" -ne 0 ]; then
    mark_failure "JSON 结果写入失败（退出码 $json_status）"
  else
    printf 'JSON 输出：%s\n' "$json_output"
  fi
}

write_json_result

say "汇总"
printf '通过：%s\n' "$passed"
printf '发现问题：%s\n' "$issues"
printf '执行失败：%s\n' "$failed"
printf '前置条件未满足：%s\n' "$blocked"
printf '未分类失败：%s\n' "$unclassified"
printf '未运行：%s\n' "$skipped"

if [ "$failed" -gt 0 ] || [ "$issues" -gt 0 ] || [ "$blocked" -gt 0 ] || [ "$unclassified" -gt 0 ]; then
  exit 1
fi
if [ "$strict" -eq 1 ] && [ "$skipped" -gt 0 ]; then
  exit 1
fi
exit 0
