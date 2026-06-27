/** DramaDashboard — the drama-level "production console" (main page).
 *
 * Rendered at the top of a drama's README page (`ai_videos/{drama}/README.md`),
 * it hosts drama-wide actions + status that don't fit the per-file toolbar:
 *  - 🔒 全局定版: lock every episode's newest takes to shot{NN}.mp4 in one pass
 *    (drama-wide counterpart to the per-episode 定版).
 *  - 📦 导出 production: copy every subtitled ep master into
 *    production/{中文|英文|中英}/ep{NN}.mp4 (follow-up 148).
 *  - 💬 全剧烧字幕 (zh/en/both): relocated here from the toolbar.
 *  - 🎞 剧集列表: one row per episode with a 一键拼接成片 button (concat that
 *    episode's locked takes into ep{NN}.mp4).
 * Future drama-level functions go here too — this is the dedicated drama page. */
import { useCallback, useEffect, useState } from "react";
import { announceToast } from "../lib/announce";
import {
  burnDramaSubtitles,
  concatEpisode,
  exportProduction,
  listDramaEpisodes,
  selectDramaTakes,
} from "../api";
import type { DramaEpisodeInfo, SubtitleLang } from "../api";
import { ApiError } from "../types";

function errKind(err: unknown): string {
  if (err instanceof ApiError) return err.detail?.kind ?? `HTTP ${err.status}`;
  if (err instanceof Error) return err.message;
  return "unknown_error";
}

const BURN_LANGS: [SubtitleLang, string][] = [
  ["zh", "💬 全剧·中文字幕"],
  ["en", "💬 全剧·EN"],
  ["both", "💬 全剧·中英"],
];

export interface DramaDashboardProps {
  path: string;       // the drama README path (any file under the drama works)
  onSaved: () => void;
}

