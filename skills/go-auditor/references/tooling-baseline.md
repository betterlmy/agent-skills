# 工具基线（第一步）

机器扫描只代表编译器和静态工具视角。先遵循目标仓库指令与 Makefile，再运行允许的命令；任何通过状态都不能替代业务语义审查。

## 前置条件

- 脚本需要 Bash、`find`、`grep`、`sed`、`wc`、`tr`、`cp` 和 `mktemp`。
- Diff 范围额外需要 Git，并要求目标位于工作树内；脚本只读 Git 状态，不执行 fetch、checkout、add 或 commit。
- `go` 与 `gofmt` 是核心工具；`goimports`、`staticcheck`、`golangci-lint`、`govulncheck` 为可选工具，缺失时明确标记未运行。
- `--json-output` 额外需要 Python 3；未请求 JSON 时不依赖 Python。
- 目标根必须存在 `go.mod` 或 `go.work`。没有 `go.work` 的多模块仓库应逐个模块运行。
- 不得自动安装缺失工具。若目标仓库规定了版本或封装命令，以其约定为准。

## 调用脚本

从已加载 `SKILL.md` 的实际路径取得 Skill 目录，从目标仓库取得仓库根，然后执行：

```bash
bash "$GO_AUDITOR_SKILL_DIR/scripts/scan.sh" "$GO_AUDITOR_ROOT"
```

不要在目标仓库里假设存在 `scripts/scan.sh`。

默认行为：

- 设置 `GOTOOLCHAIN=local`、`GOPROXY=off`，阻止自动工具链和模块网络下载。
- 强制使用 `-mod=readonly`；存在根级 `vendor/modules.txt` 且不是 workspace 时强制使用 `-mod=vendor`。脚本过滤继承 `GOFLAGS` 中会改变目录、模块文件或外部工具执行的 `-C`、`-exec`、`-mod`、`-modfile`、`-overlay`、`-toolexec` 和 `-vettool`，不会让外部环境突破审计边界。根目录存在 `go.work` 时固定使用该文件，否则设置 `GOWORK=off`。
- 不执行 `go test`、`-race` 或覆盖率命令。
- 不修改源码；临时输出写入系统临时目录并在退出时清理。Go 工具仍可能写入环境已有的构建缓存，预检时应按目标仓库约束确认。

可选参数：

```bash
bash "$GO_AUDITOR_SKILL_DIR/scripts/scan.sh" --package-dir internal/auth "$GO_AUDITOR_ROOT"
bash "$GO_AUDITOR_SKILL_DIR/scripts/scan.sh" --target internal/device --target cmd/agent "$GO_AUDITOR_ROOT"
bash "$GO_AUDITOR_SKILL_DIR/scripts/scan.sh" --target internal/auth/token.go "$GO_AUDITOR_ROOT"
bash "$GO_AUDITOR_SKILL_DIR/scripts/scan.sh" --diff working "$GO_AUDITOR_ROOT"
bash "$GO_AUDITOR_SKILL_DIR/scripts/scan.sh" --diff staged "$GO_AUDITOR_ROOT"
bash "$GO_AUDITOR_SKILL_DIR/scripts/scan.sh" --diff-range 'origin/main...HEAD' "$GO_AUDITOR_ROOT"
bash "$GO_AUDITOR_SKILL_DIR/scripts/scan.sh" --strict "$GO_AUDITOR_ROOT"
bash "$GO_AUDITOR_SKILL_DIR/scripts/scan.sh" --allow-network "$GO_AUDITOR_ROOT"
bash "$GO_AUDITOR_SKILL_DIR/scripts/scan.sh" --test --race --cover --test-timeout 2m "$GO_AUDITOR_ROOT"
bash "$GO_AUDITOR_SKILL_DIR/scripts/scan.sh" --json-output /tmp/go-audit.json "$GO_AUDITOR_ROOT"
bash "$GO_AUDITOR_SKILL_DIR/scripts/scan.sh" --output-dir /tmp/go-audit-logs "$GO_AUDITOR_ROOT"
```

