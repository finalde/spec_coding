# Follow-up draft 007 — 2026-06-21

全局导入 + 更长更细的 prompt；清空现有 BGM 重生成。

## 变更
1. **清空现有 BGM**：删除 `ai_videos/_bgm/*` 全部轨道（及 `_deleted/_bgm` 旧测试数据），用户重新生成。
2. **全局导入（像 _actor）**：左侧导航 `_bgm` 根新增「📥 导入下载音乐」按钮，一次性扫描 Downloads 近 7 天音频，按文件名里的 `bgm_NNNN` key 归位到对应轨道（`DownloadsImporter.import_bgms`，命令按 drama_name=`_bgm` 分发），未匹配进 `_bgm/_not_matched/`。**移除每个详情页单独的导入按钮**。
3. **删除每轨 import_audio 全链路**：BgmPool.import_audio / _newest_download / _clear_audio、/api/bgms/{id}/import-audio 路由、BgmCommand.import_audio、repository 协议、BgmNoDownloadAudioError、importBgmAudio（api.ts）、BgmView 的导入按钮与 handler。
4. **prompt 更长更细（≥1000 字符）**：build_bgm_prompt 重写为结构化长文 brief——风格/情绪/能量/编曲结构（intro→develop→focal point→resolve）/动态/制作混音/使用场景/严格纯音乐约束/时长；实测 ~1700–1800 字符。中文 mood/配器预设译英。保留首行 KEY。

## 备注
- 本地 GPU 生成按钮保留（可选）；主路径为 ElevenLabs 出乐 + 全局导入。
- 导入保留原扩展名命名 `bgm_NNNN.{ext}`，每轨一份音频（重导覆盖）。
