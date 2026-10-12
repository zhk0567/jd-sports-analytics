import { useCallback, useEffect, useState } from "react";
import { ActBrands } from "./acts/ActBrands";
import { ActOpen } from "./acts/ActOpen";
import { ActPrice } from "./acts/ActPrice";
import { ActScale } from "./acts/ActScale";
import { ActScene } from "./acts/ActScene";
import { ActShelf } from "./acts/ActShelf";
import { Ambient } from "./components/Ambient";
import { ProgressRail } from "./components/ProgressRail";
import { loadStory } from "./data/loadStory";
import { ACTS, type StoryData } from "./data/types";

export default function App() {
  const [story, setStory] = useState<StoryData | null>(null);
  const [error, setError] = useState<string>("");
  const [active, setActive] = useState(0);

  useEffect(() => {
    loadStory()
      .then(setStory)
      .catch((e: Error) => setError(e.message));
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute("data-act", String(active));
  }, [active]);

  useEffect(() => {
    const nodes = ACTS.map((a) => document.getElementById(a.id)).filter(
      Boolean,
    ) as HTMLElement[];
    if (!nodes.length) return;

    const io = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        if (!visible.length) return;
        const id = visible[0].target.id;
        const idx = ACTS.find((a) => a.id === id)?.index;
        if (idx != null) setActive(idx);
      },
      { threshold: [0.45, 0.6, 0.75], rootMargin: "-5% 0px -5% 0px" },
    );

    nodes.forEach((n) => io.observe(n));
    return () => io.disconnect();
  }, [story]);

  const jump = useCallback((index: number) => {
    const id = ACTS[index]?.id;
    if (!id) return;
    document.getElementById(id)?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }, []);

  useEffect(() => {
    if (!story) return;
    const onKey = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement | null)?.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
      if (
        e.key === "ArrowDown" ||
        e.key === "ArrowRight" ||
        e.key === "PageDown" ||
        e.key === " " ||
        e.key === "j"
      ) {
        e.preventDefault();
        jump(Math.min(active + 1, ACTS.length - 1));
      } else if (
        e.key === "ArrowUp" ||
        e.key === "ArrowLeft" ||
        e.key === "PageUp" ||
        e.key === "k"
      ) {
        e.preventDefault();
        jump(Math.max(active - 1, 0));
      } else if (e.key === "Home") {
        e.preventDefault();
        jump(0);
      } else if (e.key === "End") {
        e.preventDefault();
        jump(ACTS.length - 1);
      } else if (/^[1-6]$/.test(e.key)) {
        e.preventDefault();
        jump(Number(e.key) - 1);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [story, active, jump]);

  if (error) {
    return (
      <>
        <Ambient />
        <div className="story-app" style={{ paddingTop: "20vh" }}>
          <h1 className="hero-brand">
            jd-sports
            <br />
            <span>analytics</span>
          </h1>
          <p className="act-lead">无法加载故事数据：{error}</p>
          <p className="act-close">
            请先执行：python -m src.analysis.export_story
          </p>
        </div>
      </>
    );
  }

  if (!story) {
    return (
      <>
        <Ambient />
        <div className="story-app" style={{ paddingTop: "32vh" }}>
          <p className="act-lead">装载运动货架故事…</p>
        </div>
      </>
    );
  }

  return (
    <>
      <Ambient />
      <div className="story-app" data-act={active}>
        <ProgressRail active={active} onJump={jump} />
        <ActOpen story={story} onJump={jump} />
        <ActScale story={story} />
        <ActBrands story={story} />
        <ActPrice story={story} />
        <ActScene story={story} />
        <ActShelf story={story} />
      </div>
    </>
  );
}
