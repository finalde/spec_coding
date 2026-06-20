# Follow-up draft 131 — 2026-06-18
Bug：新分阶段结构（全流程编排）后无法 assign 演员到角色；要确保 assign/导入/其他功能在新旧结构下都 work。

---
target_stage: 6
target_artifacts: [libs/common/drama_layout.py, libs/infrastructure/writers/*, apps/ui/src/**]
severity: high
---

## 根因
分阶段结构把资产从 drama 根目录移到 stage 文件夹：`casting.md`/`characters`/`scenes` → `2_世界观人设/`，`episodes` → `4_剧本/`。后端/前端多处硬编码旧根路径——assign 角色尤其断在：① 前端 `isCasting` 正则只配根 `casting.md`，新位置 `2_世界观人设/casting.md` 不匹配 → CastingView 根本不渲染（无"+添加角色"）；② 后端 casting writer 写 `drama_dir/casting.md` + 找 `drama_dir/characters`（旧位置）。

## 修复
- 新增 `libs/common/drama_layout.py` 解析器：`casting_md/characters_dir/scenes_dir/episodes_dir(drama_dir)`，优先返回存在的位置（根/stage），缺省回退根（首次 create）。新旧结构都 work。
- 后端接入：casting__writer（assign/unassign/读/扫描，10+4 处）、downloads__writer（导入：characters/scenes/episodes）、sub_type_lookup（episodes）、bgm_reference__reader（episodes cue 扫描）、character_video__writer（`_is_under_character_folder` / `_character_folder_for` 容忍 stage 前缀）。
- 前端：Reader `isCasting` / `isEpisodeFile` 正则放开 stage 中间段；dramas.ts 新增 `findAssetDir`（characters/scenes 在根或 `2_世界观人设/` 下找）→ 人物/场景下拉、casting 资产恢复。
- 测试：tests/test_drama_layout.py（5 例，全过）。

## 校验
解析器对 wushen（staged）/nvdi（root）都正确；前端 tsc 干净；casting/character_video/downloads/tree 相关测试通过。
注：test_sub_type_lookup / test_tree_walker 里 `wukong_juexing` 相关失败为**既有 stale fixture**（项目已改名 wushen_juexing），与本修复无关。
