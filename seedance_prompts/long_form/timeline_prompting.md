# Timeline Prompting 範例（時間軸提示法）

在單一提示內用 `[Xs]` 時間戳分段，模型在一個 clip 內自動切鏡。每條都是可直接複製的完整提示。

## 戲劇性角色登場（雨夜城市）
```
[0s] Wide shot: A figure in a long coat stands at the end of an empty rain-slicked city street at night. Camera is static, framed from behind the figure. Neon signs reflect in puddles. High-contrast, low-key lighting.
[3s] Slow dolly forward begins, camera closing in on the figure from behind. Rain falls in foreground, shallow depth of field with bokeh streetlights.
[6s] Camera continues push in, now at medium shot. The figure turns their head slightly — profile barely visible. Tension holds.
[8s] Rack focus: background city blur sharpens briefly, then returns to subject.
Cinematic, 35mm film grain, desaturated with cold blue tones, anamorphic lens flare from streetlights.
```

## 四層結構模板（自己填）
```
[0s] [Shot type]: [subject + action], [camera movement], [lighting], [color/mood].
[3s] [Shot type]: [what changes], [camera movement], [depth of field].
[6s] [Shot type]: [next beat], [camera movement].
[8s] [transition/rack focus/cut]: [final beat].
[overall style line: film stock, grain, color grade, lens]
```
