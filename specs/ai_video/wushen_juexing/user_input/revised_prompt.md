# 原始需求 — 2026-06-13

task_type: ai_video
sub_type: novel

我要造一部短剧《被家族除名，看我武神归来之武神觉醒》。

剧情：一个王府的长公子，因为丹田破碎，被家人嫌弃，尤其是弟弟打压。
然后在系统的提示下，选择了不向王爷父亲低头，脱离王府，
觉醒武神躯和王体资质（其他资质还有天阶、低阶、玄阶等），
后拜入剑修门下的故事。

用户希望先走完整 agent_team 六阶段流程，并产出第一集 EP1。

---

---
target_stage: 4
target_artifacts:
  - final_specs/spec.md
  - ai_videos/wushen_juexing/world.md
  - ai_videos/wushen_juexing/arc_outline.md
  - ai_videos/wushen_juexing/characters/
  - ai_videos/wushen_juexing/episodes/ep01/
severity: high
---

# Follow-up draft 001 — 2026-06-13

新增剧情设定：主角穿越身份 + 三公主退婚转嫁弟弟 + 落魄剑宗与师姐 + 弟弟反派前因。

## 抽象后的指令

1. **主角穿越设定（首集 EP1）**：裴知秋是穿越者——现代（或异世）灵魂穿越到这具"丹田破碎被除名"的废柴长公子身上。系统觉醒与穿越绑定。EP1 至暗后的觉醒带穿越者视角。

2. **新增女性角色（先引入数位女角色）**：
   - **皇朝三公主**：裴知秋名义上的未婚妻。得知主角丹田破碎，当即要退婚，并将婚约**转嫁给主角的弟弟（裴昭）**。势利、骄矜，EP1 反派配角（至暗加码）。
   - **剑宗师姐**：主角后来拜入的剑道门派的师姐，**性格正直**。EP2+ 出场。

3. **主角机缘线（EP2–7）**：主角离府后获得**机缘**，**测天赋**，**选宗门**，最终选择了**落魄的剑宗**。

4. **剑宗背景（落魄剑宗）**：原本辉煌，**百年前因主力抗衡妖族、元气大伤**，如今落魄。主角拜入的就是此宗。

5. **弟弟反派前因（裴昭）**：裴昭是反派之一。**主角当年正是为救弟弟受伤，才导致丹田破碎**；但弟弟非但不感激兄长，反而处处为难。此前因是主角"不向家族低头、断绝关系、出走闯荡"的重要情感动机。

6. **EP1 切点重申**：开篇哥哥在系统提示下，**不苟且偷生，选择离开家族、断绝关系、出去闯荡**——与既有 EP1 切点一致，仅补强动机（穿越者清醒 + 救弟反被欺的寒心）。

## 落地命名（本 follow-up 自拟，用户可改）

- 皇朝三公主 = **萧绛雪**（C5）
- 落魄剑宗师姐 = **苏清歌**（C6）
- 落魄剑宗 = **太虚剑宗**（凌虚子为其隐世长老/掌门，苏清歌为大师姐）
- 妖族 = 百年前与剑宗大战、致其元气大伤的外部威胁势力

---

---
target_stage: 4
target_artifacts:
  - final_specs/spec.md
  - ai_videos/wushen_juexing/world.md
  - ai_videos/wushen_juexing/arc_outline.md
  - ai_videos/wushen_juexing/characters/
severity: medium
---

# Follow-up draft 002 — 2026-06-13

新增：落魄太虚剑宗双剑王长老 + 宗门大比存亡 stakes + 分体系等级阶梯。

## 抽象后的指令

1. **太虚剑宗双长老（剑王级别）**：剑宗有两个老头，都是**剑王级别**。其中**一个亲赴招生现场，招走了主角裴知秋**（对应 EP6–7 测天赋/选宗门招生线）。

2. **招生动因 = 宗门存亡 stakes**：每年有**宗门大比**；规则是**连续垫底 10 年的宗门将被取消**。太虚剑宗因**没有年轻一辈**，**已连续垫底 9 年**——再垫一年就要除名。故两位剑王长老不得不亲自下场招收新血，这正是他们看中天赋异象的裴知秋、急于招揽的原因。

3. **分体系等级阶梯（世界观规则）**：每个修炼体系都有自己的等级阶梯。
   - **剑修体系**：剑徒 → 剑师 → …… → **剑王** → **剑仙**。
   - **武道体系（武宗一脉）**：武徒 → 武师 → ……（沿用既有武道九境）。
   - 即：等级阶梯按「体系」区分，称谓各异，阶位相互对应。

## 落地命名 / 设定（本 follow-up 自拟，用户可改）

- 剑修等级阶梯（与武道九境对应）：剑徒 → 剑者 → 剑师 → 剑宗 → 剑王 → 剑皇 → 剑帝 → 剑圣 → **剑仙**（顶）。剑王为高阶（第 5 阶·王阶），剑仙为顶阶。
- 太虚剑宗双剑王长老：
  - **柳鹤鸣（C7）**：剑王长老，洒脱慧眼，亲赴招生现场招走裴知秋。
  - **关山岳（C8）**：剑王长老，沉稳刚直，留守宗门。
- 凌虚子（C4）定位微调：太虚剑宗**剑仙级隐世掌门**（宗门仅存的剑仙底蕴，隐世不出，故宗门大比仍靠青黄不接的年轻弟子、连年垫底）。
- 影响范围：EP6–7 招生线（arc）+ 双长老 bible + world 等级阶梯/大比 stakes；**EP1 不受影响**（EP1 无招生、无剑修等级用语）。

---

---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/episodes/ep01/
  - ai_videos/wushen_juexing/world.md
  - ai_videos/wushen_juexing/arc_outline.md
severity: high
---

# Follow-up draft 003 — 2026-06-14

EP1 开场重构为「穿越 + 系统二选一」，并据此更新下游剧情。

## 抽象后的指令

1. **第一个镜头 = 主角穿越**：S01 改为主角（现代/异世灵魂）**穿越**瞬间——睁眼发现自己成了**丹田被废、被嫌弃的王府大公子（裴知秋）**，脑中涌入原主记忆。仍是冲突冷开场（穿越即跪地受辱），不做世界观旁白。

2. **系统给「二选一」**：系统出现后给出两条路：
   - **选择一（懦弱）**：低头认命，继续留在王府当任人践踏的废物。
   - **选择二（骨气）**：挺胸抬头、与王府**断绝关系**、走出王府——**奖励：武神躯**。
   主角选「二」：当众断绝关系、走出王府，随即觉醒武神躯（+ 王体资质）。

3. **据此更新 EP1 情节**：S01（穿越开场）、系统面板镜（二选一 + 武神躯奖励）、主角宣告镜（断绝关系/走出王府）相应改写；其余镜（至暗受辱、三公主退婚、王体/武神躯觉醒打脸、宗门暗线钩）保持，仅与新开场衔接。

4. **把剩下的故事情节也更新一致**：world.md 的系统设定补「二选一 + 武神躯为选择走出的奖励」；arc_outline 的 EP1 及后续线与「穿越者 + 主动选择走出 + 武神躯奖励」自洽。

## 落地（本 follow-up）

- 系统机制：武神觉醒系统在至暗时给「懦弱留府 / 挺胸断绝走出（奖励武神躯）」二选一；主角选后者。
- EP1 总镜数（30）与总时长（183s）不变，仅 surgical 改写 S01 / S10（+ S13 台词补「断绝关系」），不整集重生成。

---

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

---

---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/episodes/ep01/
  - final_specs/spec.md
  - ai_videos/wushen_juexing/arc_outline.md
severity: high
---

# Follow-up draft 005 — 2026-06-14

每集时长改为约 1 分半（~90s）重新规划 + 每个人物首次出场给特写（预留人物介绍字幕位）。

## 抽象后的指令

1. **每集 ~90s（1 分半左右）**：从现在的每集 ~180–195s（EP1=183s）改为**每集约 90s，范围约 [85,100]s**。EP1 据此**重新规划 / re-cut**：保留主线节拍（穿越→至暗→系统二选一→断绝走出→王体+武神躯觉醒打脸→末镜钩），把镜头数从 30 收到约 16，重排时长使 时长合计 落在 ~90s。
2. **人物登场特写**：每个角色**首次出场**的那一镜要带**面部特写**（缓推至面部），并**预留人物介绍字幕位**（作者后期叠加"角色名·身份"字幕）。EP1 首次出场：裴知秋(S01) / 裴昭 / 裴霆 / 萧绛雪 / 裴府长老 / 凌虚子。
3. **divergence**：本项目每集 ~90s 与 `agent_refs/project/ai_video.md` 规则 6（180–195s）冲突——按 CLAUDE.md precedence 以本项目 spec 的 divergence note 覆盖该规则（仅限本剧），不改全局 ref。验证的 时长合计 / 镜数 bound 同步放宽到本项目目标。

## 落地

- 每集时长目标：**约 90s（1 分半），[85,100]s**；单镜仍 ≤15s、fast-cut。
- EP1 re-cut：30 镜/183s → 约 16 镜/~93s（delete-then-regen shot 层）。
- 人物登场特写契约：首次出场镜 `镜头:` 含特写/缓推至面部，Shot context 加一行「登场介绍：预留人物字幕位（角色名·身份）」，prompt 不写字幕内容（作者后期叠加）。
- 角色一句话锁定 / 场景锁定 handle 不变，仍 byte-identical。

---

---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/style_guide.md
  - ai_videos/wushen_juexing/scenes/s1_裴王府正厅/
  - ai_videos/wushen_juexing/episodes/ep01/shots/
severity: medium
---

# Follow-up draft 006 — 2026-06-14

王府色调太阴暗，要明亮点。

## 抽象后的指令

- 裴王府正厅的整体色调从「淡灰青冷调 + 四周压暗」改为**明亮通透为主**：高窗天光满堂、明亮大气、雍容；保留淡青的雅致底子但**显著提高亮度、减少压暗**。
- 戏剧性的局部压暗只在**确有必要的情绪镜**按需使用，不再作为全场默认。
- 与 follow-up 004（大气敞亮）一脉相承：大气 + 敞亮 + 明亮。
- 随 EP1 re-cut（follow-up 005）一并落到新 shots 的 `光线 / 色调:` 行。

## 落地

- style_guide §二 调色：主基调明亮通透、提亮、减压暗；冷暖对比保留但整体更亮。
- 场景档默认光源已是「高窗天光满堂、明亮通透」（follow-up 004），保持。
- EP1 新 shots `光线 / 色调:` 默认「高窗天光满堂、明亮通透、雍容大气」；仅 S05 伏地、S16 末镜等情绪镜可局部柔和压暗。

---

---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/style_guide.md
  - ai_videos/wushen_juexing/scenes/s1_裴王府正厅/
  - ai_videos/wushen_juexing/episodes/ep01/shots/
severity: medium
---

# Follow-up draft 007 — 2026-06-14

场景不用 100% 朴素写实——地板/墙壁要漂亮点，适度仙侠风（修仙题材），但不能一看就卡通或不真实。

