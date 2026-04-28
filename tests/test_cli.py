from contextlib import suppress
from unittest.mock import patch

from src.cli import main


class TestCLIParsing:
    def test_main_no_args_shows_help(self):
        with patch("sys.argv", ["wechat"]), suppress(SystemExit):
            main()
            # Should exit with 1 (no command provided)

    def test_new_subparser_requires_topic(self):
        with patch("sys.argv", ["wechat", "new"]), suppress(SystemExit):
            main()

    def test_write_subparser_requires_dir(self):
        with patch("sys.argv", ["wechat", "write"]), suppress(SystemExit):
            main()

    def test_illustrate_subparser_requires_dir(self):
        with patch("sys.argv", ["wechat", "illustrate"]), suppress(SystemExit):
            main()

    def test_finish_subparser_requires_dir(self):
        with patch("sys.argv", ["wechat", "finish"]), suppress(SystemExit):
            main()


class TestCmdNew:
    def test_cmd_new_creates_dir(self):
        with (
            patch("sys.argv", ["wechat", "new", "测试选题"]),
            patch("src.cli.ArticleGenerator") as mock_gen,
        ):
            mock_instance = mock_gen.return_value
            mock_instance.generate_outline.return_value = "test prompt"
            with suppress(SystemExit):
                main()
            mock_instance.generate_outline.assert_called_once_with("测试选题")
