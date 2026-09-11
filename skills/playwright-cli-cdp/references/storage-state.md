# 会话存储与 Cookie 管理

在 Windows PowerShell 环境中，将 `bash scripts/playwright-cdp.sh` 替换为 `powershell -ExecutionPolicy Bypass -File scripts\playwright-cdp.ps1`。

本功能用于检查、持久化与恢复 Cookie、localStorage、sessionStorage 以及完整的全量浏览器状态。注意：通过 CDP 连接已有浏览器时会复用用户的真实配置目录，在导出保存状态文件时请注意脱敏。

## 全量状态保存与恢复（Storage State）

一次性保存或加载包含 Cookie 与 localStorage 的完整状态快照：

```bash
# 保存到自动生成的唯一文件名
bash scripts/playwright-cdp.sh -s=cdp state-save

# 保存到指定的文件路径
bash scripts/playwright-cdp.sh -s=cdp state-save auth.json

# 恢复并加载已有状态文件
bash scripts/playwright-cdp.sh -s=cdp state-load auth.json
# 重新刷新当前页面以使注入的 Cookie 即刻生效
bash scripts/playwright-cdp.sh -s=cdp goto https://example.com
```

保存的 JSON 结构规范：

```json
{
  "cookies": [
    {
      "name": "session_id",
      "value": "abc123",
      "domain": "example.com",
      "path": "/",
      "expires": 1735689600,
      "httpOnly": true,
      "secure": true,
      "sameSite": "Lax"
    }
  ],
  "origins": [
    {
      "origin": "https://example.com",
      "localStorage": [
        { "name": "theme", "value": "dark" }
      ]
    }
  ]
}
```

## Cookie 细粒度操作

```bash
# 列出所有 Cookie
bash scripts/playwright-cdp.sh -s=cdp cookie-list
# 按域名或路径过滤
bash scripts/playwright-cdp.sh -s=cdp cookie-list --domain=example.com
bash scripts/playwright-cdp.sh -s=cdp cookie-list --path=/api

# 获取特定 Cookie 的值
bash scripts/playwright-cdp.sh -s=cdp cookie-get session_id

# 注入单个 Cookie
bash scripts/playwright-cdp.sh -s=cdp cookie-set session_id abc123
bash scripts/playwright-cdp.sh -s=cdp cookie-set session_id abc123 \
  --domain=example.com --path=/ --httpOnly --secure --sameSite=Lax

# 删除特定 Cookie 或清空所有 Cookie
bash scripts/playwright-cdp.sh -s=cdp cookie-delete session_id
bash scripts/playwright-cdp.sh -s=cdp cookie-clear
```

批量操作可借助 `run-code`：

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  await page.context().addCookies([
    { name: 'session_id', value: 'sess_abc123', domain: 'example.com', path: '/', httpOnly: true },
    { name: 'prefs', value: JSON.stringify({ theme: 'dark' }), domain: 'example.com', path: '/' }
  ]);
}"
```

## localStorage 交互命令

```bash
# 查看所有键值
bash scripts/playwright-cdp.sh -s=cdp localstorage-list

# 获取与设置具体键值
bash scripts/playwright-cdp.sh -s=cdp localstorage-get token
bash scripts/playwright-cdp.sh -s=cdp localstorage-set theme dark
bash scripts/playwright-cdp.sh -s=cdp localstorage-set user_settings '{"theme":"dark","language":"zh"}'

# 删除指定键或完全清空
bash scripts/playwright-cdp.sh -s=cdp localstorage-delete token
bash scripts/playwright-cdp.sh -s=cdp localstorage-clear
```

## sessionStorage 交互命令

```bash
bash scripts/playwright-cdp.sh -s=cdp sessionstorage-list
bash scripts/playwright-cdp.sh -s=cdp sessionstorage-get form_data
bash scripts/playwright-cdp.sh -s=cdp sessionstorage-set step 3
bash scripts/playwright-cdp.sh -s=cdp sessionstorage-delete step
bash scripts/playwright-cdp.sh -s=cdp sessionstorage-clear
```
