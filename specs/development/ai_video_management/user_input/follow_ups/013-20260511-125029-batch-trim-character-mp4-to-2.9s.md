# Follow-up draft 013 — 2026-05-11

一次性数据操作：把 `ai_videos/mozun_chongsheng/characters/c*/c*.mp4` 全部 19 个文件 **就地** trim 到 **exact 2.9s**（ffmpeg re-encode），让它们直接满足 character turntable rule #12.5 的 ≤ 2.9s Seedance reference 上传约束 — 之前用户手工渲染的实际时长 3-5s 各异。

## 范围说明（hook 标记 vs 实际范围）

UserPromptSubmit hook 把 prompt 归到 `ai_video_management`，但 **本 follow-up 不改 webapp 代码** — 它是 `ai_videos/mozun_chongsheng/characters/` 下的 binary file 重写（mp4 byte-level）。webapp 只读，schema 不解析时长字段，所以 ai_video_management 行为零变化。Follow-up 持久化登记于此是因为 hook 选了它；同时在 `specs/ai_video/mozun_chongsheng/changelog.md` 加 cross-ref 条目记录实际 artifact 改动。

## 用户原话

> are you able to easily cut a 4s mp4 into 2.9s, basically just take the first 2.9s
> basically for all mp4 and ai_video_management/charactor folders, help me cut them into 2.9s

（`charactor` = `character` 笔误）

## 用户在多选题中确认

1. **Output strategy**：overwrite in place（原文件被替换，no backup ; 用户接受 ; 原始版本已无）
2. **Precision**：exact 2.9s（ffmpeg re-encode，每文件 ~5-10s，总 batch 约 2 分钟）
3. **Scope**：仅 19 个 `characters/c*/*.mp4`；scene mp4s 跳过（rule #12.10 v2 已把 scene 改 3.9s，与本批操作目标冲突）；其他 drama 不影响（目前只 mozun_chongsheng）

## 执行细节

- **ffmpeg binary**：通过 `pip install --user imageio-ffmpeg` 拉来的 v7.1 bundled exe（位于 `%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.13_*\LocalCache\local-packages\Python313\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe`）；不污染系统 PATH。
- **命令模板**：`ffmpeg -y -i <src> -t 2.9 -c:v libx264 -preset fast -crf 18 -c:a aac -movflags +faststart <tmp>` → atomic rename `tmp` → `src`。`-c:a aac` 是因为部分 Kling/Seedance 输出含 audio track；`-movflags +faststart` 让网页 / webapp 内 inline 播放更快开始。
- **Atomic write**：先写 `<src>.trim.mp4` 临时文件，ffmpeg 成功后再 `mv` 覆盖原文件 — 防 ffmpeg 中途崩溃留下半截文件。
- **Verify**：每文件 trim 完用 `ffprobe -v error -show_entries format=duration` 输出实际时长；用 Python 判断 abs(duration - 2.9) < 0.05 算 OK；否则记入 errors[]。

## 19 文件清单（pre-state，post-state 见 changelog）

```
characters/c10_司空玄/c10_司空玄1.mp4
characters/c10_司空玄/c10_司空玄2.mp4
characters/c1_沧冥/c1_沧冥1.mp4
characters/c1_沧冥/c1_沧冥2.mp4
characters/c1_沧冥/c1_沧冥3.mp4
characters/c1_沧冥/c1_沧冥4.mp4
characters/c1_沧冥/c1_沧冥5.mp4
characters/c3_苏璃月/c3_苏璃月1.mp4
characters/c3_苏璃月/c3_苏璃月2.mp4
characters/c3_苏璃月/c3_苏璃月3.mp4
characters/c3_苏璃月/c3_苏璃月4.mp4
characters/c4_柳红袖/c4_柳红袖.mp4
characters/c5_苓夭夭/c5_苓夭夭.mp4
characters/c6_白月清/c6_白月清.mp4
characters/c7_赵焚天/c7_赵焚天1.mp4
characters/c7_赵焚天/c7_赵焚天2.mp4
characters/c7_赵焚天/c7_赵焚天3.mp4
characters/c8_方鼎元/c8_方鼎元.mp4
characters/c9_韩夺心/c9_韩夺心.mp4
```

（注意：`c2_*` 与 `c*_seedream.png` 同名 png 不在范围；scene `s*/s*N.mp4` 跳过；ep* prompts/shot* 下的成片 mp4 跳过。）

## 不受影响（surgical 范围之外）

- `projects/ai_video_management/` 任何代码 / 测试 / e2e — webapp 不 parse 时长字段，文件 mtime 会变但内容仍是合法 mp4
- `agent_refs/project/ai_video.md` rule #12.5（character turntable 锁 2.9s）— **本 follow-up 是把 artifact 主动对齐到现有规则**，无规则改动
- rule #12.10 v2 (scene reference 3.9s) — 与本批 character 操作正交
- `ai_videos/mozun_chongsheng/scenes/` 任何 mp4
- 其他 drama 项目（暂无）
- `characters/c*/c*_seedream.md` Seedream 立绘 prompt 文件 — 不动
- `episodes/ep*/prompts/shot*/shot*.md` shot prompt 文件 — `{ref_c{N}_*}` placeholder 仍指向同名 mp4 路径，无需 path patch；唯一不同是 mtime 与时长

## 唯一遗留风险

如果某些 source mp4 **本就 ≤ 2.9s**（用户已手工剪过 / 或 Seedance 输出就是短的），`-t 2.9` 不会扩长视频；ffmpeg 直接输出原时长，验证步骤 abs() < 0.05 误差窗会让 ≤ 2.85s 的文件标 `tolerated`（短于规则但不算 failed）。Changelog 会列出每文件 before/after 时长，用户 review 时可决定要不要 re-render。