export function DramaDashboard({ path, onSaved }: DramaDashboardProps): JSX.Element {
  const [exportBusy, setExportBusy] = useState<boolean>(false);
  const [burnBusy, setBurnBusy] = useState<boolean>(false);
  const [takesBusy, setTakesBusy] = useState<boolean>(false);
  const [episodes, setEpisodes] = useState<DramaEpisodeInfo[]>([]);
  const [concatBusyEp, setConcatBusyEp] = useState<string | null>(null);

  const reloadEpisodes = useCallback(async () => {
    try {
      const r = await listDramaEpisodes(path);
      setEpisodes(r.episodes);
    } catch {
      setEpisodes([]);
    }
  }, [path]);

  useEffect(() => {
    void reloadEpisodes();
  }, [reloadEpisodes]);

  const onSelectTakesClick = useCallback(async () => {
    setTakesBusy(true);
    try {
      const r = await selectDramaTakes(path);
      const okEps = r.outcomes.filter((o) => o.ok);
      const failed = r.outcomes.filter((o) => !o.ok);
      const totalShots = okEps.reduce((n, o) => n + o.selected, 0);
      let summary = `已全局定版 ${okEps.length} 集 / ${totalShots} 个镜头 → shot{NN}.mp4`;
      if (failed.length > 0) {
        const names = failed.map((o) => `${o.episode} (${o.reason})`).join(", ");
        summary += ` · 跳过 ${failed.length}: ${names}`;
      }
      announceToast(summary);
      await reloadEpisodes();
      onSaved();
    } catch (err) {
      announceToast(`全局定版失败: ${errKind(err)}`);
    } finally {
      setTakesBusy(false);
    }
  }, [path, reloadEpisodes, onSaved]);

  const onConcatClick = useCallback(async (ep: DramaEpisodeInfo) => {
    setConcatBusyEp(ep.episode);
    try {
      const r = await concatEpisode(ep.episode_rel);
      const out = (r.out ?? "").split("/").pop() ?? r.out;
      let summary = out
        ? `${ep.episode} 已拼接成片 → ${out}（${r.used.length} 镜）`
        : `${ep.episode} 拼接未产出成片`;
      if (r.skipped.length > 0) summary += ` · 跳过 ${r.skipped.length} 镜`;
      announceToast(summary);
      await reloadEpisodes();
      onSaved();
    } catch (err) {
      announceToast(`${ep.episode} 拼接成片失败: ${errKind(err)}`);
    } finally {
      setConcatBusyEp(null);
    }
  }, [reloadEpisodes, onSaved]);

  const onExportClick = useCallback(async () => {
    setExportBusy(true);
    try {
      const r = await exportProduction(path);
      const total = r.exported.length;
      if (total === 0) {
        announceToast("未找到带字幕的成片 — 先用「全剧烧字幕」+「整集字幕」生成 ep{NN}_{zh|en}.mp4");
      } else {
        const parts = Object.entries(r.by_lang)
          .filter(([, n]) => n > 0)
          .map(([folder, n]) => `${folder} ${n}`)
          .join(" · ");
        announceToast(`已导出 ${total} 个成片到 production/（${parts}）`);
      }
      onSaved();
    } catch (err) {
      announceToast(`导出 production 失败: ${errKind(err)}`);
    } finally {
      setExportBusy(false);
    }
  }, [path, onSaved]);

  const onBurnClick = useCallback(async (lang: SubtitleLang) => {
    setBurnBusy(true);
    try {
      const result = await burnDramaSubtitles(path, lang);
      const ok = result.outcomes.filter((o) => o.ok).length;
      const skipped = result.outcomes.filter((o) => !o.ok);
      const langLabel = lang === "both" ? "中英" : lang === "en" ? "英文" : "中文";
      let summary = `已为 ${ok} 个镜头烧入${langLabel}字幕`;
      if (skipped.length > 0) {
        const names = skipped.map((s) => `${s.episode}/${s.shot} (${s.reason})`).join(", ");
        summary += ` · 跳过 ${skipped.length}: ${names}`;
      }
      announceToast(summary);
      onSaved();
    } catch (err) {
      announceToast(`全剧烧字幕失败: ${errKind(err)}`);
    } finally {
      setBurnBusy(false);
    }
  }, [path, onSaved]);

  return (
    <section className="drama-dashboard" aria-label="剧集制作台">
      <h2 className="drama-dashboard-title">🎬 剧集制作台</h2>

      <div className="drama-dashboard-group" role="group" aria-label="定版 / 出片 / 导出">
        <span className="drama-dashboard-group-label">出片</span>
        <button type="button" className="drama-dashboard-btn drama-dashboard-btn-primary"
          onClick={onSelectTakesClick} disabled={takesBusy}
          aria-label="Lock every episode's newest take to shot{NN}.mp4 in one pass"
          title="全局定版：遍历全剧所有 episodes/ep*/shots/shot*，每镜把 renders/ 里最新的一条 take 锁定复制为 shot{NN}.mp4（renders/ 原样保留），供拼接成片使用。缺 render 的镜头跳过。不做拼接。">
          {takesBusy ? "⏳ 定版中…" : "🔒 全局定版"}
        </button>
        <button type="button" className="drama-dashboard-btn"
          onClick={onExportClick} disabled={exportBusy}
          aria-label="Export all subtitled episode masters into the production folder"
          title="把本剧所有带字幕的整集成片拷到 production/：中文 ep{NN}_zh.mp4 → 中文/、英文 ep{NN}_en.mp4 → 英文/、中英 ep{NN}_zhen.mp4 → 中英/（子文件夹内去后缀命名 ep{NN}.mp4；覆盖、不删旧文件）。需先对各集烧好字幕。">
          {exportBusy ? "⏳ 导出中…" : "📦 导出成片到 production"}
        </button>
      </div>

      <div className="drama-dashboard-group" role="group" aria-label="全剧烧字幕（按语言）">
        <span className="drama-dashboard-group-label">全剧字幕</span>
        {BURN_LANGS.map(([lang, label]) => (
          <button key={lang} type="button" className="drama-dashboard-btn"
            onClick={() => onBurnClick(lang)} disabled={burnBusy}
            aria-label={`Burn ${lang} subtitles into every shot of every episode`}
            title="遍历全剧所有 episodes/ep*/shots/shot*，每镜取最新 render + subtitles.md 烧入字幕（已存在则覆盖）。缺 render 或缺 subtitles.md 的镜头自动跳过。">
            {burnBusy ? "⏳" : label}
          </button>
        ))}
      </div>

      {episodes.length > 0 ? (
        <div className="drama-dashboard-group drama-dashboard-episodes" role="group" aria-label="剧集列表">
          <span className="drama-dashboard-group-label">剧集</span>
          <ul className="drama-episode-list">
            {episodes.map((ep) => (
              <li key={ep.episode} className="drama-episode-row">
                <span className="drama-episode-name">{ep.episode}</span>
                <span className="drama-episode-meta">
                  {ep.locked}/{ep.shots} 定版{ep.has_master ? " · 已出片" : ""}
                </span>
                <button type="button" className="drama-dashboard-btn drama-episode-concat-btn"
                  onClick={() => onConcatClick(ep)}
                  disabled={concatBusyEp !== null || ep.locked === 0}
                  aria-label={`Concat ${ep.episode} locked takes into one ep mp4`}
                  title={ep.locked === 0
                    ? "本集还没有定版的镜头（shot{NN}.mp4）——先「全局定版」或在本集工具栏单集定版后再拼接。"
                    : "把本集已定版的各镜 shot{NN}.mp4（缺则取最新 renders/ take）按顺序拼接成 ep{NN}.mp4 + segments.json（承接缝默认硬拼，不补帧）。已存在则覆盖。"}>
                  {concatBusyEp === ep.episode ? "⏳ 拼接中…" : "🎬 拼接成片"}
                </button>
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </section>
  );
}
