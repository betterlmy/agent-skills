# CodeGraph 触发评估

## 应触发

- “帮我查一下 `UserService` 的实现、调用方和影响范围。”
- “这个请求从路由到数据库经历了哪些函数？”
- “我准备重构 `ParseConfig`，哪些文件和测试可能受影响？”
- “先浏览项目结构，再定位支付模块的核心入口。”
- “用 CodeGraph 对比修改前后的调用链。”

## 不应触发

- “精确搜索错误消息 `connection refused` 出现在哪些文件。”
- “把 README 中的旧环境变量名全部替换掉。”
- “解释这段已经提供的 20 行函数。”
- “检查 JSON 配置里有没有重复键。”
- “运行现有单元测试并汇总失败结果。”

## 边界用例

- 项目未安装 CodeGraph：应说明安装副作用并征得同意，不能自动安装。
- Git 项目未忽略 `.codegraph/`：应先请求修改 `.gitignore`，不能直接初始化。
- Windows 原生 PowerShell：应使用 `scripts/codegraph.ps1`，不能假设存在 Bash。
- wrapper 不可执行或语言不受支持：应降级到文件和文本检索，不得阻塞任务。
