from src.illustrator import IllustrationPlanner


class TestIllustrationPlanner:
    def test_extract_image_slots(self):
        article = "# Title\n\n正文内容\n\n【配图：一个程序员在写代码】\n\n更多内容"
        planner = IllustrationPlanner()
        slots = planner.extract_image_slots(article)
        assert len(slots) == 1
        assert slots[0]["context"] == "一个程序员在写代码"

    def test_extract_no_slots(self):
        article = "# Title\n\n没有配图标记的文章"
        planner = IllustrationPlanner()
        slots = planner.extract_image_slots(article)
        assert len(slots) == 0

    def test_generate_illustration_prompts(self):
        planner = IllustrationPlanner()
        slots = [{"context": "封面图", "type": "cover", "position": 0}]
        results = planner.generate_illustration_prompts(slots, "扁平插画风格")
        assert len(results) == 1
        assert results[0]["filename"] == "image_00.png"
        assert "扁平插画风格" in results[0]["prompt"]

    def test_max_images_limit(self):
        planner = IllustrationPlanner(max_images=2)
        article = "# Title\n\n" + "\n\n".join([f"段落{i}\n\n## 章节{i}" for i in range(10)])
        slots = planner.plan_illustrations(article, "测试")
        assert len(slots) <= 2
