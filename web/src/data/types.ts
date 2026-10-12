export type Overview = {
  product_count: number;
  brand_count: number;
  shop_count: number;
  price_mean: number | null;
  price_median: number | null;
  comment_sum: number;
  self_operated_rate: number | null;
  known_brand_rate?: number | null;
  price_p25?: number | null;
  price_p75?: number | null;
  price_p90?: number | null;
  premium_share?: number | null;
};

export type NamedCount = {
  brand?: string;
  category_guess?: string;
  label?: string;
  price_band?: string;
  sport_scene?: string;
  gender_guess?: string;
  shop_name?: string;
  count: number;
  share?: number;
  price_mean?: number;
  price_median?: number;
  comment_sum?: number;
};

export type BrandCategory = {
  brand: string;
  category_label: string;
  count: number;
};

export type BrandPrice = {
  brand: string;
  count: number;
  price_mean: number;
  comment_sum: number;
};

export type SceneCategory = {
  sport_scene: string;
  category_label: string;
  count: number;
};

export type ShelfProduct = {
  sku_id: string;
  title: string;
  brand: string;
  price: number | null;
  category_guess?: string;
  sport_scene?: string;
  gender_guess?: string;
  image_url?: string;
  product_url?: string;
  shop_name?: string;
  comment_count?: number;
};

export type StoryData = {
  generated_at: string;
  project: string;
  thesis: Record<string, string>;
  insights: Record<string, string[]>;
  overview: Overview;
  by_brand: NamedCount[];
  by_category: NamedCount[];
  by_price_band: NamedCount[];
  by_scene: NamedCount[];
  by_gender: NamedCount[];
  brand_category: BrandCategory[];
  brand_price_scatter: BrandPrice[];
  scene_category: SceneCategory[];
  top_shops: NamedCount[];
  shelf_products: ShelfProduct[];
};

export const ACTS = [
  { id: "act-0", index: 0, label: "开场" },
  { id: "act-1", index: 1, label: "规模" },
  { id: "act-2", index: 2, label: "品牌" },
  { id: "act-3", index: 3, label: "价格" },
  { id: "act-4", index: 4, label: "场景" },
  { id: "act-5", index: 5, label: "货架" },
] as const;
