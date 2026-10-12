import { useMemo, useState } from "react";
import { ActShell } from "../components/ActShell";
import { CountUp } from "../components/CountUp";
import { ChartFrame } from "../charts/ChartFrame";
import type { StoryData } from "../data/types";

type Props = { story: StoryData };

export function ActScale({ story }: Props) {
  const ov = story.overview;
  const cats = story.by_category;
  const [selected, setSelected] = useState<string | null>(null);

  const top = cats[0];
  const topShare =
    top?.share ??
    (top
      ? Math.round((100 * top.count) / Math.max(ov.product_count, 1))
      : 0);

  const selectedRow = cats.find(
    (c) => (c.label || c.category_guess) === selected,
  );

  const treeOption = useMemo(() => {
    const labels = cats.map((d) => d.label || d.category_guess || "");
    const values = cats.map((d) => d.count);
    const palette = ["#1c2430", "#6a849c", "#d92b32", "#2a5f4a", "#9aa8b5"];
    return {
      color: palette,
      tooltip: {
        trigger: "item",
        formatter: (p: { name?: string; value?: number; percent?: number }) =>
          `${p.name}<br/>${Number(p.value).toLocaleString()} · ${Number(p.percent ?? 0).toFixed(1)}%`,
      },
      series: [
        {
          type: "treemap",
          roam: false,
          nodeClick: false,
          breadcrumb: { show: false },
          left: 0,
          right: 0,
          top: 0,
          bottom: 0,
          label: {
            show: true,
            formatter: "{b}\n{c}",
            color: "#fff",
            fontSize: 12,
            fontFamily: "Manrope, Noto Sans SC, sans-serif",
          },
          itemStyle: {
            borderColor: "rgba(247,248,250,0.95)",
            borderWidth: 3,
            gapWidth: 3,
          },
          data: labels.map((name, i) => {
            const active = !selected || selected === name;
            return {
              name,
              value: values[i],
              itemStyle: {
                color: palette[i % palette.length],
                opacity: active ? 1 : 0.28,
                borderWidth: selected === name ? 4 : 3,
                borderColor:
                  selected === name ? "#d92b32" : "rgba(247,248,250,0.95)",
              },
            };
          }),
          animationDuration: 700,
        },
      ],
    };
  }, [cats, selected]);

  const onEvents = useMemo(
    () => ({
      click: (params: Record<string, unknown>) => {
        const name = String(params.name || "");
        if (!name) return;
        setSelected((prev) => (prev === name ? null : name));
      },
    }),
    [],
  );

  return (
    <ActShell
      id="act-1"
      index={1}
      label="规模"
      claim={
        <>
          样本如何被<em>切开</em>
        </>
      }
      lead={story.thesis.scale}
      close={
        selectedRow
          ? `选中「${selected}」：${selectedRow.count.toLocaleString()} SKU，约占 ${(selectedRow.share ?? (100 * selectedRow.count) / Math.max(ov.product_count, 1)).toFixed(1)}%。再点一次取消。`
          : `最大品类约占 ${topShare}%——点击色块或标签探索。`
      }
      insights={story.insights?.scale}
    >
      <div className="stage-fill">
        <div className="callout-grid callout-grid-4 tight">
          <div className="callout">
            <div className="k">Products</div>
            <div className="v">
              <CountUp value={ov.product_count} />
            </div>
          </div>
          <div className="callout">
            <div className="k">Top share</div>
            <div className="v">
              <CountUp value={Number(topShare)} suffix="%" />
            </div>
          </div>
          <div className="callout">
            <div className="k">Median</div>
            <div className="v">
              <CountUp value={Math.round(ov.price_median ?? 0)} prefix="¥" />
            </div>
          </div>
          <div className="callout">
            <div className="k">Known</div>
            <div className="v">
              <CountUp
                value={(ov.known_brand_rate ?? 0) * 100}
                decimals={0}
                suffix="%"
              />
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
          {cats.map((c) => {
            const name = c.label || c.category_guess || "";
            return (
              <button
                type="button"
                key={name}
                className={`chip${selected === name ? " active" : ""}`}
                onClick={() =>
                  setSelected((prev) => (prev === name ? null : name))
                }
              >
                {name}
                <strong>
                  {(
                    c.share ??
                    (100 * c.count) / Math.max(ov.product_count, 1)
                  ).toFixed(0)}
                  %
                </strong>
              </button>
            );
          })}
        </div>

        <div className="panel chart-fill">
          <div className="panel-head">
            <span className="title">Category mass</span>
            <span className="meta">
              {selected ? `Focus · ${selected}` : "点击色块"}
            </span>
          </div>
          <ChartFrame
            option={treeOption}
            onEvents={onEvents}
            chartKey={selected || "all"}
          />
        </div>
      </div>
    </ActShell>
  );
}
