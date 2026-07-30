# 交互失败排查与验收边界

当元素在快照或页面上可见且启用，但普通 `click` 仍等待 actionability 直至超时时，先确定失败发生在哪一层，再选择替代路径。不要把绕过动作当成原交互已经通过。

## 1. 确认活动页面

附加到已有 Chrome 时，当前 tab 不一定处于前台。先核对 tab、URL 和页面可见性；需要时把目标页带到前台：

```bash
bash scripts/playwright-cdp.sh -s=cdp tab-list
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  await page.bringToFront();
  return {
    url: page.url(),
    title: await page.title(),
    visibility: await page.evaluate(() => document.visibilityState)
  };
}"
```

`bringToFront()` 只修正前置状态，不证明任何按钮或表单交互成功。

## 2. 检查 actionability 和命中区域

先使用稳定 locator，记录数量、可见性、启用状态、元素边界和中心点实际命中的 DOM 元素：

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const target = page.getByRole('button', { name: '提交' }).first();
  return await target.evaluate(el => {
    const rect = el.getBoundingClientRect();
    const x = rect.left + rect.width / 2;
    const y = rect.top + rect.height / 2;
    const hit = document.elementFromPoint(x, y);
    const style = getComputedStyle(el);
    return {
      rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
      disabled: el.matches(':disabled'),
      pointerEvents: style.pointerEvents,
      visibility: style.visibility,
      opacity: style.opacity,
      hit: hit ? { tag: hit.tagName, className: hit.className } : null,
      targetContainsHit: Boolean(hit && el.contains(hit))
    };
  });
}"
```

重点检查：

- 元素是否仍在移动、过渡或重新渲染；
- 中心点是否被遮罩、透明层、提示层或其他元素覆盖；
- Grid/Flex 拉伸、`transform` 或滚动是否扩大或移动了实际边界；
- locator 是否命中隐藏副本、离屏节点或多个同名元素；
- 页面是否仍在 HMR、加载态或弹窗切换过程中。

用较短的显式超时复现并保留完整 call log，避免每次等待默认 30 秒：

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  await page.getByRole('button', { name: '提交' }).click({ timeout: 3000 });
}"
```

只有已知动画或加载条件存在时才等待明确条件。不要无依据增加固定等待时间。

## 3. 按证据强度选择交互路径

优先保留真实用户路径，并在每一步后同时检查网络响应和页面结果。

### 普通指针交互

首选 locator `click()`。它会检查可见、启用、稳定和可接收事件，最接近鼠标或触控点击验收。

不要把 `force: true` 作为正常修复或验收手段。它跳过部分 actionability 检查，只适合帮助判断阻塞点；使用后必须明确说明没有验证真实命中条件。

### 键盘交互

键盘是可访问交互路径，不是指针点击的等价证明：

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const button = page.getByRole('button', { name: '提交' });
  await button.focus();
  await button.press('Enter');
}"
```

对组合框、菜单和树等复合控件，不要假设固定按键一定展开。操作后检查 `aria-expanded`、弹层可见性、当前选中值和最终显示文本。

可访问名称、DOM `textContent`、内部 value 与用户看到的 label 可能不同。若 role 查询返回内部值，应分别检查可访问树和可见 DOM；这可能是应用或组件的无障碍语义问题，不能直接归因于 CDP。

### DOM 激活和表单提交

DOM `click()`、`requestSubmit()` 可用于定位事件处理或表单链路问题，但会绕过真实指针命中：

```bash
bash scripts/playwright-cdp.sh -s=cdp run-code "async page => {
  const form = page.getByRole('button', { name: '提交' }).locator('xpath=ancestor::form');
  await form.evaluate(el => el.requestSubmit());
}"
```

`requestSubmit()` 可以验证 HTML 约束校验、`submit` 事件和应用提交处理；它不能证明提交按钮可点击、没有遮挡或能接收指针事件。

### 直接请求接口

直接调用接口只能验证路由、鉴权、请求参数、响应和服务端状态变化。它不经过页面 locator、浏览器 actionability、组件事件、表单校验或页面反馈，因此不能替代按钮、表单或完整 UI 流程验收。

## 4. 证据矩阵

| 路径 | 可以证明 | 不能证明 |
| --- | --- | --- |
| locator `click()` | actionability、指针事件、前端处理及后续结果 | 真实硬件和所有设备差异 |
| 聚焦后按键 | 焦点、键盘事件、可访问操作路径及后续结果 | 指针命中、遮挡和触控路径 |
| DOM `element.click()` | DOM click handler 及其后续逻辑 | actionability、真实命中和默认输入序列 |
| `requestSubmit()` | 表单约束、submit 事件及提交处理 | 提交按钮本身的点击路径 |
| 直接接口请求 | HTTP 契约、服务端行为和数据变化 | 任何页面交互或用户可见反馈 |

## 5. 交付时报告边界

- 原要求是按钮点击时，只有正常 locator 点击和预期结果都成功，才能报告指针交互通过。
- 仅键盘路径成功时，报告键盘交互通过，并保留指针失败事实。
- 仅 DOM 或接口路径成功时，报告具体通过的层级，不要写成 UI 验收通过。
- 保存失败 call log、关键 DOM 状态、console、相关请求和可用截图；截图失败时说明原因，并使用其他证据继续判断。
- 一个 UI 路径失败不等于后端功能失败；接口成功也不等于 UI 可用。
