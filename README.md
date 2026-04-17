# WechatArticle - 微信公众号文章生成工具

一个专注**内容生产**的公众号文章工作流工具。生成文章文字 + 配图方案，发布由你手动完成。

## 工作流程

```
选题 -> 大纲 -> 正文 -> 配图 -> 输出 -> 手动发布
```

## 快速开始

### 1. 创建新文章

```bash
uv run wechat new "你的选题"
```

这会生成大纲 prompt，保存到 `content/YYYY-MM-DD/slug/outline_prompt.txt`。

### 2. 生成大纲

将 `outline_prompt.txt` 的内容发送给 AI（Claude/DeepSeek 等），获取大纲，保存为 `outline.md`。

### 3. 生成正文

```bash
uv run wechat write --dir content/YYYY-MM-DD/slug
```

这会生成文章正文 prompt，保存到 `article_prompt.txt`。发送给 AI 获取正文，保存为 `article_raw.md`。

### 4. 规划配图

```bash
uv run wechat illustrate --dir content/YYYY-MM-DD/slug
```

分析文章配图需求，生成 `image_plan.json`，并在 `article.md` 中插入图片占位符。

然后使用 `baoyu-article-illustrator` 或 `baoyu-imagine` 生成配图，保存到 `images/` 目录。

### 5. 完成

```bash
uv run wechat finish --dir content/YYYY-MM-DD/slug
```

生成 `PUBLISH_GUIDE.md` 发布指引，汇总文章信息。

## 配置

修改 `config.yaml`：

- `ai.provider` / `ai.model`: AI 模型配置
- `style.tone`: 文章风格 (storytelling / professional / casual)
- `style.word_count`: 字数范围
- `illustration.style`: 配图风格描述
- `illustration.max_images`: 最大配图数

## 目录结构

```
content/
  YYYY-MM-DD/
    slug/
      outline.md           # 大纲
      outline_prompt.txt   # 生成大纲的 prompt
      article_raw.md       # AI 生成的原始正文
      article.md           # 插入图片占位符后的最终文章
      article_prompt.txt   # 生成正文的 prompt
      image_plan.json      # 配图方案
      meta.json            # 文章元数据
      images/              # 配图文件
      PUBLISH_GUIDE.md     # 发布指引
```
