# 页面视频录制与章节标注

在 Windows PowerShell 环境中，将 `bash scripts/playwright-cdp.sh` 替换为 `powershell -ExecutionPolicy Bypass -File scripts\playwright-cdp.ps1`。

本功能用于将浏览器自动化全过程录制为视频格式（WebM 格式，VP8/VP9 编码），极其适合用于产品 Demo 演示、功能文档展示以及验收证据归档。

## 基础录屏流程

```bash
# 启动录屏并指定目标视频文件名
bash scripts/playwright-cdp.sh -s=cdp video-start demo.webm

# 添加章节打标卡片（全屏提示，停留 2000 毫秒）
bash scripts/playwright-cdp.sh -s=cdp video-chapter "快速入门" --description="打开系统首页" --duration=2000
bash scripts/playwright-cdp.sh -s=cdp goto https://example.com
bash scripts/playwright-cdp.sh -s=cdp click e1

# 添加第二阶段章节说明
bash scripts/playwright-cdp.sh -s=cdp video-chapter "填写表单" --description="自动录入业务数据" --duration=2000
bash scripts/playwright-cdp.sh -s=cdp fill e2 "测试录入"

# 停止录屏并完成文件编码落盘
bash scripts/playwright-cdp.sh -s=cdp video-stop
```

## 通过脚本制作高品质视觉标注演示视频

若需制作带有精准打字延迟、视觉聚光高亮以及气泡说明的精美演示视频，使用 `run-code --filename=...` 运行自动化脚本。

在 `run-code` 内部，脚本注入了 `page.screencast` 扩展 API（该 API 仅在包装脚本环境有效）：

```javascript
async page => {
  await page.screencast.start({ path: 'video.webm', size: { width: 1280, height: 800 } });
  await page.goto('https://demo.playwright.dev/todomvc');

  // 展示章节卡片
  await page.screencast.showChapter('添加待办项', {
    description: '演示如何向列表中批量追加待办项',
    duration: 2000,
  });

  // 模拟拟人化打字速度
  await page.getByRole('textbox', { name: 'What needs to be done?' })
    .pressSequentially('遛狗', { delay: 80 });
  await page.getByRole('textbox', { name: 'What needs to be done?' }).press('Enter');
  await page.waitForTimeout(1000);

  // 注入局部高亮气泡标注
  const annotation = await page.screencast.showOverlay(`
    <div style="position: absolute; top: 12px; right: 12px;
      padding: 8px 16px; background: rgba(0,0,0,0.75);
      border-radius: 8px; font-size: 14px; color: white;">
      首个条目添加成功
    </div>
  `);

  await page.waitForTimeout(1500);
  await annotation.dispose(); // 移除气泡

  await page.screencast.stop();
}
```

## Screencast 浮层 API 摘要

| 接口方法 | 用途与场景 |
|---|---|
| `page.screencast.showChapter(title, options)` | 全屏展示阶段过渡章节卡片 |
| `page.screencast.showOverlay(html, options)` | 渲染自定义 HTML 浮层用于高亮标注、边框提示与引导文案 |
| `disposable.dispose()` | 手动关闭未设置持续时间的常驻浮层 |
| `page.screencast.hideOverlays()` / `showOverlays()` | 临时批量隐藏或重新显示所有当前活跃浮层 |
