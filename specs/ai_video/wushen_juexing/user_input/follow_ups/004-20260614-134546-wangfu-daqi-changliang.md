---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/scenes/s1_裴王府正厅/
  - ai_videos/wushen_juexing/episodes/ep01/shots/
severity: medium
---

# Follow-up draft 004 — 2026-06-14

王府场景 prompt 太简陋——要**大气敞亮**、描述更丰富。

## 抽象后的指令

1. 裴王府正厅的场景 prompt（立绘 + 锁定描述符）从「压暗肃穆」改为**大气、恢弘、高敞、明亮**：面阔多间的高大殿堂、高耸朱漆描金巨柱、月梁阑额普拍枋铺作斗栱、斗八藻井、高大直棂窗满堂天光、丹墀玉阶须弥座、障壁画 / 织锦壁衣、雍容陈设、青砖墁地光可鉴人；空间纵深、真实材质质感、影视级写实（反卡通）。
2. 一句话锁定 handle 同步升级为更恢弘的措辞，并**同步替换全部引用它的 shot**（保持 byte-identical），让 Seedance 文生视频的 `场景:` 行本身也大气。
3. 保持：唐宋营造法式不跨朝代、零 hex 自然色名、不点名任何影视/游戏 IP（平台合规）。

## 落地

- 旧 handle：`裴王府正厅：青砖玉阶、满堂宾客、淡灰青冷调的镇国厅堂。`
- 新 handle：`裴王府正厅：丹墀玉阶、面阔九间、大气恢弘的镇国厅堂。`（≤30 字）
- 全量替换 29 个 shot + 场景档；场景档 descriptor 字段与立绘 prompt 大幅扩写为大气敞亮。
- 戏剧性压暗仍可由各 shot 的 `光线 / 色调:` 行按需处理；场景基底为高敞明亮。
