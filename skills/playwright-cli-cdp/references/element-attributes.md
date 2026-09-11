# 页面元素属性检查指南

在 Windows PowerShell 环境中，将 `bash scripts/playwright-cdp.sh` 替换为 `powershell -ExecutionPolicy Bypass -File scripts\playwright-cdp.ps1`。

当页面快照未直接显示元素的 `id`、`class`、`data-*` 或特定 DOM 属性时，使用 `eval` 指令针对元素引用编号直接进行检查。

## 常用检查命令示例

```bash
# 获取快照（假设目标按钮引用为 e7）
bash scripts/playwright-cdp.sh -s=cdp snapshot

# 获取元素的 DOM id
bash scripts/playwright-cdp.sh -s=cdp eval "el => el.id" e7

# 获取元素全部的 CSS class 类名
bash scripts/playwright-cdp.sh -s=cdp eval "el => el.className" e7

# 读取指定的自定义属性或 aria 标签
bash scripts/playwright-cdp.sh -s=cdp eval "el => el.getAttribute('data-testid')" e7
bash scripts/playwright-cdp.sh -s=cdp eval "el => el.getAttribute('aria-label')" e7

# 获取元素的最终计算样式（Computed Style）
bash scripts/playwright-cdp.sh -s=cdp eval "el => getComputedStyle(el).display" e7
```

在自动化脚本中搭配 `--raw` 获取单行干净返回值：

```bash
TESTID=$(bash scripts/playwright-cdp.sh -s=cdp --raw eval "el => el.getAttribute('data-testid')" e7)
```
