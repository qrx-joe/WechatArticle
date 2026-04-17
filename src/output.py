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

    def generate_copy_guide(self, image_plan: list[dict]) -> str:
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

    def print_summary(self, title: str, word_count: int, image_count: int):
        """打印文章生成摘要."""
        print(f"\n{'='*50}")
        print(f"  文章生成完成")
        print(f"{'='*50}")
        print(f"  标题: {title}")
        print(f"  字数: {word_count}")
        print(f"  配图: {image_count} 张")
        print(f"  目录: {self.article_dir}")
        print(f"{'='*50}")
        print(f"\n  文件列表:")
        for f in sorted(self.article_dir.rglob("*")):
            if f.is_file():
                rel = f.relative_to(self.article_dir)
                print(f"    - {rel}")
        print(f"\n  下一步: 按 PUBLISH_GUIDE.md 指引发布")
        print(f"{'='*50}\n")
