# 用 ffmpeg 拼接多個 Seedance mp4

下載多個 clip 後，把它們接成一支長片。兩種情況：

## 情況 A：所有 clip 編碼參數一致（同解析度/幀率/編碼）
最快，無損，不重新編碼。

1. 建一個清單檔 `list.txt`（每行一個檔案，順序就是播放順序）：
```
file 'clip1.mp4'
file 'clip2.mp4'
file 'clip3.mp4'
```

2. 拼接（直接複製流，秒出）：
```
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4
```

## 情況 B：clip 參數不一致（不同解析度/幀率），或情況 A 出現卡頓/錯誤
重新編碼，統一參數後再拼。

```
ffmpeg -f concat -safe 0 -i list.txt -c:v libx264 -pix_fmt yuv420p -r 30 -c:a aac output.mp4
```

先把每段統一到同一解析度（例如豎屏 1080x1920）再拼會最穩：
```
ffmpeg -i clip1.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" -r 30 c1_norm.mp4
```
（每段都跑一次，輸出 c1_norm.mp4 / c2_norm.mp4 …，再把 normalize 後的檔名寫進 list.txt 用情況 A 拼。）

## 加轉場（淡入淡出交叉溶解）
情況 A/B 是硬切。想要交叉溶解（crossfade），用 xfade（兩段示例，0.5 秒溶解，clip1 長 8 秒則 offset 設 7.5）：
```
ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex "[0][1]xfade=transition=fade:duration=0.5:offset=7.5,format=yuv420p" -c:a aac output.mp4
```

## PowerShell 小技巧：自動生成 list.txt
在 clip 所在資料夾，把當前目錄所有 mp4（按檔名排序）寫進清單：
```powershell
Get-ChildItem *.mp4 | Sort-Object Name | ForEach-Object { "file '$($_.Name)'" } | Set-Content -Encoding utf8 list.txt
```

> Windows 上 ffmpeg 安裝：`winget install Gyan.FFmpeg`，或到 ffmpeg.org 下載靜態版加進 PATH。
