# 网络请求拦截与 Mock 指南

在 Windows PowerShell 环境中，将命令中的 `bash scripts/playwright-cdp.sh` 替换为 `powershell -ExecutionPolicy Bypass -File scripts\playwright-cdp.ps1`。

本功能用于拦截、模拟响应、修改报文或直接阻断特定网络请求。

## CLI 内置路由拦截命令

```bash
# 模拟特定的 HTTP 响应状态码（如 404）
bash scripts/playwright-cdp.sh -s=cdp route "**/*.jpg" --status=404

# 模拟自定义 JSON 响应数据
bash scripts/playwright-cdp.sh -s=cdp route "**/api/users" --body='[{"id":1,"name":"Alice"}]' --content-type=application/json

# 附加自定义响应 Header
bash scripts/playwright-cdp.sh -s=cdp route "**/api/data" --body='{"ok":true}' --header="X-Custom: value"

# 从外发请求中剥离指定 Header
bash scripts/playwright-cdp.sh -s=cdp route "**/*" --remove-header=cookie,authorization

# 列出当前所有活跃的拦截路由
bash scripts/playwright-cdp.sh -s=cdp route-list

# 移除指定的路由拦截
bash scripts/playwright-cdp.sh -s=cdp unroute "**/*.jpg"

# 清空所有路由拦截规则
bash scripts/playwright-cdp.sh -s=cdp unroute
```

## URL 匹配通配符语法

```text
**/api/users           - 精确路径匹配
**/api/*/details       - 单级路径通配符
**/*.{png,jpg,jpeg}    - 多种文件后缀扩展匹配
**/search?q=*          - URL Query 查询参数匹配
```

## 通过 run-code 进行高级复杂 Mock

当需要基于请求 Body 动态判断、改写真实响应、注入人为延迟或模拟弱网断网时，使用 `run-code`。通过 `run-code` 配置的拦截规则在页面会话生命周期内持续生效。

### 1. 基于请求 Body 动态分支返回
```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  await page.route('**/api/login', route => {
    const body = route.request().postDataJSON();
    if (body.username === 'admin') {
      route.fulfill({ body: JSON.stringify({ token: 'mock-token' }) });
    } else {
      route.fulfill({ status: 401, body: JSON.stringify({ error: 'Invalid credentials' }) });
    }
  });
}"
```

### 2. 篡改真实返回的响应体
```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  await page.route('**/api/user', async route => {
    const response = await route.fetch();
    const json = await response.json();
    json.isPremium = true; // 动态改写返回字段
    await route.fulfill({ response, json });
  });
}"
```

### 3. 模拟异常网络断开
```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  await page.route('**/api/offline', route => route.abort('internetdisconnected'));
}"
# 可选的中断原因类型：connectionrefused, timedout, connectionreset
```

### 4. 模拟网络响应延迟
```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  await page.route('**/api/slow', async route => {
    await new Promise(r => setTimeout(r, 3000)); // 人为挂起 3 秒
    route.fulfill({ body: JSON.stringify({ data: 'loaded' }) });
  });
}"
```
