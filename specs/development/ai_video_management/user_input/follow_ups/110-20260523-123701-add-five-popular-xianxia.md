# Follow-up draft 110 — 2026-05-23
Summary: 在 `CANONICAL_NOVELS` 仙侠 section 追加 5 部高人气作品 — 剑来 / 仙逆 / 大奉打更人 / 赤心巡天 / 大道争锋；用户已通过 webapp 启动 resume + parallel=2 workers，本 follow-up 在 catalog 里补 5 个 entries 让 downloader 在跑完现有 queue 后继续抓这 5 部。

## 用户意图
- 已恢复当前 in-progress download（`guangyin_zhiwai` 240/1383 起继续，serial→workers=2 提速）。
- 用户要求"download more 仙侠剧 after it" + "you can propose 2"（让 assistant 选典型 / 知名作品） + "you can try 2 workers"（worker 数量改 2）。
- Assistant 已在 sudugu.org `/paihang/xianxia.html` 排行榜前 2 页 cross-reference 现有 catalog，挑选 5 部既不重复又有完成度或人气保证的 ongoing/complete 作品。

## 追加的 5 个 `NovelSpec`
| slug | title_zh | author | sudugu id | 备注 |
|---|---|---|---|---|
| `jianlai` | 剑来 | 烽火戏诸侯 | 287 | 现象级长篇（连载中）|
| `xian_ni` | 仙逆 | 耳根 | 410 | 经典完本，与已有 `guangyin_zhiwai` 同作者 |
| `dafeng_dagengren` | 大奉打更人 | 卖报小郎君 | 405 | 高人气（与已有 `lingjing_xingzhe` 同作者） |
| `chixin_xuntian` | 赤心巡天 | 情何以甚 | 56 | 完本好评 |
| `dadao_zhengfeng` | 大道争锋 | 误道者 | 435 | 经典完本 |

## 数据契约
- 每条 entry 写法与现有 follow-up 103 expanded section 一致：单一 `_sudugu(...)` source（ttkan 备源不在本次范围 — 用户没要求，且 follow-up 107 的 multi-source fallback 在 downloader 端已支持，后续如发现 sudugu 抓不下来再补 ttkan 即可，不阻塞本次）。
- 5 个 slug 均符合 `slug.replace("_", "").isalnum()` 规则（小写 ASCII + 下划线，无中文 / 数字开头 / 特殊字符）。
- `category="xianxia"` / `category_zh="仙侠"` 与现有仙侠 entries 完全一致。
- 全部插在仙侠 section 末尾（紧贴 `cong_songzi_liyu` 之后），保留 follow-up 103 expanded comment 之下的"按 follow-up 顺序追加"惯例。

## 运行时影响
- Downloader 当前后台 task 仍在 workers=2 模式跑 catalog 所有 novels；新增 5 个 entries 会在下次启动时被 `download_all` 看见。本次不强行 restart — 当前 in-progress 跑完后，用户 / cron 下次触发即会拾取这 5 部。
- 如需立即拉起 5 部下载：等当前 background task 结束（或手动 stop）后，再次 `python -m apps.cli.novel_download --workers 2`，即拉新 entries（resumable 状态机会自动跳过现有 done chapters）。
- Workers 默认值不在本 follow-up 改动 — follow-up 106 把默认 reverted 到 1（sudugu IP-block protection），用户手动传 `--workers 2` 是 per-run opt-in。

## 不在本 follow-up 范围
- ttkan 备源 / multi-source spec（参考 follow-up 107 模式，后续按需补）。
- 玄幻 / 都市 / 历史 / 科幻 / 言情 等 category 扩充。
- workers 默认值上调（保持 follow-up 106 的 serial-by-default + opt-in parallel 策略）。
- UI 上新 entries 在 sidebar 的渲染规则不变（沿用 follow-up 104 complete-only-sidebar 行为）。
