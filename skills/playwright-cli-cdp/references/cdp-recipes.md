# CDP 原生协议高级配方

使用 `playwright-cli run-code` 直接向当前活动页面发送原生 Chrome DevTools Protocol 指令。在 Windows PowerShell 下将 `bash scripts/playwright-cdp.sh` 替换为 `powershell -ExecutionPolicy Bypass -File scripts\playwright-cdp.ps1` 即可。

每个页面创建独立的 CDP 会话：

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const cdp = await page.context().newCDPSession(page);
  return await cdp.send('Browser.getVersion');
}"
```

## 运行时 JS 表达式执行（Runtime.evaluate）

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const cdp = await page.context().newCDPSession(page);
  return await cdp.send('Runtime.evaluate', {
    expression: 'location.href',
    returnByValue: true
  });
}"
```

## 网络层深度诊断（Network Domain）

在调用特定域的指令前先显式启用该域：

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Network.enable');
  return await cdp.send('Network.getCookies', {
    urls: [page.url()]
  });
}"
```

在挂载会话后，常规的网络请求排查使用内置命令更便捷：

```bash
bash scripts/playwright-cdp.sh -s=cdp requests
bash scripts/playwright-cdp.sh -s=cdp request 3
```

## 性能指标采集（Performance.getMetrics）

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Performance.enable');
  return await cdp.send('Performance.getMetrics');
}"
```

## CPU 降频模拟（Emulation.setCPUThrottlingRate）

限制为 4 倍降频：

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
  return 'CPU 限速已设置为 4 倍';
}"
```

恢复正常频率：

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Emulation.setCPUThrottlingRate', { rate: 1 });
  return 'CPU 限速已重置';
}"
```

## 移动端设备视口与缩放模拟

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Emulation.setDeviceMetricsOverride', {
    width: 390,
    height: 844,
    deviceScaleFactor: 3,
    mobile: true
  });
  return '已应用移动端设备参数';
}"
```

清除模拟并恢复默认视口：

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Emulation.clearDeviceMetricsOverride');
  return '已恢复默认设备参数';
}"
```

## 安全与证书状态检查（Security.getVisibleSecurityState）

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Security.enable');
  return await cdp.send('Security.getVisibleSecurityState');
}"
```
