# AI-video specific validation levels — mozun_chongsheng

Run: mozun_chongsheng-20260509-164205
Stage: 5 / ai_video-specific levels (per agent_refs/validation/ai_video.md)
Mode: AUTONOMOUS

8 个 ai_video 强制 level，对应 agent_refs/validation/ai_video.md 第 1-8 条规则。

## Level 1: 语言合规

**Rule**: per agent_refs/validation/ai_video.md 规则 1
**Severity**: blocker

**Validator pseudo-code**:
```python
def validate_language_compliance(file_path: Path) -> ValidationResult:
    text = file_path.read_text(encoding='utf-8')
    # 剥离 code fence
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # 剥离 YAML frontmatter
    text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)
    # 剥离 URL
    text = re.sub(r'https?://\S+', '', text)
    # 剥离已知 proper nouns
    PROPER_NOUNS = {'Kling', 'Seedance', 'Seedream', '9:16', '4K', 'AI', 'Shorts', 'YouTube', 'shot01', ...}
    for word in PROPER_NOUNS:
        text = text.replace(word, '')
    # 计算汉字占比
    han_count = sum(1 for c in text if '一' <= c <= '鿿' or c in '，。！？；：（）「」『』、')
    total_count = sum(1 for c in text if c.strip())
    if total_count == 0:
        return ValidationResult(pass_=True)  # 空文件不计
    ratio = han_count / total_count
    return ValidationResult(pass_= ratio >= 0.95, message=f"中文比例 {ratio:.2%}")
```

**Apply to**: 所有 `ai_videos/mozun_chongsheng/**/*.md` 递归

## Level 2: 15-秒镜头原子性

**Rule**: per agent_refs/validation/ai_video.md 规则 2
**Severity**: blocker

**Validator**:
```python
def validate_shot_atomicity(shotlist_path: Path) -> ValidationResult:
    """解析 shotlist.md 的 GFM 表格，检查每行 时长 ≤ 15s"""
    issues = []
    table = parse_gfm_table(shotlist_path)
    for row in table.rows:
        if '时长' not in row:
            issues.append(f"row missing 时长: {row}")
            continue
        seconds = parse_seconds(row['时长'])  # 支持 "8s" / "10秒" / "9.5s" 等
        if seconds is None:
            issues.append(f"无法解析时长 '{row['时长']}'")
        elif seconds > 15:
            issues.append(f"shot {row['shot_id']} 时长 {seconds}s > 15s")
    return ValidationResult(pass_=not issues, issues=issues)
```

**Apply to**: 所有 `episodes/epNN/shotlist.md`

## Level 3: 角色一致性 (byte-identical lock descriptor)

**Rule**: per agent_refs/validation/ai_video.md 规则 3
**Severity**: blocker

**Validator**:
```python
def validate_character_consistency(episode_dir: Path, characters_dir: Path) -> ValidationResult:
    issues = []
    # 加载所有角色锁定句子
    locks = {}
    for char_md in characters_dir.glob('*.md'):
        text = char_md.read_text(encoding='utf-8')
        m = re.search(r'一句话锁定[^\n]*[:：][\s]*\[?([^\n\]]+)\]?', text)
        if m:
            locks[char_md.stem] = m.group(1).strip()
    # 检查 episode 内所有 shot prompt
    char_to_descriptors_in_ep = defaultdict(set)
    for prompt_md in (episode_dir / 'prompts').glob('shot*_kling.md'):
        text = prompt_md.read_text(encoding='utf-8')
        # 抽 "角色:" 行
        for line in text.split('\n'):
            m = re.match(r'\s*角色\s*[:：]\s*(.+)', line)
            if m:
                value = m.group(1).strip()
                # 找出引用的是哪个角色
                for role, lock in locks.items():
                    if lock[:20] in value:  # 头 20 字符匹配作为指认
                        char_to_descriptors_in_ep[role].add(value)
    # 同集内同角色不允许多版本
    for role, versions in char_to_descriptors_in_ep.items():
        if len(versions) > 1:
            issues.append(f"角色 {role} 在同集内出现 {len(versions)} 个不同描述符: {versions}")
        # 也检查与 characters/{role}.md 是否一致
        if locks[role] not in (next(iter(versions)) if versions else ''):
            issues.append(f"角色 {role} 在同集中的描述符与 characters/{role}.md 锁定句子不一致")
    return ValidationResult(pass_=not issues, issues=issues)
```

