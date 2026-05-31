---
target_stage: 6
target_artifacts:
  - .claude/agent_refs/project/ai_video.md
  - projects/ai_video_management/libs/infrastructure/clients/anthropic__client.py
  - projects/ai_video_management/libs/application/queries/prompt__query.py
  - projects/ai_video_management/apps/api/routes/prompt__route.py
  - projects/ai_video_management/apps/ui/src/components/PromptStructuredEditor.tsx
  - projects/ai_video_management/apps/ui/src/markdown/renderer.tsx
  - projects/ai_video_management/apps/ui/src/api.ts
severity: high
---

# Follow-up draft 117 — 2026-05-31

shot 视频 prompt 由「一次生成写满所有维度」改为「先出基础骨架 + 在 webapp 里逐栏目 AI 细化」的两段式工作流。

## 抽象指令

改变每个 shot 视频 prompt 的结构与生成方式：

1. **基础骨架版生成（stage 6）**：自动生成的 shot 视频 prompt 默认是一个 very basic version —— rule #12.4 的全部必填字段都在，但只把剧情骨干维度（场景 / 镜头景别+运动 / 至少一拍动作 / 台词 / 比例 / 时长）写实，描述性维度（逐拍运镜、多拍 timed-beat、光线/色调层次、节奏、渲染样式完整关键词）只留一行 stub，交给用户细化。落在 `.claude/agent_refs/project/ai_video.md` rule #12.4 的 2026-05-31 amendment（common surface — 适用所有 ai_video 项目）。

2. **逐栏目 AI 细化（ai_video_management webapp）**：编辑 shot 视频 prompt（结构化表单，blockKind=video）时，每个可细化维度（镜头/运镜/动作/台词·字幕/光线·色调/节奏/渲染样式）的字段标签旁出现一个 `✨ 推荐` 按钮。点击后：
   - 前端 POST `/api/prompt/suggest`，把 {该维度, 当前字段值, 本镜完整 prompt body, 本镜上下文（小说原文 + Shot context + 起始/结束帧）, 剧目, 场景} 发给后端；
   - 后端用官方 anthropic SDK（Messages API + prompt caching）实时调用 LLM，根据当前场景与已填维度，返回 3–5 条不同思路、可直接落入该字段的中文细化选项（含一句 rationale）；
   - 用户在卡片里选一个、点「填入 / 追加」确认 —— 智能合并：该字段为空则填入，非空则换行追加；其余字段不动；
   - 再走现有 per-block Save（PUT /api/file + If-Unmodified-Since）落盘。

## 落地

后端（新增 read-only `prompt` aggregate，DDD+CQRS）：

- `libs/infrastructure/clients/anthropic__client.py` — `AnthropicClient.from_env()`（读 `ANTHROPIC_API_KEY`，可选 `ANTHROPIC_SUGGEST_MODEL`，默认 claude-sonnet-4-6；无 key → None，懒加载 SDK，system 块带 ephemeral cache_control）。
- `libs/infrastructure/errors/anthropic__error.py`（infra 错误）+ `libs/domain/errors/prompt__error.py`（domain：InvalidSuggestionRequestError / SuggestionProviderUnavailableError / SuggestionGenerationFailedError；query 把 infra 错误翻译成这些）。
- `libs/application/dtos/prompt__dto.py`（SuggestRefinementsInputQdto / RefinementSuggestionQdto / SuggestRefinementsQdto）+ `mappers/prompt__mapper.py`（构造 system+user payload、按维度给写法提示、解析 LLM JSON）+ `queries/prompt__query.py`（PromptQuery.suggest_refinements 编排）。
- `apps/api/routes/prompt__route.py` — `POST /api/prompt/suggest`；`apps/api/routes/__init__.py` + `container.py`（anthropic_client Singleton + prompt_query Factory）+ `app_factory.py`（3 个 domain error → 400/503/502）接线。
- 依赖：`anthropic>=0.40` 加入 project `requirements.txt` + `pyproject.toml`（root pyproject 不镜像 ai_video_management 专属依赖，照现状不动）。env：`ANTHROPIC_API_KEY` 放 `apps/api/.env`（与 Kling key 同处，env_loader 读取）。

前端：

- `apps/ui/src/api.ts` — `suggestRefinements(req)` + 类型。
- `apps/ui/src/components/PromptStructuredEditor.tsx` — 新增 `shotContext` / `currentPath` props；blockKind=video 且有 shotContext 时，可细化维度字段标签旁渲染 ✨ 推荐按钮 + RefinePanel（拉取建议卡片、选中、确认、智能合并、重新生成、收起）。
- `apps/ui/src/markdown/renderer.tsx` — CopyableCode 把 `ctx.fileContent`（作 shotContext）+ `ctx.currentPath` 透传给 PromptStructuredEditor。
- `apps/ui/src/styles.css` — `.prompt-refine-*` 样式。

## 不动的契约

- ✨ 细化只对 shot **视频 prompt**（blockKind=video）开放；起始帧/结束帧、actor/scene/character 的结构化编辑不变（ShotPairView 直接用 PromptStructuredEditor 但不传 blockKind/shotContext，自然不出现 ✨）。
- 无 `ANTHROPIC_API_KEY` 时后端返回 503 suggestion_unavailable，前端提示「未配置 ANTHROPIC_API_KEY」；其余编辑/保存功能完全不受影响（feature 可选、优雅降级）。
- per-block inline edit（follow-up 116）、PUT /api/file 并发、负向已废止等既有契约保持不变。
- 后端调用 LLM 仅用于「建议」，不写文件；落盘仍走用户确认 + 现有 Save 链路。

## 触发原因

用户原话: "我們改一下每一個prompt的結構，自動生成的prompt顯示一個very basic version，然後在ui頁面上有一堆欄目選項，都是不同維度的prompt細化共我選擇，我點擊一個欄目的時候，你直接根據當前的場景，當前欄目，推薦給我幾個細化prompt的選擇，我選擇個點擊確認之後，你就把這個細節加入到prompt裏面"。用户通过多选锁定：建议来源 = 后端实时调用 LLM；basic version = 改自动生成（stage 6）；适用范围 = 只 shot 视频 prompt；LLM 集成 = 官方 anthropic SDK；合并方式 = 智能（空则填入，非空则追加）。
