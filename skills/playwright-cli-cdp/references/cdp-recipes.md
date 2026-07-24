# CDP Protocol Recipes

Use `playwright-cli run-code` to send raw Chrome DevTools Protocol commands from the active page. The examples use the Bash wrapper; on Windows PowerShell use `powershell -ExecutionPolicy Bypass -File scripts\playwright-cdp.ps1 ...` with the same arguments. Create a CDP session per page:

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const cdp = await page.context().newCDPSession(page);
  return await cdp.send('Browser.getVersion');
}"
```

## Runtime evaluation

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const cdp = await page.context().newCDPSession(page);
  return await cdp.send('Runtime.evaluate', {
    expression: 'location.href',
    returnByValue: true
  });
}"
```

## Network diagnostics

Enable the domain before issuing domain-specific commands:

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Network.enable');
  return await cdp.send('Network.getCookies', {
    urls: [page.url()]
  });
}"
```

For normal request inspection after attaching through `--cdp`, use:

```bash
bash scripts/playwright-cdp.sh -s=cdp requests
bash scripts/playwright-cdp.sh -s=cdp request 3
```

## Performance metrics

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Performance.enable');
  return await cdp.send('Performance.getMetrics');
}"
```

## CPU throttling

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
  return 'CPU throttling set to 4x';
}"
```

Reset:

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Emulation.setCPUThrottlingRate', { rate: 1 });
  return 'CPU throttling reset';
}"
```

## Device metrics

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Emulation.setDeviceMetricsOverride', {
    width: 390,
    height: 844,
    deviceScaleFactor: 3,
    mobile: true
  });
  return 'mobile metrics applied';
}"
```

Clear:

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Emulation.clearDeviceMetricsOverride');
  return 'device metrics cleared';
}"
```

## Security state

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Security.enable');
  return await cdp.send('Security.getCertificate', {
    origin: new URL(page.url()).origin
  });
}"
```

## Coverage

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Profiler.enable');
  await cdp.send('Profiler.startPreciseCoverage', {
    callCount: true,
    detailed: true
  });
  await page.waitForTimeout(1000);
  const coverage = await cdp.send('Profiler.takePreciseCoverage');
  await cdp.send('Profiler.stopPreciseCoverage');
  return coverage.result.map(script => ({
    url: script.url,
    functions: script.functions.length
  }));
}"
```

## Attached commands vs raw protocol

This skill is still CDP-only: first attach with `playwright-cli attach --cdp=...`, then use attached wrapper commands for clicking, typing, snapshots, screenshots, cookies, local storage, and tabs. Use raw CDP when the task needs a protocol domain such as `Browser`, `Network`, `Performance`, `Emulation`, `Security`, `Profiler`, or `Runtime`.