**Apply to**: 每个 episode 内的 prompts/* 与 characters/*.md 交叉检验

## Level 4: 双管线 + seam-frame 完整性

**Rule**: per agent_refs/validation/ai_video.md 规则 4
**Severity**: blocker

**Validator**:
```python
def validate_dual_prompt_seam_frame(episode_dir: Path, shot_count: int) -> ValidationResult:
    issues = []
    prompts_dir = episode_dir / 'prompts'
    for n in range(1, shot_count + 1):
        nn = f'{n:02d}'
        for suffix in ['_kling.md', '_seedance.md', '_lastframe_seedream.md']:
            f = prompts_dir / f'shot{nn}{suffix}'
            if not f.exists():
                issues.append(f"missing {f.name}")
    # 第一镜首帧
    if not (prompts_dir / 'shot01_startframe_seedream.md').exists():
        issues.append("missing shot01_startframe_seedream.md")
    return ValidationResult(pass_=not issues, issues=issues)
```

**Apply to**: 每个 `episodes/epNN/`

## Level 5: 比例 + Seedance 规避词字段

**Rule**: per agent_refs/validation/ai_video.md 规则 5 + spec NFR-6
**Severity**: blocker

**Validator**:
```python
def validate_ratio_and_avoidance(prompt_md: Path) -> ValidationResult:
    issues = []
    text = prompt_md.read_text(encoding='utf-8')
    # 比例字段必含
    if not re.search(r'比例\s*[:：]\s*9:16', text):
        issues.append("缺少 比例: 9:16 字段")
    # Seedance 必含 避免段
    if '_seedance' in prompt_md.name:
        if not re.search(r'^避免\s*[:：]', text, re.MULTILINE):
            issues.append("Seedance prompt 缺少 '避免:' 段")
    return ValidationResult(pass_=not issues, issues=issues)
```

**Apply to**: 所有 `episodes/epNN/prompts/shot*.md`

## Level 6: Publish 元数据完整

**Rule**: per agent_refs/validation/ai_video.md 规则 6
**Severity**: blocker

**Validator**:
```python
def validate_publish_md(publish_md: Path) -> ValidationResult:
    issues = []
    text = publish_md.read_text(encoding='utf-8')
    REQUIRED_SECTIONS = ['## 抖音', '## YouTube Shorts', '## 描述']
    for sec in REQUIRED_SECTIONS:
        if sec not in text:
            issues.append(f"缺少段 {sec}")
    # 抖音标题
    m = re.search(r'抖音标题[:：]\s*(.+)', text)
    if not m or len(m.group(1).strip()) > 25:
        issues.append("抖音标题缺失或超 25 字")
    # YouTube Shorts 双语
    m = re.search(r'YouTube Shorts\s+标题[:：]\s*(.+)', text)
    if not m or '《魔尊归来》' not in m.group(1) or 'Demon' not in m.group(1):
        issues.append("YouTube Shorts 标题缺失中英文")
    # hashtag 数量
    m = re.search(r'抖音\s+hashtag.*?[\[（](.*?)[\]）]', text, re.DOTALL)
    if m:
        tags = re.findall(r'#\S+', m.group(1))
        if not (5 <= len(tags) <= 10):
            issues.append(f"抖音 hashtag 数量 {len(tags)} 不在 [5, 10]")
    return ValidationResult(pass_=not issues, issues=issues)
```

**Apply to**: 每个 `episodes/epNN/publish.md`

## Level 7: 锁定文件 (Pinned items) 保留

**Rule**: per agent_refs/validation/ai_video.md 规则 7
**Severity**: skip in v1（无 promoted.md）

**Note**: 当前项目 stage 2-5 没有 pin 操作；本 level 在 v1 不触发。

## Level 8: 手动走查（人工签字）

**Rule**: per agent_refs/validation/ai_video.md 规则 8
**Severity**: manual_walkthrough

**触发条件**: stage 6 所有自动 level 全 pass 后

**自动 emit**:
```json
{"event": "validation.requires_manual_walkthrough", "task_id": "...", "work_unit_id": "{episode|project}", "prompt": "请打开 characters/ref_images/ 任意 2-3 份立绘 prompt 朗读 + episodes/ep01..ep05 任意一集 shotlist + 2-3 个 shot prompt，确认: (a) 角色描述跨 shot 一致；(b) 单集叙事连贯（钩 → 反转 → cliffhanger）；(c) 视觉风格符合 style_guide.md 锁定。"}
```

用户 chat 签字"通过"或具体反馈后，pipeline 关闭该 work unit。
