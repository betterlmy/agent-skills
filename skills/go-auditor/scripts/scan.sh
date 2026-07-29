#!/usr/bin/env bash
# Go 代码质量范围基线：执行格式、vet、静态检查、漏洞扫描与构建检查。
# 默认禁止 Go 工具访问网络，并以只读模块模式运行；不会执行测试或安装工具。
set -uo pipefail

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

output_file=$(mktemp "${TMPDIR:-/tmp}/go-auditor.XXXXXX") || {
  echo "错误：无法创建临时文件" >&2
  exit 2
}
cleanup() {
  rm -f "$output_file"
}
trap cleanup EXIT HUP INT TERM

passed=0
issues=0
failed=0
skipped=0
scan_files=()
package_patterns=()
scope_labels=()
diff_paths=()
diff_deleted=0

say() {
  printf '\n=== %s ===\n' "$1"
}

have() {
  command -v "$1" >/dev/null 2>&1
}

mark_pass() {
  passed=$((passed + 1))
  printf '[通过] %s\n' "$1"
}

mark_issue() {
  issues=$((issues + 1))
  printf '[发现问题] %s\n' "$1"
}

mark_failure() {
  failed=$((failed + 1))
  printf '[执行失败] %s\n' "$1"
}

mark_skip() {
  skipped=$((skipped + 1))
  printf '[未运行] %s：%s\n' "$1" "$2"
}

print_output() {
  if [ -s "$output_file" ]; then
    sed -n '1,400p' "$output_file"
    line_count=$(wc -l <"$output_file")
    if [ "$line_count" -gt 400 ]; then
      printf '输出已截断：共 %s 行，仅显示前 400 行\n' "$line_count"
    fi
  fi
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
  while IFS= read -r -d '' go_file; do
    add_scan_file "$go_file"
  done < <(
    find "$directory_path" \
      -type d \( -name .git -o -name vendor \) -prune -o \
      -type f -name '*.go' -print0
  )
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
  for go_file in "$directory_path"/*.go; do
    [ -f "$go_file" ] || continue
    [ -L "$go_file" ] && continue
    add_scan_file "$go_file"
  done
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
  if [ -d "$owner_dir" ]; then
    add_package_pattern "$owner_dir"
  fi
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
  "$@" >>"$output_file" 2>/dev/null
  git_status=$?
  if [ "$git_status" -ne 0 ]; then
    echo "错误：无法读取 Git diff，请确认 revision 与仓库状态" >&2
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

existing_go_flags="${GOFLAGS-}"
case " $existing_go_flags " in
  *" -mod="*) ;;
  *) existing_go_flags="${existing_go_flags:+$existing_go_flags }-mod=$module_mode" ;;
esac
go_env+=("GOFLAGS=$existing_go_flags")

run_command() {
  check_name="$1"
  required_tool="$2"
  shift 2

  if ! have "$required_tool"; then
    mark_skip "$check_name" "未安装 $required_tool"
    return
  fi

  : >"$output_file"
  "$@" >"$output_file" 2>&1
  command_status=$?
  print_output
  if [ "$command_status" -eq 0 ]; then
    mark_pass "$check_name"
  else
    mark_failure "$check_name（退出码 $command_status）"
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
printf 'Go package 范围：%s\n' "${#package_patterns[@]}"
if [ -n "$diff_kind" ]; then
  printf 'Diff Go 路径：%s\n' "${#diff_paths[@]}"
  printf '当前不存在或不可扫描的 Diff 路径：%s\n' "$diff_deleted"
fi
printf '模块模式：%s\n' "$module_mode"
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
  run_command "go vet $package_label" "go" env "${go_env[@]}" go vet "${package_patterns[@]}"
  run_command "go build $package_label" "go" env "${go_env[@]}" go build "${package_patterns[@]}"
  run_command "staticcheck $package_label" "staticcheck" env "${go_env[@]}" staticcheck "${package_patterns[@]}"
  run_command "golangci-lint $package_label" "golangci-lint" env "${go_env[@]}" golangci-lint run "${package_patterns[@]}"
  if [ "$allow_network" -eq 1 ]; then
    run_command "govulncheck $package_label" "govulncheck" env "${go_env[@]}" govulncheck "${package_patterns[@]}"
  else
    mark_skip "govulncheck $package_label" "离线模式不访问漏洞数据库；确认授权后使用 --allow-network"
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

say "汇总"
printf '通过：%s\n' "$passed"
printf '发现问题：%s\n' "$issues"
printf '执行失败：%s\n' "$failed"
printf '未运行：%s\n' "$skipped"
printf '竞态与覆盖率未自动执行；获得授权后应使用目标项目既有 Makefile 或 CI 命令运行\n'

if [ "$failed" -gt 0 ] || [ "$issues" -gt 0 ]; then
  exit 1
fi
if [ "$strict" -eq 1 ] && [ "$skipped" -gt 0 ]; then
  exit 1
fi
exit 0
