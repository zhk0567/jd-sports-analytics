import { motion } from "framer-motion";
import { useMemo, useState } from "react";
import { ActShell } from "../components/ActShell";
import { ChartFrame } from "../charts/ChartFrame";
import { CountUp } from "../components/CountUp";
import type { StoryData } from "../data/types";

type Props = { story: StoryData };

function parseBand(band: string): [number, number] {
  const cleaned = band.replace(/[^\d\-–~+]/g, "");
  if (band.includes("+") || /以上|≥/.test(band)) {
    const n = Number(cleaned.replace(/\D/g, "")) || 4000;
    return [n, Infinity];
  }
  const parts = cleaned
    .split(/[-–~]/)
    .map((x) => Number(x))
    .filter((x) => !Number.isNaN(x));
  if (parts.length >= 2) return [parts[0], parts[1]];
  if (parts.length === 1) return [parts[0], parts[0]];
  return [0, Infinity];
}

export function ActPrice({ story }: Props) {
  const ov = story.overview;
  const bands = story.by_price_band;
  const maxBand = Math.max(...bands.map((d) => d.count), 1);
  const premiumShare = Math.round((ov.premium_share ?? 0) * 100);
  const [selectedBand, setSelectedBand] = useState<string | null>(null);

  const selectedMeta = bands.find((b) => b.price_band === selectedBand);
  const bandRange = selectedBand ? parseBand(selectedBand) : null;

  const ladderOption = useMemo(() => {
    const pts = [...story.brand_price_scatter]
      .filter((d) => d.brand !== "未知品牌")
      .sort((a, b) => a.price_mean - b.price_mean)
      .slice(0, 14);

    const maxCount = Math.max(...pts.map((d) => d.count), 1);

    return {
      grid: { left: 58, right: 56, top: 8, bottom: 36 },
      tooltip: {
        formatter: (p: { name?: string; value?: number[]; dataIndex?: number }) => {
          const d = pts[p.dataIndex ?? 0];
          if (!d) return String(p.name || "");
          return `${d.brand}<br/>均价 ¥${Math.round(d.price_mean)}<br/>SKU ${d.count.toLocaleString()}`;
        },
      },
      xAxis: {
        type: "value",
        name: "均价 ¥",
        nameLocation: "middle",
        nameGap: 24,
        nameTextStyle: { color: "#5a6270", fontSize: 11 },
        min: 0,
        splitLine: { lineStyle: { color: "rgba(14,17,22,0.06)" } },
        axisLabel: {
          color: "#5a6270",
          fontSize: 10,
          formatter: (v: number) => `¥${v}`,
        },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      yAxis: {
        type: "category",
        data: pts.map((d) => d.brand),
        axisLabel: {
          color: "#0e1116",
          fontSize: 11,
          fontWeight: 600,
        },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      series: [
        {
          type: "bar",
          barWidth: 12,
          z: 1,
          silent: true,
          data: pts.map((d) => {
            const inBand =
              !bandRange ||
              (d.price_mean >= bandRange[0] && d.price_mean < bandRange[1]);
            return {
              value: d.price_mean,
              itemStyle: {
                color: inBand
                  ? "rgba(106,132,156,0.35)"
                  : "rgba(106,132,156,0.1)",
                borderRadius: [0, 5, 5, 0],
              },
            };
          }),
        },
        {
          type: "scatter",
          z: 3,
          symbolSize: (_val: number[], params: { dataIndex?: number }) => {
            const d = pts[params.dataIndex ?? 0];
            if (!d) return 14;
            return Math.max(12, Math.min(26, 10 + (20 * d.count) / maxCount));
          },
          data: pts.map((d, yi) => {
            const inBand =
              !bandRange ||
              (d.price_mean >= bandRange[0] && d.price_mean < bandRange[1]);
            return {
              name: d.brand,
              value: [d.price_mean, yi],
              itemStyle: {
                color: inBand ? "#d92b32" : "rgba(106,132,156,0.35)",
                borderColor: "#fff",
                borderWidth: 2.5,
                shadowBlur: inBand && bandRange ? 6 : 0,
                shadowColor: "rgba(217,43,50,0.25)",
              },
              label: {
                show: true,
                position: "right",
                formatter: `${d.count}`,
                color: inBand ? "#0e1116" : "#9aa8b5",
                fontSize: 11,
                fontWeight: 600,
                distance: 10,
              },
            };
          }),
        },
      ],
    };
  }, [story.brand_price_scatter, bandRange]);

  return (
    <ActShell
      id="act-3"
      index={3}
      label="价格"
      claim={
        <>
          贵与多<em>并不等同</em>
        </>
      }
      lead={story.thesis.price}
      close={
        selectedMeta
          ? `「${selectedBand}」：${selectedMeta.count.toLocaleString()} SKU（${((100 * selectedMeta.count) / Math.max(ov.product_count, 1)).toFixed(1)}%）。右侧只亮均价落在该带的品牌。`
          : "点击价格带，联动右侧品牌均价阶梯。"
      }
      insights={story.insights?.price}
    >
      <div className="stage-fill price-stage">
        <div className="callout-grid callout-grid-4 tight price-stats">
          <div className="callout">
            <div className="k">P25</div>
            <div className="v">
              <CountUp value={Math.round(ov.price_p25 ?? 0)} prefix="¥" />
            </div>
          </div>
          <div className="callout accent-soft">
            <div className="k">Median</div>
            <div className="v">
              <CountUp value={Math.round(ov.price_median ?? 0)} prefix="¥" />
            </div>
          </div>
          <div className="callout">
            <div className="k">P75</div>
            <div className="v">
              <CountUp value={Math.round(ov.price_p75 ?? 0)} prefix="¥" />
            </div>
          </div>
          <button
            type="button"
            className={`callout interactive${selectedBand && /900|4000|\+/.test(selectedBand) ? " active" : ""}`}
            onClick={() => {
              const premium = bands.find((b) =>
                /900|4000|\+|以上/.test(String(b.price_band)),
              );
              setSelectedBand((prev) =>
                prev === premium?.price_band
                  ? null
                  : premium?.price_band || null,
              );
            }}
          >
            <div className="k">≥900</div>
            <div className="v">
              <CountUp value={premiumShare} suffix="%" />
            </div>
          </button>
        </div>

        <div className="split-stage flex-grow price-split">
          <div className="panel spectrum-panel">
            <div className="panel-head">
              <span className="title">Price spectrum</span>
              <span className="meta">
                {selectedBand ? "已锁定" : "点击分档"}
              </span>
            </div>
            <div className="spectrum compact">
              {bands.map((d, i) => {
                const active = selectedBand === d.price_band;
                const dim = selectedBand != null && !active;
                const isPremium = i >= bands.length - 2;
                return (
                  <button
                    type="button"
                    className={`spectrum-row interactive${active ? " active" : ""}${dim ? " dim" : ""}`}
                    key={d.price_band || i}
                    onClick={() =>
                      setSelectedBand((prev) =>
                        prev === d.price_band ? null : d.price_band || null,
                      )
                    }
                  >
                    <div className="band">{d.price_band}</div>
                    <div className="track">
                      <motion.div
                        className="fill"
                        initial={{ width: 0 }}
                        whileInView={{
                          width: `${(100 * d.count) / maxBand}%`,
                        }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.65, delay: i * 0.04 }}
                        style={{
                          background: isPremium
                            ? "linear-gradient(90deg,#6a849c,#d92b32)"
                            : "linear-gradient(90deg,#9aa8b5,#6a849c)",
                        }}
                      />
                    </div>
                    <div className="n">{d.count.toLocaleString()}</div>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="panel chart-fill">
            <div className="panel-head">
              <span className="title">Brand price ladder</span>
              <span className="meta">
                {selectedBand ? `Filter · ${selectedBand}` : "均价 × SKU"}
              </span>
            </div>
            <ChartFrame
              option={ladderOption}
              chartKey={selectedBand || "all"}
            />
          </div>
        </div>
      </div>
    </ActShell>
  );
}
