"""小红书版本生成器 - 将公众号长文转为小红书5卡片笔记."""

import re
from pathlib import Path


class XHSGenerator:
    """生成小红书版本的文案、配图 prompts 和发布指南."""

    def __init__(self, article_dir: Path):
        self.article_dir = article_dir
        self.xhs_dir = article_dir / "images" / "xhs"
        self.prompts_dir = self.xhs_dir / "prompts"

    def generate(self, article: str, title: str) -> dict[str, Path]:
        """生成所有小红书相关文件，返回生成的文件路径字典."""
        self.xhs_dir.mkdir(parents=True, exist_ok=True)
        self.prompts_dir.mkdir(parents=True, exist_ok=True)

        # 1. 分析文章结构
        analysis = self._analyze_article(article, title)

        # 2. 生成5张卡片文案
        cards = self._generate_cards(analysis)
        xhs_version = self._build_xhs_version(cards, analysis)
        xhs_path = self.article_dir / "xhs-version.md"
        xhs_path.write_text(xhs_version, encoding="utf-8")

        # 3. 生成配图 prompts
        prompts = self._generate_image_prompts(cards, analysis)
        prompts_path = self.article_dir / "xhs-prompts.md"
        prompts_path.write_text(prompts, encoding="utf-8")

        # 4. 生成单独的 prompt 文件到 images/xhs/prompts/
        self._write_individual_prompts(cards)

        # 5. 生成发布指南
        guide = self._generate_publish_guide(cards)
        guide_path = self.article_dir / "XHS_PUBLISH_GUIDE.md"
        guide_path.write_text(guide, encoding="utf-8")

        return {
            "xhs_version": xhs_path,
            "prompts": prompts_path,
            "guide": guide_path,
        }

    def _analyze_article(self, article: str, title: str) -> dict:
        """分析文章结构，提取关键元素."""
        # 提取标题（如果 article 以 # 开头）
        lines = article.strip().split("\n")
        first_line = lines[0].strip() if lines else ""
        if first_line.startswith("# "):
            title = first_line[2:].strip()

        # 提取章节
        sections = []
        current_section = {"title": "", "content": "", "level": 0}
        for line in lines:
            if line.startswith("## "):
                if current_section["content"]:
                    sections.append(current_section)
                current_section = {"title": line[3:].strip(), "content": "", "level": 2}
            elif line.startswith("### "):
                if current_section["content"]:
                    sections.append(current_section)
                current_section = {"title": line[4:].strip(), "content": "", "level": 3}
            else:
                current_section["content"] += line + "\n"
        if current_section["content"]:
            sections.append(current_section)

        # 提取加粗文字（可能的金句）
        bold_phrases = re.findall(r"\*\*(.+?)\*\*", article)
        key_quotes = [b for b in bold_phrases if len(b) > 10 and len(b) < 80][:5]

        # 提取列表项
        list_items = re.findall(r"^[\s]*[-*]\s+(.+)$", article, re.MULTILINE)

        # 提取引言/blockquote
        blockquotes = re.findall(r"^\s*\>\s*(.+)$", article, re.MULTILINE)

        # 检测文章类型和核心主题
        content_lower = article.lower()
        has_story = any(w in content_lower for w in ["那年", "有一天", "后来", "当时", "记得"])
        has_tutorial = any(w in content_lower for w in ["步骤", "教程", "如何", "方法", "技巧"])
        has_review = any(w in content_lower for w in ["测评", "对比", "体验", "使用", "推荐"])

        article_type = (
            "story"
            if has_story
            else ("tutorial" if has_tutorial else ("review" if has_review else "insight"))
        )

        # 提取时间/数字对比（小红书封面钩子常用）
        time_patterns = re.findall(r"(\d+)\s*(个月|年|天|小时|周|分钟)", article)
        number_hooks = re.findall(r"(\d+)[\s]*([%％倍个种项张条件]+)", article)

        return {
            "title": title,
            "sections": sections,
            "key_quotes": key_quotes,
            "list_items": list_items[:8],
            "blockquotes": blockquotes[:3],
            "article_type": article_type,
            "time_hooks": time_patterns,
            "number_hooks": number_hooks,
            "word_count": len(article),
        }

    def _generate_cards(self, analysis: dict) -> list[dict]:
        """生成5张卡片的内容."""
        sections = analysis["sections"]
        article_type = analysis["article_type"]
        quotes = analysis["key_quotes"]

        cards = []

        # 卡片1：封面 - 强钩子
        hook = self._generate_hook(analysis)
        cards.append(
            {
                "number": 1,
                "type": "cover",
                "title": "封面",
                "hook": hook,
                "body": f"{hook}\n\n经济学女生｜零基础｜AI编程\n\n不是我开始得早\n是我差点就放弃了😭",
                "visual_theme": "暗到明的光线变化，女孩+笔记本电脑",
            }
        )

        # 卡片2：故事起点 / 问题
        problem_content = self._extract_problem_section(sections)
        cards.append(
            {
                "number": 2,
                "type": "problem",
                "title": "故事起点" if article_type == "story" else "核心问题",
                "hook": problem_content["hook"],
                "body": problem_content["body"],
                "visual_theme": problem_content["visual"],
            }
        )

        # 卡片3：转折点 / 方案
        turning_content = self._extract_turning_section(sections)
        cards.append(
            {
                "number": 3,
                "type": "turning",
                "title": "转折点" if article_type == "story" else "解决方案",
                "hook": turning_content["hook"],
                "body": turning_content["body"],
                "visual_theme": turning_content["visual"],
            }
        )

        # 卡片4：领悟 / 干货
        insight_content = self._extract_insight_section(sections, quotes)
        cards.append(
            {
                "number": 4,
                "type": "insight",
                "title": "核心领悟" if article_type == "story" else "关键要点",
                "hook": insight_content["hook"],
                "body": insight_content["body"],
                "visual_theme": insight_content["visual"],
            }
        )

        # 卡片5：结尾 + CTA
        ending_content = self._generate_ending(analysis)
        cards.append(
            {
                "number": 5,
                "type": "ending",
                "title": "结尾",
                "hook": ending_content["hook"],
                "body": ending_content["body"],
                "visual_theme": ending_content["visual"],
            }
        )

        return cards

    def _generate_hook(self, analysis: dict) -> str:
        """生成封面钩子标题."""
        time_hooks = analysis["time_hooks"]
        title = analysis["title"]

        # 如果有时间对比，优先用
        if len(time_hooks) >= 2:
            return f"{time_hooks[0][0]}{time_hooks[0][1]}没做到的事，AI {time_hooks[1][0]}{time_hooks[1][1]}帮我做完了"

        # 如果有数字钩子
        if analysis["number_hooks"]:
            nh = analysis["number_hooks"][0]
            return f"试了{nh[0]}{nh[1]}后，我终于找到了答案"

        # 从标题改造
        if "，" in title or "。" in title:
            short = title.split("，")[0].split("。")[0]
            return short + "💡"

        return title + "｜普通人真实记录"

    def _extract_problem_section(self, sections: list) -> dict:
        """提取故事起点/问题部分."""
        if not sections:
            return {
                "hook": "曾经我也以为这件事很难",
                "body": "直到我亲身经历之后，才发现真相完全不同...\n\n你们有过这样的经历吗？",
                "visual": "困惑的人看着复杂的迷宫",
            }

        # 找第一个有实质内容的章节
        for sec in sections:
            content = sec["content"].strip()
            if len(content) > 50:
                lines = content.split("\n")
                # 提取前3-4个非空段落
                paragraphs = [line.strip() for line in lines if line.strip()][:4]
                body = "\n\n".join(paragraphs)

                # 找列表项
                list_in_section = re.findall(r"^[\s]*[-*]\s+(.+)$", content, re.MULTILINE)
                if list_in_section:
                    body += "\n\n想解决但不敢碰的问题：\n" + "\n".join(
                        [f"• {item}" for item in list_in_section[:5]]
                    )

                return {
                    "hook": sec["title"],
                    "body": body,
                    "visual": "旧电脑/落灰的桌面/墙上日历",
                }

        return {
            "hook": "故事从这里开始",
            "body": sections[0]["content"][:300] if sections else "",
            "visual": "温馨的日常场景",
        }

    def _extract_turning_section(self, sections: list) -> dict:
        """提取转折点/方案部分."""
        if len(sections) < 2:
            return {
                "hook": "转机出现了",
                "body": "一个偶然的机会，我发现了完全不同的方法...",
                "visual": "闪电/光束/开门",
            }

        # 找中间的章节
        mid_idx = len(sections) // 2
        sec = sections[mid_idx]
        content = sec["content"].strip()
        lines = content.split("\n")
        paragraphs = [line.strip() for line in lines if line.strip()][:5]

        # 找加粗的关键结论
        bold = re.findall(r"\*\*(.+?)\*\*", content)
        key_point = bold[0] if bold else sec["title"]

        body = "\n\n".join(paragraphs)
        if len(body) > 500:
            body = body[:500] + "..."

        return {
            "hook": key_point,
            "body": body,
            "visual": "进度条飞速填满/机器人助手/彩色对勾",
        }

    def _extract_insight_section(self, sections: list, quotes: list[str]) -> dict:
        """提取核心领悟/干货部分."""
        # 找后面的章节（通常是总结/领悟）
        if len(sections) >= 3:
            sec = sections[-2]
        elif sections:
            sec = sections[-1]
        else:
            sec = {"title": "核心领悟", "content": ""}

        content = sec["content"].strip()

        # 优先用金句
        hook = quotes[0] if quotes else sec["title"]

        # 提取前后对比
        before_after = re.findall(r"以前(.+?)现在(.+?)[。\n]", content)
        body_lines = []
        if before_after:
            body_lines.append("💡 我终于懂了：\n")
            for before, after in before_after[:2]:
                body_lines.append(f"以前：{before} ❌")
                body_lines.append(f"现在：{after} ✅\n")

        # 补充段落
        lines = content.split("\n")
        paragraphs = [line.strip() for line in lines if line.strip() and not line.startswith("#")][
            :3
        ]
        if paragraphs:
            body_lines.append("\n".join(paragraphs))

        body = "\n".join(body_lines) if body_lines else content[:400]

        return {
            "hook": hook,
            "body": body,
            "visual": "锁着的门→敞开的门/灯泡发光/前后对比",
        }

    def _generate_ending(self, analysis: dict) -> dict:
        """生成结尾卡片."""
        sections = analysis["sections"]

        # 提取最后的段落作为结尾
        last_content = ""
        if sections:
            last_sec = sections[-1]
            last_content = last_sec["content"].strip()

        # 提取自我介绍相关
        about_me = []
        lines = last_content.split("\n")
        for line in lines:
            if any(kw in line for kw in ["关于我", "我是谁", "背景", "专业"]):
                about_me.append(line.strip())

        # 构建互动问题
        if analysis["article_type"] == "story":
            cta = "💬 你有没有类似的经历？\n欢迎在评论区聊聊 👇"
        elif analysis["article_type"] == "tutorial":
            cta = "💬 你试过这个方法吗？\n有什么问题评论区问我 👇"
        else:
            cta = "💬 你怎么看？\n评论区聊聊你的想法 👇"

        body_parts = [
            "所以这个号会发：\n",
            "✅ 我真实在用的AI工具（亲测两周以上）",
            "✅ 我做项目的过程和踩坑记录",
            "✅ 一个经济学女生看AI的视角\n",
        ]

        if about_me:
            body_parts.append("\n".join(about_me[:3]))

        body_parts.append(f"\n{cta}")

        return {
            "hook": "所以我开了这个号 ✨",
            "body": "\n".join(body_parts),
            "visual": "金色日落/开阔道路/前行的人影",
        }

    def _build_xhs_version(self, cards: list[dict], analysis: dict) -> str:
        """构建完整的 xhs-version.md 内容."""
        title = analysis["title"]
        lines = [
            f"# 小红书版本 - {title}",
            "",
            f"> 源自公众号文章《{title}》",
            "> 适配平台：小红书（5张卡片系列笔记）",
            "",
            "---",
            "",
            "## 发布信息",
            "",
            f"- **小红书标题**：{cards[0]['hook']}",
            "- **话题标签**：#AI编程 #ClaudeCode #零基础学编程 #自我成长 #效率工具 #女性成长 #编程入门 #AI工具",
            "- **发布时间建议**：工作日晚 20:00-22:00 或周末下午 14:00-16:00",
            "- **账号定位**：经济学背景女生，记录用AI学编程的真实历程",
            "",
            "---",
            "",
        ]

        for card in cards:
            lines.extend(
                [
                    f"## 卡片 {card['number']}：{card['title']}",
                    "",
                    "**文案内容**：",
                    "",
                    "```",
                    card["body"],
                    "```",
                    "",
                    "**视觉要点**：",
                    f"- {card['visual_theme']}",
                    "",
                    "---",
                    "",
                ]
            )

        lines.extend(
            [
                "## 整体发布策略",
                "",
                "1. **首图测试**：可以先发一张封面测试点击率，如果低就换标题重新发",
                "2. **评论区预埋**：自己先评论一条相关话题，引导互动",
                "3. **系列感**：如果这篇数据好，可以连续发相关主题",
                "4. **引流注意**：小红书严禁直接引流公众号，可以在简介放，正文不要放链接",
                "",
                "---",
                "",
                "*Generated by WechatArticle xhs command*",
            ]
        )

        return "\n".join(lines)

    def _generate_image_prompts(self, cards: list[dict], analysis: dict) -> str:
        """生成配图 prompts 文档."""
        visual_prompts = [
            {
                "theme": "封面",
                "en": "A warm and inspiring illustration for a Xiaohongshu cover. Split composition: dark blue-purple night sky transitioning to warm golden sunrise light at the bottom. A young woman sitting at a desk with a laptop, the screen emitting a soft glow that illuminates her face. The scene transforms from dim/monochrome (left) to bright/colorful (right), symbolizing awakening and breakthrough. Soft watercolor texture, dreamy atmosphere, pastel colors with golden accents. Include subtle coding elements (floating brackets, pixels) dissolving into light particles. 3:4 vertical format, clean minimalist design with space for text overlay at top.",
                "cn": "温暖治愈的小红书封面插画。画面从左上角的深蓝紫色夜空渐变到右下角的暖金色日出。一位年轻女生坐在书桌前用笔记本电脑，屏幕发出柔和光芒照亮她的脸。画面从暗淡（左）到明亮多彩（右），象征觉醒与突破。水彩质感，梦幻氛围，pastel色系配金色点缀。漂浮的代码符号化作光点消散。3:4竖版，顶部留白。",
            },
            {
                "theme": "故事起点",
                "en": "A cozy flat illustration of an old laptop sitting on a wooden desk, covered with a thin layer of dust. The screen shows a simple note-taking app interface. Around the laptop are sticky notes with handwritten text crossed out in red. A small calendar on the wall shows months passing by. Muted blue-gray color palette with warm wood tones. Soft shadows, gentle melancholy mood. Minimalist style, plenty of white space for text. 3:4 vertical format.",
                "cn": "温馨的扁平插画。一台旧笔记本电脑放在木质书桌上，覆盖着薄薄灰尘。屏幕显示简单备忘录界面。电脑周围贴着便利贴，手写文字被红笔划掉。墙上小日历显示月份流逝。muted蓝灰色配温暖木色。柔和阴影，淡淡的惆怅感。极简风格，大量留白。3:4竖版。",
            },
            {
                "theme": "转折点",
                "en": "An energetic modern illustration showing a laptop screen exploding with colorful checkmarks and completion notifications. A progress bar rapidly filling from 0% to 100%. Small robot/AI assistant character (cute, friendly) helping organize floating UI elements into neat rows. Electric blue and purple gradient background with motion blur effects. Lightning bolt accents, speed lines. Dynamic diagonal composition. Clean vector illustration style, bold colors, high contrast. 3:4 vertical format with space for text.",
                "cn": "充满活力的现代插画。笔记本电脑屏幕迸发出彩色对勾和完成通知。进度条从0%飞速填满到100%。可爱的AI小助手机器人帮忙整理漂浮的UI元素，排列整齐。电光蓝和紫色渐变背景，动态模糊效果。闪电装饰，速度线。动态对角线构图。clean矢量插画风格，大胆色彩，高对比度。3:4竖版，留白用于文字。",
            },
            {
                "theme": "核心领悟",
                "en": "A split-screen illustration showing a transformation. Left side (cool blue-gray): a person standing in front of a locked door, looking confused, with question marks floating around. Right side (warm golden): the same person standing in an open doorway with bright light streaming through, confidently holding a glowing lightbulb. The two halves are connected by a subtle gradient transition. Clean geometric style, warm and inspiring mood. Minimal details, symbolic and metaphorical. Soft pastel colors on the warm side. 3:4 vertical format with center space for a bold quote.",
                "cn": "分屏式插画展示转变。左侧（冷蓝灰色）：一个人站在锁着的门前，表情困惑，周围漂浮问号。右侧（暖金色）：同一个人站在敞开的门口，明亮光线涌入，自信地捧着发光灯泡。两半由微妙渐变连接。clean几何风格，温暖励志氛围。极简细节，象征隐喻。暖侧用柔和pastel色。3:4竖版，中间留白用于金句。",
            },
            {
                "theme": "结尾",
                "en": "A serene landscape illustration at golden hour. A wide open road stretching into a beautiful sunset with rays of light breaking through clouds. A small silhouette of a person walking confidently on the road. The sky is painted in warm orange, pink, and soft purple gradients. Floating light particles and soft bokeh effects. In the foreground, small wildflowers blooming. Dreamy, hopeful, inspiring atmosphere. Watercolor texture mixed with clean vector elements. 3:4 vertical format, top area reserved for text.",
                "cn": "宁静的黄金时刻风景插画。一条宽阔开阔的道路延伸至美丽日落，光线穿透云层。一个小小的人影自信地走在路上。天空绘有温暖的橙色、粉色和柔和紫色渐变。漂浮的光粒子和柔和散景效果。前景有小野花在绽放。梦幻、充满希望、励志的氛围。水彩质感混合clean矢量元素。3:4竖版，顶部留白用于文字。",
            },
        ]

        lines = [
            "# 小红书配图 Prompts",
            "",
            "## 通用设置",
            "",
            "- **尺寸**：1080 x 1440 px (3:4 竖版)",
            "- **风格**：扁平插画 / 治愈系 / 温暖明亮",
            "- **质量**：高清 / 2K",
            "",
        ]

        for i, (card, vp) in enumerate(zip(cards, visual_prompts, strict=False)):
            lines.extend(
                [
                    f"## 卡片 {i + 1}：{card['title']}",
                    "",
                    f"**构图**：竖版 3:4，{card['visual_theme']}",
                    "",
                    "**英文 Prompt**：",
                    "```",
                    vp["en"],
                    "```",
                    "",
                    "**中文 Prompt**（国产工具更友好）：",
                    "```",
                    vp["cn"],
                    "```",
                    "",
                    "---",
                    "",
                ]
            )

        lines.extend(
            [
                "## 工具推荐",
                "",
                "| 工具 | 优点 | 推荐度 |",
                "|------|------|--------|",
                "| 即梦 (Jimeng) | 中文理解好，免费额度多 | ⭐⭐⭐⭐⭐ |",
                "| 通义万相 | 阿里云，插画风格稳定 | ⭐⭐⭐⭐ |",
                "| 豆包 (Seedream) | 字节跳动，中文场景好 | ⭐⭐⭐⭐ |",
                "| Midjourney | 质量最高，需翻墙 | ⭐⭐⭐⭐ |",
                "",
                "*Generated by WechatArticle xhs command*",
            ]
        )

        return "\n".join(lines)

    def _write_individual_prompts(self, cards: list[dict]) -> None:
        """将每张图的 prompt 写入单独文件."""
        visual_prompts = [
            {
                "en": "A warm and inspiring illustration for a Xiaohongshu cover. Split composition: dark blue-purple night sky transitioning to warm golden sunrise light at the bottom. A young woman sitting at a desk with a laptop, the screen emitting a soft glow that illuminates her face. The scene transforms from dim/monochrome (left) to bright/colorful (right), symbolizing awakening and breakthrough. Soft watercolor texture, dreamy atmosphere, pastel colors with golden accents. Include subtle coding elements (floating brackets, pixels) dissolving into light particles. 3:4 vertical format, clean minimalist design with space for text overlay at top.",
                "cn": "温暖治愈的小红书封面插画。画面从左上角的深蓝紫色夜空渐变到右下角的暖金色日出。一位年轻女生坐在书桌前用笔记本电脑，屏幕发出柔和光芒照亮她的脸。画面从暗淡（左）到明亮多彩（右），象征觉醒与突破。水彩质感，梦幻氛围，pastel色系配金色点缀。漂浮的代码符号化作光点消散。3:4竖版，顶部留白。",
            },
            {
                "en": "A cozy flat illustration of an old laptop sitting on a wooden desk, covered with a thin layer of dust. The screen shows a simple note-taking app interface. Around the laptop are sticky notes with handwritten text crossed out in red. A small calendar on the wall shows months passing by. Muted blue-gray color palette with warm wood tones. Soft shadows, gentle melancholy mood. Minimalist style, plenty of white space for text. 3:4 vertical format.",
                "cn": "温馨的扁平插画。一台旧笔记本电脑放在木质书桌上，覆盖着薄薄灰尘。屏幕显示简单备忘录界面。电脑周围贴着便利贴，手写文字被红笔划掉。墙上小日历显示月份流逝。muted蓝灰色配温暖木色。柔和阴影，淡淡的惆怅感。极简风格，大量留白。3:4竖版。",
            },
            {
                "en": "An energetic modern illustration showing a laptop screen exploding with colorful checkmarks and completion notifications. A progress bar rapidly filling from 0% to 100%. Small robot/AI assistant character (cute, friendly) helping organize floating UI elements into neat rows. Electric blue and purple gradient background with motion blur effects. Lightning bolt accents, speed lines. Dynamic diagonal composition. Clean vector illustration style, bold colors, high contrast. 3:4 vertical format with space for text.",
                "cn": "充满活力的现代插画。笔记本电脑屏幕迸发出彩色对勾和完成通知。进度条从0%飞速填满到100%。可爱的AI小助手机器人帮忙整理漂浮的UI元素，排列整齐。电光蓝和紫色渐变背景，动态模糊效果。闪电装饰，速度线。动态对角线构图。clean矢量插画风格，大胆色彩，高对比度。3:4竖版，留白用于文字。",
            },
            {
                "en": "A split-screen illustration showing a transformation. Left side (cool blue-gray): a person standing in front of a locked door, looking confused, with question marks floating around. Right side (warm golden): the same person standing in an open doorway with bright light streaming through, confidently holding a glowing lightbulb. The two halves are connected by a subtle gradient transition. Clean geometric style, warm and inspiring mood. Minimal details, symbolic and metaphorical. Soft pastel colors on the warm side. 3:4 vertical format with center space for a bold quote.",
                "cn": "分屏式插画展示转变。左侧（冷蓝灰色）：一个人站在锁着的门前，表情困惑，周围漂浮问号。右侧（暖金色）：同一个人站在敞开的门口，明亮光线涌入，自信地捧着发光灯泡。两半由微妙渐变连接。clean几何风格，温暖励志氛围。极简细节，象征隐喻。暖侧用柔和pastel色。3:4竖版，中间留白用于金句。",
            },
            {
                "en": "A serene landscape illustration at golden hour. A wide open road stretching into a beautiful sunset with rays of light breaking through clouds. A small silhouette of a person walking confidently on the road. The sky is painted in warm orange, pink, and soft purple gradients. Floating light particles and soft bokeh effects. In the foreground, small wildflowers blooming. Dreamy, hopeful, inspiring atmosphere. Watercolor texture mixed with clean vector elements. 3:4 vertical format, top area reserved for text.",
                "cn": "宁静的黄金时刻风景插画。一条宽阔开阔的道路延伸至美丽日落，光线穿透云层。一个小小的人影自信地走在路上。天空绘有温暖的橙色、粉色和柔和紫色渐变。漂浮的光粒子和柔和散景效果。前景有小野花在绽放。梦幻、充满希望、励志的氛围。水彩质感混合clean矢量元素。3:4竖版，顶部留白用于文字。",
            },
        ]

        for i, (card, vp) in enumerate(zip(cards, visual_prompts, strict=False)):
            # 保存英文版本
            en_path = self.prompts_dir / f"{i + 1:02d}-{card['type']}.md"
            en_content = f"{vp['en']}\n"
            en_path.write_text(en_content, encoding="utf-8")

    def _generate_publish_guide(self, cards: list[dict]) -> str:
        """生成发布指南."""
        lines = [
            "# 小红书发布指南",
            "",
            "> 源自公众号文章，适配小红书5卡片系列笔记",
            "",
            "---",
            "",
            "## 一、图片生成清单",
            "",
            "### 工具选择建议",
            "",
            "| 工具 | 优点 | 推荐度 |",
            "|------|------|--------|",
            "| **即梦 (Jimeng)** | 中文理解好，出图快，免费额度多 | ⭐⭐⭐⭐⭐ |",
            "| **通义万相** | 阿里云，插画风格稳定 | ⭐⭐⭐⭐ |",
            "| **豆包 (Seedream)** | 字节跳动，中文场景理解好 | ⭐⭐⭐⭐ |",
            "| **Midjourney** | 质量最高，但需翻墙+付费 | ⭐⭐⭐⭐ |",
            "",
            "### 通用设置",
            "",
            "- **尺寸**：1080 x 1440（3:4 竖版）",
            "- **风格**：插画 / 扁平风 / 治愈系",
            "- **质量**：高清 / 2K",
            "",
            "---",
            "",
            "## 二、5张卡片 Prompt（直接复制使用）",
            "",
        ]

        visual_prompts = [
            {
                "cn": "温暖治愈的小红书封面插画。画面从左上角的深蓝紫色夜空渐变到右下角的暖金色日出。一位年轻女生坐在书桌前用笔记本电脑，屏幕发出柔和光芒照亮她的脸。画面从暗淡（左）到明亮多彩（右），象征觉醒与突破。水彩质感，梦幻氛围，pastel色系配金色点缀。漂浮的代码符号化作光点消散。3:4竖版，顶部留白。",
            },
            {
                "cn": "温馨的扁平插画。一台旧笔记本电脑放在木质书桌上，覆盖着薄薄灰尘。屏幕显示简单备忘录界面。电脑周围贴着便利贴，手写文字被红笔划掉。墙上小日历显示月份流逝。muted蓝灰色配温暖木色。柔和阴影，淡淡的惆怅感。极简风格，大量留白。3:4竖版。",
            },
            {
                "cn": "充满活力的现代插画。笔记本电脑屏幕迸发出彩色对勾和完成通知。进度条从0%飞速填满到100%。可爱的AI小助手机器人帮忙整理漂浮的UI元素，排列整齐。电光蓝和紫色渐变背景，动态模糊效果。闪电装饰，速度线。动态对角线构图。clean矢量插画风格，大胆色彩，高对比度。3:4竖版，留白用于文字。",
            },
            {
                "cn": "分屏式插画展示转变。左侧（冷蓝灰色）：一个人站在锁着的门前，表情困惑，周围漂浮问号。右侧（暖金色）：同一个人站在敞开的门口，明亮光线涌入，自信地捧着发光灯泡。两半由微妙渐变连接。clean几何风格，温暖励志氛围。极简细节，象征隐喻。暖侧用柔和pastel色。3:4竖版，中间留白用于金句。",
            },
            {
                "cn": "宁静的黄金时刻风景插画。一条宽阔开阔的道路延伸至美丽日落，光线穿透云层。一个小小的人影自信地走在路上。天空绘有温暖的橙色、粉色和柔和紫色渐变。漂浮的光粒子和柔和散景效果。前景有小野花在绽放。梦幻、充满希望、励志的氛围。水彩质感混合clean矢量元素。3:4竖版，顶部留白用于文字。",
            },
        ]

        for i, (card, vp) in enumerate(zip(cards, visual_prompts, strict=False)):
            lines.extend(
                [
                    f"### 卡片 {i + 1}：{card['title']}",
                    "",
                    "```",
                    vp["cn"],
                    "```",
                    "",
                ]
            )

        lines.extend(
            [
                "---",
                "",
                "## 三、发布操作步骤",
                "",
                "### Step 1：生成图片",
                "",
                "1. 打开你选择的AI画图工具（推荐即梦）",
                "2. 逐张复制上面的 Prompt（中英文任选，中文对国产工具更友好）",
                "3. 设置尺寸为 **3:4 竖版**（或 1080x1440）",
                "4. 生成后下载，按顺序命名：",
                "   - `01-cover.png`",
                "   - `02-story.png`",
                "   - `03-turning.png`",
                "   - `04-insight.png`",
                "   - `05-ending.png`",
                "",
                "### Step 2：添加文字",
                "",
                "**工具推荐**：",
                "- 手机：醒图、美图秀秀、黄油相机",
                "- 电脑：Figma、Canva、PS",
                "",
                "**文字排版要点**：",
                "- 封面：大标题居中，字体粗重，加阴影或描边确保可读性",
                "- 内容卡片：文字放在图片空白区域，不要遮挡主体",
                "- 每行不超过15个字，多用换行",
                "- emoji 适当点缀，但不要过多",
                "",
                "### Step 3：小红书发布",
                "",
                "1. 打开小红书 App -> 点击底部'+'",
                "2. 选择5张图片，**确保顺序正确**（封面在第1张）",
                f"3. 填写标题：`{cards[0]['hook']}`",
                "4. 复制 `xhs-version.md` 中每张卡片的文案，粘贴到对应位置",
                "5. 添加话题标签：",
                "   `#AI编程 #ClaudeCode #零基础学编程 #自我成长 #效率工具 #女性成长 #编程入门 #AI工具`",
                "6. 发布",
                "",
                "---",
                "",
                "## 四、发布后操作（重要！）",
                "",
                "### 立即执行（发布后5分钟内）",
                "",
                "- [ ] 自己评论第一条：引导互动的话题",
                "- [ ] 回复前3条评论（哪怕是简单的'谢谢''是的'）",
                "",
                "### 数据监测（发布后24小时）",
                "",
                "- [ ] 小眼睛（阅读量）> 500：正常",
                "- [ ] 小眼睛 < 200：考虑换封面标题重新发",
                "- [ ] 点赞 > 阅读量 x 5%：内容质量过关",
                "- [ ] 收藏 > 点赞：说明干货价值高",
                "",
                "---",
                "",
                "## 五、禁忌清单",
                "",
                "- ❌ 正文出现'关注我的公众号''搜XXX'",
                "- ❌ 放二维码（任何平台的）",
                "- ❌ 引导加微信/私信",
                "- ❌ 连续发相同内容",
                "- ❌ 短时间内大量删评",
                "",
                "---",
                "",
                "*Generated by WechatArticle xhs command*",
            ]
        )

        return "\n".join(lines)
