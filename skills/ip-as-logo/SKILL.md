---
name: ip-as-logo
description: 生成极简、可爱、拟人化的方形 IP 角色形象，采用圆润厚重的形态、两种明确的主体颜色、一种纯色背景以及标志性的下角探出式构图。Use when 创建动物、生物、机器人、小幽灵、植物、物品或其他拟人化 IP 角色形象，包括推导三种与产品调性契合的设计方向并批量生成六个独立候选方案供用户确认；不用于需要可编辑 SVG/矢量的 Logo 设计任务。
---

# IP as Logo

打造极致简约可爱的拟人化 IP 角色符号：一个小巧、讨喜、在 `32 × 32` 微小尺寸下依然清晰可辨的紧凑形象，而非复杂的角色插画。

## 标准工作流程

1. **解析诉求**：明确提取用户指定的主体 IP 意向及现有产品上下文。除非用户主动要求精细控制色彩模式，否则不要向用户抛出繁琐的色彩模式选项。
2. **只读探索上下文**：当用户未明确指定 IP 形象主体且当前工作区为产品仓库时，先查阅只读上下文（如 README、产品文档、Package/App 元数据、官网落地页文案、Manifest 及设计 Token）。只要能以合理把握推断出产品定位、核心受众与预期调性，即视为上下文已充分。
3. **针对性澄清**：若产品上下文严重不足，发起单轮结构化提问，涵盖：产品做什么、服务谁、期望给人怎样的感受。严禁发起多轮繁琐的问卷调查，得到答复后直接按照最受支撑的理解推进。
4. **提案并批量生成**：在上下文明确后，正式生成前必须先向用户呈现 3 个精炼的设计方向，并明确提议单次批量生成 6 个独立候选方案。除非用户当前输入已明确授权直接输出 6 张图或指示无需再次确认，否则必须等待用户确认后再调用模型生成。
5. **构思 3 个差异化方向**：
   - 用户已明确指定 IP 形象时：保持该主体不变，从外轮廓剪影特征、次级色块分布、物种标志性器官或性格神态等维度，提出 3 种截然不同的造型切入点；
   - 用户未指定具体主体时：提出 3 种真正不同的 IP 形象主体或拟人隐喻，分别对应不同的产品特质或品牌承诺；切勿在没有依据的情况下随意给出 3 种不相关的随机动物。
6. **严格响应用户反馈**：
   - 若用户认可所有 3 个方向并同意 6 张图提议：每个方向各生成 2 个独立变体，分别编号为 `A1`、`A2`、`B1`、`B2`、`C1`、`C2`。将 `A1`、`B1`、`C1` 分配在**左下角**探出，将 `A2`、`B2`、`C2` 分配在**右下角**探出，确保每个设计方向从左右两侧各测试一次；
   - 若用户锁定其中 1 个方向但依然希望生成 6 张图：针对该方向生成 6 个精细控制的变体，标记为 `A1` 至 `A6`。奇数编号统一从左下角探出，偶数编号统一从右下角探出；
   - 若用户拒绝默认数量、方向或构图分布，严格遵循用户的替换指示，绝不辩解；
   - 其他偶数批次规模，在左下角与右下角之间平分；若为奇数批次，有目的地将多余的一张分配给某一侧并说明。除非用户明确要求，否则绝不使用底部居中。
7. **严格遵循三语义色原则**：全图严格限制使用正好 3 种语义颜色：正好 2 种 IP 主体基础色 + 正好 1 种纯色背景。面部五官线条必须复用 2 种主体色之一，严禁额外引入新的语义色。除非用户明确要求其他颜色配比。保持产品线索、辨识特征、复杂度上限与配色方案一致，便于对比。
8. **核实图像生成能力**：在向用户承诺生成前，先确认当前运行环境中可用的生图工具。在支持 ImageGen 的环境中使用该工具；在其他环境中查找已配置的图像生成渠道；若完全无生图能力，如实询问用户是否能提供或配置对应服务，绝不伪造生成结果。
9. **支持并发时并行生成**：若运行时支持子 Agent，在可用并发额度内并行生成 6 个独立候选图。为每个子 Agent 分配相同的产品简报、共享约束以及指定的单一方向变体；在容量受限时分批运行。若无子 Agent 能力，通过独立的单次生图请求依次执行。
10. **背景色板处理**：若用户提供了背景色调板，除非另有说明，否则所有提供色仅用于背景。独立为 IP 主体挑选 2 种主体色。任何历史示例色板仅供启发，不可当作封闭的白名单。
11. **遵循复杂度预算抽象主体**：每张候选图均独立生成为全分辨率方形素材；切勿要求模型生成九宫格、联排或多图拼接。测试纯 Prompt 复现度时，切勿将先前候选图作为图像参考传给模型。
12. **单次抽卡交付**：将每批生成视为单次创作成图。对要求的每张图生成一次，完整保留并原样交付所有结果。不得自行充当过滤器拦截交付、私自将图片标记为“推荐/不推荐”、自动重新生成，或使用后期处理修改图像。
13. **完整交付与标注文档**：完整保留所有生成结果，清晰输出对应标签、IP 方向与设计意图、分配角落、存储路径、Prompt 与配色映射以及图片分辨率。将所有结果集中呈现；仅在用户明确要求再次尝试时才生成补充或替换版本。

