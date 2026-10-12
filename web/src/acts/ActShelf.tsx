import { useMemo, useState } from "react";
import { ActShell } from "../components/ActShell";
import type { StoryData } from "../data/types";

type Props = { story: StoryData };

/** Prefer a larger JD CDN variant when possible. */
function enlargeJdImage(url: string): string {
  if (!url) return url;
  return url.replace(/\/n[0-9]+\//, "/n0/");
}

export function ActShelf({ story }: Props) {
  const all = story.shelf_products;
  const brands = useMemo(
    () =>
      Array.from(new Set(all.map((p) => p.brand).filter(Boolean))).slice(0, 8),
    [all],
  );
  const scenes = useMemo(
    () =>
      Array.from(
        new Set(all.map((p) => p.sport_scene).filter(Boolean)),
      ).slice(0, 6),
    [all],
  );

  const [brand, setBrand] = useState<string | null>(null);
  const [scene, setScene] = useState<string | null>(null);
  const [picked, setPicked] = useState<string | null>(null);

  const filtered = useMemo(() => {
    return all.filter((p) => {
      if (brand && p.brand !== brand) return false;
      if (scene && p.sport_scene !== scene) return false;
      return true;
    });
  }, [all, brand, scene]);

  const look = filtered.slice(0, 6);
  const focus = look.find((p) => p.sku_id === picked) || look[0] || null;
  const focusImg = enlargeJdImage((focus?.image_url || "").trim());

  return (
    <ActShell
      id="act-5"
      index={5}
      label="货架"
      claim={
        <>
          落到<em>具体商品</em>
        </>
      }
      lead={story.thesis.shelf}
      close={story.thesis.close}
      insights={story.insights?.shelf}
    >
      <div className="stage-fill shelf-stage">
        <div className="shelf-filters">
          <div className="chip-row shelf-chips">
            <button
              type="button"
              className={`chip${!brand ? " active" : ""}`}
              onClick={() => setBrand(null)}
            >
              品牌·全部
            </button>
            {brands.map((b) => (
              <button
                type="button"
                key={b}
                className={`chip${brand === b ? " active" : ""}`}
                onClick={() => setBrand((prev) => (prev === b ? null : b))}
              >
                {b}
              </button>
            ))}
          </div>
          <div className="chip-row shelf-chips">
            <button
              type="button"
              className={`chip${!scene ? " active" : ""}`}
              onClick={() => setScene(null)}
            >
              场景·全部
            </button>
            {scenes.map((s) => (
              <button
                type="button"
                key={s}
                className={`chip${scene === s ? " active" : ""}`}
                onClick={() =>
                  setScene((prev) => (prev === s ? null : s || null))
                }
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        <div className="shelf-interact">
          <div className="lookbook catalog">
            {look.length === 0 ? (
              <div className="empty-hint">没有匹配商品，试试清除筛选。</div>
            ) : (
              look.map((p, i) => {
                const price =
                  p.price != null ? `¥${Math.round(Number(p.price))}` : "—";
                const img = enlargeJdImage((p.image_url || "").trim());
                const active = focus?.sku_id === p.sku_id;
                return (
                  <button
                    type="button"
                    key={p.sku_id || i}
                    className={`product-tile${active ? " active" : ""}`}
                    onClick={() => setPicked(p.sku_id)}
                  >
                    <div className="thumb">
                      {img ? (
                        <img src={img} alt="" loading="lazy" decoding="async" />
                      ) : (
                        <div className="thumb-fallback" />
                      )}
                    </div>
                    <div className="tile-body">
                      <div className="tile-top">
                        <span className="tile-brand">
                          {p.brand || "未知"}
                          {p.sport_scene ? ` · ${p.sport_scene}` : ""}
                        </span>
                        <span className="tile-price">{price}</span>
                      </div>
                      <div className="tile-title">{p.title}</div>
                    </div>
                  </button>
                );
              })
            )}
          </div>

          {focus ? (
            <aside className="inspect-card">
              <div className="inspect-hero">
                {focusImg ? (
                  <img src={focusImg} alt="" />
                ) : (
                  <div className="thumb-fallback" />
                )}
              </div>
              <div className="inspect-body">
                <div className="inspect-kicker">Selected SKU</div>
                <div className="inspect-brand">
                  {focus.brand}
                  {focus.sport_scene ? ` · ${focus.sport_scene}` : ""}
                </div>
                <h3 className="inspect-title">{focus.title}</h3>
                <div className="inspect-price">
                  {focus.price != null
                    ? `¥${Math.round(Number(focus.price))}`
                    : "—"}
                </div>
                <dl className="inspect-meta">
                  <div>
                    <dt>店铺</dt>
                    <dd>{focus.shop_name || "—"}</dd>
                  </div>
                  <div>
                    <dt>评论</dt>
                    <dd>
                      {focus.comment_count != null
                        ? focus.comment_count.toLocaleString()
                        : "—"}
                    </dd>
                  </div>
                  <div>
                    <dt>SKU</dt>
                    <dd>{focus.sku_id}</dd>
                  </div>
                </dl>
                <a
                  className="inspect-link"
                  href={focus.product_url || "#"}
                  target="_blank"
                  rel="noreferrer"
                >
                  打开京东详情 →
                </a>
              </div>
            </aside>
          ) : null}
        </div>
      </div>
    </ActShell>
  );
}