## 抽象后的指令

- 美术方向从「纯朴素写实」调为**电影级唯美仙侠写实**：在照片级真实质感打底之上，叠加唯美/仙侠元素——
  - **地面**：磨光纹样青砖 / 碾玉装纹样石板，光可鉴人、淡淡倒影；
  - **墙壁**：障壁画 / 织锦壁衣 / 碾玉装·五彩遍装彩画 / 描金线脚，精致不素白；
  - **仙气氛围**：极淡薄雾、丁达尔光束、微尘流光（**克制用量**），鎏金描金点缀。
- **铁律：不卡通、不失真**。保持影视级真人实拍质感主导；**严禁** 卡通 / 动画感 / anime / 国漫 / 3D 游戏画面 / CG 渲染感 / 塑料感 / 扁平光 / 星点闪光过曝过饱和。避开 nvdi 019 失败模式：不挂游戏/动漫参考锚、不堆粒子光效。
- 唐宋营造法式不跨明清；零 hex 自然色名；不点名 IP。

## 落地

- style_guide：画风关键词加「电影级唯美仙侠 + 精致纹样场景」，新增「美术方向（唯美仙侠写实 + 反卡通铁律）」段。
- scene 档 s1_裴王府正厅：地面/墙壁/仙气氛围细节扩写为唯美仙侠 + 立绘 prompt 风格行调整 + 反卡通反向词强化。
- EP1 16 个 shot 的 `渲染样式:` 统一升级（加 电影级唯美仙侠 + 精致纹样场景 + 淡仙气，保留 影视级真人写实/photorealism 主导）。

---

---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/scenes/s1_裴王府正厅/
severity: medium
---

# Follow-up draft 008 — 2026-06-14

场景生成分步走（video-first），且场景 video 每一秒的朝向必须与截帧方向一一对应。

## 抽象后的指令

场景生成流水线分三步：
1. **背景图 seed prompt**：生成一张基底背景图（即现在的 Seedream 立绘风格，保留）。
2. **场景 video prompt**：另给一条视频 prompt，用户把第①步的背景图**上传作 reference**，生成一段**环视各角度**的场景视频。
3. **一键截各方向场景图**：用户下载视频后，用 webapp 已有功能一键从视频里截出**各个方向**的场景图（DownloadsImporter 按 `bg{N}_{方位}` 方位段路由到对应 plate folder）。

**核心要求**：场景 video 的**每一秒朝向**必须与**截帧方向 / plate 方位**严格一一对应——即视频 prompt 要带**逐秒方位时间轴**（朝北/朝东/朝南/朝西/高位俯瞰…），且与背景图系统 index 表里「方位 ↔ 秒段 ↔ 截帧时点 ↔ plate folder」完全吻合，这样用户在某一秒截帧 = 已知方位的 plate。

## 落地

- scene 档 s1_裴王府正厅 重构为三段：① 步骤一·背景图 seed prompt（保留现有立绘）② 步骤二·场景 walk-through video prompt（15s，逐秒方位时间轴，上传背景图作 reference）③ 背景图系统 index（方位↔秒段↔截帧时点↔plate folder）。
- 建 folder-per-朝向 plate（`scenes/s1_裴王府正厅/bg{N}_{方位}_{描述}/{同名}.md`），每 plate 的 image prompt `主体:` 行以「{scene} {方位}视角」开头（nvdi 015：方位段须进 主体行，供下载文件名路由）。
- 唯美仙侠写实 + 反卡通铁律（follow-up 007）延续；零 hex；不点名 IP。

---

---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/style_guide.md
  - ai_videos/wushen_juexing/scenes/s1_裴王府正厅/
  - ai_videos/wushen_juexing/episodes/ep01/shots/
severity: medium
---

# Follow-up draft 009 — 2026-06-14

色彩要明亮，不要整体都是墨绿色/暗红色，还要带点仙侠气。

## 抽象后的指令

- 整体调色**明亮化**：去掉"整体墨绿/暗红/淡灰青冷调/压暗"的沉闷感。
- 主色调改为：**明亮朱红描金 + 天青/青碧透亮 + 月白 + 米白暖金天光**；减少暗红、墨绿、玄青沉调。
- **仙侠气**：青碧透亮、淡金流光、暖金天光、月白仙气、极淡薄雾丁达尔光（克制）。
- 保留**照片级写实 + 反卡通铁律**（follow-up 007）。

## 落地（保护项）

- **保留**觉醒 motif「**残血暗红**」（S13 武神躯裂纹专用，不属于"整体"暗红，保留）。
- **保留**角色身份色：裴霆「**玄青蟒纹**」是其专属锁定色（byte-identical 跨镜），不动；裴知秋「玄黑描金」等同理。本次只调**场景/整体环境**调色，不动角色锁定描述符。
- sweep：`淡灰青冷调`→`明亮天青米白暖调`、`朱漆暗红`→`明亮朱红`、`玄青织锦`→`天青织锦`、`顶光压暗`→`高窗天光满堂明亮`、`四周压暗`→`四周明亮通透`；情绪镜（S05 伏地/S16 末镜）的"柔和压暗"保留。
- style_guide §二 调色 + §七 角色主色（场景相关）更新；scene 档配色 + 立绘/video/plate prompts 更新。

---

---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/
  - final_specs/spec.md
severity: low
---

# Follow-up draft 010 — 2026-06-14

所有 prompt 都不用刻意说明是 9:16，用户自己在平台 set。

## 抽象后的指令

- 所有 pasteable prompt 代码块**不再写** `比例: 9:16`（用户在 Kling/Seedance/即梦 平台自行设画幅）。
- prompt 相关的 `画幅: 9:16 …` / `构图: 9:16 竖屏…` 行去掉 9:16（保留"竖屏"方向词即可）。
- 验证不再要求 `比例: 9:16`（本项目 divergence：覆盖 ai_video 规则 12.4「比例必填」/ 规则 7 / move #5「缺比例=blocker」——仅本剧）。

## 落地

- sweep：删除所有 `比例: 9:16` 行；`画幅: 9:16 竖屏 / 4K…`→`画幅: 竖屏 / 4K…`；`构图: 9:16 竖屏`→`构图: 竖屏`。
- spec NFR-6 + validation(structure_schema/acceptance/publish) 去掉 比例 必填 gate（记 divergence）。
- 保留"竖屏"作为方向提示（非比例数字）。

---

---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/style_guide.md
  - ai_videos/wushen_juexing/scenes/s1_裴王府正厅/
  - ai_videos/wushen_juexing/episodes/ep01/shots/
severity: high
---

# Follow-up draft 011 — 2026-06-14

色调还是太暗，需要大改 prompt：室内放高雅黄色灯笼（暖黄灯火），参考美学、漂亮 fancy；这是仙侠剧，不必严格还原王府古建，观众看着漂亮即可。

## 抽象后的指令

- **大改场景 prompt**，整体更亮、更华美：
  - **室内高雅黄色灯笼 / 宫灯**成列高悬 + 玉阶两侧立地宫灯，**暖黄灯火盈盈**——这是主要提亮手段。
  - 叠加 fancy 仙侠美学元素：鎏金描金、琉璃、轻垂纱幔、玉阶生辉、暖金流光、淡仙气薄雾丁达尔光（克制）。
  - 整体调色：**暖黄灯火 + 米白天光 + 描金 + 朱红 + 天青点缀**，明亮暖调、华美考究。
- **放宽古建考据**：以**美学与仙侠观感优先**，不必与真实王府古建一模一样；唐宋营造法式作风味参考即可，不强求、明清禁令放宽（漂亮 > 考据）。
- 仍**反卡通**：照片级写实质感主导，漂亮 fancy 但不是动画/CG/塑料感。

## 落地

- style_guide：美术方向加「暖黄宫灯/灯笼提亮 + 仙侠华美 fancy + 美学观感优先（不强求古建考据）」。
- scene 档 s1：立绘 seed + walk-through video + 5 plate 的 细节/光线 大改——加暖黄宫灯灯笼、纱幔琉璃鎏金、暖金流光、明亮暖调 fancy。
- EP1 shots（正厅 S01–S15）`光线 / 色调:` 前置「暖黄宫灯灯火盈盈、明亮暖调」提亮；S16 室外不加宫灯。

---

---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/scenes/s1_裴王府正厅/
  - ai_videos/wushen_juexing/style_guide.md
severity: medium
---

# Follow-up draft 012 — 2026-06-14

场景 bg prompt 应说明：生成的是**高清图片**，且**镜头与位置要精准**——因为这是用来做 shot 背景板的。

## 抽象后的指令

- 每个场景 bg prompt（步骤一 seed + 5 个方向 plate 的 image prompt）都要显式声明：
  1. **画质 = 高清**：4K 超高清、高分辨率、细节锐利清晰；本图用作 shot 背景板，画面要干净、透视稳定。
  2. **镜头 / 机位精准**：明确视角方位、机位高度（水平视平线）、焦距感（标准镜头约 35–50mm 等效）、透视稳定不畸变、构图位置精准、并预留人物站位空间。
- 原因：bg 图是 shot 的背景参考板，镜头/位置不精准会导致各 shot 透视/站位对不齐。

## 落地

- scene 档 seed prompt + bg1..bg5 plate prompt 各加 `画质:` 与 `镜头 / 机位:` 两行（方位按各自）。
- style_guide / 背景图系统 index 加一句「bg prompt 须声明高清 + 精准镜头机位（作 shot 背景板）」。

---

# Follow-up draft 013 — 2026-06-14

角色 prompt 必须生成视频，统一为「视频 reference」格式（与《女帝退婚后悔了》一致）。

---

武神觉醒 8 个角色档（c1–c8）原本使用已弃用的「Seedream 立绘 prompt」（rule #12.2，输出静态 PNG），导致角色 prompt 生成的是图片而非视频。这与统一 setting 不符：`.claude/agent_refs/project/ai_video.md` §12.5 规定「视频 reference」7s 单 take turntable prompt（rule #12.5 v11）**完全 supersede 旧的立绘单 prompt 格式**，《女帝退婚后悔了》各角色档已采用此格式（渲染 mp4）。

要求：把 8 个角色档底部的 prompt section 从「Seedream 立绘」改为「视频 reference prompt（rule #12.5 v11）」，结构与 nvdi_tuihun_houhuile 各角色档逐字对齐——主体一句话锁定 + 角色造型块 + 身高/服装/面部细节 + 5-phase timed 姿态（0-2s 正面 / 2-3s 左转 / 3-4s 侧身 / 4-5s 左转 / 5-7s 背面）+ 镜头/光线/渲染/比例/时长/音频 + 3 句数字计数台词配音对照表。角色锁定描述符（顶部表格）保持不变，仅替换 prompt section。

---

---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/scenes/s1_裴王府正厅/
severity: medium
---

# Follow-up draft 013 — 2026-06-14

15s 场景视频要能一键按方位截帧到 bgX_(东/南/西/北/中) 文件夹（webapp video 上加按钮）；且视频逐秒朝向必须与截帧 function 的时间点严格一致（如前段正北、转正东…，截帧时点刚好镜头对准该方向）。

