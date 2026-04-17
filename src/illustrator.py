import json
import re
from pathlib import Path


class IllustrationPlanner:
    """分析文章内容，规划配图需求."""

    PLACEHOLDER_PATTERN = re.compile(r"【配图[：:](.*?)】")

    def __init__(self, max_images: int = 5):
        self.max_images = max_images

    def extract_image_slots(self, article: str) -> list[dict]:
        """从文章中提取所有配图占位符."""
        slots = []
        for match in self.PLACEHOLDER_PATTERN.finditer(article):
            slots.append({
                "position": match.start(),
                "context": match.group(1).strip(),
                "original": match.group(0),
            })
        return slots

    def plan_illustrations(self, article: str, title: str) -> list[dict]:
        """规划整篇文章的配图方案."""
        slots = self.extract_image_slots(article)

        # 如果没有显式占位符，智能识别配图位置
        if not slots:
            slots = self._detect_image_needs(article, title)

        # 限制数量
        if len(slots) > self.max_images:
            # 保留：封面 + 均匀分布的正文配图
            cover = next((s for s in slots if s.get("type") == "cover"), None)
            body = [s for s in slots if s.get("type") != "cover"]
            # 均匀选择
            step = max(1, len(body) // (self.max_images - 1))
            selected_body = body[::step][: self.max_images - 1]
            slots = ([cover] if cover else []) + selected_body

        return slots

    def _detect_image_needs(self, article: str, title: str) -> list[dict]:
        """智能检测文章中的配图需求."""
        slots = []

        # 封面图
        slots.append({
            "position": 0,
            "context": f"文章封面：{title}",
            "type": "cover",
        })

        # 按段落检测关键概念（简化版）
        paragraphs = article.split("\n\n")
        for i, para in enumerate(paragraphs):
            if len(para) > 200 and "##" in para:
                # 章节开头附近可能需要配图
                heading = para.split("\n")[0] if "\n" in para else para[:50]
                slots.append({
                    "position": article.find(para),
                    "context": f"章节配图：{heading}",
                    "type": "inline",
                })

        return slots

    def generate_illustration_prompts(self, slots: list[dict], style: str) -> list[dict]:
        """为每个配图位置生成 AI 绘画 prompt."""
        results = []
        for i, slot in enumerate(slots):
            context = slot["context"]
            prompt = f"{style}，{context}" if style else context
            results.append({
                "index": i,
                "filename": f"image_{i:02d}.png",
                "position": slot.get("position", 0),
                "context": context,
                "prompt": prompt,
                "type": slot.get("type", "inline"),
            })
        return results

    def insert_image_placeholders(self, article: str, image_plan: list[dict]) -> str:
        """在文章中插入统一的图片占位标记，用于后续替换为实际图片."""
        result = article
        offset = 0

        for img in sorted(image_plan, key=lambda x: x["position"]):
            placeholder = f"\n\n![{img['context']}](images/{img['filename']})\n\n"
            pos = img["position"] + offset
            # 找到合适的位置插入（段落边界）
            insert_pos = self._find_insert_position(result, pos)
            result = result[:insert_pos] + placeholder + result[insert_pos:]
            offset += len(placeholder)

        return result

    def _find_insert_position(self, text: str, pos: int) -> int:
        """找到最近的段落边界作为插入位置."""
        # 向后找换行
        next_nl = text.find("\n\n", pos)
        if next_nl != -1:
            return next_nl + 2
        # 向前找换行
        prev_nl = text.rfind("\n\n", 0, pos)
        if prev_nl != -1:
            return prev_nl + 2
        return len(text)
