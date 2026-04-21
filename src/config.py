import os
from pathlib import Path

import yaml


class Config:
    def __init__(self, path: str = "config.yaml"):
        self.path = Path(path)
        self._data = {}
        if self.path.exists():
            with open(self.path, encoding="utf-8") as f:
                self._data = yaml.safe_load(f) or {}

    def get(self, key: str, default=None):
        keys = key.split(".")
        value = self._data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    @property
    def ai_provider(self) -> str:
        return self.get("ai.provider", "claude")

    @property
    def ai_model(self) -> str:
        return self.get("ai.model", "claude-sonnet-4-6")

    @property
    def api_key(self) -> str | None:
        env_map = {
            "claude": "CLAUDE_API_KEY",
            "openai": "OPENAI_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
        }
        env_var = env_map.get(self.ai_provider, f"{self.ai_provider.upper()}_API_KEY")
        return os.environ.get(env_var)

    @property
    def style_tone(self) -> str:
        return self.get("style.tone", "storytelling")

    @property
    def word_count_min(self) -> int:
        return self.get("style.word_count.min", 1500)

    @property
    def word_count_max(self) -> int:
        return self.get("style.word_count.max", 3000)

    @property
    def paragraph_style(self) -> str:
        return self.get("style.paragraph_style", "short")

    @property
    def illustration_enabled(self) -> bool:
        return self.get("illustration.enabled", True)

    @property
    def illustration_style(self) -> str:
        return self.get("illustration.style", "")

    @property
    def max_images(self) -> int:
        return self.get("illustration.max_images", 5)
