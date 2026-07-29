# 前向评估记录

## 优化前基线

- 静态 Skill 审计通过，21 项脚本与报告测试通过。
- 一个真实的 11-package 工具库使用 `./...` 扫描时，被文本输出误写成“Go package 范围：1”。
- 离线模块缓存不完整时，vet、build 和 staticcheck 分别重复报告相同依赖错误。
- 继承 `GOFLAGS=-mod=mod`、Git ignored 文件和纯删除 package 等边界没有回归测试。

## 优化后结果

- 同一真实仓库输出“package pattern 数量：1”，真实 package 因离线依赖无法完整解析时明确写“未知”。
- 相同依赖问题只形成一个“前置条件未满足”，依赖 package 语义的工具级联跳过。
- 真实、无外部依赖的三 package fixture 能把一个 `./...` pattern 展开并报告为三个 package。
- 单元测试覆盖只读 GOFLAGS、工具状态分类、Git ignore、纯删除 Diff、显式 test/race/coverage、JSON 一致性和原子写入。

## 尚未完成的对比

- 未运行无 Skill 的完整审计输出对比；本轮主要验证确定性脚本契约，不能据此声称语义问题召回率已经提高。
- 触发用例仍是人工评估素材，尚无模型执行器、token/time 统计和自动评分。