## 抽象后的指令
- webapp：scene 视频上加按钮，一点即按方位时间点截帧、生成到各 bg{N}_{方位}_ 文件夹（作 shot 背景板）。
- 一致性铁律：场景 video 的逐秒朝向 = 截帧 function 的时间点 = plate 方位。
- 方位集对齐为 北/东/南/西/中（bg5 高位俯瞰→中）。

## 落地（drama 侧）
- scene video 逐秒方位时间轴与截帧时点统一：北@1.5 / 东@4.5 / 南@7.5 / 西@10.5 / 中@13.5（5 dwell×3s，dwell 中点截帧）。
- bg5_高位俯瞰_中轴全景 → bg5_中_中轴俯瞰（folder+file+引用）；index 表方位列改「中（高位俯瞰）」。
- webapp 侧功能见 ai_video_management（新增 extract-scene-plates 端点 + SiblingMedia「🧭 截取方向背景图」按钮）。

---

# Follow-up draft 014 — 2026-06-14

角色 turntable prompt 触发 Kling「违反社区规范」拒绝生成，须清除真人合规违规项。

---

反馈：c1 裴知秋的视频 reference prompt 被 Kling 以违反社区规范拒绝生成。

根因（对照 `.claude/agent_refs/project/ai_video.md` §563 = nvdi follow-up 020 平台审核合规）：turntable 生成块（```text``` 段）含两类真人合规违规项——
1. **真人演员名**：c1 面部细节行「类比 … (e.g. 罗云熙 / 王鹤棣 清冷态)」直接点名真人演员（§020 ① 禁 IP / 真人名；Kling 对公众人物名尤其敏感）。
2. **真人素材引用**：8 档共有的「角色造型 (覆盖演员照片日常素颜 + 现成短假发…演员素颜 入画)」+「严禁照抄演员参考照片」（§020 ④ 人脸属敏感个人信息，勿在 prompt 提真人 / 演员照片）。

注：§12.7 要求在 turntable 角色字段嵌入 1-2 名 specific 演员锚点，与 §020 直接冲突——§020（平台审核）胜，因为它正是「不符合平台规则→生成失败」的成因。

要求：8 档 turntable 生成块全部去真人化——删除演员名、把「覆盖演员照片…」改为纯画面「造型锁定 (以下文字为唯一造型依据, 画面严禁现代元素…)」、把「严禁照抄演员参考照片」改为「以本 prompt 文字为准, 古装造型」。保留纯风格写实词（影视级真人写实 / 真人皮肤毛孔 / photorealism 等，§593 推荐，非真人引用）。同时在 §12.5 增补合规优先条，防止后续 regen 按 §12.7 重新写回演员名。

---

---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/episodes/ep01/
  - ai_videos/wushen_juexing/world.md
  - final_specs/spec.md
  - ai_videos/wushen_juexing/arc_outline.md
severity: high
---

# Follow-up draft 014 — 2026-06-14

EP1 收窄 + 加回忆镜。

## 抽象后的指令

1. **王体资质移出 EP1**：王体（资质）应是**之后几集、从门派测试才测出来**的，本集不需要。EP1 删除王体资质显化（九柱冲霄）+ 长老测资质镜。
2. **三公主退婚移出 EP1**：公主退婚不是这一集。EP1 删除萧绛雪退婚转嫁镜（萧绛雪 bible 保留，EP2+ 再出）。
3. **EP1 聚焦**：交代清楚**主角穿越 + 系统二选一选项**即可（武神躯作为"选择②断绝走出"的系统奖励，本集觉醒——这是体质金手指，与"资质"无关，故保留）。
4. **加回忆镜**：插入回忆——当年黑衣人夜袭，主角**为弟弟裴昭挡下黑衣人一掌、丹田破碎**；以及伤愈后**弟弟恩将仇报、当众看不起 / 推搡哥哥**。回忆用暖黄泛旧回忆色调，与当下区分。

## 落地

- world §三：EP1 系统奖励=武神躯（体质，单段觉醒，不再"先王体后武神躯"）；王体资质=后续门派测试才显（资质轴 top tier 保留、揭示后移）。
- EP1 re-cut（16 镜 ~94s）：删退婚/王体/长老镜，加 3 个回忆镜（救弟挡掌 / 丹田破碎 / 恩将仇报）；保留 穿越开场 / 至暗除族 / 系统二选一 / 断绝走出 / 武神躯觉醒 / 剑修末镜钩。
- 登场特写：裴知秋/裴昭/裴霆/凌虚子（萧绛雪、长老本集不出场）。
- arc：EP1 line 更新；王体资质 reveal 落到门派测试集（约 EP8）。

---

# Follow-up draft 015 — 2026-06-14

王爷（裴霆）穿着颜色要和儿子不同、符合王爷身份，并加胡子。

---

c3 裴霆（镇国裴王府王爷）原主色 `玄青蟒纹王袍`，与长子裴知秋的 `玄黑` 太接近（都偏暗冷），不够区分，也不够彰显王爷身份。

要求：
1. **改主色**：玄青 → **深紫描金蟒纹王袍**（短锁定串作「深紫金蟒王袍」）。深紫 = 亲王/王爷皇室身份色，与两个儿子明确区分（裴知秋玄黑 / 裴昭朱红），与其余角色（月白/孔雀蓝/竹青/烟灰/玄褐）不撞色；蟒纹 + 描金强化王爷规制。
2. **加胡子**：短须 → **蓄修剪利落的霜白络腮短髯**（与两鬓霜白同色，45-50 岁魁梧王爷更显威严）。短锁定串并入「鬓髯」。

颜色 + 胡子写进 byte-identical 一句话锁定，跨集逐镜传播。

---

---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/characters/
  - final_specs/spec.md
  - ai_videos/wushen_juexing/style_guide.md
severity: medium
---

# Follow-up draft 016 — 2026-06-14

新加角色（沈婉）prompt 太少、而且不是视频——角色应有转盘视频 prompt。

## 抽象后的指令

- 角色档现在只有一段 Seedream 立绘（静态图），**缺角色转盘 video prompt**。按 ai_video.md 规则 12.5：角色与场景同构，走两步——
  1. **立绘 seed 图**（已有）。
  2. **角色转盘 video prompt（turntable）**：上传立绘作 image-to-video reference，生成 ~7s 转盘视频（正面→侧面→背面 360° 缓转），渲染出 turntable.mp4，作为该角色在每个 shot 图生视频的人物锚点（锁定面孔/服装/体型跨镜一致）。
- 适用**全部 9 个角色**（不止沈婉），补齐两步流水线；prompt 细节加丰富。

## 落地

- 每个 `characters/cN_{名}/cN_{名}.md` 在 Seedream 立绘段之后追加「# 角色转盘 video prompt（turntable）」段：含用法说明 + 转盘 prompt（主体/角色锁定串/镜头360°缓转/动作正侧背/光线三点布光/渲染样式/时长7s；外貌服装发型道具 byte-identical 复用本档锁定描述符）。
- spec FR-5 + style_guide：角色=立绘 seed 图 + 转盘 video（两步），与场景两步流水线对齐。
- 比例不写（follow-up 010）。

---

---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/characters/
  - final_specs/spec.md
  - ai_videos/wushen_juexing/arc_outline.md
  - ai_videos/wushen_juexing/episodes/ep01/
severity: medium
---

# Follow-up draft 017 — 2026-06-14

沈婉不是继母，只是偏爱小儿子。

## 抽象后的指令

- 沈婉是裴知秋的**亲生母亲（生母）**，不是继母 / 养母。她同时是裴昭的生母——即裴知秋与裴昭是**同母胞弟**（裴昭是主角的亲弟弟，不再是「异母弟」）。
- 性格不变：与冷酷父亲不同，不因丹田被废就把主角当弃子、仍真心疼爱，**但偏爱小儿子裴昭**。

## 落地

- c9 沈婉：继母/养母 → 生母（裴知秋与裴昭的亲生母亲）；偏爱幼子裴昭。
- c2 裴昭：异母弟 → 同母胞弟（主角亲弟）。
- c1 裴知秋：异母弟 → 胞弟；关系网「母亲沈婉（生母，偏爱幼弟）」；移除「生母身世疑云」设定（生母在世，无身世之谜）。
- spec C9 行 / arc EP10（原「生母身世疑云」改为「身世 / 玉佩来历疑云」，不涉生母）/ README / EP1 shot02·shot04·script 的「异母/继母」措辞同步。

---

---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/characters/
  - final_specs/spec.md
  - validation/consistency.md
severity: high
---

# Follow-up draft 018 — 2026-06-14

沈婉 prompt 仍和主角 video prompt 天差地别——所有角色按同一标准；并保证未来新角色统一。

## 抽象后的指令
- 角色 prompt 必须**全部统一到同一标准**（rule #12.5 v11 的「视频 reference prompt」：7s 单 take 转身 + 中文计数 + 造型锁定/面部细节/镜头/光线/渲染等齐全字段 + 计数台词表）。
- 沈婉(c9) 此前是旧式简版（Seedream 立绘 + 临时转盘），与 c1–c8 的 v11 标准不一致 → 升级到同标准。
- 我 follow-up 016 给 c1–c8 追加的「角色转盘」段是冗余（它们已有 v11）→ 删除。
- **保证未来新角色统一**：标准写入 spec FR-5（指向 rule 12.5 v11 + c1 范例）+ 新增机检 consistency C-7。

## 落地
- c1–c8：删冗余「# 角色转盘 video prompt」段（保留各自 v11 视频 reference prompt + 计数台词表）。
- c9 沈婉：删旧式立绘+临时转盘，重建为 v11 视频 reference prompt（按沈婉锁定描述符填充）+ 计数台词表。
- spec FR-5 重写为「角色 prompt 统一标准 rule 12.5 v11」+ 未来一致性保证；validation 新增 C-7（机检每角色档恰 1 个 v11 段 + 计数台词、无旧式段）。

---

---
target_stage: 6
target_artifacts:
  - .claude/skills/ai_video__dialogue_master/
  - ai_videos/wushen_juexing/episodes/ep01/
severity: high
---

# Follow-up draft 019 — 2026-06-14

EP1 纯文本对白太浅、不像正常人说话、缺因果；建「情节对白大师」skill 审查+直接改；补主角↔系统互动。

## 抽象后的指令
1. 建 **情节对白大师 skill**（`.claude/skills/ai_video__dialogue_master/`）：站普通观众立场审每个 shot/集的情节+对白，发现浅/假/缺因果/有漏洞/系统缺互动就**当场改**。
2. 用它把 EP1 对白改深：给因果、说人话（如"裴家不养废物"→讲清"你丹田碎了修不了武、裴家以武立命、容不下废人占嫡位"）。
3. **补主角↔系统互动**：系统不能只单方面弹面板，主角要与系统有来回（发现/质疑/调侃/抉择）。

