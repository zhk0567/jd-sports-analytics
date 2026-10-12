import { ACTS } from "../data/types";

type Props = {
  active: number;
  onJump: (index: number) => void;
};

export function ProgressRail({ active, onJump }: Props) {
  const prev = active > 0 ? active - 1 : null;
  const next = active < ACTS.length - 1 ? active + 1 : null;

  return (
    <nav className="progress-rail" aria-label="故事进度">
      <button
        type="button"
        className="rail-step"
        disabled={prev == null}
        aria-label={prev != null ? `上一幕 ${ACTS[prev].label}` : "已是第一幕"}
        onClick={() => prev != null && onJump(prev)}
      >
        ↑
      </button>

      <div className="rail-acts">
        {ACTS.map((act) => (
          <button
            key={act.id}
            type="button"
            className={active === act.index ? "active" : ""}
            aria-label={`第${act.index}幕 ${act.label}`}
            onClick={() => onJump(act.index)}
          >
            <span className="dot" />
            <span className="label">{act.label}</span>
          </button>
        ))}
      </div>

      <button
        type="button"
        className="rail-step"
        disabled={next == null}
        aria-label={next != null ? `下一幕 ${ACTS[next].label}` : "已是最后一幕"}
        onClick={() => next != null && onJump(next)}
      >
        ↓
      </button>

      <div className="rail-meta">
        {String(active).padStart(2, "0")}/{String(ACTS.length - 1).padStart(2, "0")}
      </div>
    </nav>
  );
}
