import ReactECharts from "echarts-for-react";
import { useInView } from "framer-motion";
import { useMemo, useRef } from "react";

type ChartEvents = Record<string, (params: Record<string, unknown>) => void>;

type Props = {
  option: Record<string, unknown>;
  /** px number, or "100%" to fill flex parent */
  height?: number | string;
  onEvents?: ChartEvents;
  /** force remount when selection changes */
  chartKey?: string | number;
};

export function ChartFrame({
  option,
  height = "100%",
  onEvents,
  chartKey,
}: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, amount: 0.3 });

  const merged = useMemo(() => {
    if (!inView) {
      return {
        ...option,
        animation: false,
      };
    }
    return {
      animation: true,
      animationDuration: 700,
      animationEasing: "cubicOut",
      textStyle: {
        fontFamily: "Manrope, Noto Sans SC, Segoe UI, sans-serif",
        color: "#14171C",
      },
      ...option,
    };
  }, [inView, option]);

  const style =
    typeof height === "number"
      ? { height, width: "100%" as const }
      : { height, width: "100%" as const, minHeight: 0 };

  return (
    <div ref={ref} className="chart-host">
      <ReactECharts
        key={chartKey}
        option={merged}
        style={style}
        opts={{ renderer: "canvas" }}
        notMerge
        onEvents={onEvents}
      />
    </div>
  );
}
