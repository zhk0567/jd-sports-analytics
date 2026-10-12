import { motion } from "framer-motion";
import { CountUp } from "../components/CountUp";
import type { StoryData } from "../data/types";

type Props = {
  story: StoryData;
  onJump?: (index: number) => void;
};

const fade = {
  initial: { y: 12 },
  animate: { y: 0 },
  transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] },
};

export function ActOpen({ story, onJump }: Props) {
  const ov = story.overview;
  const med = ov.price_median != null ? Math.round(ov.price_median) : 0;
  const mean = ov.price_mean != null ? Math.round(ov.price_mean) : 0;
  const commentsWan = Math.round((ov.comment_sum || 0) / 10000);
  const notes = (story.insights?.open || []).slice(0, 2);

  return (
    <section className="act act-open" id="act-0" data-act={0}>
      <div className="open-stage">
        <div className="open-watermark" aria-hidden>
          {ov.product_count > 999
            ? `${Math.round(ov.product_count / 1000)}K`
            : ov.product_count}
        </div>

        <div className="open-left">
          <p className="act-kicker">
            <span className="bar" />
            <span>Act 00 · 开场</span>
          </p>

          <motion.h1 className="hero-brand" {...fade}>
            jd-sports
            <br />
            <span>analytics</span>
          </motion.h1>

          <motion.p
            className="open-quote"
            {...fade}
            transition={{ ...fade.transition, delay: 0.05 }}
          >
            {story.thesis.open}
          </motion.p>

          {notes.length > 0 ? (
            <ul className="open-notes">
              {notes.map((n) => (
                <li key={n}>{n}</li>
              ))}
            </ul>
          ) : null}

          <div className="open-strip">
            {story.shelf_products.slice(0, 5).map((p) => (
              <a
                key={p.sku_id}
                className="tile"
                href={p.product_url || "#"}
                target="_blank"
                rel="noreferrer"
                style={
                  p.image_url
                    ? { backgroundImage: `url(${p.image_url})` }
                    : undefined
                }
                title={p.title}
              />
            ))}
          </div>

          <button
            type="button"
            className="scroll-hint as-btn"
            onClick={() => onJump?.(1)}
          >
            <i />
            下一幕 · 规模
          </button>
        </div>

        <motion.div
          className="open-right open-stats"
          initial={{ x: 12 }}
          animate={{ x: 0 }}
          transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
        >
          <button
            type="button"
            className="open-stat interactive"
            onClick={() => onJump?.(1)}
          >
            <div className="label">样本体量</div>
            <div className="value accent">
              <CountUp value={ov.product_count} />
            </div>
            <span className="stat-go">规模 →</span>
          </button>
          <button
            type="button"
            className="open-stat interactive"
            onClick={() => onJump?.(3)}
          >
            <div className="label">中位 / 均价</div>
            <div className="value">
              <CountUp value={med} prefix="¥" />
              <span className="dim"> / ¥{mean.toLocaleString()}</span>
            </div>
            <span className="stat-go">价格 →</span>
          </button>
          <button
            type="button"
            className="open-stat interactive"
            onClick={() => onJump?.(2)}
          >
            <div className="label">品牌 · 店铺</div>
            <div className="value">
              <CountUp value={ov.brand_count} />
              <span className="dim">
                {" "}
                · {ov.shop_count.toLocaleString()}
              </span>
            </div>
            <span className="stat-go">品牌 →</span>
          </button>
          <button
            type="button"
            className="open-stat interactive"
            onClick={() => onJump?.(1)}
          >
            <div className="label">自营 · 已知品牌</div>
            <div className="value">
              <CountUp
                value={(ov.self_operated_rate ?? 0) * 100}
                decimals={0}
                suffix="%"
              />
              <span className="dim">
                {" "}
                · {Math.round((ov.known_brand_rate ?? 0) * 100)}%
              </span>
            </div>
            <span className="stat-go">规模 →</span>
          </button>
          <div className="open-stat span-2">
            <div className="label">评论总量（万）</div>
            <div className="value">
              <CountUp value={commentsWan} />
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
