# 多鏡頭序列提示（Multi-Shot Labeling）

單一提示內用 `[Shot N: ...]`、`[Cut to: ...]`、`[Dissolve to: ...]` 標記最多約 5 個鏡頭；`@Character1`、`@ProductRef`、`@OutfitRef`、`@BuildingRef` 是參考標籤，對應你上傳的參考圖/影片，用來鎖定主體一致性。每條可直接複製。

### 1. 英雄旅程轉場
```
[Shot 1: Wide shot] @Character1 standing on a cliff overlooking a futuristic Tokyo, neon lights reflecting in puddles. [Cut to: Extreme Close-up] @Character1's eyes narrowing as a digital HUD overlays their pupil.
```

### 2. 產品揭示
```
[Shot 1: Macro] @ProductRef rotating slowly on a velvet pedestal, soft rim lighting, luxury aesthetic. [Shot 2: Lifestyle] A hand in elegant attire reaching out to grab @ProductRef on a marble countertop.
```

### 3. 子彈時間動作
```
[Shot 1: Medium shot] @Character1 dodging a projectile in slow motion, body contorting. [Cut to: Tracking shot] Camera follows @Character1 sliding across a glass floor while firing a tether.
```

### 4. 情感敘事
```
[Shot 1: Tight shot] @Character1 looking hopeful, eyes misty. [Cut to: Profile shot] @Character1 smiling as warm golden-hour sunlight hits their face.
```

### 5. 科幻場景切換
```
[Shot 1] @Character1 in a sterile white laboratory, holding a glowing vial. [Dissolve to] @Character1 in a lush alien jungle, the vial now glowing green.
```

### 6. 時裝伸展台
```
[Shot 1: Full body] @Character1 walking down a dark runway, spotlights following. [Cut to: Low angle] Tracking @Character1's boots hitting the floor. [Shot 3: Close up] The fabric of the @OutfitRef shimmering.
```

### 7. 恐怖 / 懸疑
```
[Shot 1: POV] Walking through a dark hallway, flashlight flickering. [Shot 2: Close up] @Character1's terrified face reflected in a cracked mirror. [Cut to: Wide] An empty chair rocking slowly.
```

### 8. 自然縮時
```
[Shot 1: Wide] A desert landscape at noon, harsh sun. [Time-lapse transition] The stars rotating over the same desert landscape. [Shot 2: Close up] A single flower blooming in the sand.
```

### 9. 第一人稱 POV
```
[Shot 1: POV] Hands reaching for a steering wheel of a vintage car. [Cut to: Side profile] @Character1 laughing while driving, wind in hair. [Shot 3: Wide] The car driving into the sunset.
```

### 10. 建築漫遊
```
[Shot 1: Drone wide] The @BuildingRef exterior at dusk. [Cut to: Tracking shot] Moving through the front door into a minimalist living room. [Shot 3: Macro] Focus on the texture of the oak wood floors.
```
