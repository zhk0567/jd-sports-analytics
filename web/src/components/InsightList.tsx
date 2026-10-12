type Props = {
  items: string[];
  title?: string;
  max?: number;
  compact?: boolean;
};

export function InsightList({
  items,
  title = "Key readings",
  max = 3,
  compact = false,
}: Props) {
  const list = (items || []).slice(0, max);
  if (!list.length) return null;
  return (
    <div className={`insight-box${compact ? " compact" : ""}`}>
      <div className="insight-title">{title}</div>
      <ul>
        {list.map((t) => (
          <li key={t}>{t}</li>
        ))}
      </ul>
    </div>
  );
}
