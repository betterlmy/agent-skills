# 自定义 Playwright 代码执行指南

在 Windows PowerShell 环境中，将 `bash scripts/playwright-cdp.sh` 替换为 `powershell -ExecutionPolicy Bypass -File scripts\playwright-cdp.ps1`。

当 CLI 内置指令无法覆盖复杂业务操作时，使用 `run-code` 直接在页面上下文中执行任意 Playwright 异步代码。

## 基础语法

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  // 此处编写标准的 Playwright 代码
  // 可通过 page.context() 调用浏览器上下文级操作
}"
```

也可以从外部独立脚本文件中加载执行：

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code --filename=./my-script.js
```

传入的参数必须为一个独立的异步函数表达式，不支持顶层的 `import`、`export` 或 `require` 模块语句。

## 地理位置模拟（Geolocation）

```bash
# 模拟旧金山地理坐标
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  await page.context().grantPermissions(['geolocation']);
  await page.context().setGeolocation({ latitude: 37.7749, longitude: -122.4194 });
}"

# 模拟伦敦地理坐标
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  await page.context().grantPermissions(['geolocation']);
  await page.context().setGeolocation({ latitude: 51.5074, longitude: -0.1278 });
}"

# 清除所有已授权权限
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  await page.context().clearPermissions();
}"
```

## 权限授权（Permissions）

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  await page.context().grantPermissions([
    'geolocation',
    'notifications',
    'camera',
    'microphone'
  ]);
}"

# 仅向特定 Origin 授权读取剪贴板
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  await page.context().grantPermissions(['clipboard-read'], {
    origin: 'https://example.com'
  });
}"
```

## 媒体特性模拟（Media Emulation）

```bash
# 暗色模式（Dark mode）
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  await page.emulateMedia({ colorScheme: 'dark' });
}"

# 减少动态效果偏好（prefers-reduced-motion）
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
}"

# 打印媒体样式模拟（Print styles）
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  await page.emulateMedia({ media: 'print' });
}"
```

## 等待策略（Wait Strategies）

```bash
# 等待网络空闲（Network Idle）
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  await page.waitForLoadState('networkidle');
}"

# 等待特定加载动画遮罩消失
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  await page.locator('.loading').waitFor({ state: 'hidden' });
}"

# 等待特定的全局 JavaScript 条件为真
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  await page.waitForFunction(() => window.appReady === true);
}"
```
