# SVG 安全与技术规范

## 安全子集

Logo 默认只使用静态 SVG。允许的主要元素包括：

```text
svg g defs title desc path rect circle ellipse line polyline polygon
linearGradient radialGradient stop clipPath mask symbol use text tspan
```

禁止：

- `script`、`foreignObject`、`image`、动画元素和未知命名空间元素。
- 任何以 `on` 开头的事件属性。
- DTD、实体声明、`javascript:`、`data:` 和远程 URL。
- 外部样式表、远程字体和非本地 `href`。

优先使用展示属性而不是嵌入 `<style>`。这让文件更容易审计、嵌入和重着色。

## 文本与 XML

用户提供的品牌名、标语和描述必须按 XML 转义：

| 原字符 | XML 文本 |
| --- | --- |
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&quot;`，用于双引号属性 |
| `'` | `&apos;`，用于单引号属性 |

不要通过删除字符来让 XML 通过。名称 `A&B` 必须仍显示为 `A&B`。

## 根元素与尺寸

使用 SVG 命名空间与 `viewBox`：

```xml
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 320 96"
     role="img"
     aria-labelledby="logo-title logo-desc">
  <title id="logo-title">Acme logo</title>
  <desc id="logo-desc">Interlocking geometric mark beside the Acme wordmark</desc>
  <!-- static vector content -->
</svg>
```

`viewBox` 应紧贴设计所需画布并保留有意的安全空间。`width`、`height` 可以为预览提供默认值，但缩放能力来自 `viewBox`，不是“相对单位”。

## ID 与引用

- 每个 ID 在文件中唯一；多份 SVG 嵌入同一页面时，使用带品牌或变体前缀的 ID。
- `fill="url(#acme-gradient)"`、`clip-path="url(#acme-clip)"` 等引用必须指向当前文件存在的 ID。
- `<use href="#acme-mark">` 只允许本地片段引用。
- 不要把用户输入直接拼成 ID；先规范化并确保唯一。

## 字体策略

草稿阶段可用 `<text>` 加速迭代。最终交付时选择其一：

1. 将字形转换为路径，保留单独的可编辑源稿和字体记录。
2. 保留 `<text>`，明确指定字体族、字重、回退字体和许可/替换风险。

转路径会提高跨环境一致性，但会降低可编辑性和文本可访问性。无论选择哪种方式，`<title>` 与 `<desc>` 都应描述品牌名称和标记。

## 静态验证

运行：

```bash
python3 scripts/validate_svg.py logo.svg
python3 scripts/validate_svg.py path/to/logo-directory
```

验证器检查 UTF-8、XML 结构、安全子集、无外链、唯一 ID、本地引用、`viewBox`、`title` 和 `desc`。验证通过不代表视觉正确，还必须进行渲染检查。

不要为通过验证而删除品牌文字、关闭检查或扩大允许元素。若确有必要使用安全子集之外的元素，应先说明用途、嵌入环境和风险，再由用户决定是否接受。
