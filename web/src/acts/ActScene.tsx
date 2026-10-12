import { useMemo, useState } from "react";
import { ActShell } from "../components/ActShell";
import { ChartFrame } from "../charts/ChartFrame";
import { CountUp } from "../components/CountUp";
import type { StoryData } from "../data/types";

type Props = { story: StoryData };

export function ActScene({ story }: Props) {
  const scenes = (story.by_scene || [])
    .filter((d) => d.sport_scene && d.sport_scene !== "其他")
    .slice(0, 6);
  const total = scenes.reduce((s, d) => s + d.count, 0) || 1;
  const topScene = scenes[0];
  const topShare = topScene ? Math.round((100 * topScene.count) / total) : 0;
  const male = story.by_gender?.find((g) => g.gender_guess === "男");
  const female = story.by_gender?.find((g) => g.gender_guess === "女");
  const n = Math.max(story.overview.product_count, 1);
  const [selected, setSelected] = useState<string | null>(null);

  const focusCats = useMemo(() => {
    if (!selected) return [];
    return story.scene_category
      .filter((d) => d.sport_scene === selected)
      .sort((a, b) => b.count - a.count)
      .slice(0, 3);
  }, [selected, story.scene_category]);

  const option = useMemo(() => {
    const links = story.scene_category
      .filter((d) => d.sport_scene !== "其他")
      .filter((d) => !selected || d.sport_scene === selected)
      .map((d) => ({
        source: d.sport_scene,
        target: d.category_label,
        value: d.count,
      }));
    const nodes = Array.from(
      new Set(links.flatMap((l) => [l.source, l.target])),
    ).map((name) => ({ name }));

    return {
      tooltip: { trigger: "item" },
      series: [
        {
          type: "sankey",
          data: nodes,
          links,
          emphasis: { focus: "adjacency" },
          lineStyle: { color: "gradient", curveness: 0.5, opacity: 0.4 },
          itemStyle: { borderWidth: 0 },
          label: {
            color: "#0e1116",
            fontSize: 11,
            fontFamily: "Noto Sans SC, sans-serif",
          },
          levels: [
            { depth: 0, itemStyle: { color: "#2a5f4a" } },
            { depth: 1, itemStyle: { color: "#6a849c" } },
          ],
          left: 4,
          right: 4,
          top: 8,
          bottom: 8,
          animationDuration: 700,
        },
      ],
    };
  }, [story.scene_category, selected]);

  return (
    <ActShell
      id="act-4"
      index={4}
      label="场景"
      claim={
        <>
          人在什么场<em>买什么</em>
        </>
      }
      lead={story.thesis.scene}
      close={
        selected && focusCats.length
          ? `「${selected}」主要流向：${focusCats.map((c) => `${c.category_label} ${c.count}`).join(" · ")}。再点标签取消。`
          : "点击场景标签，过滤下方流向。"
      }
      insights={story.insights?.scene}
    >
      <div className="stage-fill">
        <div className="callout-grid tight">
          <div className="callout">
            <div className="k">Top scene</div>
            <div className="v text">
              {topScene?.sport_scene || "—"}
              <span className="dim"> {topShare}%</span>
            </div>
          </div>
          <div className="callout">
            <div className="k">Male / Female</div>
            <div className="v">
              <CountUp
                value={Math.round((100 * (male?.count || 0)) / n)}
                suffix="%"
              />
              <span className="dim">
                {" "}
                / {Math.round((100 * (female?.count || 0)) / n)}%
              </span>
            </div>
          </div>
          <div className="callout">
            <div className="k">Scenes</div>
            <div className="v">
              <CountUp value={scenes.length} />
            </div>
          </div>
        </div>

        <div className="chip-row">
          <button
            type="button"
            className={`chip${!selected ? " active" : ""}`}
            onClick={() => setSelected(null)}
          >
            全部
          </button>
          {scenes.map((s) => (
            <button
              type="button"
              className={`chip${selected === s.sport_scene ? " active" : ""}`}
              key={s.sport_scene}
              onClick={() =>
                setSelected((prev) =>
                  prev === s.sport_scene ? null : s.sport_scene || null,
                )
              }
            >
              {s.sport_scene}
              <strong>{Math.round((100 * s.count) / total)}%</strong>
            </button>
          ))}
        </div>

        <div className="panel chart-fill">
          <div className="panel-head">
            <span className="title">Scene → category</span>
            <span className="meta">
              {selected ? `Focus · ${selected}` : "Flow"}
            </span>
          </div>
          <ChartFrame option={option} chartKey={selected || "all"} />
        </div>
      </div>
    </ActShell>
  );
}
