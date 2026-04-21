import tempfile

from src.config import Config


class TestConfig:
    def test_defaults(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("# empty config\n")
            f.flush()
            config = Config(f.name)
            assert config.style_tone == "storytelling"
            assert config.word_count_min == 1500
            assert config.word_count_max == 3000
            assert config.max_images == 5

    def test_custom_values(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("""
style:
  tone: professional
  word_count:
    min: 2000
    max: 4000
illustration:
  max_images: 3
""")
            f.flush()
            config = Config(f.name)
            assert config.style_tone == "professional"
            assert config.word_count_min == 2000
            assert config.word_count_max == 4000
            assert config.max_images == 3

    def test_missing_file_uses_defaults(self):
        config = Config("nonexistent.yaml")
        assert config.style_tone == "storytelling"
