from pathlib import Path


class ArticleOutput:
    """管理文章输出格式."""

    def __init__(self, article_dir: Path):
        self.article_dir = article_dir
        self.images_dir = article_dir / "images"

    def save_markdown(self, content: str, filename: str = "article.md"):
        """保存 Markdown 格式文章."""
        path = self.article_dir / filename
        path.write_text(content, encoding="utf-8")
        return path

    def save_outline(self, content: str):
        """保存大纲."""
        path = self.article_dir / "outline.md"
        path.write_text(content, encoding="utf-8")
        return path

    def generate_copy_guide(self, image_plan: list[dict]) -> Path:
        """生成手动复制到公众号的指引文档."""
        lines = [
            "# 发布指引",
            "",
            "## 操作步骤",
            "",
            "1. 打开微信公众号后台编辑器",
            "2. 复制 `article.md` 中的 Markdown 内容",
            "3. 使用 Markdown 转公众号工具（如墨滴、壹伴等）粘贴转换",
            "4. 按以下说明插入配图：",
            "",
        ]

        for img in image_plan:
            lines.append(f"### 图片 {img['index'] + 1}: {img['filename']}")
            lines.append(f"- **位置**: {img['context']}")
            lines.append(f"- **文件**: `{self.images_dir / img['filename']}`")
            lines.append(f"- **Prompt**: {img['prompt']}")
            lines.append("")

        lines.append("## 提示")
        lines.append("- 封面图请单独上传到公众号封面位置")
        lines.append("- 正文配图请在对应位置插入")
        lines.append("- 建议先预览效果再发布")

        guide = "\n".join(lines)
        path = self.article_dir / "PUBLISH_GUIDE.md"
        path.write_text(guide, encoding="utf-8")
        return path

    def generate_jike_prompt(self) -> str:
        """生成即刻版本改写 prompt."""
        prompt = """请将以上公众号长文改写为即刻（Jike）短版本。

## 即刻平台特点
- 内容长度：200-400 字最佳（主帖）
- 格式：纯文本+图，不需要复杂排版
- 阅读场景：信息流刷过，3秒定生死，开头必须有钩子
- 不需要标题，开头第一句就是标题
- 标签很重要，决定推荐流量，必须加相关标签

## 输出要求

### 1. 主帖文案
- 用第一人称，语气真实自然
- 开头一句必须是强钩子（悬念、冲突、反常识）
- 主体 200-400 字，保留最核心的故事线
- 结尾要有情绪落点或行动号召
- 添加 3-5 个相关标签（格式：#标签名）

### 2. 评论区补充（可选）
- 如果主帖内容较长，可以拆分成 2-3 条评论补充
- 每条评论 50-150 字
- 评论可以展开细节、解释背景、或引导互动

### 3. 配图建议
- 说明主帖配哪张图（从文章配图方案中选择）
- 即刻信息流中显示为正方形缩略图

### 4. 发布时机建议
- 最佳发布时间：工作日晚上 21:00-23:00

## 输出格式

请按以下格式输出：

```
## 主帖
[主帖文案]

## 评论1
[评论内容]

## 评论2
[评论内容]

## 标签建议
#标签1 #标签2 #标签3

## 配图建议
主帖配图：[图片文件名]
```
"""
        return prompt

    def generate_summary_prompt(self) -> str:
        """生成文章摘要 prompt."""
        prompt = """请根据以上公众号文章内容，生成一段文章摘要。

## 摘要要求
- 字数：80-120 字
- 必须是独立的钩子，不能只是第一句话的复述
- 要传达文章的核心洞察或冲突，让读者有点击欲望
- 不要用"本文介绍了""这篇文章讲述了"这类套话
- 可以用数据、对比、反常识来制造吸引力

## 输出格式

只输出摘要文本，不要加标题、引号或其他格式标记。"""
        return prompt

    def print_summary(self, title: str, word_count: int, image_count: int):
        """打印文章生成摘要."""
        print(f"\n{'=' * 50}")
        print("  文章生成完成")
        print(f"{'=' * 50}")
        print(f"  标题: {title}")
        print(f"  字数: {word_count}")
        print(f"  配图: {image_count} 张")
        print(f"  目录: {self.article_dir}")
        print(f"{'=' * 50}")
        print("\n  文件列表:")
        for f in sorted(self.article_dir.rglob("*")):
            if f.is_file():
                rel = f.relative_to(self.article_dir)
                print(f"    - {rel}")
        print("\n  下一步: 按 PUBLISH_GUIDE.md 指引发布")
        print(f"{'=' * 50}\n")
