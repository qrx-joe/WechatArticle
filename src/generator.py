import json
import re
from datetime import datetime
from pathlib import Path

from .config import Config


def generate_slug(title: str) -> str:
    """从标题生成 URL slug."""
    slug = re.sub(r"[^\w\s-]", "", title)
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug.strip("-").lower()[:50]


def create_article_dir(title: str) -> Path:
    """创建文章存储目录."""
    today = datetime.now().strftime("%Y-%m-%d")
    slug = generate_slug(title) or f"article-{datetime.now().strftime('%H%M%S')}"
    article_dir = Path("content") / today / slug
    article_dir.mkdir(parents=True, exist_ok=True)
    (article_dir / "images").mkdir(exist_ok=True)
    return article_dir


def save_article_state(article_dir: Path, state: dict):
    """保存文章元数据."""
    meta_path = article_dir / "meta.json"
    meta_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def load_article_state(article_dir: Path) -> dict:
    """加载文章元数据."""
    meta_path = article_dir / "meta.json"
    if meta_path.exists():
        return json.loads(meta_path.read_text(encoding="utf-8"))
    return {}


class ArticleGenerator:
    def __init__(self, config: Config | None = None):
        self.config = config or Config()

    def generate_outline(self, topic: str) -> str:
        """生成文章大纲."""
        tone = self.config.style_tone
        word_min = self.config.word_count_min
        word_max = self.config.word_count_max

        prompt = f"""你是一位资深公众号写手，擅长用{tone}风格写作。

请为以下选题生成一份详细的文章大纲：

选题：{topic}

要求：
1. 文章字数控制在 {word_min} - {word_max} 字
2. 目标读者是中文互联网用户，风格要适合公众号传播
3. 大纲需要包含：标题建议、引言要点、每个章节的核心论点、章节间过渡逻辑
4. 每个章节标注预估字数
5. 标注需要配图的位置（如"【配图：XXX场景】"）
6. 结尾要有总结和行动号召

请直接输出大纲内容。"""

        return prompt

    def generate_article(self, topic: str, outline: str) -> str:
        """根据大纲生成完整文章."""
        tone = self.config.style_tone
        para_style = self.config.paragraph_style
        word_min = self.config.word_count_min
        word_max = self.config.word_count_max

        para_instruction = {
            "short": "每段控制在 2-3 句话，适合手机屏幕阅读",
            "medium": "每段 3-5 句话",
            "long": "段落可以较长，适合深度阅读",
        }.get(para_style, "每段控制在 2-3 句话")

        prompt = f"""你是一位资深公众号写手，擅长用{tone}风格写作。

选题：{topic}

大纲：
{outline}

请根据以上大纲撰写完整的公众号文章。

写作要求：
1. 总字数 {word_min} - {word_max} 字
2. {para_instruction}
3. 使用 Markdown 格式
4. 保留大纲中的配图标记（【配图：XXX】），这些标记之后会替换为实际图片
5. 标题用 #，章节用 ##，小节用 ###
6. 适当使用加粗、引用块等格式增强可读性
7. 语言自然流畅，避免 AI 腔
8. 开头要有吸引人的钩子，结尾要有总结

请直接输出完整文章内容。"""

        return prompt

    def refine_article(self, article: str, feedback: str) -> str:
        """根据反馈修改文章."""
        prompt = f"""请根据以下反馈修改文章。

原文：
{article}

反馈：
{feedback}

请输出修改后的完整文章，保持 Markdown 格式。"""

        return prompt
