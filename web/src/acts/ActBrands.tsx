import { motion } from "framer-motion";
import { useMemo, useState } from "react";
import { ActShell } from "../components/ActShell";
import { ChartFrame } from "../charts/ChartFrame";
import type { StoryData } from "../data/types";

type Props = { story: StoryData };

export function ActBrands({ story }: Props) {
  const rows = [...story.by_brand]
    .filter((d) => d.brand && d.brand !== "未知品牌")
    .slice(0, 8);
  const max = Math.max(...rows.map((d) => d.count), 1);
  const [selected, setSelected] = useState<string | null>(null);
  const focus = selected ? rows.find((r) => r.brand === selected) : null;

  const heatOption = useMemo(() => {
    const brands = Array.from(
      new Set(
        story.brand_category
          .filter((d) => d.brand !== "未知品牌")
          .map((d) => d.brand),
      ),
    ).slice(0, 7);
    const cats = Array.from(
      new Set(story.brand_category.map((d) => d.category_label)),
    );
    const data: [number, number, number][] = [];
    brands.forEach((b, yi) => {
      cats.forEach((c, xi) => {
        const hit = story.brand_category.find(
          (d) => d.brand === b && d.category_label === c,
        );
        const count = hit?.count || 0;
        const dim = selected && selected !== b;
        data.push([xi, yi, dim ? Math.round(count * 0.12) : count]);
      });
    });
    return {
      tooltip: {
        formatter: (p: { value?: number[] }) => {
          const v = p.value || [0, 0, 0];
          const b = brands[v[1]];
          const c = cats[v[0]];
          const real =
            story.brand_category.find(
              (d) => d.brand === b && d.category_label === c,
            )?.count || 0;
          return `${b} · ${c}<br/>${real}`;
        },
      },
      grid: { left: 64, right: 8, top: 8, bottom: 28 },
      xAxis: {
        type: "category",
        data: cats,
        axisLabel: { color: "#5a6270", fontSize: 10, rotate: 18 },
      },
      yAxis: {
        type: "category",
        data: brands,
        axisLabel: {
          color: "#0e1116",
          fontSize: 11,
        },
      },
      visualMap: {
        min: 0,
        max: Math.max(
          ...story.brand_category
            .filter((d) => brands.includes(d.brand))
            .map((d) => d.count),
          1,
        ),
        show: false,
        inRange: { color: ["#f4f6f8", "#6a849c", "#d92b32"] },
      },
      series: [
        {
          type: "heatmap",
          data,
          emphasis: {
            itemStyle: { shadowBlur: 6, shadowColor: "rgba(0,0,0,0.2)" },
          },
        },
      ],
    };
  }, [story.brand_category, selected]);

  const onEvents = useMemo(
    () => ({
      click: (params: Record<string, unknown>) => {
        const value = params.value as number[] | undefined;
        if (!value) return;
        const brands = Array.from(
          new Set(
            story.brand_category
              .filter((d) => d.brand !== "未知品牌")
              .map((d) => d.brand),
          ),
        ).slice(0, 7);
        const brand = brands[value[1]];
        if (!brand) return;
        setSelected((prev) => (prev === brand ? null : brand));
      },
    }),
    [story.brand_category],
  );

  return (
    <ActShell
      id="act-2"
      index={2}
      label="品牌"
      claim={
        <>
          谁在<em>占货架</em>
        </>
      }
      lead={story.thesis.brands}
      close={
        focus
          ? `${focus.brand}：${focus.count} SKU · 均价 ¥${Math.round(focus.price_mean ?? 0)} · 中位 ¥${Math.round(focus.price_median ?? 0)}。再点取消。`
          : "点击品牌行或热力格，锁定单一品牌。"
      }
      insights={story.insights?.brands}
    >
      <div className="stage-fill split-stage">
        <div className="panel rank-panel">
          <div className="panel-head">
            <span className="title">Brand race</span>
            <span className="meta">
              {selected ? `Focus · ${selected}` : "可点击"}
            </span>
          </div>
          <div className="rank-list compact">
            {rows.map((d, i) => {
              const active = selected === d.brand;
              const dim = selected != null && !active;
              return (
                <motion.button
                  type="button"
                  className={`rank-row interactive${active ? " active" : ""}${dim ? " dim" : ""}`}
                  key={d.brand}
                  initial={{ x: 12 }}
                  whileInView={{ x: 0 }}
                  viewport={{ once: true, amount: 0.2 }}
                  transition={{ duration: 0.35, delay: i * 0.03 }}
                  onClick={() =>
                    setSelected((prev) =>
                      prev === d.brand ? null : d.brand || null,
                    )
                  }
                >
                  <div className="idx">{String(i + 1).padStart(2, "0")}</div>
                  <div className="name">
                    {d.brand}
                    {d.price_mean != null ? (
                      <span className="sub">¥{Math.round(d.price_mean)}</span>
                    ) : null}
                  </div>
                  <div className="count">{d.count}</div>
                  <div className="bar-track">
                    <motion.div
                      className="bar-fill"
                      initial={{ width: 0 }}
                      whileInView={{ width: `${(100 * d.count) / max}%` }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.7, delay: 0.05 + i * 0.02 }}
                    />
                  </div>
                </motion.button>
              );
            })}
          </div>
        </div>

        <div className="panel chart-fill">
          <div className="panel-head">
            <span className="title">Brand × category</span>
            <span className="meta">Heat</span>
          </div>
          <ChartFrame
            option={heatOption}
            onEvents={onEvents}
            chartKey={selected || "all"}
          />
        </div>
      </div>
    </ActShell>
  );
}
