# 真實案例：60 秒沙漠菲律賓棍術（4 段 × 15s）

來源：GitHub [woodfantasy/Seedance2.0-ShotDesign-Skills](https://github.com/woodfantasy/Seedance2.0-ShotDesign-Skills) — `SKILL.md`

做法：整支 60 秒 = 4 段各 15s。**每段是一個獨立提示，在 Seedance 各生成一個 clip，最後按順序拼接**。每段開頭都重複同一行風格/氛圍描述（這是跨段連貫的關鍵），每段結尾畫面收束到穩定姿勢（站立→交織→旋風→收勢），方便無縫剪接。

段落銜接策略：
- 第1→2段：從孤立的起手式 → 爆發的近距離連續攻擊
- 第2→3段：能量峰值，加入旋轉與騰空打擊
- 第3→4段：逐漸減速進入冥想式收勢與遠景孤立

---

## 第 1 段 / 4 — 起手式（Seedance 設 15s）
```
Sunset desert Philippine Kali martial arts, cinematic realism, dark gold warm tones, desolate atmosphere.
Pervasive sand haze throughout, heat shimmer distorting distance, ochre texture every frame.
0-3s: Aerial drone descending, vast desert stretching to horizon, sunset painting dunes deep gold, solitary figure with dual rattan sticks standing in distance.
3-7s: Dolly tracking slow push to medium-wide, warrior crosses sticks at chest in opening salute, footsteps compress sand slightly, stick wood grain sharp in backlight.
7-11s: Side tracking shot, warrior steps forward, right stick diagonal strike meets left stick horizontal block, sand surface ripples outward.
11-15s: Slow push to warrior's back silhouette, both sticks at rest, dust settling gently, frame stabilizes.
Lighting: Low-angle sunset backlight dark gold + sand scatter warm diffusion (source), heat refraction softening edges + sand particles luminous in backlight (behavior), dark gold warm base + deep brown shadow (tone).
SFX: Wind across sand, rattan impact crack, particle settling whisper.
Negative: any text, subtitles, logos or watermarks
```

## 第 2 段 / 4 — Sinawali 交織（Seedance 設 15s）
```
Sunset desert Philippine Kali martial arts, cinematic realism, dark gold warm tones, desolate atmosphere.
Pervasive sand haze throughout, heat shimmer distorting distance, ochre texture every frame.
0-3s: Medium close-up frontal, warrior initiates Sinawali combinations, dual sticks alternating diagonal strikes forming intersecting X-patterns, stick shadows overlapping.
3-7s: Extreme close-up hands gripping sticks, knuckles whitening, sweat trailing rattan grooves, wrist rotations driving tip arcs at accelerating pace.
7-11s: Low-angle upward shot, warrior accelerating strike frequency, dual sticks meeting increasingly rapid impacts, fan-shaped sand clouds burst with each collision, breaching silence builds.
11-15s: Medium side profile, dual sticks cross-block defined pose, shockwave disturbs sand beneath feet, motion ceases.
Lighting: Low-angle sunset backlight dark gold + sand scatter warm diffusion (source), heat refraction softening edges + sand particles luminous in backlight (behavior), dark gold warm base + deep brown shadow (tone).
SFX: Dense rattan impacts staccato, stick air whine, sand particle percussion burst.
Negative: any text, subtitles, logos or watermarks
```

## 第 3 段 / 4 — Redonda 旋風（Seedance 設 15s）
```
Sunset desert Philippine Kali martial arts, cinematic realism, dark gold warm tones, desolate atmosphere.
Pervasive sand haze throughout, heat shimmer distorting distance, ochre texture every frame.
0-3s: Low-angle side tracking, warrior charges forward, dual sticks drag sand leaving parallel furrows, feet compress explosive sand columns.
3-7s: 180° orbital shot, warrior spinning Redonda windmill combinations, dual sticks inscribe overlapping circles, sand whirls into helical vortex column.
7-11s: Extreme close-up face, sweat and sand mixture, intense focused gaze, sunset amber reflects in pupils, hair whipped by rotation airflow.
11-15s: Wide side profile, warrior launches airborne dual-stick descending cross-strike, landing impact triggers fan-shaped sand spray, freezes mid-air form.
Lighting: Low-angle sunset backlight dark gold + sand scatter warm diffusion (source), heat refraction softening edges + sand particles luminous in backlight (behavior), dark gold warm base + deep brown shadow (tone).
SFX: Foot compression explosions, stick orbital whoosh crescendo, aerial strike dull percussive boom.
Negative: any text, subtitles, logos or watermarks
```

## 第 4 段 / 4 — 夕陽收勢（Seedance 設 15s）
```
Sunset desert Philippine Kali martial arts, cinematic realism, dark gold warm tones, desolate atmosphere.
Pervasive sand haze throughout, heat shimmer distorting distance, ochre texture every frame.
0-3s: Medium frontal, warrior kneels single leg, dual sticks cross-planted in sand ahead, dust cascades like gold rain curtain.
3-7s: Slow push to face close-up, warrior closes eyes breathing rhythm, chest rise-fall gradually stabilizes, sweat droplets absorb into sand.
7-11s: Gradual pull back, warrior rises retrieving sticks to back carry, silhouette aligns sunset horizon, desert returns calm.
11-15s: Aerial ascending drone, top-down reveals warrior as shrinking point in sand sea, sunset half-submerged horizon, frame fade to warm gold.
Lighting: Low-angle sunset backlight dark gold + sand scatter warm diffusion (source), heat refraction softening edges + sand particles luminous in backlight (behavior), dark gold warm base + deep brown shadow (tone).
SFX: Breathing deceleration, wind diminish, final sand whisper silence.
Negative: any text, subtitles, logos or watermarks
```

---

**拼接策略**：把 4 段按順序導入剪輯軟體（或用 [../concat_ffmpeg.md](../concat_ffmpeg.md) 的 ffmpeg）。每段都以穩定構圖收尾（下跪→起身→離場），專為無縫硬切設計。