- `--target`：文件只做该文件的格式检查，目录递归；可重复组合文件或目录。
- `--package-dir`：只包含目录直属 Go 文件，不递归子 package；可重复。
- `--diff working|staged` 与 `--diff-range`：从 Git 解析 Go 路径，并将工具检查扩展到所属 package；不能和路径范围混用。
- `--strict`：任何可选工具缺失也返回非零，适合明确要求完整工具链的门禁。
- `--allow-network`：沿用环境中的 Go 软件源配置。仅在目标仓库授权联网且已确认适用软件源后使用。
- `--test`、`--race`、`--cover`：显式运行当前 package 范围的动态检查；默认关闭。仓库存在相关 Makefile 或 CI 命令时优先使用仓库约定，不用这些通用选项替代。
- `--test-timeout`：设置 Go 测试超时，默认 `2m`。
- `--json-output`：把范围、package、状态和命令记录原子写入指定 JSON；相对路径以目标根解析，拒绝符号链接和不存在的父目录。
- `--output-dir`：把 package 探测、格式和各工具的完整原始输出写入已存在的空目录，避免覆盖已有文件；默认不保留。原始输出可能包含源码片段或环境诊断，分享前必须按目标仓库规则检查并脱敏。

## 状态与退出码

| 状态 | 含义 |
| --- | --- |
| 通过 | 工具实际执行且退出成功，没有发现该检查定义的问题 |
| 发现问题 | 工具正常执行并发现格式漂移等代码问题 |
| 前置条件未满足 | package、依赖、平台或权限条件不足，相关工具可能级联跳过 |
| 工具失败 | 工具无法启动或自身异常，不能推断代码是否存在问题 |
| 未分类失败 | 工具非零退出但证据不足，保留输出与退出码等待人工判断 |
| 未运行 | 工具缺失或检查未获授权，不等同于通过 |

- 退出码 0：已执行检查均通过；非 strict 模式允许可选工具缺失或范围内没有当前 Go 文件。
- 退出码 1：发现问题、工具执行失败，或 strict 模式存在跳过项。
- 退出码 2：参数、目录或模块预检失败。

脚本先用最终 Go 环境解析 package，分别输出 package pattern 与真实 package 数；解析失败时真实数量写“未知”，相关语义工具级联跳过。脚本最多展示每项检查前 400 行输出，并记录可读取的工具版本、实际命令、工作目录、退出码和耗时。报告必须回到完整 CI 日志或按需复跑确认，不能将截断输出视为完整命中数。

## 工具覆盖面

| 工具 | 覆盖面 | 判读要点 |
| --- | --- | --- |
| `gofmt -l` / `goimports -l` | 格式与 import 漂移 | 机械一致性候选，不自动上升为高严重度 |
| `go vet` + package 范围 | 编译器级可疑构造 | 文件和 diff 范围会扩展到所属 package |
| `go build` + package 范围 | 可编译性 | 先区分代码失败、离线依赖缺失和平台构建约束 |
| `staticcheck` | 常见缺陷与无效代码 | 按规则编号回读源码确认 |
| `golangci-lint` | 聚合多种 linter | 以仓库配置和锁定版本为准 |
| `govulncheck` | 已知漏洞及可达性 | 离线模式跳过；获准联网后确认调用可达性、版本和缓解措施 |

重点关注错误检查、复杂度、重复代码、安全、错误链、nil、资源关闭、Context 传播和热点分配等规则，但不得因为某个 linter 未启用就断言仓库存在对应缺陷。

## 测试、竞态与覆盖率

这些命令可能耗时、访问外部服务或依赖仓库专用环境，默认不执行。只有目标仓库授权后，才优先按其 Makefile 或 CI 约定运行；没有仓库约定时可以使用脚本的显式选项。例如：

```bash
go test ./...
go test -race ./...
go test -cover ./...
```

报告分别记录“通过”“失败”“未运行”，并说明实际命令与 package 范围。局部审计优先运行所属 package 测试，不自动扩大到 `./...`；覆盖率百分比只描述覆盖范围，不代表断言质量。

## 产出

- 每个工具的状态、实际命令、工作目录、退出码、耗时、关键输出与失败分类。
- 请求 `--json-output` 时，文本与 JSON 使用同一份事件和命令记录；JSON 包含 schema 版本与输出截断标记。
- 请求 `--output-dir` 时记录完整输出路径；未请求时继续使用退出即清理的临时文件。
- 格式或 linter 命中数；输出截断时明确标注。
- 未安装、未授权或因离线依赖无法执行的项目。
- 用户范围、当前 Go 文件数、package pattern、成功解析时的真实 package，以及无法扫描的删除路径。
- 在 `repo`/`module` 范围内报告工程配置缺口；局部范围只报告与目标直接相关的配置证据。
