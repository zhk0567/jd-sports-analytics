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
  const parts = cleaned.split(/[-–~]/).map((x) => Number(x)).filter((x) => !Number.isNaN(x));
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

  const bubbleOption = useMemo(() => {
    const pts = story.brand_price_scatter.filter((d) => d.brand !== "未知品牌");
    return {
      grid: { left: 42, right: 12, top: 16, bottom: 28 },
      xAxis: {
        name: "均价",
        nameTextStyle: { color: "#5a6270", fontSize: 10 },
        splitLine: { lineStyle: { color: "rgba(14,17,22,0.07)" } },
        axisLabel: { color: "#5a6270", fontSize: 10 },
      },
      yAxis: {
        name: "商品数",
        nameTextStyle: { color: "#5a6270", fontSize: 10 },
        splitLine: { lineStyle: { color: "rgba(14,17,22,0.07)" } },
        axisLabel: { color: "#5a6270", fontSize: 10 },
      },
      tooltip: {
        formatter: (p: unknown) => {
          const item = p as { name?: string; value?: number[] };
          const v = item.value || [0, 0, 0];
          return `${item.name}<br/>均价 ¥${Number(v[0]).toFixed(0)}<br/>商品 ${v[1]}`;
        },
      },
      series: [
        {
          type: "scatter",
          symbolSize: (val: number[]) =>
            Math.max(12, Math.min(44, Math.sqrt(val[2] || 1) / 70)),
          data: pts.map((d) => {
            const inBand =
              !bandRange ||
              (d.price_mean >= bandRange[0] && d.price_mean < bandRange[1]);
            return {
              name: d.brand,
              value: [d.price_mean, d.count, d.comment_sum || 1],
              itemStyle: {
                color: inBand
                  ? "rgba(106,132,156,0.78)"
                  : "rgba(106,132,156,0.14)",
                borderColor: inBand ? "#d92b32" : "rgba(14,17,22,0.12)",
                borderWidth: inBand ? 1.4 : 0.6,
              },
            };
          }),
          animationDuration: 700,
        },
      ],
    };
  }, [story.brand_price_scatter, bandRange]);

  const onEvents = useMemo(
    () => ({
      click: (params: Record<string, unknown>) => {
        const name = String(params.name || "");
        if (!name) return;
        // clicking a bubble clears band filter and could show brand — keep simple: clear
        setSelectedBand(null);
      },
    }),
    [],
  );

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
          ? `「${selectedBand}」：${selectedMeta.count.toLocaleString()} SKU（${((100 * selectedMeta.count) / Math.max(ov.product_count, 1)).toFixed(1)}%）。气泡只亮均价落在该带的品牌。`
          : "点击价格带，联动右侧气泡高亮。"
      }
      insights={story.insights?.price}
    >
      <div className="stage-fill">
        <div className="callout-grid callout-grid-4 tight">
          <div className="callout">
            <div className="k">P25</div>
            <div className="v">
              <CountUp value={Math.round(ov.price_p25 ?? 0)} prefix="¥" />
            </div>
          </div>
          <div className="callout">
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

        <div className="split-stage flex-grow">
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
                          background:
                            i >= bands.length - 2
                              ? "linear-gradient(90deg,#6a849c,#d92b32)"
                              : "linear-gradient(90deg,#8fa6b8,#6a849c)",
                        }}
                      />
                    </div>
                    <div className="n">{d.count}</div>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="panel chart-fill">
            <div className="panel-head">
              <span className="title">Price × scale</span>
              <span className="meta">
                {selectedBand ? `Filter · ${selectedBand}` : "Bubble"}
              </span>
            </div>
            <ChartFrame
              option={bubbleOption}
              onEvents={onEvents}
              chartKey={selectedBand || "all"}
            />
          </div>
        </div>
      </div>
    </ActShell>
  );
}
