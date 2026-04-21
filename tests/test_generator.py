from src.generator import generate_slug


class TestGenerateSlug:
    def test_simple_chinese(self):
        assert generate_slug("hello world") == "hello-world"

    def test_with_punctuation(self):
        assert generate_slug("hello, world!") == "hello-world"

    def test_multiple_spaces(self):
        assert generate_slug("hello   world") == "hello-world"

    def test_leading_trailing_dash(self):
        assert generate_slug("-hello world-") == "hello-world"

    def test_long_title_truncated(self):
        long_title = "a" * 100
        result = generate_slug(long_title)
        assert len(result) <= 50
