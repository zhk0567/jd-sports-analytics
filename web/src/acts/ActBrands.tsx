import { useMemo, useState } from "react";
import { ActShell } from "../components/ActShell";
import { ChartFrame } from "../charts/ChartFrame";
import type { StoryData } from "../data/types";

type Props = { story: StoryData };

const CAT_COLORS: Record<string, string> = {
  鞋类: "#d92b32",
  服饰: "#6a849c",
  装备: "#2a5f4a",
  营养: "#c4a35a",
  其他: "#9aa8b5",
};

export function ActBrands({ story }: Props) {
  const rows = [...story.by_brand]
    .filter((d) => d.brand && d.brand !== "未知品牌")
    .slice(0, 8);
  const [selected, setSelected] = useState<string | null>(null);
  const focus = selected ? rows.find((r) => r.brand === selected) : null;

  const stackOption = useMemo(() => {
    const brandNames = [...story.by_brand]
      .filter((d) => d.brand && d.brand !== "未知品牌")
      .slice(0, 8)
      .map((d) => d.brand || "");
    const totals = Object.fromEntries(
      brandNames.map((b) => [
        b,
        story.by_brand.find((d) => d.brand === b)?.count || 0,
      ]),
    );
    const cats = Array.from(
      new Set(story.brand_category.map((d) => d.category_label)),
    ).sort((a, b) => {
      const order = ["鞋类", "服饰", "装备", "营养", "其他"];
      return order.indexOf(a) - order.indexOf(b);
    });
    const yBrands = [...brandNames].reverse();

    const series = cats.map((cat, ci) => ({
      name: cat,
      type: "bar" as const,
      stack: "total",
      barWidth: 22,
      emphasis: { focus: "series" as const },
      itemStyle: {
        color: CAT_COLORS[cat] || "#9aa8b5",
        borderRadius: ci === cats.length - 1 ? [0, 4, 4, 0] : 0,
      },
      data: yBrands.map((brand) => {
        const hit = story.brand_category.find(
          (d) => d.brand === brand && d.category_label === cat,
        );
        const count = hit?.count || 0;
        const dim = selected != null && selected !== brand;
        return {
          value: count,
          itemStyle: { opacity: dim ? 0.2 : 1 },
        };
      }),
      label:
        ci === cats.length - 1
          ? {
              show: true,
              position: "right" as const,
              formatter: (p: { name?: string }) => {
                const n = totals[p.name || ""] || 0;
                return n.toLocaleString();
              },
              color: "#0e1116",
              fontSize: 12,
              fontWeight: 600,
              distance: 8,
            }
          : undefined,
    }));

    return {
      tooltip: {
        trigger: "axis",
        axisPointer: { type: "shadow" },
        formatter: (
          items: { seriesName?: string; value?: number; name?: string }[],
        ) => {
          if (!Array.isArray(items) || !items.length) return "";
          const brand = items[0]?.name || "";
          const lines = items
            .filter((it) => Number(it.value) > 0)
            .map(
              (it) =>
                `${it.seriesName}：${Number(it.value).toLocaleString()}`,
            );
          const total = items.reduce((s, it) => s + Number(it.value || 0), 0);
          return `${brand}<br/>合计 ${total.toLocaleString()}<br/>${lines.join("<br/>")}`;
        },
      },
      legend: {
        top: 0,
        left: "center",
        itemWidth: 12,
        itemHeight: 12,
        itemGap: 16,
        textStyle: { color: "#5a6270", fontSize: 12 },
      },
      grid: { left: 72, right: 64, top: 36, bottom: 28 },
      xAxis: {
        type: "value",
        splitLine: { lineStyle: { color: "rgba(14,17,22,0.06)" } },
        axisLabel: { color: "#5a6270", fontSize: 11 },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      yAxis: {
        type: "category",
        data: yBrands,
        axisLabel: {
          color: "#0e1116",
          fontSize: 13,
          fontWeight: 600,
        },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      series,
    };
  }, [story.by_brand, story.brand_category, selected]);

  const onEvents = useMemo(
    () => ({
      click: (params: Record<string, unknown>) => {
        const brand = String(params.name || "");
        if (!brand) return;
        setSelected((prev) => (prev === brand ? null : brand));
      },
    }),
    [],
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
          : "点击堆叠条，锁定单一品牌看品类构成。"
      }
      insights={story.insights?.brands}
    >
      <div className="stage-fill">
        <div className="chip-row brand-chips">
          {rows.map((d, i) => {
            const active = selected === d.brand;
            const dim = selected != null && !active;
            return (
              <button
                type="button"
                key={d.brand}
                className={`chip interactive${active ? " active" : ""}${dim ? " dim" : ""}`}
                onClick={() =>
                  setSelected((prev) =>
                    prev === d.brand ? null : d.brand || null,
                  )
                }
              >
                <span className="chip-idx">
                  {String(i + 1).padStart(2, "0")}
                </span>
                {d.brand}
                <span className="chip-n">{d.count}</span>
              </button>
            );
          })}
        </div>
        <div className="panel chart-fill brand-stack-panel">
          <div className="panel-head">
            <span className="title">Brand × category</span>
            <span className="meta">
              {selected ? `Focus · ${selected}` : "SKU 构成"}
            </span>
          </div>
          <ChartFrame
            option={stackOption}
            onEvents={onEvents}
            chartKey={selected || "all"}
          />
        </div>
      </div>
    </ActShell>
  );
}
