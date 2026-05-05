# WechatArticle

> 一个专注内容生产的多平台文章工作流 CLI 工具，一键完成从选题到公众号/小红书/即刻多平台分发的全流程。

---

## 项目背景

### 技术栈

| 层级 | 技术 | 版本 |
|---|---|---|
| 语言 | Python | 3.11 |
| 包管理 | uv | 0.6.0 |
| 运行时依赖 | PyYAML | >=6.0 |
| 代码质量 | ruff | >=0.9.0 |
| 类型检查 | pyright | >=1.1 |
| 测试框架 | pytest + pytest-cov | >=8.0 / >=6.0 |
| Git Hooks | pre-commit | >=4.0 |
| CI/CD | GitHub Actions | checkout@v4 / setup-python@v5 / setup-uv@v4 |
| 浏览器自动化 | Chrome CDP | remote-debugging-protocol |

### 技术亮点

- **内容生产工作流设计**：将公众号内容创作抽象为 7 个可编排的阶段（选题、大纲、正文、配图、输出、多平台适配、自动发布），每个阶段对应一个 CLI 命令，降低内容创作者的操作门槛
- **Prompt 工程体系搭建**：设计分层 Prompt 模板系统，将文章风格（storytelling / professional / casual）、字数控制、段落节奏等写作参数配置化，实现同一选题在不同风格下的快速 A/B 测试
- **自动化配图规划**：基于内容结构分析自动识别配图需求位置，生成平台适配的 AI 绘画 Prompt，解决"文章写完了不知道配什么图"的效率瓶颈
- **跨平台内容适配引擎**：针对小红书、即刻等平台的内容消费特征，将公众号长文重构为平台原生的叙事结构——小红书 5 卡片（封面情绪钩子 + 内容卡片 + 行动号召）、即刻短版本（信息流 3 秒钩子），而非简单截断
- **无官方 API 场景下的自动化发布**：微信公众号未开放草稿箱写入 API，通过 Chrome DevTools Protocol 绕过限制，实现本地浏览器到公众号后台的自动内容注入，覆盖 Windows / Linux / macOS 多平台 Chrome 环境
- **质量保障体系**：从 0 搭建 CI/CD Pipeline，引入类型检查、代码规范、测试覆盖率（60% 门槛），在快速迭代和功能稳定之间建立平衡

### 项目演示

- [公众号文章：使用示例](https://mp.weixin.qq.com/s/9Ym7lqLYFp1-pZHDmZgoRA)

### 学到的内容

**1. MVP 优先，工程化后置**

项目启动后 3 天内从空架子（`ba5db48`）到第一篇完整文章（`685db3b` / `01ac121`），验证了"选题 → 大纲 → 正文 → 配图 → 发布"全流程可行后，才引入 CI/CD、测试、类型检查（`8cc8057`）。过早的工程化会拖慢创意验证，但功能跑通后不及时补工程化会导致技术债累积——`ec92b0f` 专门有一个 `fix code duplication` 的 commit，就是前期快速迭代留下的坑。

**2. 多平台分发 ≠ 简单裁剪**

从单平台（公众号）扩展到即刻短版本（`1fa1605`）和小红书 5 卡片（`6f63229`），发现每个平台有自己的内容语法：小红书需要封面情绪钩子 + 标签驱动流量，即刻需要在信息流里 3 秒定生死的开头。不能简单截断长文，必须针对平台重新设计叙事结构。

**3. Prompt 工程需要基础设施**

初期把 prompt 逻辑直接耦合在 CLI 里，后来发现无法做风格切换和 A/B 测试。后来将 prompt 模板抽离成独立模块（`generator.py` / `illustrator.py` / `output.py`），通过 `config.yaml` 配置 tone、word_count、paragraph_style，prompt 才能像代码一样被版本管理和迭代。

**4. CI/CD 是"痛过才知道"**

初期没设 lint 和类型检查，直到代码重复到需要专门 commit 来修复（`ec92b0f`）。设置 60% 测试覆盖率门槛（`--cov-fail-under=60`）而非追求 100%，是对 CLI 工具特性的务实权衡——IO 和外部依赖（Chrome、文件系统）的 mock 成本高于收益，核心算法（配图规划、prompt 生成）覆盖到即可。

**5. 产物管理需要持续迭代**

内容生产工具的"什么该进 git"是个渐进校准的过程：先忘记忽略生成的配图文件（`6841eed`），再完善 `.gitignore` 规则（`e7ddcc8`），最后清理废弃草稿和过时索引（`12618c1`）。自动化生成的大量产物如果不加管理，会迅速污染仓库。

---

## 使用文档

### 快速开始

```bash
# 1. 创建新文章
uv run wechat new "你的选题"

# 2. 生成正文
uv run wechat write --dir content/YYYY-MM-DD/slug

# 3. 规划配图
uv run wechat illustrate --dir content/YYYY-MM-DD/slug

# 4. 完成并生成发布指引
uv run wechat finish --dir content/YYYY-MM-DD/slug

# 5. 生成小红书版本
uv run wechat xhs --dir content/YYYY-MM-DD/slug

# 6. 发布到公众号草稿箱
uv run wechat post --dir content/YYYY-MM-DD/slug
```

### 工作流程

```
选题 -> 大纲 -> 正文 -> 配图 -> 输出 -> 多平台物料生成
                                    |
                                    +-- 公众号: wechat post (自动写入草稿箱)
                                    +-- 小红书: wechat xhs (生成文案+配图Prompt+指南)
                                    +-- 即刻: wechat jike (生成短版本+指南)
```

### 命令说明

| 命令 | 说明 |
|---|---|
| `wechat new` | 生成大纲 prompt，保存到 `outline_prompt.txt` |
| `wechat write` | 生成正文 prompt，保存到 `article_prompt.txt` |
| `wechat illustrate` | 分析配图需求，生成 `image_plan.json`，在 `article.md` 中插入图片占位符 |
| `wechat finish` | 生成 `PUBLISH_GUIDE.md` 发布指引，汇总文章信息 |
| `wechat xhs` | 生成小红书 5 卡片笔记（文案 + 配图 Prompts + 发布指南），**需手动发布** |
| `wechat post` | 启动 Chrome，通过 CDP 发布文章到微信公众号草稿箱 |

### 配置

修改 `config.yaml`：

- `ai.provider` / `ai.model`: AI 模型配置（claude / openai / deepseek）
- `style.tone`: 文章风格（storytelling / professional / casual / academic）
- `style.word_count`: 字数范围
- `illustration.style`: 配图风格描述
- `illustration.max_images`: 最大配图数
- `xhs.card_count`: 小红书卡片数量
- `xhs.default_tags`: 小红书默认标签

### 目录结构

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
      xhs-version.md          # 小红书版本（5 卡片文案）
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
