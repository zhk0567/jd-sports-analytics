import { useEffect, useRef, useState } from "react";

type Props = {
  value: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  className?: string;
};

function format(n: number, decimals: number, prefix: string, suffix: string) {
  const body =
    decimals > 0 ? n.toFixed(decimals) : Math.round(n).toLocaleString("zh-CN");
  return `${prefix}${body}${suffix}`;
}

export function CountUp({
  value,
  decimals = 0,
  prefix = "",
  suffix = "",
  className,
}: Props) {
  const ref = useRef<HTMLSpanElement>(null);
  const [text, setText] = useState(() =>
    format(value, decimals, prefix, suffix),
  );
  const started = useRef(false);
  const valueRef = useRef(value);

  useEffect(() => {
    valueRef.current = value;
    // if already animated once, jump to new value
    if (started.current) {
      setText(format(value, decimals, prefix, suffix));
    }
  }, [value, decimals, prefix, suffix]);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const run = () => {
      if (started.current) return;
      started.current = true;
      const start = performance.now();
      const dur = 900;
      const from = 0;
      const to = valueRef.current;

      const tick = (now: number) => {
        const t = Math.min(1, (now - start) / dur);
        const eased = 1 - Math.pow(1 - t, 3);
        const current = from + (to - from) * eased;
        setText(format(current, decimals, prefix, suffix));
        if (t < 1) requestAnimationFrame(tick);
        else setText(format(valueRef.current, decimals, prefix, suffix));
      };
      requestAnimationFrame(tick);
    };

    const io = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) run();
      },
      { threshold: 0.2 },
    );
    io.observe(el);
    const timer = window.setTimeout(run, 400);
    return () => {
      io.disconnect();
      window.clearTimeout(timer);
    };
  }, [decimals, prefix, suffix]);

  return (
    <span ref={ref} className={className}>
      {text}
    </span>
  );
}