在生成前呈现 3 个方向时，每个方向用一行紧凑说明：`<IP形象主体> — <产品契合点> — <核心剪影特征>`。文末直接提议生成 6 张图。除非用户要求，否则不要把前期推导变成漫长的品牌研讨会。

## 复杂度预算（Complexity Budget）

- **外轮廓剪影**：由大约 `4–7` 个大型基础几何形构成连续、饱满、有分量感的外形。合并或剔除任何不承载辨识度、表情或独特个性的细碎形状。
- **标志性特征**：最多保留 1 处物种定义级特征：例如一个巨大的大嘴鸟囊喙、一对卷曲的大羊角，或一个宽大的护目镜面罩。
- **色彩区域**：内部色块严格对应 2 种主体色。五官仅限两只眼睛；仅在表情确有需要时才增加一张微小的嘴巴。除非辨识度必需，否则省略眉毛、高光点、鼻孔、毛发纹理、描边线条和装饰斑点。
- **剔除繁琐细节**：彻底剔除重复的羽毛、鳞片、毛发簇、盔甲接缝、纽扣、螺丝、数字、文字标贴等插画级冗余细节。
- **憨态幼态核心**：简约、可爱、具有婴儿般亲和力的钝感是决定性特质。大头身比、紧凑结构、圆润脸颊、间距较宽的简单眼睛，以及温和友善的神态。
- **微尺寸验证**：在黑色剪影和 `32 × 32` 像素微小尺寸下必须能一眼辨认。任何在该尺寸下模糊成噪点的细节，必须放大、合并或彻底删除。

## 形态语言与构图规则

- 采用厚实、圆润、饱满的轮廓曲线和大面积色块。
- **严厉禁止尖锐形态**：禁止尖角、尖耳朵、尖喙、细长尾巴、细触角、细线微笑、狭窄缝隙以及锐利的火焰或羽毛尖端。所有必需的尖端必须替换为肉眼可见的钝圆头。
- 成对出现的标志性特征（如双耳、双角、双翼、双腮、双铃铛）必须两边均完整呈现在画面中。
- **角落探出构图**：角色必须正向朝上，从指定的左下角（lower-left）或右下角（lower-right）探出，占据整个画布约 `85–95%` 的面积，使 IP 在视觉上占据绝对统治地位。
- 允许并在画面边缘做轻度裁剪以增强“从角落探出”的生动感，但不可死板规定边缘贴合像素。
- **严禁居中**：除非用户明确要求，否则绝不可将角色居中或底部居中放置。
- 构图保持正向立姿；未经明确要求，绝不可旋转画布或将主形倾斜。

## 视觉处理与简约质感

- 从大块干净的语义几何形和最具辨识度的极简剪影出发。角色应在五官细节被注意之前，就能凭剪影被瞬间识别。
- 宁可少而大、软而整，绝不画蛇添足。严禁为了解释解剖结构或材质质感而随意增加多余线条。
- 五官必须极小、极简且处于从属地位。禁止在眼睛、嘴巴、鼻子等微小部位添加高光反光点或深度凹坑渲染。
- 背景必须呈现为视觉上纯净均匀的单色纯色，绝无复杂场景、背景纹理、光晕、暗角或光影变化。
- 质感要求：仅在 Prompt 骨架中使用约定的单一句子触发微妙的立体感；切勿展开为数值参数或关于渐变、高光、阴影的复杂说明。模型自行附带的轻微光影、温润渐变属于正常现象，不可作为重新生成的理由。
- 视觉风格保持纯粹的平面图形感与极简微质感，切勿要求黏土、充气、塑料、毛绒玩具或逼真写实渲染。

## 色彩与画布规范

- **三语义色法则**：整张图片严格限制为 3 种语义颜色：2 种 IP 主体基础色 + 1 种纯色背景。
- 从产品定位、主体身份、调性和用户诉求中提取 2 种主体色。将其组织为大块、有目的的色彩块面；复用其中一种作为五官颜色，另一种作为连贯的特征色块，避免分散零碎的装饰碎块。
- 主体颜色独立于背景色进行选取。偏向清晰、明快的色彩，但不强制全局饱和度或色彩空间死板限制。
- 背景色自由选取或采用用户提供的色板。除非用户要求鲜艳背景，否则适当降低背景饱和度，使其呈现柔和、内敛、干净克制且有高级感的有色调，而非刺眼、发灰或脏浊。
- 确保 IP 主体剪影、五官与背景之间有清晰分明的视觉反差。若用户指定的背景对比度较弱，优先微调主体颜色，而非强行替换用户要求的背景。
- 在同一批次中，主动变化 2 种主体色的搭配策略，避免千篇一律地重复中性灰组合。
- 两种主体色作为语义色系对待，同色系内出现的自然轻微明暗过渡不视为违规。
- 在 Prompt 中直接点名背景纯色名称。要求背景填满所有开放区域和未被占用的角落，而指定的探出角落由角色占据。在 Prompt 中切勿使用 `opaque`、`alpha`、`transparency` 等底层图像模式术语。
- 画布统一生成直接的 `1:1` 正方形，直角外框。请求分辨率约 `1536 × 1536`；若服务端输出限制为 `1254 × 1254`，原样保留原生输出，绝不可为了凑数而盲目重采样拉伸。

