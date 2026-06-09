# kling_autopilot

用 Playwright 驱动 Kling 网页端,自动把提示词填进去、在「定员行」处做 `@元素` 下拉选择、设画幅/时长、点生成、等完成并下载。为没有 video API、只能手动操作网页的场景做的 RPA 工具。

## ⚠️ 先读这条

Kling(快手)网页端**很可能在服务条款里限制自动化**(它在卖 API)。这是**你自己的账号、个人自用**,要不要用由你判断。降低风险:小批量、控速、加随机停顿、别一口气狂刷;先 `--dry-run` 和 `--no-generate` 验证,不要无人值守批量提交。

## 设计要点:为什么可行

所有 `@元素` 都集中在提示词**顶部一行「定员」**(见 `samples/shot07.prompt.txt`),其余正文是纯文本。脚本因此只需在那一行做几次 `@` 交互,其余一次性逐字输入。`@` 的标准动作:输入 `@` → 等下拉 → 输入元素名过滤 → 点中匹配项。

> 元素名用**简体**,且与提示词正文**一字不差**(繁简一致才不会断指代)。

## 安装

```powershell
cd tools/kling_autopilot
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## 配置

```powershell
copy config.example.yaml config.yaml
```

编辑 `config.yaml`,把所有 `TODO` 按 Kling 实际页面填:

- `create_url` — 你的创建页 URL。
- `user_data_dir` — 持久化登录目录;**首次手动登录一次**(扫码/验证码人工过),之后复用会话。
- `selectors.*` — F12 inspect 这几个元素的真实 selector:提示词输入框、`@` 下拉容器、下拉项、画幅控件、时长控件、生成按钮、结果就绪标志、下载按钮。
- `elements` — 每个元素的 `name`(提示词里 `@` 后的字)/`search`(@ 后输入的过滤词)/`label`(下拉项可见文字)。

找不准 selector 就把那几块的 HTML 发我一起调。

## 用法

提示词解析(不开浏览器,先看拆分对不对):

```powershell
python run.py samples/shot07.prompt.txt --dry-run
```

填好但不提交(肉眼确认 @ 选对了):

```powershell
python run.py samples/shot07.prompt.txt --no-generate
```

完整跑 + 下载:

```powershell
python run.py samples/shot07.prompt.txt --download-to ../../ai_videos/nvdi_tuihun_houhuile/episodes/ep01/shots/shot07/shot07.mp4
```

## 提示词文件格式

纯文本,`@元素名` 内联标记(元素名须在 `config.yaml` 的 `elements` 里)。解析器把整段拆成「文本段 / @元素」序列:文本逐字输入,`@元素` 走下拉。`samples/shot07.prompt.txt` 是现成模板。

## 文件

| 文件 | 职责 |
|---|---|
| `segments.py` | 提示词 → 文本/@元素 段序列(与 Kling 无关,可单测) |
| `config.py` | 强类型读 `config.yaml` |
| `kling_session.py` | Playwright 驱动:填框 / @ 下拉 / 设参 / 生成 / 下载 |
| `run.py` | CLI:`--dry-run` / `--no-generate` / `--download-to` |
| `config.example.yaml` | 配置模板(含 TODO) |
| `samples/shot07.prompt.txt` | 示例提示词(顶部定员行 + 简体元素名) |

## 现状

- 与 Kling 无关的逻辑(解析、流程、CLI、dry-run)已可用。
- `selectors.*` 是占位,需按真实 DOM 填;`set_params` 的画幅/时长选择是 best-effort,可能要按实际控件改。
- 先用一个 shot 跑通,再考虑批量(批量时务必控速)。
