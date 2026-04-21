# WechatArticle - 微信公众号文章生成工具

一个专注**内容生产**的公众号文章工作流工具。生成文章文字 + 配图方案，发布由你手动完成。

## 工作流程

```
选题 -> 大纲 -> 正文 -> 配图 -> 输出 -> 发布
```

## 快速开始

### 1. 创建新文章

```bash
uv run wechat new "你的选题"
```

这会生成大纲 prompt，保存到 `content/YYYY-MM-DD/slug/outline_prompt.txt`。将 prompt 发送给 AI 获取大纲，保存为 `outline.md`。

### 2. 生成大纲

将 `outline_prompt.txt` 的内容发送给 AI（Claude/DeepSeek 等），获取大纲，保存为 `outline.md`。

### 3. 生成正文

```bash
uv run wechat write --dir content/YYYY-MM-DD/slug
```

这会生成文章正文 prompt，保存到 `article_prompt.txt`。将 prompt 发送给 AI 获取正文，保存为 `article_raw.md`。

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

### 6. 生成小红书版本

```bash
uv run wechat xhs --dir content/YYYY-MM-DD/slug
```

自动生成小红书5卡片系列笔记：
- `xhs-version.md` — 5张卡片的文案
- `xhs-prompts.md` — 5张配图的中英文 Prompt
- `XHS_PUBLISH_GUIDE.md` — 发布指南（含工具推荐、操作步骤、禁忌清单）
- `images/xhs/prompts/*.md` — 每张图的单独 Prompt 文件

生成配图后，用醒图/黄油相机添加文字即可发布。

### 7. 发布到公众号

```bash
uv run wechat post --dir content/YYYY-MM-DD/slug
```

自动启动 Chrome，通过 CDP 发布文章到微信公众号草稿箱。

### 即刻版

如需生成即刻版本，手动创建 `jike-version.md`，并参考 `JIKE_PUBLISH_GUIDE.md` 发布。

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
      outline.md              # 大纲
      outline_prompt.txt      # 生成大纲的 prompt
      article_raw.md          # AI 生成的原始正文
      article.md              # 插入图片占位符后的最终文章
      article_prompt.txt      # 生成正文的 prompt
      jike-version.md         # 即刻版本（如有）
      xhs-version.md          # 小红书版本（5卡片文案）
      xhs-prompts.md          # 小红书配图 Prompts
      image_plan.json         # 配图方案
      meta.json               # 文章元数据
      prompts/                # 公众号配图 prompt 文件
      images/                 # 配图文件
        xhs/                  # 小红书配图
          prompts/            # 小红书单独 prompt 文件
      PUBLISH_GUIDE.md        # 公众号发布指引
      JIKE_PUBLISH_GUIDE.md   # 即刻发布指引
      XHS_PUBLISH_GUIDE.md    # 小红书发布指引
```