## 落地
- skill 已建（D1–D6 台词准则 + P1–P6 情节准则 + 系统互动 P4 + review→直接改 workflow）。
- EP1：S02/S03/S04/S07/S16 等浅台词改深加因果；S08/S12/S15 润；S09 扩成主角↔系统来回对话（系统绑定→主角质疑→系统给二选一→主角冷笑选②），时长 7→9s；dialogue.md/script.md 同步。
- 台词层 surgical：shot 数仍 16、锁定串/零hex 不变；总时长 94→96s（仍 ∈[85,100]）。

---

---
target_stage: 6
target_artifacts:
  - .claude/agent_refs/project/ai_video.md
  - CLAUDE.md
  - episodes/ep01/shots/shot*.md
severity: high
---

# Follow-up draft 020 — 2026-06-14

武帝觉醒(wushen_juexing) 的 shot prompt 和别的剧（nvdi_tuihun_houhuile）差太多——之前告诉过的一些要求没 update 进 skill / CLAUDE setting / refs，导致新剧生成时丢了整层格式。

## 抽象后的指令

- nvdi 通过 follow-up 009/010/034 发展出的「导演级 + TTS-解耦」shot 模板此前只在 nvdi 项目级（034 明确"不改通用契约"），从未升级进通用 ref → 新剧 wushen 生成时缺失。**现正式升级为所有 ai_video 剧通用标准**。
- 三项决定（用户确认）：
  1. **台词配音(TTS)层 → 升级为通用标准**：每个有台词的 shot 加 `## 台词配音 prompt` 块（角色 / 音色锁定 voice_id / 情绪 / 语速 / 类型 / 台词 / 时长目标）+ `tools/mux_av.py` 音画解耦；推翻旧「v1 不生成 TTS / visuals-only」。
  2. **取消 起始帧/结束帧** 两个静帧 block（2026-05-27 强制规则作废）。
  3. **现在就重生成 wushen ep01 全部 16 镜** 到统一标准。

## 落地

1. **通用规则**：`.claude/agent_refs/project/ai_video.md` 新增 2026-06-14 amendment（canonical shot 模板 + 台词配音 TTS 层 + 面部辨识特征）；rule 12.1 配音参考段撤销「v1 不生成 TTS」改为 voice_id 锁定源；2026-05-27 起始帧/结束帧 amendment 标 ABOLISHED。`CLAUDE.md` AI-video 节同步收窄 visuals-only、记录 canonical shot 模板 + 配音层 + 帧块作废。
2. **wushen ep01 全 16 镜 regen**（stage-6 delete-then-write，4 个并行 worker）：补齐 参考头/角色锁定+面部辨识特征/情节/场景/走位(世界坐标)/比例 9:16 + 台词配音块（voice_id 锁定 PZQ-lead-01/PZ-brat-01/PT-patriarch-01/SW-consort-01/LXZ-immortal-01）；删 起始帧/结束帧/负向/场景视角锚；默剧镜(05/06/10/13/14)标 SFX 无台词。
3. 审计：`.audit/adhoc_agents/2026-06-14/wushen_juexing-20260614-191047/`（events.jsonl + 4 spawns）。

校验：16/16 shot YAML 信封/参考/角色+面部辨识/走位/情节/比例=1；起始帧/结束帧/负向/场景视角锚 残留=0。

---

---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/episodes/ep01/
  - ai_videos/wushen_juexing/world.md
  - characters/
  - final_specs/spec.md
severity: high
---

# Follow-up draft 020 — 2026-06-14

EP1 对白密度太低（现仅约应有的 1/3）；用户给出前 30 秒应有的对白长度与风格参考。

## 用户参考对白（前 ~30s，= 约 1/3 EP1）
- 王爷：逆子。你竟敢公然忤逆尊长，真以为我不敢执行家法、打断你的腿么。
- 主角：打断我的腿？来啊，反正你堂堂镇北王、神威盖世，捏死我这个丹田破碎的废物比捏死一只蚂蚁还简单——什么血缘亲情。
- 主角内心独白：我既然穿越过来了，这（废物的命）休想让我再做。
- 回忆 1 年前 旁白：（王爷）既然丹田已废，留他在王府也是丢脸，明早送去熊武城，让他自生自灭。（王妃）只要昭儿没事就好，知秋这身子，废了也就废了。
- 弟弟：你这是什么态度，竟敢对父亲如此无礼？父亲对你还不够好吗，你一个不能修炼的废物。

## 抽象后的指令
1. **对白密度 ×3**：EP1 不是主角沉默挨骂，而是一场**有来有回的对峙**——主角主动硬刚、反讽、戳穿伪善（"什么血缘亲情"）。每段冲突都要多句你来我往，不是单句口号。
2. **新 canon**：① 裴霆 = **镇北王**（裴王府 = 镇北王府）；② **熊武城** = 流放废物 / 自生自灭之地（王爷要把主角送去）。
3. **回忆**补：1 年前王爷决定把废了的主角送熊武城自生自灭、王妃偏袒幼子（"只要昭儿没事就好"）。
4. 主角穿越者主动、嘴硬、戳穿，不窝囊。

## 落地
- world/spec/c3 裴霆/README：加 镇北王 + 熊武城。
- EP1 re-cut 为**对白驱动**版（约 22 镜，因对白密度大，时长升至约 130–150s，覆盖 follow-up 005 的 90s——dialogue-rich 优先）。
- dialogue.md / script.md / shotlist 全面加密对白，按用户参考风格（主角硬刚+反讽+因果+对峙）。

---

---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/episodes/ep01/shots/
  - .claude/agent_refs/project/ai_video.md
  - .claude/agent_refs/validation/ai_video.md
  - validation/structure_schema.md
severity: medium
---

# Follow-up draft 021 — 2026-06-14

用户指出不一致：`nvdi_tuihun_houhuile`（女帝退婚后悔了）每个 shot 是一个**文件夹** `shots/shotNN/`（内含 `shotNN.md` + `renders/` 渲染媒体），而 `wushen_juexing`（武神觉醒）的 shot 是扁平的 `shots/shotNN.md` 文件。要求把 wushen_juexing 修正为文件夹结构，并保证两剧 behaviour 一致。

## 根因
- 规范本身就要求 folder-per-shot：`agent_refs/project/ai_video.md` rule #12.9 明确 `episodes/ep{NN}/shots/shot{NN}/shot{NN}.md`；webapp 显示契约 / 渲染导入路由 `shots/shotNN/renders/` / 台词烧录 `subtitles.md` 全部依赖该文件夹。
- 但 ref 的 layout 示意图（authoring order + 目录树）漂移成了扁平 `shotNN.md`，且 wushen_juexing 的 `structure_schema.md` S-LAYOUT-4 把「扁平 shotNN.md 才是 prompt 源」写成了规则——本会话早先还把 worker 生成的 `shotNN/shotNN.md` 当成「nested-dir bug」误「修复」成扁平，方向正好反了。

## 抽象后的指令（common-level + project）
1. wushen_juexing 22 个扁平 `shotNN.md` → `shotNN/shotNN.md` 文件夹。
2. 修正 ref layout 示意图（目录树 + authoring order 第 5 步）为 folder-per-shot，引用 rule #12.9。
3. 新增机检规则：validation/ai_video.md move #10 + 严重度行；wushen_juexing structure_schema S-LAYOUT-4 改写为 folder-per-shot blocker。
4. 全仓库一致：两剧都 folder-per-shot，无扁平 shot md。

---

# Follow-up draft 022 — 2026-06-14

shot prompt 不提字幕，只放台词 + 标 正常台词/内心独白（内心独白嘴不动）。

---

shot 视频 prompt 的 dialogue 字段不得出现任何字幕信息（用户后期自加字幕）。规则统一（common-level，已写入 `.claude/agent_refs/project/ai_video.md` §12.4 v2 + CLAUDE.md）：

- 字段 label `台词 / 字幕:` → `台词:`。
- 删除所有字幕细节：内嵌硬字幕 / 后期软字幕 / 软字幕 / 硬字幕 / 系统字幕样式 / 鎏金字幕 / 字体调性 / 硬字幕随…浮现 / 不上字幕 / 登场字幕位 / 黑屏硬字幕卡「下一集」。
- 每条台词标 `正常台词`（口型随台词开合）或 `内心独白`（嘴唇不动、不对口型，靠表情/眼神演内心）。
- 台词原文 verbatim 保留。

本剧 EP1 全部 shot（22 文件）已迁移。

---

---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/episodes/ep01/
  - ai_videos/wushen_juexing/episodes/ep02/
  - ai_videos/wushen_juexing/arc_outline.md
  - final_specs/spec.md
  - validation/
  - .claude/agent_refs/project/ai_video.md
severity: high
---

# Follow-up draft 022 — 2026-06-14

重新编排每集时长：**每集控制在 1 分半左右（~90s）；超出的内容顺延到下一集**（对白不删、不压缩）。

## 背景
follow-up 020 为加密对白把 EP1 膨胀到 136s/22 镜，与「1 分半/集」冲突。用户的解法不是删对白，而是**按 ~90s 切分、溢出顺延**。

## 抽象后的指令（common-level + project）
1. 每集 ~90s（[85,100]s / 14–18 镜）。
2. 对白密度全保留（follow-up 020 的对峙不删）。
3. 单集内容超出 ~90s → 超出的镜顺延下一集（拆在就近场景/节拍边界，重编号）。
4. 溢出段所在集可暂短（<90s/<14 镜），标「溢出段·待补」，待该集自有剧情补足。

## 落地
- EP1（136s/22 镜）按 90s 切分：EP1 = S01–S15（15 镜/90s，收在「武神觉醒系统于至暗绑定」钩子）；溢出 S16–S22 → EP2 shot01–07（46s，二选一/走出/武神躯觉醒/凌虚子末镜）。
- EP2 新建：shots 文件夹（移入并重编号 02集NN镜 / ep02 / work_unit_id）+ script/dialogue/shotlist/publish。
- arc_outline / spec FR-7(+FR-7b)/FR-9/NFR-4 / validation bounds 回到 ~90s + 溢出豁免；project ref ai_video.md 加「overflow cascades, never trim dialogue」通则。

---

---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/episodes/ep01/shots/
  - ai_videos/wushen_juexing/episodes/ep02/shots/
  - ai_videos/wushen_juexing/scenes/
  - .claude/agent_refs/project/ai_video.md
  - validation/structure_schema.md
severity: medium
---

# Follow-up draft 023 — 2026-06-14

用户发现：新生成的 shot prompt 的 `参考:` 里没有场景了——每个 shot 都应该有场景。另：如果镜头是人物近景，背景可以模糊处理。

## 根因
FU020 重生成时，回忆镜（S10–13）与末镜（凌虚子·王府外）被当成「无背景板」生成，`参考:` 只列了人物、省掉了场景——违反 rule 12.4 / 参考行格式「每个场景都要列入参考」。

## 抽象后的指令（common-level）
1. **每个 shot 必须有场景**（含回忆/一次性/室外镜）：无复用主场景的镜也要建轻量·单角度 scene 资产并在 `参考:` + `场景:` 双引用。任何 shot 的 `参考:` 缺场景 = blocker。
2. **人物近景/特写 → 背景浅景深虚化柔焦、主体清晰**；中景/全景需交代环境的镜不虚化。

