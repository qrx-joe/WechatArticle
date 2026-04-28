import tempfile
from pathlib import Path

from src.xhs_generator import XHSGenerator

SAMPLE_ARTICLE = """# AI编程的意外收获

## 起因

那天下着大雨，我坐在咖啡馆里打开了 Claude Code。以前我总觉得自己学不会编程，**经济学背景让我对技术充满畏惧**。

记得三个月没写出一行代码的我，决定试试 AI 辅助编程。当时真的很焦虑。

## 转折

后来我惊讶地发现，AI 不仅帮我写代码，还在教我理解编程思维。

- 第一步：学会描述需求
- 第二步：理解 AI 的实现
- 第三步：自己修改和调试

## 领悟

以前觉得编程是天才的专利，现在明白它是一种**表达逻辑的语言**。

## 总结

如果你也在犹豫要不要学编程，试试 AI 辅助。它改变的不是你的能力，而是你和技术的距离。
"""


class TestXHSGenerator:
    def test_analyze_article(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = XHSGenerator(Path(tmpdir))
            analysis = gen._analyze_article(SAMPLE_ARTICLE, "测试标题")
            assert analysis["title"] == "AI编程的意外收获"
            assert len(analysis["sections"]) >= 2
            assert analysis["article_type"] == "story"

    def test_analyze_article_extracts_bold_quotes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = XHSGenerator(Path(tmpdir))
            analysis = gen._analyze_article(SAMPLE_ARTICLE, "")
            assert len(analysis["key_quotes"]) >= 1

    def test_generate_cards(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = XHSGenerator(Path(tmpdir))
            analysis = gen._analyze_article(SAMPLE_ARTICLE, "测试")
            cards = gen._generate_cards(analysis)
            assert len(cards) == 5
            assert cards[0]["type"] == "cover"
            assert cards[-1]["type"] == "ending"

    def test_generate_creates_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = XHSGenerator(Path(tmpdir))
            result = gen.generate(SAMPLE_ARTICLE, "测试文章")
            assert result["xhs_version"].exists()
            assert result["prompts"].exists()
            assert result["guide"].exists()

    def test_generate_xhs_version_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = XHSGenerator(Path(tmpdir))
            result = gen.generate(SAMPLE_ARTICLE, "测试文章")
            content = result["xhs_version"].read_text(encoding="utf-8")
            assert "小红书版本" in content
            assert "卡片 1" in content
            assert "卡片 5" in content

    def test_generate_prompts_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = XHSGenerator(Path(tmpdir))
            result = gen.generate(SAMPLE_ARTICLE, "测试文章")
            content = result["prompts"].read_text(encoding="utf-8")
            assert "Prompt" in content
            assert "3:4" in content

    def test_visual_prompts_constant(self):
        assert len(XHSGenerator._VISUAL_PROMPTS) == 5
        for vp in XHSGenerator._VISUAL_PROMPTS:
            assert "en" in vp
            assert "cn" in vp
            assert len(vp["en"]) > 50
            assert len(vp["cn"]) > 50

    def test_individual_prompt_files_created(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = XHSGenerator(Path(tmpdir))
            gen.generate(SAMPLE_ARTICLE, "测试文章")
            prompts_dir = Path(tmpdir) / "images" / "xhs" / "prompts"
            assert prompts_dir.exists()
            files = list(prompts_dir.glob("*.md"))
            assert len(files) == 5
