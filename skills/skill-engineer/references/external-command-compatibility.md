# 外部命令兼容性契约

直接依赖外部 CLI 命令、参数、输出字段或内部 API 的 Skill，必须在 frontmatter 的 metadata 中声明：

```yaml
metadata:
  external-cli: "true"
  cli-compatibility: "references/cli-compatibility.md"
```

`references/cli-compatibility.md` 必须留在当前 Skill 包内，由 `SKILL.md` 直接链接，并包含：

```markdown
<!-- cli-compatibility-contract:v1 -->

| 本机验证版本 | `x.y.z` 或“未安装，当前没有本机验证版本” |

## 关键能力

列出无副作用的版本检查、帮助探测、最小试运行或输出字段检查。

## 版本不一致时

说明继续、降级、停止和安装升级的边界。
```

版本号只表示已验证基线。没有跨版本测试证据时，不要声明最低、最高或完整支持范围。版本一致也不能替代能力探测；版本不同但能力存在时，可以继续并明确报告“未经当前基线验证”。

安装、升级、全局写入、下载包、启动容器和执行远程脚本仍分别受用户授权边界约束。

已有面向其他宿主的顶层字段按宿主契约保留；不要为通过 Codex 校验移除其他宿主需要的 user-invocable、argument-hint 或平台元数据。此类包分别记录宿主验证结果。新的自有扩展统一放 metadata。
