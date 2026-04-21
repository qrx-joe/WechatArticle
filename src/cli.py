"""CLI 入口 - 微信公众号文章生成工具."""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from .config import Config
from .generator import ArticleGenerator, create_article_dir, load_article_state, save_article_state
from .illustrator import IllustrationPlanner
from .output import ArticleOutput


def find_bun() -> Path | None:
    """查找 bun 可执行文件."""
    bun = shutil.which("bun")
    if bun:
        return Path(bun)
    windows_path = Path.home() / ".bun" / "bin" / "bun.exe"
    if windows_path.exists():
        return windows_path
    unix_path = Path.home() / ".bun" / "bin" / "bun"
    if unix_path.exists():
        return unix_path
    return None


def find_wechat_script() -> Path | None:
    """查找 baoyu-post-to-wechat 的 wechat-article.ts 脚本."""
    env_path = os.environ.get("BAOYU_WECHAT_SCRIPT")
    if env_path and Path(env_path).exists():
        return Path(env_path)
    default = (
        Path.home()
        / ".claude"
        / "skills"
        / "baoyu-post-to-wechat"
        / "scripts"
        / "wechat-article.ts"
    )
    if default.exists():
        return default
    return None


def launch_chrome_if_needed(cdp_port: int = 9222) -> bool:
    """如果 Chrome debug port 不可用，尝试启动 Chrome."""
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json/version", timeout=2)
        return True
    except Exception:
        pass

    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    for c in [shutil.which("google-chrome-stable"), shutil.which("chromium")]:
        if c:
            candidates.insert(0, c)

    profile_dir = Path.home() / "AppData" / "Roaming" / "baoyu-skills" / "chrome-profile"

    for chrome in candidates:
        if not chrome or not Path(chrome).exists():
            continue
        try:
            subprocess.Popen(
                [
                    str(chrome),
                    f"--remote-debugging-port={cdp_port}",
                    f"--user-data-dir={profile_dir}",
                    "--no-first-run",
                    "--no-default-browser-check",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            for _ in range(30):
                try:
                    urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json/version", timeout=1)
                    return True
                except Exception:
                    time.sleep(0.5)
        except Exception:
            continue
    return False


def cmd_post(args):
    """发布文章到微信公众号草稿箱."""
    article_dir = Path(args.dir)

    article_path = article_dir / "article.md"
    if not article_path.exists():
        article_path = article_dir / "article_raw.md"
    if not article_path.exists():
        print("错误: 找不到文章文件 (article.md 或 article_raw.md)")
        sys.exit(1)

    bun = find_bun()
    if not bun:
        print("错误: 找不到 bun")
        print('安装命令: powershell -c "irm https://bun.sh/install.ps1 | iex"')
        sys.exit(1)

    script = find_wechat_script()
    if not script:
        print("错误: 找不到 baoyu-post-to-wechat 技能脚本")
        print("请确保已安装该技能，或设置环境变量 BAOYU_WECHAT_SCRIPT")
        sys.exit(1)

    cdp_port = args.cdp_port or 9222
    chrome_ready = launch_chrome_if_needed(cdp_port)
    if not chrome_ready:
        print("警告: 无法自动启动 Chrome，请手动启动:")
        print(
            f'  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" '
            f"--remote-debugging-port={cdp_port} "
            f'--user-data-dir="%APPDATA%\\baoyu-skills\\chrome-profile" '
            f"--no-first-run --no-default-browser-check"
        )
        print("然后重新运行此命令。")
        sys.exit(1)

    cmd = [
        str(bun),
        "run",
        str(script),
        "--markdown",
        str(article_path),
        "--theme",
        args.theme or "default",
        "--cdp-port",
        str(cdp_port),
    ]
    if args.no_cite:
        cmd.append("--no-cite")

    print(f"\n发布文章: {article_path}")
    print(f"Theme: {args.theme or 'default'}")
    print("如果未登录，请在浏览器中扫码登录微信公众平台...\n")

    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def cmd_new(args):
    """创建新文章项目."""
    topic = args.topic
    print(f"\n选题: {topic}")
    print("正在生成大纲...\n")

    config = Config()
    generator = ArticleGenerator(config)

    # 生成大纲 prompt（需外部调用 AI 执行）
    outline_prompt = generator.generate_outline(topic)

    article_dir = create_article_dir(topic)
    save_article_state(
        article_dir,
        {
            "topic": topic,
            "status": "outlined",
            "dir": str(article_dir),
        },
    )

    # 保存大纲 prompt，供用户自行调用 AI
    prompt_path = article_dir / "outline_prompt.txt"
    prompt_path.write_text(outline_prompt, encoding="utf-8")

    print(f"大纲生成 prompt 已保存到: {prompt_path}")
    print(f"项目目录: {article_dir}")
    print("\n请将此 prompt 发送给 AI 获取大纲，保存为 outline.md")


def cmd_write(args):
    """根据大纲生成正文."""
    article_dir = Path(args.dir)
    state = load_article_state(article_dir)
    topic = state.get("topic", "未命名")

    outline_path = article_dir / "outline.md"
    if not outline_path.exists():
        print(f"错误: 找不到大纲文件 {outline_path}")
        sys.exit(1)

    outline = outline_path.read_text(encoding="utf-8")
    print(f"\n选题: {topic}")
    print("正在生成文章正文 prompt...\n")

    config = Config()
    generator = ArticleGenerator(config)
    article_prompt = generator.generate_article(topic, outline)

    prompt_path = article_dir / "article_prompt.txt"
    prompt_path.write_text(article_prompt, encoding="utf-8")

    save_article_state(article_dir, {**state, "status": "writing"})

    print(f"文章生成 prompt 已保存到: {prompt_path}")
    print("\n请将此 prompt 发送给 AI 获取正文，保存为 article_raw.md")


def cmd_illustrate(args):
    """规划配图并生成 prompts."""
    article_dir = Path(args.dir)
    state = load_article_state(article_dir)

    article_path = article_dir / "article_raw.md"
    if not article_path.exists():
        article_path = article_dir / "article.md"

    if not article_path.exists():
        print("错误: 找不到文章文件")
        sys.exit(1)

    article = article_path.read_text(encoding="utf-8")
    title = state.get("topic", "")

    config = Config()
    planner = IllustrationPlanner(max_images=config.max_images)

    print("分析文章配图需求...")
    slots = planner.plan_illustrations(article, title)
    image_plan = planner.generate_illustration_prompts(slots, config.illustration_style)

    # 保存配图方案
    plan_path = article_dir / "image_plan.json"
    plan_path.write_text(json.dumps(image_plan, ensure_ascii=False, indent=2), encoding="utf-8")

    # 插入图片占位符
    article_with_images = planner.insert_image_placeholders(article, image_plan)
    output = ArticleOutput(article_dir)
    output.save_markdown(article_with_images)

    save_article_state(article_dir, {**state, "status": "illustrated"})

    print(f"\n配图方案已保存到: {plan_path}")
    print(f"共 {len(image_plan)} 张配图:")
    for img in image_plan:
        print(f"  [{img['index'] + 1}] {img['filename']}: {img['context']}")
    print("\n请使用 baoyu-article-illustrator 或 baoyu-imagine 生成配图")
    print(f"图片保存到: {article_dir / 'images'}")


def cmd_finish(args):
    """完成文章，生成发布指引."""
    article_dir = Path(args.dir)
    state = load_article_state(article_dir)

    article_path = article_dir / "article.md"
    if not article_path.exists():
        print("错误: 找不到 article.md")
        sys.exit(1)

    article = article_path.read_text(encoding="utf-8")
    word_count = len(article)

    # 加载配图方案
    plan_path = article_dir / "image_plan.json"
    image_plan = []
    if plan_path.exists():
        image_plan = json.loads(plan_path.read_text(encoding="utf-8"))

    output = ArticleOutput(article_dir)
    output.generate_copy_guide(image_plan)
    save_article_state(article_dir, {**state, "status": "ready", "word_count": word_count})

    output.print_summary(state.get("topic", ""), word_count, len(image_plan))


def main():
    parser = argparse.ArgumentParser(description="微信公众号文章生成工具")
    sub = parser.add_subparsers(dest="command")

    # new: 创建新文章
    p_new = sub.add_parser("new", help="创建新文章项目")
    p_new.add_argument("topic", help="文章选题/主题")

    # write: 生成正文
    p_write = sub.add_parser("write", help="根据大纲生成正文 prompt")
    p_write.add_argument("--dir", "-d", required=True, help="文章目录路径")

    # illustrate: 规划配图
    p_ill = sub.add_parser("illustrate", help="规划配图方案")
    p_ill.add_argument("--dir", "-d", required=True, help="文章目录路径")

    # finish: 完成
    p_finish = sub.add_parser("finish", help="生成发布指引")
    p_finish.add_argument("--dir", "-d", required=True, help="文章目录路径")

    # post: 发布到草稿箱
    p_post = sub.add_parser("post", help="发布文章到微信公众号草稿箱")
    p_post.add_argument("--dir", "-d", required=True, help="文章目录路径")
    p_post.add_argument(
        "--theme", "-t", default="default", help="文章主题 (default, grace, simple, modern)"
    )
    p_post.add_argument("--cdp-port", type=int, default=9222, help="Chrome debug port")
    p_post.add_argument("--no-cite", action="store_true", help="禁用底部引用")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "new": cmd_new,
        "write": cmd_write,
        "illustrate": cmd_illustrate,
        "finish": cmd_finish,
        "post": cmd_post,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
