# 自动化测试代码生成指南

在 Windows PowerShell 环境中，将 `bash scripts/playwright-cdp.sh` 替换为 `powershell -ExecutionPolicy Bypass -File scripts\playwright-cdp.ps1`。

当在命令行执行 `goto`、`click`、`fill` 等页面交互指令时，包装脚本会在标准输出中实时打印对应的标准 Playwright TypeScript 代码片段。通过收集这些生成的代码片段，可以快速组装端到端自动化测试用例，免去手工编写复杂定位器的繁琐。

## 交互录制示例流程

```bash
bash scripts/playwright-cdp.sh -s=cdp goto https://example.com/login
bash scripts/playwright-cdp.sh -s=cdp snapshot
# 输出快照：e1 [textbox "Email"], e2 [textbox "Password"], e3 [button "Sign In"]

bash scripts/playwright-cdp.sh -s=cdp fill e1 "user@example.com"
# 命令输出打印对应的 Playwright 代码：
# await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');

bash scripts/playwright-cdp.sh -s=cdp fill e2 "password123"
bash scripts/playwright-cdp.sh -s=cdp click e3
```

## 组装完整的测试文件

复制捕获到的代码片段，并补充核心断言：

```typescript
import { test, expect } from '@playwright/test';

test('用户登录成功链路', async ({ page }) => {
  await page.goto('https://example.com/login');
  await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
  await page.getByRole('textbox', { name: 'Password' }).fill('password123');
  await page.getByRole('button', { name: 'Sign In' }).click();

  await expect(page).toHaveURL(/.*dashboard/);
});
```

## 最佳实践准则

### 优先采用语义化定位器（Semantic Locators）

生成的代码默认使用面向可访问性角色的定位器（Role-based Locators），这比脆弱易变的 CSS 选择器具备更强的抗改版韧性：

```typescript
// 推荐：具备语义抗脆弱性
await page.getByRole('button', { name: '提交' }).click();

// 避免：脆弱的 CSS 路径
await page.locator('#main > div > button.btn-primary').click();
```

### 手工补充严谨断言

命令行录制仅记录行为动作，测试断言必须人工补充。通过 `generate-locator`、`eval` 与 `snapshot` 提取断言所需的目标值：

```bash
# 获取特定图元的稳定 Locator 表达式
bash scripts/playwright-cdp.sh -s=cdp --raw generate-locator e5
# 示例输出：getByRole('button', { name: '提交' })

# 抓取期望的文本内容
bash scripts/playwright-cdp.sh -s=cdp --raw eval "el => el.textContent" e5

# 抓取输入框当前的值
bash scripts/playwright-cdp.sh -s=cdp --raw eval "el => el.value" e5
```

常见断言示例：

```typescript
await expect(page.getByRole('alert', { name: '保存成功' })).toBeVisible();
await expect(page.getByTestId('main-header')).toHaveText('欢迎回来，管理员');
await expect(page.getByRole('textbox', { name: 'Email' })).toHaveValue('user@example.com');
await expect(page.getByRole('checkbox', { name: '记住我' })).toBeChecked();
```