## 落地
- 新建 4 个场景资产：s2_回忆书房 / s3_回忆内室 / s4_回忆庭院（夜袭夜+凉薄日两态）/ s5_王府外高地（含步骤一背景图 seed prompt、高清+精准机位、回忆镜暖黄泛旧）。
- 回忆镜 S10–13 + 末镜 ep02/S07：`参考:` 补场景 token、`场景:` 改为 `{scene} · 一句话锁定`、Reference uploads 补场景背景图。
- 18 个特写/近景镜的 `镜头:` 行追加「人物近景/特写时背景浅景深虚化柔焦、主体清晰」。
- project ref ai_video.md：加两条 dated amendment（每镜必有场景含回忆 / 近景背景虚化）。
- validation structure_schema：加 S-SHOT-SCENE-REF（blocker）+ S-SHOT-CLOSEUP-BLUR（warning）。

---

---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/world.md
  - ai_videos/wushen_juexing/style_guide.md
  - ai_videos/wushen_juexing/episodes/ep01/shots/shot15/
  - ai_videos/wushen_juexing/episodes/ep02/shots/shot01/
  - ai_videos/wushen_juexing/episodes/ep02/shots/shot04/
  - .claude/agent_refs/project/ai_video.md
severity: medium
---

# Follow-up draft 025 — 2026-06-15

系统应该是**直接在画面出现对话框**，给主角**送大礼**。

## 抽象后的指令（common-level + project）
1. 「武神觉醒系统」的一切交互（绑定/提示/二选一/发奖）= **直接出现在画面中的悬浮鎏金描边对话框 / UI 面板**（系统流游戏既视感）：框内鎏金字、选项带【】按钮高亮，主角与观众都看得见；系统文字 = 在画对话框内嵌字 + 「叮」提示音（非纯画外音/软字幕）。
2. **送大礼仪式**：发奖不是平淡兑现，而是弹「恭喜宿主获得：武神躯」贺词框 + 礼花鎏金 + 鎏金光门/礼匣自对话框炸开把武神躯大礼加身。

## 落地
- world.md §四 / style_guide.md：系统视觉改为「在画对话框 + 送大礼」。
- 系统相关 shot：EP1 S15（绑定→对话框弹现）、EP2 S01（二选一对话框带按钮）、EP2 S04（送大礼贺词框+光门大礼+觉醒）。
- ai_video.md：加通则「系统流金手指 = 在画对话框 + 送大礼」（institutional memory，未来系统流剧复用）。

---

---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/episodes/ep01/
  - ai_videos/wushen_juexing/episodes/ep02/
  - ai_videos/wushen_juexing/world.md
  - final_specs/spec.md
severity: high
---

# Follow-up draft 027 — 2026-06-15（监制大改）

用户以「监制 skill」(ai_video__dialogue_master) 身份审 EP1 剧情/台词/运镜连贯性并大改。

## 抽象后的指令
1. EP1 剧情/台词/运镜不够连贯——重排、按因果衔接。
2. **系统早现**：开场不久系统就出来，给男主二选一【苟活 / 硬刚】；选【硬刚】即**激活武神觉醒系统**。
3. **和系统对话太少**——全程增加主角↔系统来回（监制 P4）。
4. 可增 shot 做铺垫，或移部分到 EP2。

## 落地
- world.md §四：系统机制改为「早现 + 苟活/硬刚二选一、选硬刚激活；断绝走出再领武神躯大礼」。
- EP1 re-cut 为 14 镜/~90s：穿越→至暗→**系统早现二选一**→选硬刚激活→有底气硬刚对峙(系统撑腰)→回忆铺垫→决心断绝(hook)。
- EP2（溢出段 7 镜/44s）：断绝走出→系统送大礼武神躯觉醒→震惊→宣言→凌虚子末镜。
- spec FR-7/FR-7b、arc_outline EP1/EP2、各 publish 同步。

## ⚠ 事故记录（render 数据丢失）
执行 re-cut 时，归档命令对含空格的渲染文件名 word-split 失败、`mv` 静默未移动，随后 `rm -rf shots` 把仍在 `renders/` 内的 **17 个用户渲染 mp4 一并删除**（gitignored、不在回收站、不可恢复）。**唯一幸存：`episodes/ep01/ep01.mp4`（91s 全集合成片，含全部已渲染镜头画面）。** 教训：删除前必须用 `find -print0 | xargs -0` / 逐文件确认归档成功再删；已在复盘中记录。

---

---
target_stage: 6
target_artifacts: [ai_videos/wushen_juexing/episodes/ep01/, scenes/s1_裴王府正厅/]
severity: medium
---
# Follow-up draft 028 — 2026-06-15（监制/台词大师审）
1. 台词连贯性：EP1 S07 主角"打断我的腿？来啊"在裴霆威胁(原S08)之前出现=突兀。修：S07=裴霆先出威胁、S08=主角回怼+系统撑腰（因果顺序）。
2. shot prompt 细节/走位：shot2 生成视频主角背对王爷=错。修：锁定主角面朝北(朝向裴霆)、切忌背对；正反打约定(裴霆向bg1_朝北/主角脸向bg3_朝南)。shot14 误把裴霆置于南门=错，修回北端高座。同类问题全查。
3. shot1 吐血突兀 → 去掉，改胸口剧痛闷哼撑地。
落地：shot01(去血)/shot02(锁朝向)/shot07+08(因果互换)/shot14(裴霆归位)；s1 场景加「站位锚/朝向约定」；script/dialogue/shotlist 同步。

---

---
target_stage: 4
target_artifacts: [ai_videos/wushen_juexing/arc_outline.md]
severity: medium
---
# Follow-up draft 029 — 2026-06-15
用户要 1–80 集每集一句话大纲；给定必要情节：测资质石(测试好/超过弟弟/各大宗门疯抢)→选落魄剑宗→宗门内速成剑修(超越前辈)→跟师姐出去历练。其余自行补全。暂不生成 ep/shot。
落地：arc_outline.md §分集一行大纲 重写为完整 EP1–80 每集一句；必要情节锚 EP6–8(测资质石超弟/疯抢)/EP9(选落魄太虚剑宗)/EP11–13(速成超前辈)/EP15–16+(随师姐历练)；对齐既有 canon(凌虚子/苏清歌/大比除名/王体/妖族/沈婉在世)。三幕拍点表同步。

---

---
target_stage: 6
target_artifacts: [episodes/ep02/, world.md, final_specs/spec.md, arc_outline.md]
severity: high
---
# Follow-up draft 030 — 2026-06-15
EP2 还看不出武神觉醒——藏锋不显、留到后面"众人才发现"做大钩子。落地：world §三/§四 武神躯 EP2 系统私下暗授、潜伏不显、众人看不出；公开显化("送大礼"仪式+暖金裂纹+降维碾压)移到后续 reveal(arc EP25 武神躯·众人才发现)。EP2 re-cut 6 镜/38s：断绝走出→系统暗授(仅主角可见对话框+内敛微表情)→众人当废物嗤笑→离场宣言(反讽)→凌虚子隐隐生疑不识破。删觉醒态、无暖金裂纹/光门/满堂震惊。spec FR-7b/体质轴同步。

---

---
target_stage: 6
target_artifacts: [characters/c6_云清越/, world.md, arc_outline.md]
severity: medium
---
# Follow-up draft 031 — 2026-06-15
师姐换名 苏清歌→云清越；性格正直但**起初不信主角实力、小看他**(被"短命"误判+废物出身带偏)，被一次次打脸方改观(成长弧)。落地：全 canon 文件 苏清歌→云清越(含 c6 folder+file 改名)；c6 bible 角色定位/性格/台词/弧光 重写为"正直却初期小看→打脸改观"；world/arc 同步。

---

---
target_stage: 4
target_artifacts: [world.md, arc_outline.md, characters/c4_凌虚子/, characters/c6_云清越/]
severity: medium
---
# Follow-up draft 032 — 2026-06-15
测资质石碑出箴言：先赞主角天赋，中段埋钩"此等天赋必伴大磨难、寿元不长"，箴言出到一半石碑就碎、最后一句(揭示他乃命定武神、磨难莫须有)没显露。之后师傅师姐众人都以为主角过 X 天就死，虽功夫长进快、众人态度反复横跳(小人嘴脸)，后发现没死=好钩；唯系统知他本是命定武神、"短命"纯属莫须有。落地：world §一 新增"测资质石碑·箴言短命大钩子"；arc EP7(石碑双钩)/EP8(疯抢+短命摇摆)/EP10-13(短命致众人反复)/EP23(死期没死打脸)；c4/c6 bible 加"信他短命"。

---

---
target_stage: 6
target_artifacts: [episodes/ep01/shots/, episodes/ep02/shots/, .claude/agent_refs/project/ai_video.md, style_guide.md]
severity: medium
---
# Follow-up draft 033 — 2026-06-15
每个 shot 视频不显示字幕——从视频 prompt 去掉所有字幕相关信息、保留台词(作口型/配音)，用户后期自加字幕。落地：EP1/EP2 全 shot 台词字段删"内嵌硬字幕/硬字幕/白底黑边"、渲染样式加"画面不烧任何字幕文字(台词后期另加)"；"下一集"卡改黑屏转场后期叠字；系统对话框(画面 UI)保留。规则进 ai_video.md + style_guide §六。

---

