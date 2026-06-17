# Follow-up draft 001 — 2026-06-16
BGM generation form: preset dropdowns + optional free-text override; and make generation failures diagnosable.

## 指令
- **生成表单的自由文本字段改为「dropdown 预设 + 可选自定义框」**：mood（氛围）和 instruments（配器）原来是纯 free-text input，改为先给一个常用值的 dropdown（首项「（不限）」= 空），旁边再留一个 optional 的 free-text box；自定义框非空时优先，留空则用 dropdown 选项。预设是纯前端便捷词表（后端仍接受任意 ≤200 字自由文本，无新增枚举）。notes（备注）保持纯 textarea。
- **生成失败信息要可诊断**：子进程失败时，错误展示取的是 stderr 的「前 300 字」——那只是 traceback 头部，把真正的异常（如 `ModuleNotFoundError: No module named 'torchaudio'`）藏在了末尾。改为取 stderr 的**最后一行非空内容**（traceback 的异常摘要行），用户一眼能看到根因。
- **生成依赖说明**：实际生成需要 `tools/stableaudio_gen.requirements.txt` 的重型依赖（torch / torchaudio / stable-audio-tools / einops）装在专用 venv，并通过 `BGM_PYTHON` 环境变量指向该解释器；webapp 自身进程不装 torch。当前失败根因即该解释器缺 torchaudio / stable-audio-tools。