## 提示词骨架（Prompt Skeleton）

### 按模型能力路由约束

根据运行时元数据、配置文档或用户说明确定实际生图模型。切勿凭空捏造不支持的参数。

**关键规则**：仅将目标产物描述为一幅纯粹的“图像（Image）”。**绝对不要在生成提示词中出现 `logo`、`brand mark`、`app icon`、`icon asset` 等字眼。** 切勿在提示词前添加揭示其为图标/Logo 的前置支架。该禁令仅适用于发给模型的生图 Prompt，外层的用户对话及 Skill 自身依然可以使用正常的业务表述。

- **现代指令遵循模型（如 GPT Image 2、Nano Banana Pro、Seedream 5.0 Pro 等）**：使用完整正向提示词，并在提示词内部以自然的 `Constraints:` 行表达最小排除项；不需要也不应为这类模型创建独立的负向提示词载荷。
- **显式支持负向提示词的老式模型（带有 `negative_prompt` 参数）**：保持正向提示词不变，通过专属参数传递负向排除词；同时从正向提示词中移除 `Constraints:` 行，避免双重传递冗余。
- **无负向参数的老式模型**：遵循其标准格式；仅能提供单字符串时，保留紧凑的 `Constraints:` 结尾行。
- 在交付报告中清晰记录所用模型、约束传递模式（`main-prompt constraints` 或 `dedicated negative parameter`）以及实际使用的约束内容。

当存在专属的负向提示词参数时，使用以下适配内容：

```text
text, watermark, borders, frames, cards, presentation masks, extra subjects, scenery, thin fragile lines, sharp tips, photorealistic materials, strong three-dimensional rendering, external cast shadows
```

现代指令模型与单提示词接口的完整提示词骨架（英文以确保模型最大理解精度）：

```text
Create one complete full-bleed 1:1 square image.
Background: fill the entire square with solid <background>. Keep <background> visible in every open area and in the corners not occupied by the character; the assigned emergence corner must be occupied by the character.
Subject: place one extremely simplified, cute, endearing <subject> IP character on the background, reduced to one soft rounded continuous silhouette and one defining feature.
Complexity: use only 4–7 large basic shapes and at most two broad internal color regions. Use two simple eyes and add one tiny mouth only when it helps the expression. Remove every nonessential line, outline, anatomical detail, texture, and decoration. Keep the character readable at 32 × 32.
Color behavior: use exactly three semantic colors in the complete image: exactly two IP base colors plus the background color. Choose the two IP colors from the subject and context, organize both into broad purposeful masses, and reuse them for facial marks. Choose the background independently or follow the user's supplied background. Unless the user asks for vivid color, lower the background saturation slightly so it feels gently muted and restrained while remaining clearly chromatic, clean, and intentional rather than gray or muddy. Keep the IP, facial marks, and background clearly separated. Treat any example palette as optional inspiration, never as an allowlist.
Composition: keep the character upright and emerging from the assigned <lower-left or lower-right>, filling about 85–95% of the square so it remains visually dominant. Cropping at the bottom or assigned side is welcome when it strengthens the corner emergence. Preserve both paired identifying features. Never center or bottom-center the character.
Style: make simplification, cuteness, and lovable baby-like appeal the strongest qualities. Use large soft forms, compact proportions, thick rounded contours, and an ultra-clean graphic treatment. Prefer one clear shape over several explanatory details. Add an extremely, extremely subtle, almost imperceptible sense of depth through a barely-there neo-skeuomorphic treatment.
Finish: show only the character on the full-canvas background, with clean surfaces and normal square outer corners.
Constraints: Use no text or watermark. Add no borders, frames, cards, or presentation masks. Include one character only, with no extra subjects or scenery. Use no fragile lines, sharp tips, unnecessary outlines, tiny details, or decorative marks. Add no photorealistic material, dramatic bevel, glossy hotspot, deep occlusion, extrusion, strong three-dimensional rendering, or external cast shadow. Keep the background solid and uniform, with no texture, vignette, or lighting variation.
```

## 交付与交付物呈现

- 将生成视为确定性的随机采样抽卡，而非符合性单元测试。
- 按要求的数量生成一次候选，并原样交付所有返回的图像文件。
- 默认不主动检查或报告透明通道、Alpha 通道或背景模式细节。
- 严禁自行拦截交付、将候选图武断归类为“合规/不合规”，或因为背景、色彩、细节、构图、光影微调而自动反复重试。
- 绝不通过后期处理强行修改结果。若用户在查看后提出调整要求，基于用户的明确新指令重新生成新的独立候选。