---
target_stage: 6
target_artifacts: [episodes/ep01/shots/, episodes/ep02/shots/, .claude/agent_refs/project/ai_video.md]
severity: medium
---
# Follow-up draft 034 — 2026-06-15
shot4 台词排版导致 Kling 混乱（多说话人挤一行 + "..." 内嵌 『』「」 引号 + 注释混在台词里）。改用更好的 structure。落地：所有 shot 视频块 `台词:` 改为——首行说明（画面不显示文字、仅供口型/配音；逐条↓），随后每个发声单元各占一行 `· {说话人}〔{类型·口型}〕：{纯文本台词}`；正文不加任何引号、不嵌套；系统名直写（去『』）。规则进 ai_video.md (#034) + recut 模板。

---

---
target_stage: 6
target_artifacts: [episodes/ep01/shots/shot04-06, world.md, arc_outline.md, final_specs/spec.md]
severity: medium
---
# Follow-up draft 035 — 2026-06-15
完善系统出场与主角对话：系统须解释两个选择的结果——【继续苟活】(当一辈子任人践踏的废物) vs 【觉醒武神】(反抗到底、觉醒武神之力逆天改命)；选觉醒武神→激活系统。另：shot prompt 要简单清晰，否则 Seedance confuse。
落地：shot04(系统出场·绑定自报)/shot05(二选一·系统解释两条路结果)/shot06(选觉醒武神·激活金光内敛) 重写——台词解释结果、视觉字段精简短句；二选一标签 苟活/硬刚 → 继续苟活/觉醒武神（硬刚保留为态度词）；world §四 / shotlist / script / dialogue / shot13 / spec FR-7 / arc 同步。prompt 字段普遍缩短(情节/走位/动作 简洁短句)以适配 Seedance。

---

# Follow-up draft 036 — 2026-06-15
EP1 S03 去掉两个具体动作：弟弟「抬脚踩兄长肩头」、母亲「搂/拢幼子」。

---
target_stage: 6
target_artifacts:
  - episodes/ep01/shots/shot03/shot03.md
  - episodes/ep01/script.md
  - episodes/ep01/dialogue.md
  - episodes/ep01/shotlist.md
severity: low
---

## 指令
EP1 第 3 镜（弟弟讥讽 + 母亲偏袒）中删除两个肢体动作：

1. 裴昭**不要把脚踩到主角肩上**——改为走到跪着的兄长面前、居高临下俯睨、折扇敲掌心的冷笑，讥讽态度与信息量不变。
2. 沈婉**不要有搂/拢幼子的动作**——改为侧身而立、别眼偏袒，台词与「偏爱幼子」的人物底色不变（仅去掉当场抱孩子的物理动作）。

注：沈婉「偏爱幼子裴昭」是人物性格/关系设定，保留；仅移除 S03 当场的肢体动作。

---

# Follow-up draft 037 — 2026-06-15
EP1 shot05：Seedance 反复「读台词乱套」——全员无口型镜的 `视频 prompt` 不应再写台词全文。

---
target_stage: 6
target_artifacts:
  - episodes/ep01/shots/shot05/shot05.md
severity: low
---

## 指令
shot05 是「系统二选一」镜，两个发声单元都不对口型（系统=画外提示音、裴知秋=内心独白），无任何在画人物开口。Seedance 却把 `视频 prompt` 的 `台词:` 全文当语音去生成、反复乱套。

修正：全员无口型镜的 `台词:` 字段**不写台词全文**——只声明「无人开口、嘴唇不动、勿生成任何配音/语音/口型；台词后期 TTS 另配」，逐行标说话人 + 类型(画外/OS)·不对口型，并保留系统流对话框在画 UI 字（选项按钮【继续苟活】【觉醒武神】）。台词全文只留在 `## 台词配音 prompt` 块。

此为通用规律（非只 shot05）：已写入 `.claude/agent_refs/project/ai_video.md` —— 「全员无口型镜：`台词:` 不写台词全文」。混排镜（含 ≥1 句在画对白）不剥离，仍写正文供 lip-sync。

---

# Follow-up draft 038 — 2026-06-15
EP1 全镜台词朝向/眼神排查 + 全员无口型镜台词剥离（监制 skill 升级后全量复审）。

---
target_stage: 6
target_artifacts:
  - episodes/ep01/shots/*
severity: low
---

## 指令
shot03 弟弟与母亲说台词时面朝方向不对、像「对着空气说」。引申：说台词时的朝向/角度、人物间彼此朝向很重要，须在 prompt 写死。

监制 skill（`.claude/skills/ai_video__dialogue_master/SKILL.md`）已升级：新增「朝向/眼神/走位审查 C1–C4」（说话人朝向写死 / 对谁说=视线落点 / 人物相对位置+互相朝向 / OS·内心独白的朝向），并把上一轮的「全员无口型镜不写台词全文」收进硬约束；同时修正 skill 内过时约束（`台词 / 字幕:`→`台词:`、撤销 v1 不下发 TTS）。

用升级后的 skill 全量复审 EP1 14 镜并落地修复：
- **全员无口型镜剥离台词正文**（防 Seedance 误读）：shot01/04/05/06/13。
- **在画对白补朝向/眼神**（谁面向谁、视线落点写进台词 tag + 走位/动作）：shot02/03/07/08/09/10/11/12/14。

---

# Follow-up draft 039 — 2026-06-15
全员无口型镜不可剥离台词正文（修订 037）——shot05 剥离后视频完全没台词声音。

---
target_stage: 6
target_artifacts: [episodes/ep01/shots/shot01, shot04, shot05, shot06, shot13]
severity: medium
---

## 指令
037 规定"全员无口型镜不写台词全文"实测错误：视频模型(Seedance)从 `台词:` 文本生成配音，删正文=成片无台词声音。修正：任何镜都保留台词正文；全员无口型镜防"读台词乱套"改用**强标 `画外配音 voice-over` + `嘴唇不动不对口型` + 系统句 `无任何在画人物对此口型/嘴动`**（先前乱套真因=画外音被 lip-sync 到在画脸上），而非删文。已恢复 shot01/04/05/06/13 台词正文 + VO 标注；ai_video.md「全员无口型镜」规则与监制 skill 硬约束同步修订。

---

# Follow-up draft 040 — 2026-06-15
镜头时长须容得下台词（语速别飙）+ 上限 15 秒。

---
target_stage: 6
target_artifacts: [episodes/ep01/shots/*, episodes/ep01/shotlist.md, final_specs/spec.md]
severity: medium
---

## 指令
shot09 等镜时长太短、台词念不完、语速飙。规则：一镜总台词字数÷时长 ≤5 字/秒（目标~4），超标则①加时长(硬上限15秒)②精简台词③拆镜；改后 `时长:`/`Duration`/各句 `时长目标`/`动作`时间窗 同步。
EP1 全镜重配：S01 6→7、S04 6→10、S05 7→15(+精简)、S08 7→13(+精简)、S09 7→15(+精简)、S10 5→6、S12 6→11、S13 6→13；总时长 ~90s→~132s（单镜仍≤15s）。shotlist/spec 同步。监制 skill 新增「时长/台词节奏审查」。

---

# Follow-up draft 041 — 2026-06-15
主角眼里闪的红光有点假。

---
target_stage: 6
target_artifacts: [episodes/ep01/shots/shot01, shot04, shot06, shot13, episodes/ep01/script.md, shotlist.md]
severity: low
---

## 指令
prompt 写的是金光，但模型把"瞳泛金/瞳心泛金"眼内光斑渲染成假红光。修正：删掉一切眼内发光（瞳泛金等），能量入体改"额心/眉心一缕微光内敛"，眼神变化全靠表演；相关镜 `光线` 末尾加"眼睛里不加任何发光特效/有色光斑（不要红光、不要瞳孔发光）"。shot04/06/13/script/shotlist 已改。监制 skill + ai_video 同步成规则。

---

# Follow-up draft 042 — 2026-06-15
shot08 系统台词前半段没声音；主角念台词慢了点。用户决策：系统读完整台词（option B）。

---
target_stage: 6
target_artifacts: [episodes/ep01/shots/shot08, shot04, shot05, shot06, shot13]
severity: medium
---

## 指令
系统(鎏金对话框)全剧统一：**保留配音、读完整台词**。系统语音由该 shot `台词配音` 块用锁定 voice_id 独立 TTS 生成、后期 mux，`时长目标` 配足整句（防前半段没声音）；视频 prompt 系统句标 `画外配音 voice-over·无任何在画人物对此口型`（系统音来自 TTS 轨、不靠视频模型自动读，模型自动读会断读）。系统文字仍作在画对话框 UI 字。shot08 同时提速：15s→13s、主角时长目标 9→8s。

---

# Follow-up draft 043 — 2026-06-15
台词朝向细化：shot9 主角背对弟弟、shot10 嘴动/眼神乱/两人太近/运镜局促、shot3 出现两个主角。

---
target_stage: 6
target_artifacts: [episodes/ep01/shots/shot03, shot09, shot10]
severity: medium
---

## 指令
- shot09：主角说台词时转头背对了弟弟（"偏头"被模型理解成转背）。改"转身正脸朝向东侧的裴昭、与他面对面、绝不背对"。监制 skill C2 加"慎用偏头"。
- shot10：①主角内心独白嘴却动了→强标"双唇全程紧闭绝不动嘴、本镜只有沈婉嘴动"；②主角眼神不知朝哪→写死"目光失神垂落身前地面、不乱飘"；③两人太近→拉开一臂以上间距、镜头分别给到二人不挤一框；④运镜局促→由锁机位改"缓推+横移、自沈婉移到主角"。
- shot03：同一沉默角色(裴知秋)被多处具名+多位置短语→模型渲染成两个。改为只在走位具名一次、其余用"他/兄长"，走位首句加"全画面共三人各一名互不重复"。监制 skill 加防角色重复 C5。

---

# Follow-up draft 044 — 2026-06-15
shot14 台词"这废物也不稀罕"很怪，应作"我也不稀罕"；监制 skill 持续优化台词。

---
target_stage: 6
target_artifacts: [episodes/ep01/shots/shot14, episodes/ep01/dialogue.md, script.md, shotlist.md]
severity: low
---

## 指令
说自己别用第三人称自指。shot14 "正好——这废物，也不稀罕"→"正好——我也不稀罕"（4 处同步）。监制 skill D1 加"自指用「我」"。

---

# Follow-up draft 045 — 2026-06-15
shot12 分不清回忆还是现实；回忆应换画面色彩突出。

---
target_stage: 6
target_artifacts: [episodes/ep01/shots/shot11, shot12]
severity: low
---

## 指令
回忆镜须一眼可辨、明显区别于当下：`情节` 首段标 `【回忆·时间·事件】`，`光线` 用强回忆滤镜（做旧泛黄+低饱和暖褐+四角暗角晕影+轻微胶片颗粒+柔光朦胧+边缘微虚），`渲染样式` 加"回忆段做旧泛黄胶片质感（区别于当下）"。shot11/12 已改。监制 skill 加规则。

---

# Follow-up draft 046 — 2026-06-15
shot12 两个王爷 + 主角/弟弟面朝向；shot11 回忆色彩对齐 shot12；监制 skill 加跨镜运镜连贯审查，review 全部 shot 运镜流畅性。

---
target_stage: 6
target_artifacts: [episodes/ep01/shots/shot03, shot10, shot11, shot12]
severity: medium
---

## 指令
- shot12 出现两个镇北王（一站一坐）：同一角色多处具名致重复。改"镇北王裴霆全画面只有一人、始终端坐高座、绝不再出现站着的王爷"+走位"共三人各一名互不重复"。
- shot12 主角与弟弟面朝向：裴昭改"转身正脸朝向中轴的裴知秋、面对面讥讽（不背对）"。
- shot11 回忆色彩对齐 shot12（强回忆滤镜：做旧泛黄+暗角+颗粒+柔光+边缘虚），已统一。
- 监制 skill 新增**运镜连贯性审查（跨镜 M1–M6）**：轴线一致(180°)/视线匹配/景别节奏/运动顺承/站位进出画一致/同角色唯一。
- 全镜 review 结论：当下正厅 N–S 对峙轴(S02/07/08/14)一致、系统镜(S04–06)一致、重复人物已修。修复一处**站位不连贯**：沈婉 S03 在东、S10 却在西(bg4_朝西)——统一为**裴昭+沈婉同在东侧(家人一侧，全剧固定)**，主角居中、S09→S10 主角持续朝东，更连贯；S10 改 bg2_朝东_东列长案、S03 裴昭改自东侧越众。

---

# Follow-up draft 047 — 2026-06-16
shot11 弟弟被袭呆站如木头人不合常理；shot12 父亲端坐正对台下宣判不合情景（应背对二子说）；熊武城改名。

---
target_stage: 6
target_artifacts: [episodes/ep01/shots/shot11, shot12, episodes/ep01/script.md, world.md, arc_outline.md, final_specs/spec.md]
severity: medium
---

## 指令
- **shot11**：黑衣人来袭，年少裴昭全程呆站如木头人→不合常理。重排：裴昭吓得瞳孔骤缩、惊呼、踉跄后退；裴知秋扑身**一把推开**弟弟、横身硬挡一掌；裴昭被推到身后跌坐惊惧、毫发无伤。小说原文/情节/走位/动作/Summary 同步。
- **shot12**：镇北王端坐高座正对台下宣判逐令，不合情景→改**背对两个儿子、负手而立、头也不回**地撂下逐令（凉薄）；背身故不强求口型、末尾仅微侧冷峻侧脸。保留"全画面只一个王爷"。小说原文/情节/走位/动作/镜头/台词/Summary + script.md 场景四 同步。
- **地名改名**：熊武城 → **蛮荒城**（流放/自生自灭之地），canon 全量替换（world/arc/spec/script/dialogue/shotlist/shot12/scenes/s2_回忆书房；audit log 与历史 follow-up 保留原名作记录）。
- 监制 skill 新增 P7「表演/走位合常理」：配角对事件须有合理反应（不呆站）、权势者姿态贴情绪（凉薄可背身）。

---

# Follow-up draft 048 — 2026-06-16
为 EP1 全部 14 个 shot 生成双语字幕文件（中文+英文）。

---
target_stage: 6
target_artifacts: [episodes/ep01/shots/*/subtitles.md]
severity: low
---

