import { ACTS } from "../data/types";

type Props = {
  active: number;
  onJump: (index: number) => void;
};

export function ActNav({ active, onJump }: Props) {
  const prev = active > 0 ? active - 1 : null;
  const next = active < ACTS.length - 1 ? active + 1 : null;
  const label = ACTS[active]?.label ?? "";

  return (
    <div className="act-nav" role="navigation" aria-label="幕间导航">
      <button
        type="button"
        className="act-nav-btn"
        disabled={prev == null}
        onClick={() => prev != null && onJump(prev)}
        aria-label={prev != null ? `上一幕 ${ACTS[prev].label}` : "已是第一幕"}
      >
        ← 上一幕
      </button>
      <div className="act-nav-mid">
        <span className="act-nav-index">
          {String(active).padStart(2, "0")} / {String(ACTS.length - 1).padStart(2, "0")}
        </span>
        <span className="act-nav-label">{label}</span>
        <span className="act-nav-hint">↑↓ / 空格切幕 · 点击图表探索</span>
      </div>
      <button
        type="button"
        className="act-nav-btn primary"
        disabled={next == null}
        onClick={() => next != null && onJump(next)}
        aria-label={next != null ? `下一幕 ${ACTS[next].label}` : "已是最后一幕"}
      >
        下一幕 →
      </button>
    </div>
  );
}
