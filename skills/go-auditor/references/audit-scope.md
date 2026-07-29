# 审计范围

范围控制决定成本和结论边界。始终选择能回答用户问题的最窄范围，再读取必要上下文；上下文扩展不等于扩大正式审计范围。

## 范围映射

| 用户目标 | 范围 | 脚本参数 | 最少上下文 |
| --- | --- | --- | --- |
| 整个仓库或 workspace | `repo` | 仓库根，不加范围参数 | 所有 module、根配置、CI 与主要入口 |
| 单个 module | `module` | module 根，不加范围参数 | `go.mod`、公开入口、直接依赖和测试 |
| 单个 package | `package` | `--package-dir DIR` | package 文件、package 测试、直接接口 |
| 目录树 | `directory` | `--target DIR` | 目录内 package、直接上游和下游 |
| 文件集 | `files` | 每个文件一个 `--target FILE` | 所属 package、相关测试和调用契约 |
| 高风险域 | `hotspot` | 对相关目录或 package 组合使用上述参数 | 入口、授权或事务边界、调用方和测试 |
| 未提交变更 | `diff` | `--diff working` | 变更文件、所属 package、相关测试 |
| 暂存区变更 | `diff` | `--diff staged` | 同上 |
| Git revision range | `diff` | `--diff-range RANGE` | 变更文件、所属 package、相关测试和影响面 |

所有路径相对目标根解析，也允许传入目标根内部的绝对路径。脚本拒绝目标根之外的路径和符号链接文件。

## 范围扩展规则

- `files` 和 `diff`：格式检查只看目标 Go 文件；`go vet`、build 和静态工具扩展到文件所属 package，因为 Go 工具需要 package 语义。
- `package`：只审计当前 package，不递归子 package；读取直接调用方只用于判断影响，不自动把调用方纳入问题统计。
- `directory`：递归审计目录下的 Go 文件和 package。
- `hotspot`：允许组合多个 package 或目录，但必须逐项列出，不用模糊关键词替代实际路径。
- `repo` 与 `module`：只有这些范围可以输出对应层级的整体健康度结论。
- Git 仓库的 repo、module、directory 和 package 范围默认只包含已跟踪文件及未被 ignore 的未跟踪文件；显式指定的文件目标不受该默认收集规则影响。非 Git 目录才降级使用文件系统遍历。

报告分别列出：

1. 用户要求的正式审计范围。
2. 为理解行为而读取的上下文范围。
3. 工具实际执行的 package 范围。
4. 未审计区域及不可外推的结论。

## Diff 来源

### 工作区

`--diff working` 合并以下 Go 路径并去重：

- 未暂存变更。
- 已暂存变更。
- 未跟踪且未被 `.gitignore` 排除的文件。

### 暂存区

`--diff staged` 只读取 index 相对 `HEAD` 的变更。适合提交前检查。

### Revision range

`--diff-range RANGE` 将 RANGE 原样交给 `git diff`，例如 `origin/main...HEAD` 或 `HEAD~3..HEAD`。不得自行 fetch、切换分支或修改 Git 状态；revision 不存在时报告预检失败。

### Diff 证据要求

- 先读取 patch，区分新增、修改、重命名和删除；未跟踪文件按新增文件读取，因为它们尚无 Git patch。
- 脚本只检查当前工作树中仍存在的 Go 文件；删除文件仍需从 patch 审查契约和影响。所属目录已无可构建 Go 文件时，不把空目录交给 Go 工具。
- 不只评论变更行：结论可以引用所属函数、接口或测试上下文，但要说明问题是否由本次变更引入。
- 对既有问题标注“上下文中已存在”，不要伪装成本次 diff 引入。
- 不获取 PR 元数据、不发表评论、不改变 index 或工作树。

## 无匹配内容

范围内没有 Go 文件或 diff 中没有 Go 变更时，明确报告“没有可审计的 Go 代码”，不要自动扩大到整个仓库。