## 指令
每个 `episodes/ep01/shots/shot{NN}/subtitles.md` 写入双语台词时间轴：每行 `起-止(秒) 中文 || English`，时间窗源自各句台词配音 `时长目标`。中文取自各 shot `## 台词配音` 块，英文为对应翻译（蛮荒城→Manhuang City、镇北王府→Zhenbei Manor）。配合 ai_video_management webapp 的「💬中文 / 💬EN / 💬中英」三按钮可分别烧出对应语言成片。规则见 ai_video.md rule 11c（双语格式）。

---

# Follow-up draft 049 — 2026-06-16
确保 EP2 开场与 EP1 结尾连贯（消除"气场反转"重演的突兀），并把"改动剧本/台词后默认自检连贯性"写进标准流程。

---
target_stage: 6
target_artifacts:
  - episodes/ep02/shots/shot01/shot01.md
  - episodes/ep02/script.md
severity: medium
---

## 指令
- **跨集边界连贯**：EP1 末镜（S14）已让裴知秋"撑直佝偻脊背、气场由颓转锋、撂下'我也不稀罕'"。EP2 开场（shot01 / script 场景一）不得重演这一"撑身气场反转"beat——改为承接 EP1 已反转的状态：脊背已挺直、气场未散，直接续上"把话彻底说绝"。小说原文/Summary/情节/动作/script 场景一同步。
- 顺带把该镜标志断绝台词白话化并全局 byte-identical 同步（"用不着你赶。我裴知秋今天把话撂在这儿——从今往后，我跟镇北王府恩断义绝，这扇门，我自己走出去！"）。
- **流程通则（common-level，已写入 harness）**：每次改动剧本/台词（script.md / dialogue.md / shot `台词:` / 镜头剧情）后，**默认自动**自检叙事连贯性，无需用户提醒——查相邻镜衔接 + 跨集边界（首/末镜对照上一集结尾/下一集开场），前集已发生的关键转折不重演只承接。已落地 CLAUDE.md「General coding rules」+ ai_video.md「2026-06-16 amendment」。

---

# Follow-up draft 050 — 2026-06-16
消除 EP1 S14 ↔ EP2 S01 的重复「与家族决裂」宣告（EP2 起始重复/突兀）；并要求建立"全剧所有 EP 台词+剧情统一 review"的流程。

---
target_stage: 6
target_artifacts:
  - episodes/ep02/shots/shot01/shot01.md
  - episodes/ep02/script.md
  - episodes/ep02/dialogue.md
  - episodes/ep02/shotlist.md
severity: medium
---

## 指令
- **问题**：EP1 S14 已让主角撂下"镇北王府容不下废物？正好——我也不稀罕"（口头决裂 + 升镜黑屏，观感像已离场）；EP2 S01 又来一段更长的决裂宣告"用不着你赶…恩断义绝，这扇门我自己走出去！"——两段决裂宣告叠在跨集边界上，S01/S02 读起来像在重启已经结束的戏（"你不是已经走了么"）。
- **决策（用户选定·只改 EP2、不动已出片的 EP1）**：EP1 不变（"我也不稀罕"即口头决裂）。**EP2 S01 去掉重复宣告**，改为承接上集的**沉默转身离场（默剧·无台词）**——垂眼、不再多言、转身走向逆光朱门。决裂之言留在 EP1 末句，离场宣言只保留 S05「今天赶我走的人，将来都得仰起头来看我」。EP2 少一个名场面台词但叙事最顺、不重复。
- 同步：shot01（小说原文/Summary/情节/走位/动作/台词/节奏，删 台词配音 块改默剧）、script.md 场景一、dialogue.md（S01 改默剧注）、shotlist.md（S01 行 + 标记 改"沉默离场·承接上集"）、characters/c1_裴知秋 标志台词（去 orphan 的"用不着你赶…"、换 EP1 实际签名句"我也不稀罕"）。

## 流程要求（common-level）
用户指出：单纯"相邻镜 + 边界"自检不足以发现"整段开场重复上一集已结束的戏"。需要一个**全剧统一 review 流程**——把所有 EP 的台词与剧情（至少每集开场/结尾 beat + 标志台词）当成一条序列通读，专查：跨集重复 beat/重复宣告、冗余开场、矛盾、标志台词复用、爽点升级一致性。已落地 CLAUDE.md「Narrative-edit coherence check」扩条 + ai_video.md「2026-06-16 amendment」§全剧序列 review。

---

# Follow-up draft 051 — 2026-06-16
EP2 全删重写（修复重复+矛盾的根因）：① EP1 只激活系统、未给武神躯；EP2 S03 之前在"再次恭喜武神躯"= 重复 EP1。② 角色档把 EP1 写成"当场公开觉醒武神躯+暖金裂纹+光柱"——与已出片 EP1（只激活系统、藏锋）和 arc（武神躯=EP2 暗授藏锋、威能留 EP25）矛盾。用户决定：全删 ep02/ 从头重写；武神躯留 EP2 但重新设计为"断绝后兑现的大礼"、不重复。

---
target_stage: 6
target_artifacts:
  - episodes/ep02/**
  - characters/c1_裴知秋/c1_裴知秋.md
severity: high
---

## 指令（用户两项决策）
1. **全删 ep02/ 从头重写**（scope=episode 2 regen）：删除 episodes/ep02 全部 markdown（script/dialogue/shotlist/publish + 14 个 shotNN.md），**保留 renders/ 已渲染 mp4**（S01/S02/S03 已出片、不销毁用户资产；新 spec 与旧 render 不符、需用户重渲染）。保留 characters/world/style_guide/arc/EP1。按 arc_outline 第 25 行 EP2 定义重写一份内部连贯、不重复 EP1、走位逻辑干净的 EP2。
2. **武神躯 = EP2 兑现的"首份大礼"、重新设计不重复**：EP1（已出片·canon）只激活武神觉醒系统、未给武神躯，末镜系统设钩"断绝即领首份大礼"。EP2 S03 = 兑现该钩（【断绝】达成→武神躯**注入识海/筋骨**、藏锋、众人看不出），**措辞与视觉都区别于 EP1 的"绑定/二选一/激活/金光入眉心"**；S09 系统改"前路指引"。藏锋契约：全集无武神躯威能显化、威能留 EP25。
3. **修正过时角色档**：c1_裴知秋 弧光/标志能力表/角色定位把"EP1 当场觉醒王体+武神躯·暖金裂纹·九道光柱·镇国虚影"改正为：EP1=系统激活（无公开异象）、EP2=武神躯暗授藏锋（无体外异象）、EP25+=威能显化（暖金裂纹/光柱/虚影留此）。

## 流程教训（common-level，已落地）
"每次只改一点点"治标不治本——当一集整体充满重复/矛盾且与上集 canon 冲突时，应**全删该集从头重写**（regen 契约 scope=episode N），而非无尽 surgical。且重写前必须先核对**跨集 canon 真值源**（已出片的前集 actual 内容 > 过时的角色档/arc 文字），把过时档案一并改正。已强化 ai_video.md §全剧序列 review + CLAUDE.md。

---

# Follow-up draft 052 — 2026-06-16
EP2 从零重写（再次）：上一轮 regen 只是复刻了旧 spine，前三镜跟之前没区别、仍在重踏 EP1 的"大厅+弟弟+系统框"。用户要求：把 EP2 所有信息（shot + dialogue.md + script.md 等）统统删干净、清除所有 memory、先从零重写小说原文，再据此重写剧情和台词，再重新生成 shot。

---
target_stage: 6
target_artifacts:
  - episodes/ep02/**
severity: high
---

## 指令
1. **全删 ep02/ 所有 markdown**（source/script/dialogue/shotlist/publish + 全部 shotNN.md），**read-zero 不沿用旧 EP2 任何文字**（"清除 memory"=不带入旧结构；本仓无 auto-memory 存储）。保留已渲染 renders/*.mp4（S01–03·不销毁用户资产、待用户重渲染）。
2. **先写小说原文**：新建 `episodes/ep02/source_novel.md`（第二章原文）作为 EP2 派生源——采用「走出去」forward 结构：开篇主角已**转身迈步走出**、把"断绝"用脚步执行掉，**不回大厅静站对峙、不重演 EP1 的大厅/弟弟/系统框**；武神躯大礼在他走出去的过程中**边走边领**（不停步、藏锋、无静态系统框镜）；大厅压到最短，篇幅让给离府/赶路/系统初引/玉佩/城门钩等 EP2 自有新内容。
3. **据原文重写剧情+台词**：script.md（剧情）、dialogue.md（台词）从 source_novel.md 派生。
4. **重新生成 shot**：shotlist.md（14 镜/89s）+ 14 个 shotNN.md（14 个 stage-6 worker 并行、parent 锁 spine + WORKER_CONTEXT 后 fan-out）。
5. 藏锋契约（全集无武神躯威能显化、威能留 EP25）、台词 v2、走位连续律、不重复 EP1 全部沿用。

## 流程教训（common-level）
"regen 复刻旧 spine"是坑：当用户要"从头重写"且问题在结构本身时，**必须从 source（小说原文）层重写、read-zero**，而不是拿旧 script/shotlist 当 spine 复刻。已强化：top-down 重写应从 `source_novel.md` 起，剧情/台词/分镜逐层派生。

---

# Follow-up draft 053 — 2026-06-16
EP2 台词/情节大师全量 review + 修：① shot2 系统台词"潜伏待显"太文绉绉、换通俗；② 全集台词/情节流畅性 review（含语速节奏）；③ 所有 shot 的 `参考:`/`场景:`/`Reference uploads:` 必须精确 match 角色 id/name 与场景 id/bg name（用户发现多处不精确）。

---
target_stage: 6
target_artifacts:
  - episodes/ep02/shots/*/shot*.md
  - episodes/ep02/{script.md, dialogue.md, source_novel.md, shotlist.md}
