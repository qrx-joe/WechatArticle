import tempfile
from pathlib import Path

from src.output import ArticleOutput


class TestArticleOutput:
    def test_save_markdown(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = ArticleOutput(Path(tmpdir))
            path = output.save_markdown("# Hello\n\nWorld")
            assert path.exists()
            assert path.read_text(encoding="utf-8") == "# Hello\n\nWorld"

    def test_save_markdown_custom_filename(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = ArticleOutput(Path(tmpdir))
            path = output.save_markdown("content", filename="article_raw.md")
            assert path.name == "article_raw.md"
            assert path.read_text(encoding="utf-8") == "content"

    def test_save_outline(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = ArticleOutput(Path(tmpdir))
            path = output.save_outline("## 大纲")
            assert path.name == "outline.md"
            assert path.read_text(encoding="utf-8") == "## 大纲"

    def test_generate_copy_guide(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = ArticleOutput(Path(tmpdir))
            image_plan = [
                {"index": 0, "filename": "image_00.png", "context": "封面", "prompt": "test"},
                {"index": 1, "filename": "image_01.png", "context": "正文", "prompt": "test2"},
            ]
            path = output.generate_copy_guide(image_plan)
            assert path.exists()
            content = path.read_text(encoding="utf-8")
            assert "图片 1" in content
            assert "图片 2" in content
            assert "image_00.png" in content

    def test_generate_copy_guide_empty_plan(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = ArticleOutput(Path(tmpdir))
            path = output.generate_copy_guide([])
            content = path.read_text(encoding="utf-8")
            assert "发布指引" in content

    def test_generate_jike_prompt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = ArticleOutput(Path(tmpdir))
            prompt = output.generate_jike_prompt()
            assert "即刻" in prompt
            assert "主帖" in prompt

    def test_generate_summary_prompt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = ArticleOutput(Path(tmpdir))
            prompt = output.generate_summary_prompt()
            assert "摘要" in prompt
            assert "80-120" in prompt

    def test_print_summary(self, capsys):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = ArticleOutput(Path(tmpdir))
            output.print_summary("测试标题", 2000, 3)
            captured = capsys.readouterr()
            assert "测试标题" in captured.out
            assert "2000" in captured.out
