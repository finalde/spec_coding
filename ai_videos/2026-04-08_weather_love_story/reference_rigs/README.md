# 男性角色参考图 → 3D 模型

本目录已放入你提供的 **正面 / 侧面 / 背面** 三视图 PNG（`man_front.png`、`man_side.png`、`man_back.png`），便于在 DCC 或图生 3D 工具里对齐比例。

## 为何这里没有 `.glb` / `.fbx` / `.obj`

在当前开发环境里，**不能**仅凭对话就从位图「写出」工业可用的三角网格文件：需要运行 **图像→网格** 的深度学习推理（显存与权重下载）或手工/半自动建模。下面是可以由 **你本机或服务端** 完成的可行路径。

## 可选方案（按常见程度）

### 1. 单张主视图快速出粗模（开源 TripoSR）

多数流程只吃 **一张** 图，可优先用 **正面** `man_front.png` 试跑；侧面/背面用于之后在 Blender 里对照修形。

- 仓库：<https://github.com/VAST-AI-Research/TripoSR>  
- 需要：Python 3.10+、PyTorch、CUDA（推荐）；按官方 README 安装后运行推理脚本，一般可导出 **`.obj` / `.glb`**（以仓库说明为准）。

### 2. 在线 / API 图生 3D

使用带 **image-to-3D** 的产品（例如 Meshy、Rodin、Luma Genie 等），上传 `man_front.png`（或按站点要求的多视图），下载返回的 **GLB/OBJ**。注意服务条款与隐私。

### 3. Blender 人工建模（质量最高）

将三张图作为 **背景参考图 / Image Plane** 对齐，用 **雕刻或重拓扑** 做衣褶与大衣版型；适合《天气恋人》里远景人形也要稳定的项目。

## 产出建议

- 导出 **GLB**（含 PBR 贴图）便于 Seedance / 实时引擎。  
- 若只有粗模，可在 Blender 里 **减面 + 烘焙法线**，再进工作流。

若你希望在 **本仓库** 里加一条可复现命令（例如 Docker + TripoSR 脚本），可以说一下你的环境是否有 **NVIDIA GPU + 已装 CUDA**，可以再帮你写最小 `Makefile` / `run.sh` 脚手架。