severity: medium
---

## 指令
1. **"潜伏待显"通俗化**：S02 系统台词 `首份大礼【武神躯】——发放中，潜伏待显` → `断绝达成。首份大礼【武神躯】，已注入宿主体内。`（"潜伏/暗藏不显"之意改由裴知秋内心"先沉到骨子里——这些人还不配看见"承载）。全项目零"潜伏待显"残留。
2. **全集台词流畅性 + 语速节奏 review**（ai_video__dialogue_master）：发现并修以下"念不完/语速飙"（字数÷时长>5字/秒）：
   - S02 系统(38字/4s≈9.5字/s)+内心(27/3s) → 精简为系统(20字)+内心(18字)、Duration 7→8s、各句时长目标 4+4。
   - S03 名场面宣言(~44字/7s≈6.3字/s，太赶) → Duration 7→9s、宣言去"堂堂正正地"略精简(~43字/9s≈4.8字/s)、时长目标 9s；签名句"今天赶我走的人，将来都得仰起头来看我"byte-identical 保留。
   - S08 系统(44字/4s≈11字/s)+内心(24/2s) → 去文绉绉("脱离桎梏/淬炼己身/前路机缘自有指引")改白话"宿主已脱身。武神躯初成、根基未稳，先找个清静地方好好修炼"；内心精简"也好。这身子，我自己一寸寸夺回来"；Duration 6→8s、时长目标 5+3。
   - S01 裴昭赌约(35字)动作窗仅 2.5s(≈14字/s) → 动作改为裴昭 1.5–8s 全程嗤笑立赌、时长目标 8→7s(5字/s)。
   情节链(P1–P7)/朝向走位(C1–C5,M1–M6)复核通过：走出去 forward 连续位移、转身只 S01 一次、系统 beat 跨集功能各异、藏锋一致、黑影仅剪影。
3. **参考精确匹配 id/name**（全 14 shot 的 `参考:`/`场景:`/`Reference uploads:`/`Scene:`）：角色用精确名（裴知秋/裴昭/凌虚子，去"turntable.mp4"/"c1_前缀"杂串）；场景/bg 用各 scene 档真实 bg 名（不再用 `s6_王府外长街`/`s7_镇北城门`/`bg s6_…`/"inline bg"/`s1_正厅` 这类非 bg/错名）。逐镜 bg 按各 scene 档"出片选 plate"指引锁定：
   - S01 bg5_中_中轴俯瞰+bg2_朝东_东列长案；S02 bg5+bg3_朝南_厅门逆光；S03 bg3_朝南_厅门逆光（scene s1_裴王府正厅）。
   - S04 s5_王府外高地/bg1_远眺王府（去"inline bg"）。
   - S05/S06 bg1_府门石阶；S07 bg2_长街主向；S08/S09/S10 bg3_街心华灯；S11 bg4_长街远景城道（归 s6_王府外长街·城门在望，非 s7）（scene s6_王府外长街）。
   - S12 bg1_城门洞主向；S13 bg2_城楼飞檐；S14 bg3_门洞幽暗内（scene s7_镇北城门）。
   时长合计 89→94s（S02/S03/S08 加时；14 镜不变）。

## 流程教训（common-level）
shot worker 产出的 `参考:` 易出现"角色名+turntable.mp4""scene-id 当 bg""inline bg"等不精确串；台词易超 5 字/秒念不完。已知应在 WORKER_CONTEXT/校验环节强制：参考字段=精确角色名 + scene 档真实 bg 名；每句台词字数÷时长目标≤5 且各句时长目标之和≤shot 时长。

---

# Follow-up draft 054 — 2026-06-17
EP2 shot1：弟弟裴昭说话时背对着远去的哥哥，不合理。修 shot1，并优化流程（为什么 review 漏了）。

---
target_stage: 6
target_artifacts:
  - episodes/ep02/shots/shot01/shot01.md
severity: medium
---

## 根因
裴知秋朝南门离去（背影远去），裴昭在东列长案。原 prompt 走位写"面朝兄长背影"（意图对），但叠加"身体半侧 / 过肩奚落"+ 机位"横摇带向裴昭中景"——模型把裴昭渲染成正面朝镜头、背对着远去的哥哥（对空气说话）。属"偏头→背对"陷阱的同族。

## review 为何漏（流程缺口）
ai_video__dialogue_master 的 C2 只禁了"偏头"、且 review 只核"朝向有没有写"——没把"过肩 / 半侧"列为同族危险写法，也没有"对正在离去 / 背对的对象说话"这一几何 + 机位（说话人正面朝镜头而对象在身后）的专项检查。

## 指令
1. 修 shot1：裴昭"啪"合扇后**整个人转身、正面朝向兄长离去的方向（朝南）、目光锁其远去背影**提声立赌；机位改侧方、同框二人朝向一致、**绝不让裴昭正面朝镜头而主角在其身后**；去"过肩 / 身体半侧 / 斜睨背影"等易致背对写法。镜头/走位/动作/台词朝向 tag/Summary/标题/节奏/情绪 + shotlist + script 全部同步。
2. 优化流程（common-level）：
   - ai_video__dialogue_master skill **C2** 增"对正在离去 / 背对的对象说话"专项：禁"过肩 / 侧身 / 半侧奚落"，写"说话人整个人转身正面朝其离去方向、目光锁其背影"，机位用侧方 / 反打使朝向一致、绝不正面朝镜头而对象在身后（shot01 教训）。
   - ai_video.md §2026-06-16 amendment item 1 同步加"说话人朝向必须对着所说对象（含离去 / 背对对象）"通用约束。

---

# Follow-up 055 — 2026-06-17（台词/小说原文全白话 + review_suite 重跑 EP1/EP2）

## 指令
1. 台词、小说原文、prompt 正文一律白话文、禁古语/文言/对仗格言腔（仙侠题材亦然；系统播报也白话，保留系统流术语）。
2. 用九维审查 skill（review_suite）全量重跑 EP1 + EP2 并 surgical 修复。
3. 同角色全剧锁定同一 voice_id，权威源回填 casting.md。

## 已落地
白话化（何曾→哪、系统书面腔→口语、除其族籍→逐出族谱、以武神之身→成为武神 等）；EP1 起身/气场反转 beat 去重演（只反转一次）；EP2 shot03 离场宣言 9s→10s 补收尾 beat；系统 voice_id 统一 SYS-gold-01、裴昭统一 PZ-brat-01、casting.md 回填锁定。
（白话铁律 + 九维 skill + 默认跑 suite 已落公共面 ai_video.md/CLAUDE.md，后续 regen 自动套用。）

---

# Follow-up draft 055 — 2026-06-17
① EP2 shot2 内心台词"来了。先沉到骨子里"太突兀；② 要一个新文件：当前 EP 下所有 shot prompt 的集合。

---
target_stage: 6
target_artifacts:
  - episodes/ep02/shots/shot02/shot02.md
  - episodes/ep02/all_shot_prompts.md
severity: low
---

## 指令
1. **shot2 台词去突兀**（ai_video__dialogue_master·D5 情绪真实/D1 说人话）：系统刚告知"武神躯已注入体内"，主角反应却跳过"认出是什么"直接喊"先沉到骨子里"（命令式、跳 beat、像作者速记）。改为先认出再决定藏：`原来……这就是武神躯。先收着——这些人，还不配看见。`（18字/4s=4.5字/秒）。shot02 台词/情节/台词配音 + dialogue.md + script.md + source_novel.md + shotlist.md 六处同步。
2. **新文件 `episodes/ep02/all_shot_prompts.md`**：自动汇编全 14 镜的【视频 prompt】+【台词配音 prompt】代码块（含小标题 + 时长），复制即用；只读快照，改动改各 shot 源后重新汇编。

---

# Follow-up draft 056 — 2026-06-17
按用户《EP2 全镜优化方案》改 EP2 全 14 镜 prompt（台词去机器化/情节衔接/运镜影视化/节奏/表演拟人化），并把这些原则融入 skill。两处异议经用户裁定。

---
target_stage: 6
target_artifacts: [episodes/ep02/**, characters/c1_裴知秋, arc_outline.md, style_guide.md]
severity: medium
---

## 用户裁定的两处异议
1. **签名台词**：用户的新 S03 宣言替换全剧锁定签名句。裁定=**全剧换新宣言**。新签名（白话·byte-identical 锁定）：「总有一天，我会站上武神之位，让你们所有人都仰起头来看我」。已全量替换：ep02(script/dialogue/shotlist/shot03/source_novel/publish/all_shot_prompts) + characters/c1 标志台词&弧光 + arc_outline(EP71-80/EP2/EP75) + style_guide 改写示例。
2. **白话 vs 文言**：用户部分新台词偏文言。裁定=**全部白话化**。今日之辱→今天的屈辱；他日/登临武神之位/皆要仰视→站上武神之位/仰起头来看我；莫测道韵→说不清的气机；经脉尽损→丹田碎了(canon)。

## EP2 全 14 镜优化（14 worker 并行·parent 锁 spine+OPT_CONTEXT 后 fan-out）
- 台词去机器化+白话（S01 区区废物大放厥词 / S02 系统"绑定成功体魄重塑中"+裴知秋"百倍讨回" / S03 新白话宣言 / S04 凌虚子白话生疑 / S08 系统"僻静处稳固修为"+裴知秋"我说了算" / S10 玉佩白话）。
- 运镜影视化：S01 侧方动态分层(裴昭朝向统一)、S02 侧后跟移微推锁侧脸、S03 跟拍门前微滞推门外天光、S04 远景极速推脸、S07 低位跟拍拉长光影、S11 低位仰拍随孤影极缓抬升压迫、S13 上下分镜双区、S14 纵深极速推进黑屏卡点。
- 表演拟人化：微表情层次(S05 回望先怅然转决绝、S06 步伐虚浮渐沉稳、S09 自然突发诧异)。
- 藏锋：能量入体只内在感+眼底锋芒、无金光入眉心/裂纹/光柱(全集校验零真实泄露)；描述符 byte-identical(1 distinct)；台词 v2 零字幕 token；时长合计 95s(S03 10s)。
- 重生 all_shot_prompts.md 快照。

## 融入 skill（下次一次性过关）
- ai_video__camera_master：单镜审查加「影视化动态运镜铁律」（杜绝死板固定机位/呆板对称、微推拉/虚实/情绪特写/动态机位、远景极缓抬升/跟移贴步伐/双区分镜）。
- ai_video__action_master：加 A7「表演拟人化·情绪层次」（去机械完美走位、关键情绪给层次/转折）。
- ai_video__dialogue_master：D1 加「真人脱口而出·禁规整书面长句/念稿」。
