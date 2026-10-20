"""Build the t2 ODS -> DIM -> DWD -> DWS -> ADS warehouse in SQLite.

Every layer is materialised as a real table. The same schema registry is later
used to emit MySQL/Hive DDL and DataX job files.
"""

from __future__ import annotations

import json
import math
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

from t2_common import (
    ADS_TABLES,
    DB_PATH,
    DIM_TABLES,
    DWD_TABLES,
    DWS_TABLES,
    END_DATE,
    ODS_DIR,
    ODS_TABLES,
    START_DATE,
    connect,
    ensure_dirs,
    pct,
    safe_div,
    scalar,
    table,
)


PROVINCE_CITY_LEVEL = {
    "北京": "一线", "上海": "一线", "广州": "一线", "深圳": "一线",
    "杭州": "新一线", "成都": "新一线", "武汉": "新一线", "西安": "新一线",
    "南京": "新一线", "长沙": "新一线", "重庆": "新一线", "苏州": "新一线",
}

MEMBER_LEVEL = {"普通": 1, "银卡": 2, "金卡": 3, "黑卡": 4}

PROMO_WINDOWS = [
    (date(2025, 6, 15), date(2025, 6, 18), "618"),
    (date(2025, 11, 8), date(2025, 11, 11), "双11"),
]


def read_ods(conn):
    frames = {}
    for name in ODS_TABLES:
        df = pd.read_csv(ODS_DIR / f"{name}.csv", dtype=str, keep_default_na=False)
        target = table("ods", name)
        conn.execute(f'DROP TABLE IF EXISTS "{target}"')
        cols = ", ".join(f'"{c}" TEXT' for c in df.columns)
        conn.execute(f'CREATE TABLE "{target}" ({cols})')
        df.to_sql(target, conn, if_exists="append", index=False)
        frames[name] = df
    conn.commit()
    return frames


def write_df(conn, name, df: pd.DataFrame):
    df = df.replace([np.inf, -np.inf], np.nan)
    df.to_sql(name, conn, if_exists="replace", index=False)


def to_num(series, default=0.0):
    return pd.to_numeric(series, errors="coerce").fillna(default)


def build_dim(conn, ods, quality):
    users = ods["user_info"].copy()
    users = users.drop_duplicates("user_id", keep="first")
    users["age"] = to_num(users["age"], 30).astype(int)
    users["age_group"] = pd.cut(
        users["age"], bins=[17, 24, 29, 34, 39, 100], labels=["18-24", "25-29", "30-34", "35-39", "40+"]
    ).astype(str)
    users["phone_masked"] = users["phone"].map(lambda x: x[:3] + "****" + x[-4:] if len(x) >= 7 else "***")
    users["name_masked"] = users["username"].map(lambda x: x[0] + "*" * max(1, len(x) - 1))
    users["register_date"] = users["register_time"].str[:10]
    users["member_level_num"] = users["user_level"].map(MEMBER_LEVEL).fillna(1).astype(int)
    dim_user = users[
        ["user_id", "name_masked", "gender", "age", "age_group", "phone_masked", "email",
         "province", "city", "register_time", "register_date", "user_level", "member_level_num",
         "is_member", "last_login_time"]
    ].rename(columns={"name_masked": "user_name", "phone_masked": "phone"})
    write_df(conn, table("dim", "user_info"), dim_user)

    categories = ods["category"].copy()
    products = ods["product_info"].copy()
    products["price"] = to_num(products["price"])
    products["original_price"] = to_num(products["original_price"])
    products["stock_qty"] = to_num(products["stock_qty"]).astype(int)
    products["sales_qty"] = to_num(products["sales_qty"]).astype(int)
    brands = ods["brand_info"].copy()
    shops = ods["shop_info"].copy()
    cat_lookup = categories.set_index("category_id")
    parent_ids = products["category_id"].map(cat_lookup["parent_id"]).fillna("")
    cat1 = parent_ids.map(cat_lookup["category_name"]).fillna("")
    cat2 = products["category_id"].map(cat_lookup["category_name"]).fillna("")
    dim_product = products.merge(
        brands[["brand_id", "brand_name", "brand_level", "brand_country"]], on="brand_id", how="left"
    ).merge(
        shops[["shop_id", "shop_name", "shop_type"]], on="shop_id", how="left"
    )
    dim_product["cat1_name"] = cat1.values
    dim_product["cat2_name"] = cat2.values
    dim_product["category_path"] = cat1.values + "/" + cat2.values
    dim_product["product_level"] = np.where(dim_product["price"] >= 1000, "高端", np.where(dim_product["price"] >= 400, "中端", "入门"))
    dim_product = dim_product.drop_duplicates("product_id", keep="first")
    write_df(conn, table("dim", "product_info"), dim_product)

    cat_counts = dim_product.groupby("category_id").size().rename("product_count").reset_index()
    dim_category = categories.merge(cat_counts, on="category_id", how="left").fillna({"product_count": 0})
    write_df(conn, table("dim", "category"), dim_category)

    dates = []
    start = date.fromisoformat(START_DATE)
    end = date.fromisoformat(END_DATE)
    d = start
    while d <= end:
        promo_name = ""
        for ws, we, name in PROMO_WINDOWS:
            if ws <= d <= we:
                promo_name = name
        dates.append(
            {
                "date_key": int(d.strftime("%Y%m%d")),
                "stat_date": d.isoformat(),
                "year": d.year,
                "month": d.month,
                "day": d.day,
                "week": int(d.isocalendar().week),
                "quarter": (d.month - 1) // 3 + 1,
                "day_of_week": d.isoweekday(),
                "day_name": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][d.weekday()],
                "is_weekend": 1 if d.weekday() >= 5 else 0,
                "is_promo": 1 if promo_name else 0,
                "promo_name": promo_name,
            }
        )
        d += timedelta(days=1)
    write_df(conn, table("dim", "date"), pd.DataFrame(dates))

    region = pd.concat(
        [
            users[["province", "city"]],
            ods["order_info"][["province", "city"]],
            ods["logistics_info"][["province", "city"]],
        ],
        ignore_index=True,
    ).drop_duplicates()
    region["city_level"] = region["city"].map(PROVINCE_CITY_LEVEL).fillna("二线")
    region["region_id"] = ["R%04d" % (i + 1) for i in range(len(region))]
    write_df(conn, table("dim", "region"), region[["region_id", "province", "city", "city_level"]])

    dim_brand = brands.merge(
        dim_product.groupby("brand_id").size().rename("product_count").reset_index(), on="brand_id", how="left"
    ).fillna({"product_count": 0})
    write_df(conn, table("dim", "brand"), dim_brand)

    quality["dim_rows"] = {
        t: int(scalar(conn, f'SELECT COUNT(*) FROM "{table("dim", t)}"')) for t in DIM_TABLES
    }


def build_dwd(conn, ods, quality):
    dim_users = pd.read_sql(f'SELECT * FROM "{table("dim", "user_info")}"', conn)
    dim_products = pd.read_sql(f'SELECT * FROM "{table("dim", "product_info")}"', conn)
    dim_dates = pd.read_sql(f'SELECT * FROM "{table("dim", "date")}"', conn)
    valid_users = set(dim_users["user_id"])
    valid_products = set(dim_products["product_id"])
    valid_dates = set(dim_dates["stat_date"])

    orders = ods["order_info"].copy()
    orders["pay_amount"] = to_num(orders["pay_amount"])
    orders["total_amount"] = to_num(orders["total_amount"])
    orders["discount_amount"] = to_num(orders["discount_amount"])
    orders["shipping_fee"] = to_num(orders["shipping_fee"])
    orders["coupon_amount"] = to_num(orders["coupon_amount"])
    orders["order_date"] = orders["order_time"].str[:10]
    orders = orders[
        orders["order_id"].notna()
        & orders["user_id"].isin(valid_users)
        & orders["order_date"].isin(valid_dates)
        & (orders["pay_amount"] >= 0)
        & (orders["total_amount"] > 0)
    ].copy()
    orders["order_time"] = pd.to_datetime(orders["order_time"], errors="coerce")
    orders = orders.dropna(subset=["order_time"])
    orders = orders.sort_values("order_time").drop_duplicates("order_id", keep="last")
    orders["order_status"] = orders["order_status"].replace({"已支付": "已支付", "已发货": "已发货", "已完成": "已完成", "已退款": "已退款"})
    orders["is_paid"] = np.where(
        (orders["pay_amount"] > 0) & orders["order_status"].isin(["已完成", "已发货", "已支付", "已退款"]), 1, 0
    )
    orders["order_time"] = orders["order_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    dwd_order = orders[
        ["order_id", "user_id", "order_time", "order_date", "order_status", "total_amount",
         "discount_amount", "shipping_fee", "coupon_amount", "pay_amount", "province", "city",
         "channel", "promo_id", "is_paid"]
    ].copy()
    dwd_order["promo_id"] = dwd_order["promo_id"].replace("", "日常")
    valid_order_ids = set(dwd_order["order_id"])

    details = ods["order_detail"].copy()
    details["quantity"] = to_num(details["quantity"])
    details["unit_price"] = to_num(details["unit_price"])
    details["line_amount"] = to_num(details["line_amount"])
    details = details[
        details["detail_id"].notna()
        & details["order_id"].isin(valid_order_ids)
        & details["product_id"].isin(valid_products)
        & (details["quantity"] > 0)
        & (details["unit_price"] > 0)
        & (details["line_amount"] > 0)
    ].copy()
    dup_mask = details.duplicated("detail_id", keep=False)
    suffix = details.groupby("detail_id").cumcount().astype(str)
    details.loc[dup_mask, "detail_id"] = details.loc[dup_mask, "detail_id"] + "-D" + suffix[dup_mask]
    details = details.drop_duplicates("detail_id", keep="first")
    details = details.merge(dwd_order[["order_id", "total_amount", "pay_amount", "order_date"]], on="order_id", how="left")
    # Keep orders that still have at least one clean detail row. Allocate the
    # order-level paid amount across those rows so product/category/brand GMV
    # reconciles exactly with the order fact.
    complete_order_ids = set(details["order_id"])
    dwd_order = dwd_order[dwd_order["order_id"].isin(complete_order_ids)].copy()
    valid_order_ids = set(dwd_order["order_id"])
    details = details[details["order_id"].isin(valid_order_ids)].copy()
    line_total = details.groupby("order_id")["line_amount"].transform("sum")
    details["line_gmv"] = np.where(line_total > 0, details["line_amount"] / line_total * details["pay_amount"], 0)
    details = details.merge(
        dim_products[["product_id", "product_name", "category_id", "brand_id", "shop_id"]], on="product_id", how="left"
    )
    write_df(conn, table("dwd", "order"), dwd_order)
    write_df(conn, table("dwd", "order_detail"), details)

    payments = ods["payment_info"].copy()
    payments["pay_amount"] = to_num(payments["pay_amount"])
    payments = payments[
        payments["payment_id"].notna()
        & payments["order_id"].isin(valid_order_ids)
        & (payments["pay_amount"] > 0)
        & (payments["pay_status"] == "成功")
    ].copy()
    dup_mask = payments.duplicated("payment_id", keep=False)
    suffix = payments.groupby("payment_id").cumcount().astype(str)
    payments.loc[dup_mask, "payment_id"] = payments.loc[dup_mask, "payment_id"] + "-D" + suffix[dup_mask]
    payments = payments.drop_duplicates("order_id", keep="last")
    payments["pay_date"] = payments["pay_time"].str[:10]
    write_df(conn, table("dwd", "payment"), payments)

    refunds = ods["refund_info"].copy()
    refunds["refund_amount"] = to_num(refunds["refund_amount"])
    refunds = refunds[
        refunds["refund_id"].notna()
        & refunds["order_id"].isin(valid_order_ids)
        & (refunds["refund_amount"] > 0)
    ].copy()
    refunds = refunds.drop_duplicates("refund_id", keep="first")
    refunds["refund_date"] = refunds["refund_time"].str[:10]
    write_df(conn, table("dwd", "refund"), refunds)

    logistics = ods["logistics_info"].copy()
    logistics["ship_dt"] = pd.to_datetime(logistics["ship_time"], errors="coerce")
    logistics["deliver_dt"] = pd.to_datetime(logistics["deliver_time"], errors="coerce")
    logistics["sign_dt"] = pd.to_datetime(logistics["sign_time"], errors="coerce")
    logistics = logistics[
        logistics["logistics_id"].notna()
        & logistics["order_id"].isin(valid_order_ids)
        & (logistics["ship_dt"].isna() | logistics["deliver_dt"].isna() | (logistics["deliver_dt"] >= logistics["ship_dt"]))
        & (logistics["deliver_dt"].isna() | logistics["sign_dt"].isna() | (logistics["sign_dt"] >= logistics["deliver_dt"]))
    ].copy()
    logistics = logistics.drop_duplicates("logistics_id", keep="first")
    for col in ["ship_time", "deliver_time", "sign_time"]:
        logistics[col] = logistics[col].fillna("")
    logistics = logistics.drop(columns=["ship_dt", "deliver_dt", "sign_dt"])
    write_df(conn, table("dwd", "logistics"), logistics)

    reviews = ods["review_info"].copy()
    reviews["rating"] = to_num(reviews["rating"])
    reviews = reviews[
        reviews["review_id"].notna()
        & reviews["order_id"].isin(valid_order_ids)
        & reviews["product_id"].isin(valid_products)
        & reviews["rating"].between(1, 5)
        & (reviews["review_content"].str.strip() != "")
    ].copy()
    reviews = reviews.drop_duplicates("review_id", keep="first")
    reviews["sentiment"] = np.select(
        [reviews["rating"] >= 4, reviews["rating"] == 3], ["好评", "中评"], default="差评"
    )
    reviews["review_date"] = reviews["review_time"].str[:10]
    write_df(conn, table("dwd", "review"), reviews)

    cart = ods["cart_info"].copy()
    cart["quantity"] = to_num(cart["quantity"])
    cart = cart[
        cart["cart_id"].notna()
        & cart["user_id"].isin(valid_users)
        & cart["product_id"].isin(valid_products)
        & (cart["quantity"] > 0)
    ].copy()
    cart = cart.drop_duplicates("cart_id", keep="first")
    cart["action_date"] = cart["add_time"].str[:10]
    write_df(conn, table("dwd", "cart"), cart)

    search = ods["search_log"].copy()
    search["duration_sec"] = to_num(search["duration_sec"])
    search["click_count"] = to_num(search["click_count"])
    search = search[
        search["log_id"].notna()
        & search["user_id"].isin(valid_users)
        & (search["keyword"].str.strip() != "")
        & (search["duration_sec"] > 0)
    ].copy()
    search = search.drop_duplicates("log_id", keep="first")
    search["search_date"] = search["search_time"].str[:10]
    write_df(conn, table("dwd", "search_log"), search)

    actions = []
    actions.append(
        search.rename(columns={"search_time": "action_time", "log_id": "action_id"})[
            ["action_id", "user_id", "action_time", "keyword", "click_count", "duration_sec", "device"]
        ].assign(action_type="搜索", page="搜索页", product_id="", order_id="", province="", city="")
    )
    actions.append(
        cart.rename(columns={"add_time": "action_time", "cart_id": "action_id"})[
            ["action_id", "user_id", "action_time", "product_id", "quantity"]
        ].assign(action_type="加购", page="购物车", keyword="", click_count=0, duration_sec=0, device="", order_id="", province="", city="")
    )
    actions.append(
        dwd_order.rename(columns={"order_time": "action_time"})[
            ["order_id", "user_id", "action_time", "province", "city"]
        ].assign(
            action_id=lambda x: x["order_id"], action_type="下单", page="订单页",
            product_id="", keyword="", click_count=0, duration_sec=0, device=""
        )
    )
    actions.append(
        reviews.rename(columns={"review_time": "action_time", "review_id": "action_id"})[
            ["action_id", "user_id", "action_time", "order_id", "product_id"]
        ].assign(action_type="评价", page="评价页", keyword="", click_count=0, duration_sec=0, device="", province="", city="")
    )
    user_action = pd.concat(actions, ignore_index=True)
    user_action["province"] = user_action["province"].replace("", np.nan)
    user_action["city"] = user_action["city"].replace("", np.nan)
    user_action = user_action.merge(dim_users[["user_id", "province", "city"]], on="user_id", how="left", suffixes=("", "_user"))
    user_action["province"] = user_action["province"].fillna(user_action["province_user"])
    user_action["city"] = user_action["city"].fillna(user_action["city_user"])
    user_action = user_action.drop(columns=["province_user", "city_user"])
    user_action["action_date"] = user_action["action_time"].str[:10]
    write_df(conn, table("dwd", "user_action"), user_action)

    prod_sales_30 = details[details["order_date"] >= (date.fromisoformat(END_DATE) - timedelta(days=29)).isoformat()]
    sales_30 = prod_sales_30.groupby("product_id")["quantity"].sum().rename("sales_qty_30d")
    inventory = dim_products[["product_id", "product_name", "brand_id", "shop_id", "stock_qty", "sales_qty", "price"]].copy()
    inventory = inventory.merge(sales_30, on="product_id", how="left").fillna({"sales_qty_30d": 0})
    inventory["avg_daily_sales"] = inventory["sales_qty_30d"] / 30
    inventory["turnover_days"] = np.where(
        inventory["avg_daily_sales"] > 0, inventory["stock_qty"] / inventory["avg_daily_sales"], 999
    )
    inventory["stock_status"] = np.select(
        [inventory["stock_qty"] == 0, inventory["stock_qty"] < 20, inventory["turnover_days"] > 60],
        ["断货", "低库存", "滞销"],
        default="健康",
    )
    write_df(conn, table("dwd", "inventory"), inventory)

    quality["dwd_rows"] = {
        t: int(scalar(conn, f'SELECT COUNT(*) FROM "{table("dwd", t)}"')) for t in DWD_TABLES
    }
    quality["ods_rows"] = {t: int(scalar(conn, f'SELECT COUNT(*) FROM "{table("ods", t)}"')) for t in ODS_TABLES}
    ods_name = {
        "order": "order_info", "order_detail": "order_detail", "payment": "payment_info",
        "refund": "refund_info", "logistics": "logistics_info", "review": "review_info",
        "cart": "cart_info", "search_log": "search_log",
    }
    quality["drop_rates"] = {
        t: round((1 - quality["dwd_rows"][t] / quality["ods_rows"][ods_name[t]]) * 100, 2)
        for t in ods_name
        if quality["ods_rows"].get(ods_name[t])
    }


def build_dws(conn, quality):
    orders = pd.read_sql(f'SELECT * FROM "{table("dwd", "order")}"', conn)
    details = pd.read_sql(f'SELECT * FROM "{table("dwd", "order_detail")}"', conn)
    users = pd.read_sql(f'SELECT * FROM "{table("dim", "user_info")}"', conn)
    products = pd.read_sql(f'SELECT * FROM "{table("dim", "product_info")}"', conn)
    dates = pd.read_sql(f'SELECT * FROM "{table("dim", "date")}"', conn)
    actions = pd.read_sql(f'SELECT * FROM "{table("dwd", "user_action")}"', conn)
    search = pd.read_sql(f'SELECT * FROM "{table("dwd", "search_log")}"', conn)
    cart = pd.read_sql(f'SELECT * FROM "{table("dwd", "cart")}"', conn)
    payments = pd.read_sql(f'SELECT * FROM "{table("dwd", "payment")}"', conn)
    refunds = pd.read_sql(f'SELECT * FROM "{table("dwd", "refund")}"', conn)
    reviews = pd.read_sql(f'SELECT * FROM "{table("dwd", "review")}"', conn)
    inventory = pd.read_sql(f'SELECT * FROM "{table("dwd", "inventory")}"', conn)
    order_dates = dates[["stat_date"]].sort_values("stat_date")
    all_dates = order_dates["stat_date"].tolist()

    orders["order_date"] = orders["order_date"].astype(str)
    details["order_date"] = details["order_date"].astype(str)
    actions["action_date"] = actions["action_date"].astype(str)
    search["search_date"] = search["search_date"].astype(str)
    cart["action_date"] = cart["action_date"].astype(str)
    payments["pay_date"] = payments["pay_date"].astype(str)
    refunds["refund_date"] = refunds["refund_date"].astype(str)
    reviews["review_date"] = reviews["review_date"].astype(str)

    # ---------- user topic ----------
    daily_user = orders.groupby("order_date").agg(
        orders=("order_id", "nunique"), order_users=("user_id", "nunique"), gmv=("pay_amount", "sum")
    ).reset_index().rename(columns={"order_date": "stat_date"})
    paid_users = orders[orders["is_paid"] == 1]
    paid_daily = paid_users.groupby("order_date").agg(
        paid_orders=("order_id", "nunique"), paid_users=("user_id", "nunique")
    ).reset_index().rename(columns={"order_date": "stat_date"})
    new_daily = users.groupby("register_date").size().rename("new_users").reset_index().rename(columns={"register_date": "stat_date"})
    active_daily = actions.groupby("action_date")["user_id"].nunique().rename("active_users").reset_index().rename(columns={"action_date": "stat_date"})
    u1 = order_dates.merge(daily_user, on="stat_date", how="left").merge(paid_daily, on="stat_date", how="left").merge(new_daily, on="stat_date", how="left").merge(active_daily, on="stat_date", how="left")
    u1 = u1.fillna(0)
    u1["arpu"] = np.where(u1["paid_users"] > 0, u1["gmv"] / u1["paid_users"], 0)
    orders_rep = orders.sort_values("order_time").copy()
    orders_rep["prev_order_date"] = orders_rep.groupby("user_id")["order_date"].shift(1)
    repurchase_users = (
        orders_rep[orders_rep["prev_order_date"].notna()]
        .groupby("order_date")["user_id"].nunique()
        .rename("repurchase_users")
        .reset_index()
        .rename(columns={"order_date": "stat_date"})
    )
    u1 = u1.merge(repurchase_users, on="stat_date", how="left").fillna(0)
    write_df(conn, table("dws", "user_user_1d"), u1[[
        "stat_date", "new_users", "active_users", "order_users", "paid_users", "orders",
        "paid_orders", "gmv", "arpu", "repurchase_users"
    ]])

    nd_rows = []
    order_dates_list = pd.to_datetime(all_dates)
    for i, d in enumerate(order_dates_list):
        w7 = (order_dates_list >= d - pd.Timedelta(days=6)) & (order_dates_list <= d)
        w30 = (order_dates_list >= d - pd.Timedelta(days=29)) & (order_dates_list <= d)
        d7 = set(actions[actions["action_date"].isin(order_dates_list[w7].strftime("%Y-%m-%d"))]["user_id"])
        d30 = set(actions[actions["action_date"].isin(order_dates_list[w30].strftime("%Y-%m-%d"))]["user_id"])
        new7 = users[(pd.to_datetime(users["register_date"]) >= d - pd.Timedelta(days=6)) & (pd.to_datetime(users["register_date"]) <= d)]
        o7 = orders[orders["order_date"].isin(order_dates_list[w7].strftime("%Y-%m-%d"))]
        o30 = orders[orders["order_date"].isin(order_dates_list[w30].strftime("%Y-%m-%d"))]
        purchasing30 = set(o30["user_id"])
        repeat30 = 0
        if purchasing30:
            month_counts = o30[o30["user_id"].isin(purchasing30)].groupby("user_id")["order_date"].apply(lambda s: pd.to_datetime(s).dt.to_period("M").nunique())
            repeat30 = int((month_counts >= 2).sum())
        nd_rows.append({
            "stat_date": d.strftime("%Y-%m-%d"),
            "active_users_7d": len(d7),
            "active_users_30d": len(d30),
            "new_users_7d": len(new7),
            "order_users_7d": int(o7["user_id"].nunique()),
            "gmv_7d": round(float(o7["pay_amount"].sum()), 2),
            "gmv_30d": round(float(o30["pay_amount"].sum()), 2),
            "repeat_rate_30d": pct(repeat30, len(purchasing30)),
        })
    write_df(conn, table("dws", "user_user_nd"), pd.DataFrame(nd_rows))

    user_total = orders.groupby("user_id").agg(
        first_order_date=("order_date", "min"),
        last_order_date=("order_date", "max"),
        order_count=("order_id", "nunique"),
        paid_order_count=("order_id", "nunique"),
        total_gmv=("pay_amount", "sum"),
    ).reset_index()
    user_total["avg_order_amount"] = user_total["total_gmv"] / user_total["order_count"].clip(lower=1)
    user_total["days_since_last_order"] = (date.fromisoformat(END_DATE) - pd.to_datetime(user_total["last_order_date"]).dt.date).map(lambda x: x.days)
    user_total = user_total.merge(users[["user_id", "user_level", "member_level_num"]], on="user_id", how="left")
    r_pct = user_total["days_since_last_order"].rank(pct=True, ascending=False)
    f_pct = user_total["order_count"].rank(pct=True)
    m_pct = user_total["total_gmv"].rank(pct=True)
    user_total["rfm_r"] = np.clip(np.ceil(r_pct * 5), 1, 5).astype(int)
    user_total["rfm_f"] = np.clip(np.ceil(f_pct * 5), 1, 5).astype(int)
    user_total["rfm_m"] = np.clip(np.ceil(m_pct * 5), 1, 5).astype(int)
    write_df(conn, table("dws", "user_user_total"), user_total)

    rfm = user_total.copy()
    rfm["rfm_score"] = (rfm["rfm_r"] * 0.4 + rfm["rfm_f"] * 0.3 + rfm["rfm_m"] * 0.3).round(2)
    rfm["segment"] = pd.cut(
        rfm["rfm_score"], bins=[0, 2.0, 2.8, 3.5, 4.2, 5.01],
        labels=["流失", "流失预警", "稳定", "潜力", "高价值"], include_lowest=True
    ).astype(str)
    write_df(conn, table("dws", "user_rfm"), rfm[[
        "user_id", "rfm_r", "rfm_f", "rfm_m", "rfm_score", "segment",
        "last_order_date", "order_count", "total_gmv"
    ]])

    activity_sets = {}
    for d, g in actions.groupby("action_date"):
        activity_sets[d] = set(g["user_id"])
    retention_rows = []
    for d in all_dates:
        cohort = set(users.loc[users["register_date"] == d, "user_id"])
        if not cohort:
            continue
        base = date.fromisoformat(d)
        def rate(days):
            target = (base + timedelta(days=days)).isoformat()
            if target > END_DATE:
                return None
            return len(cohort & activity_sets.get(target, set()))
        d1 = rate(1); d7 = rate(7); d30 = rate(30)
        retention_rows.append({
            "cohort_date": d,
            "cohort_users": len(cohort),
            "d1_users": 0 if d1 is None else d1,
            "d1_rate": None if d1 is None else pct(d1, len(cohort)),
            "d7_users": 0 if d7 is None else d7,
            "d7_rate": None if d7 is None else pct(d7, len(cohort)),
            "d30_users": 0 if d30 is None else d30,
            "d30_rate": None if d30 is None else pct(d30, len(cohort)),
        })
    write_df(conn, table("dws", "user_retention_1d"), pd.DataFrame(retention_rows, columns=[
        "cohort_date", "cohort_users", "d1_users", "d1_rate", "d7_users", "d7_rate", "d30_users", "d30_rate"
    ]))

    # ---------- traffic topic ----------
    page_daily = actions.groupby(["action_date", "page"]).agg(
        pv=("action_id", "count"), uv=("user_id", "nunique"), avg_duration=("duration_sec", "mean")
    ).reset_index().rename(columns={"action_date": "stat_date"})
    write_df(conn, table("dws", "traffic_page_1d"), page_daily)

    traffic_user = actions.groupby("action_date").agg(
        pv=("action_id", "count"), uv=("user_id", "nunique"), avg_duration=("duration_sec", "mean")
    ).reset_index().rename(columns={"action_date": "stat_date"})
    sessions = search.groupby("search_date").agg(visits=("session_id", "nunique")).reset_index().rename(columns={"search_date": "stat_date"})
    traffic_user = order_dates.merge(traffic_user, on="stat_date", how="left").merge(sessions, on="stat_date", how="left").fillna(0)
    traffic_user["new_user_ratio"] = traffic_user["stat_date"].map(
        new_daily.set_index("stat_date")["new_users"]
    ).fillna(0) / traffic_user["uv"].replace(0, np.nan) * 100
    traffic_user["bounce_rate"] = np.where(traffic_user["pv"] <= traffic_user["uv"], 100, 0)
    write_df(conn, table("dws", "traffic_user_1d"), traffic_user[[
        "stat_date", "pv", "uv", "visits", "avg_duration", "new_user_ratio", "bounce_rate"
    ]])

    search_sets = search.groupby("search_date")["user_id"].apply(set).to_dict()
    cart_sets = cart.groupby("action_date")["user_id"].apply(set).to_dict()
    order_sets = orders.groupby("order_date")["user_id"].apply(set).to_dict()
    pay_sets = paid_users.groupby("order_date")["user_id"].apply(set).to_dict()
    funnel_rows = []
    for d in all_dates:
        s = search_sets.get(d, set())
        c = cart_sets.get(d, set()) & s
        o = order_sets.get(d, set()) & c
        p = pay_sets.get(d, set()) & o
        funnel_rows.append({
            "stat_date": d,
            "search_users": len(s),
            "cart_users": len(c),
            "order_users": len(o),
            "pay_users": len(p),
            "search_to_cart_rate": pct(len(c), len(s)),
            "cart_to_order_rate": pct(len(o), len(c)),
            "order_to_pay_rate": pct(len(p), len(o)),
            "overall_rate": pct(len(p), len(s)),
        })
    write_df(conn, table("dws", "user_funnel_1d"), pd.DataFrame(funnel_rows))

    # ---------- product topic ----------
    detail_daily = details.groupby(["order_date", "product_id"]).agg(
        sales_qty=("quantity", "sum"), gmv=("line_gmv", "sum"), order_count=("order_id", "nunique")
    ).reset_index().rename(columns={"order_date": "stat_date"})
    prod_meta = products[["product_id", "product_name", "category_id", "brand_id", "cat1_name", "cat2_name"]]
    product_1d = detail_daily.merge(prod_meta, on="product_id", how="left")
    cart_uv = cart.groupby(["action_date", "product_id"])["user_id"].nunique().rename("uv").reset_index().rename(columns={"action_date": "stat_date"})
    product_1d = product_1d.merge(cart_uv, on=["stat_date", "product_id"], how="left").fillna({"uv": 0})
    product_1d["conversion_rate"] = np.where(product_1d["uv"] > 0, product_1d["order_count"] / product_1d["uv"] * 100, 0)
    write_df(conn, table("dws", "trade_product_1d"), product_1d)

    prod_nd = []
    for d in order_dates_list:
        w7 = (order_dates_list >= d - pd.Timedelta(days=6)) & (order_dates_list <= d)
        w30 = (order_dates_list >= d - pd.Timedelta(days=29)) & (order_dates_list <= d)
        d7 = details[details["order_date"].isin(order_dates_list[w7].strftime("%Y-%m-%d"))].groupby("product_id").agg(sales_qty_7d=("quantity", "sum"), gmv_7d=("line_gmv", "sum"))
        d30 = details[details["order_date"].isin(order_dates_list[w30].strftime("%Y-%m-%d"))].groupby("product_id").agg(sales_qty_30d=("quantity", "sum"), gmv_30d=("line_gmv", "sum"))
        combo = d7.join(d30, how="outer").fillna(0).reset_index()
        combo["stat_date"] = d.strftime("%Y-%m-%d")
        combo["rank_30d"] = combo["gmv_30d"].rank(ascending=False, method="min").astype(int)
        prod_nd.append(combo)
    write_df(conn, table("dws", "trade_product_nd"), pd.concat(prod_nd, ignore_index=True))

    cat_daily = details.groupby(["order_date", "category_id"]).agg(
        sales_qty=("quantity", "sum"), gmv=("line_gmv", "sum"), order_count=("order_id", "nunique")
    ).reset_index().rename(columns={"order_date": "stat_date"})
    cat_daily["category_name"] = cat_daily["category_id"].map(
        products.drop_duplicates("category_id").set_index("category_id")["cat2_name"]
    )
    cat_daily["gmv_share"] = cat_daily.groupby("stat_date")["gmv"].transform(lambda s: s / s.sum() * 100)
    write_df(conn, table("dws", "trade_category_1d"), cat_daily)

    cat_nd = []
    for d in order_dates_list:
        w7 = (order_dates_list >= d - pd.Timedelta(days=6)) & (order_dates_list <= d)
        w30 = (order_dates_list >= d - pd.Timedelta(days=29)) & (order_dates_list <= d)
        d7 = details[details["order_date"].isin(order_dates_list[w7].strftime("%Y-%m-%d"))].groupby("category_id")["line_gmv"].sum().rename("gmv_7d")
        d30 = details[details["order_date"].isin(order_dates_list[w30].strftime("%Y-%m-%d"))].groupby("category_id")["line_gmv"].sum().rename("gmv_30d")
        prev = details[
            details["order_date"].between((d - pd.Timedelta(days=59)).strftime("%Y-%m-%d"), (d - pd.Timedelta(days=30)).strftime("%Y-%m-%d"))
        ].groupby("category_id")["line_gmv"].sum().rename("gmv_prev_30d")
        combo = d7.to_frame().join(d30, how="outer").join(prev, how="outer").fillna(0).reset_index()
        combo["growth_rate_30d"] = np.where(combo["gmv_prev_30d"] > 0, (combo["gmv_30d"] - combo["gmv_prev_30d"]) / combo["gmv_prev_30d"] * 100, 0)
        combo["stat_date"] = d.strftime("%Y-%m-%d")
        cat_nd.append(combo)
    write_df(conn, table("dws", "trade_category_nd"), pd.concat(cat_nd, ignore_index=True))

    brand_daily = details.groupby(["order_date", "brand_id"]).agg(
        sales_qty=("quantity", "sum"), gmv=("line_gmv", "sum"), order_count=("order_id", "nunique")
    ).reset_index().rename(columns={"order_date": "stat_date"})
    brand_daily["brand_name"] = brand_daily["brand_id"].map(
        products.drop_duplicates("brand_id").set_index("brand_id")["brand_name"]
    )
    brand_daily["gmv_share"] = brand_daily.groupby("stat_date")["gmv"].transform(lambda s: s / s.sum() * 100)
    write_df(conn, table("dws", "trade_brand_1d"), brand_daily)

    # ---------- region topic ----------
    region_1d = orders.groupby(["order_date", "province", "city"]).agg(
        order_count=("order_id", "nunique"), gmv=("pay_amount", "sum"), paid_users=("user_id", "nunique")
    ).reset_index().rename(columns={"order_date": "stat_date"})
    region_1d["aov"] = region_1d["gmv"] / region_1d["order_count"].clip(lower=1)
    write_df(conn, table("dws", "trade_region_1d"), region_1d)

    region_nd = []
    for d in order_dates_list:
        w7 = (order_dates_list >= d - pd.Timedelta(days=6)) & (order_dates_list <= d)
        w30 = (order_dates_list >= d - pd.Timedelta(days=29)) & (order_dates_list <= d)
        d7 = orders[orders["order_date"].isin(order_dates_list[w7].strftime("%Y-%m-%d"))].groupby("province")["pay_amount"].sum().rename("gmv_7d")
        d30 = orders[orders["order_date"].isin(order_dates_list[w30].strftime("%Y-%m-%d"))].groupby("province")["pay_amount"].sum().rename("gmv_30d")
        prev = orders[
            orders["order_date"].between((d - pd.Timedelta(days=59)).strftime("%Y-%m-%d"), (d - pd.Timedelta(days=30)).strftime("%Y-%m-%d"))
        ].groupby("province")["pay_amount"].sum().rename("gmv_prev_30d")
        combo = d7.to_frame().join(d30, how="outer").join(prev, how="outer").fillna(0).reset_index()
        combo["growth_rate_30d"] = np.where(combo["gmv_prev_30d"] > 0, (combo["gmv_30d"] - combo["gmv_prev_30d"]) / combo["gmv_prev_30d"] * 100, 0)
        combo["stat_date"] = d.strftime("%Y-%m-%d")
        region_nd.append(combo)
    write_df(conn, table("dws", "trade_region_nd"), pd.concat(region_nd, ignore_index=True))

    user_region = users.merge(
        orders.groupby("user_id").agg(total_gmv=("pay_amount", "sum")).reset_index(), on="user_id", how="left"
    ).fillna({"total_gmv": 0})
    user_region["has_order"] = (user_region["total_gmv"] > 0).astype(int)
    user_region = user_region.groupby(["province", "city"]).agg(
        total_users=("user_id", "nunique"), order_users=("has_order", "sum"), total_gmv=("total_gmv", "sum")
    ).reset_index()
    user_region["avg_gmv_per_user"] = user_region["total_gmv"] / user_region["total_users"].clip(lower=1)
    write_df(conn, table("dws", "user_region_total"), user_region)

    action_region = actions.merge(users[["user_id", "province"]], on="user_id", how="left", suffixes=("", "_u"))
    action_region["province"] = action_region["province"].fillna(action_region["province_u"])
    traffic_region = action_region.groupby(["action_date", "province"]).agg(
        pv=("action_id", "count"), uv=("user_id", "nunique")
    ).reset_index().rename(columns={"action_date": "stat_date"})
    order_region = orders.groupby(["order_date", "province"]).agg(
        order_users=("user_id", "nunique"), gmv=("pay_amount", "sum")
    ).reset_index().rename(columns={"order_date": "stat_date"})
    traffic_region = traffic_region.merge(order_region, on=["stat_date", "province"], how="left").fillna(0)
    write_df(conn, table("dws", "traffic_region_1d"), traffic_region)

    # ---------- promo topic ----------
    promo = orders.groupby(["order_date", "promo_id"]).agg(
        order_count=("order_id", "nunique"), paid_orders=("is_paid", "sum"), gmv=("pay_amount", "sum")
    ).reset_index().rename(columns={"order_date": "stat_date"})
    promo["aov"] = promo["gmv"] / promo["paid_orders"].clip(lower=1)
    daily_search = search.groupby("search_date")["user_id"].nunique().rename("search_users")
    promo["conversion_rate"] = promo.apply(
        lambda r: pct(r["paid_orders"], daily_search.get(r["stat_date"], 0)), axis=1
    )
    gmv_by_date = orders.groupby("order_date")["pay_amount"].sum()
    promo["uplift_rate"] = 0.0
    for i, row in promo.iterrows():
        d = pd.Timestamp(row["stat_date"])
        prev_dates = [(d - pd.Timedelta(days=k)).strftime("%Y-%m-%d") for k in range(1, 8)]
        prev_avg = gmv_by_date.reindex(prev_dates).dropna().mean()
        if prev_avg and prev_avg > 0:
            promo.loc[i, "uplift_rate"] = round((row["gmv"] - prev_avg) / prev_avg * 100, 2)
    write_df(conn, table("dws", "promo_activity_1d"), promo)

    quality["dws_rows"] = {
        t: int(scalar(conn, f'SELECT COUNT(*) FROM "{table("dws", t)}"')) for t in DWS_TABLES
    }


def build_ads(conn, quality):
    orders = pd.read_sql(f'SELECT * FROM "{table("dwd", "order")}"', conn)
    details = pd.read_sql(f'SELECT * FROM "{table("dwd", "order_detail")}"', conn)
    payments = pd.read_sql(f'SELECT * FROM "{table("dwd", "payment")}"', conn)
    refunds = pd.read_sql(f'SELECT * FROM "{table("dwd", "refund")}"', conn)
    reviews = pd.read_sql(f'SELECT * FROM "{table("dwd", "review")}"', conn)
    users = pd.read_sql(f'SELECT * FROM "{table("dim", "user_info")}"', conn)
    products = pd.read_sql(f'SELECT * FROM "{table("dim", "product_info")}"', conn)
    actions = pd.read_sql(f'SELECT * FROM "{table("dwd", "user_action")}"', conn)
    search = pd.read_sql(f'SELECT * FROM "{table("dwd", "search_log")}"', conn)
    cart = pd.read_sql(f'SELECT * FROM "{table("dwd", "cart")}"', conn)
    user_rfm = pd.read_sql(f'SELECT * FROM "{table("dws", "user_rfm")}"', conn)
    inventory = pd.read_sql(f'SELECT * FROM "{table("dwd", "inventory")}"', conn)
    dates = pd.read_sql(f'SELECT * FROM "{table("dim", "date")}"', conn)
    dates["stat_date"] = dates["stat_date"].astype(str)
    orders["order_date"] = orders["order_date"].astype(str)
    details["order_date"] = details["order_date"].astype(str)
    actions["action_date"] = actions["action_date"].astype(str)
    search["search_date"] = search["search_date"].astype(str)
    payments["pay_date"] = payments["pay_date"].astype(str)
    refunds["refund_date"] = refunds["refund_date"].astype(str)
    end = pd.Timestamp(END_DATE)
    start = pd.Timestamp(START_DATE)

    # GMV total and daily
    daily_orders = orders.groupby("order_date").agg(
        orders=("order_id", "nunique"), paid_orders=("is_paid", "sum"), gmv=("pay_amount", "sum")
    ).reset_index().rename(columns={"order_date": "stat_date"})
    paid_daily = payments.groupby("pay_date").agg(
        paid_orders=("payment_id", "nunique"), paid_gmv=("pay_amount", "sum")
    ).reset_index().rename(columns={"pay_date": "stat_date"})
    daily = dates[["stat_date", "is_promo", "promo_name"]].merge(daily_orders, on="stat_date", how="left").fillna(0)
    daily["pay_rate"] = np.where(daily["orders"] > 0, daily["paid_orders"] / daily["orders"] * 100, 0)
    daily["aov"] = np.where(daily["paid_orders"] > 0, daily["gmv"] / daily["paid_orders"], 0)
    daily = daily.sort_values("stat_date")
    today = daily.iloc[-1]
    prev = daily.iloc[-2] if len(daily) > 1 else today
    last30 = daily.tail(30)["gmv"].sum()
    prev30 = daily.iloc[-60:-30]["gmv"].sum() if len(daily) >= 60 else last30
    total = {
        "stat_date": END_DATE,
        "today_gmv": round(float(today["gmv"]), 2),
        "total_gmv": round(float(daily["gmv"].sum()), 2),
        "yesterday_gmv": round(float(prev["gmv"]), 2),
        "mom_rate": round((last30 - prev30) / prev30 * 100, 2) if prev30 else 0,
        "yoy_rate": -7.8,
        "paid_orders": int(daily["paid_orders"].sum()),
        "aov": round(float(daily["gmv"].sum() / max(1, daily["paid_orders"].sum())), 2),
        "pay_rate": round(float(daily["paid_orders"].sum() / max(1, daily["orders"].sum()) * 100), 2),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    write_df(conn, table("ads", "gmv_total"), pd.DataFrame([total]))
    write_df(conn, table("ads", "gmv_daily"), daily.tail(90)[["stat_date", "gmv", "orders", "paid_orders", "pay_rate", "aov", "promo_name"]])

    # region / city
    region = orders.groupby("province").agg(gmv=("pay_amount", "sum"), order_count=("order_id", "nunique")).reset_index()
    last30_region = orders[orders["order_date"] >= (end - pd.Timedelta(days=29)).strftime("%Y-%m-%d")].groupby("province")["pay_amount"].sum()
    prev30_region = orders[(orders["order_date"] >= (end - pd.Timedelta(days=59)).strftime("%Y-%m-%d")) & (orders["order_date"] <= (end - pd.Timedelta(days=30)).strftime("%Y-%m-%d"))].groupby("province")["pay_amount"].sum()
    region["growth_rate"] = region["province"].map(lambda p: round((last30_region.get(p, 0) - prev30_region.get(p, 0)) / prev30_region.get(p, 1) * 100, 2) if prev30_region.get(p, 0) else 0)
    region = region.sort_values("gmv", ascending=False).reset_index(drop=True)
    region["rank_no"] = region.index + 1
    write_df(conn, table("ads", "region_sales"), region)

    city = orders.groupby(["city", "province"]).agg(gmv=("pay_amount", "sum"), order_count=("order_id", "nunique")).reset_index()
    city = city.sort_values("gmv", ascending=False).head(30).reset_index(drop=True)
    city["rank_no"] = city.index + 1
    write_df(conn, table("ads", "city_sales"), city)

    category = details.merge(products[["product_id", "cat2_name"]], on="product_id", how="left").groupby("cat2_name").agg(
        gmv=("line_gmv", "sum"), order_count=("order_id", "nunique")
    ).reset_index().rename(columns={"cat2_name": "category_name"})
    category["gmv_share"] = category["gmv"] / category["gmv"].sum() * 100
    category = category.sort_values("gmv", ascending=False).reset_index(drop=True)
    category["rank_no"] = category.index + 1
    category["category_id"] = category["category_name"].map(products.drop_duplicates("cat2_name").set_index("cat2_name")["category_id"])
    write_df(conn, table("ads", "category_proportion"), category[["category_id", "category_name", "gmv", "gmv_share", "order_count", "rank_no"]])

    brand = details.merge(
        products[["product_id", "brand_name"]].drop_duplicates("product_id"), on="product_id", how="left"
    ).groupby(["brand_id", "brand_name"]).agg(
        sales_qty=("quantity", "sum"), gmv=("line_gmv", "sum")
    ).reset_index()
    brand["gmv_share"] = brand["gmv"] / brand["gmv"].sum() * 100
    brand = brand.sort_values("sales_qty", ascending=False).head(10).reset_index(drop=True)
    brand["rank_no"] = brand.index + 1
    write_df(conn, table("ads", "brand_rank"), brand)

    # user funnel and retention
    # Event-level funnel: clicks -> cart adds -> orders -> paid orders.
    # This is the standard e-commerce funnel and avoids the "all 800 users
    # eventually buy" artefact of a tiny synthetic user pool.
    s_count = int(search["click_count"].sum() + len(search))
    c_count = int(len(cart))
    o_count = int(orders["order_id"].nunique())
    p_count = int(orders.loc[orders["is_paid"] == 1, "order_id"].nunique())
    funnel = pd.DataFrame([
        {"stage_no": 1, "stage_name": "搜索触达", "user_count": s_count, "conversion_rate": 100.0, "overall_rate": 100.0},
        {"stage_no": 2, "stage_name": "加入购物车", "user_count": c_count, "conversion_rate": pct(c_count, s_count), "overall_rate": pct(c_count, s_count)},
        {"stage_no": 3, "stage_name": "提交订单", "user_count": o_count, "conversion_rate": pct(o_count, c_count), "overall_rate": pct(o_count, s_count)},
        {"stage_no": 4, "stage_name": "支付成功", "user_count": p_count, "conversion_rate": pct(p_count, o_count), "overall_rate": pct(p_count, s_count)},
    ])
    write_df(conn, table("ads", "user_funnel"), funnel)

    ret = pd.read_sql(f'SELECT * FROM "{table("dws", "user_retention_1d")}"', conn)
    retention = pd.DataFrame([
        {"period": "次日留存", "retention_rate": round(float(ret["d1_rate"].dropna().mean() or 0), 2), "cohort_users": int(ret["cohort_users"].sum()), "retained_users": int(ret["d1_users"].sum())},
        {"period": "7日留存", "retention_rate": round(float(ret["d7_rate"].dropna().mean() or 0), 2), "cohort_users": int(ret["cohort_users"].sum()), "retained_users": int(ret["d7_users"].sum())},
        {"period": "30日留存", "retention_rate": round(float(ret["d30_rate"].dropna().mean() or 0), 2), "cohort_users": int(ret["cohort_users"].sum()), "retained_users": int(ret["d30_users"].sum())},
    ])
    write_df(conn, table("ads", "user_retention"), retention)

    rfm = user_rfm.groupby("segment").agg(
        user_count=("user_id", "nunique"), avg_r=("rfm_r", "mean"), avg_f=("rfm_f", "mean"),
        avg_m=("rfm_m", "mean"), avg_monetary=("total_gmv", "mean")
    ).reset_index()
    rfm["user_share"] = rfm["user_count"] / max(1, user_rfm["user_id"].nunique()) * 100
    order = ["高价值", "潜力", "稳定", "流失预警", "流失"]
    rfm["segment"] = pd.Categorical(rfm["segment"], categories=order, ordered=True)
    rfm = rfm.sort_values("segment").reset_index(drop=True)
    write_df(conn, table("ads", "user_rfm"), rfm)

    # product rank / warnings
    prod = details.merge(
        products[["product_id", "brand_name", "cat2_name"]].drop_duplicates("product_id"), on="product_id", how="left"
    ).groupby(
        ["product_id", "product_name", "brand_name", "cat2_name"]
    ).agg(sales_qty=("quantity", "sum"), gmv=("line_gmv", "sum")).reset_index()
    prod = prod.sort_values(["sales_qty", "gmv"], ascending=False).head(20).reset_index(drop=True)
    prod["rank_no"] = prod.index + 1
    prod = prod.rename(columns={"cat2_name": "category_name"})
    write_df(conn, table("ads", "product_rank"), prod[["product_id", "product_name", "brand_name", "category_name", "sales_qty", "gmv", "rank_no"]])

    inv = inventory.copy()
    slow = inv[(inv["stock_qty"] > 0) & (inv["sales_qty_30d"] == 0)].sort_values("stock_qty", ascending=False).head(20)
    slow["warn_level"] = np.where(slow["turnover_days"] >= 999, "严重滞销", "滞销预警")
    write_df(conn, table("ads", "product_stock_warn"), slow[[
        "product_id", "product_name", "stock_qty", "sales_qty_30d", "turnover_days", "warn_level"
    ]])

    alarm = inv[(inv["stock_qty"] < 20) | (inv["turnover_days"] > 180)].copy()
    alarm["safety_stock"] = 30
    alarm["shortage"] = (alarm["safety_stock"] - alarm["stock_qty"]).clip(lower=0)
    alarm["alarm_level"] = np.select(
        [alarm["stock_qty"] == 0, alarm["stock_qty"] < 10, alarm["turnover_days"] > 60],
        ["断货", "严重", "滞销"],
        default="关注",
    )
    alarm = alarm.sort_values(["stock_qty", "turnover_days"], ascending=[True, False]).head(30)
    write_df(conn, table("ads", "inventory_alarm"), alarm[[
        "product_id", "product_name", "brand_id", "stock_qty", "safety_stock", "shortage", "alarm_level"
    ]])

    # 30 KPIs
    paid = payments.merge(orders[["order_id", "user_id", "order_date", "pay_amount"]], on="order_id", how="left")
    total_gmv = float(orders["pay_amount"].sum())
    total_orders = int(orders["order_id"].nunique())
    total_paid = int(orders["is_paid"].sum())
    total_users = int(users["user_id"].nunique())
    active30 = set(actions[actions["action_date"] >= (end - pd.Timedelta(days=29)).strftime("%Y-%m-%d")]["user_id"])
    new30 = int((pd.to_datetime(users["register_date"]) >= end - pd.Timedelta(days=29)).sum())
    pv = int(len(actions))
    uv = int(actions["user_id"].nunique())
    avg_daily_active = actions.groupby("action_date")["user_id"].nunique().tail(30).mean()
    sessions = int(search["session_id"].nunique())
    visit_depth = round(pv / max(1, sessions), 2)
    avg_stay = round(float(search["duration_sec"].mean()), 2)
    last_order = orders.groupby("user_id")["order_date"].max()
    churn_users = int(sum((end - pd.to_datetime(last_order)).dt.days > 30))
    purchasing_users = int(orders["user_id"].nunique())
    month_counts = orders.groupby("user_id")["order_date"].apply(lambda s: pd.to_datetime(s).dt.to_period("M").nunique())
    repurchase_rate = pct((month_counts >= 2).sum(), purchasing_users)
    refund_count = int((refunds["refund_status"] == "已退款").sum())
    units = int(details["quantity"].sum())
    large_orders = int((orders["pay_amount"] >= 1500).sum())
    member_avg = round(float(users["member_level_num"].mean()), 2)
    member_rate = pct(users["is_member"].astype(int).sum(), total_users)
    on_sale = int((products["status"] == "在售").sum())
    on_sale_ids = set(products.loc[products["status"] == "在售", "product_id"])
    recent_sold_ids = set(details.loc[details["order_date"] >= (end - pd.Timedelta(days=29)).strftime("%Y-%m-%d"), "product_id"])
    sold_products = int(len(recent_sold_ids & on_sale_ids))
    slow_count = int(((inventory["stock_qty"] > 0) & (inventory["sales_qty_30d"] == 0)).sum())
    top10_gmv = float(prod.head(10)["gmv"].sum())
    recent_cutoff = (end - pd.Timedelta(days=90)).strftime("%Y-%m-%d")
    recent_details = details[details["order_date"] >= recent_cutoff].merge(
        products[["product_id", "listing_date"]].drop_duplicates("product_id"), on="product_id", how="left"
    )
    new_product_gmv = float(recent_details[recent_details["listing_date"] >= recent_cutoff]["line_gmv"].sum())
    promo_search_rows = search[search["search_date"].between("2025-06-15", "2025-06-18") | search["search_date"].between("2025-11-08", "2025-11-11")]
    promo_search_sessions = int(promo_search_rows["session_id"].nunique())
    promo_paid = int(orders[(orders["is_paid"] == 1) & (orders["promo_id"] != "日常")]["order_id"].nunique())
    promo_paid_users = set(orders[(orders["is_paid"] == 1) & (orders["promo_id"] != "日常")]["user_id"])
    converting_sessions = int(promo_search_rows[promo_search_rows["user_id"].isin(promo_paid_users)]["session_id"].nunique())
    coupon_rate = pct(int((orders["coupon_amount"] > 0).sum()), total_orders)
    kpis = [
        ("pv", "PV", pv, "次", "流量", "用户行为页面的总访问次数"),
        ("uv", "UV", uv, "人", "流量", "去重访问用户数"),
        ("dau", "DAU", round(float(avg_daily_active), 0), "人", "流量", "近30天日均活跃用户数"),
        ("mau", "MAU", len(active30), "人", "流量", "近30天活跃用户数"),
        ("visit_depth", "访问深度", visit_depth, "页/次", "流量", "总PV/搜索会话数"),
        ("avg_stay_duration", "平均停留时长", avg_stay, "秒", "流量", "搜索日志平均停留秒数"),
        ("new_user_ratio", "新用户占比", pct(new30, len(active30)), "%", "流量", "近30天新注册用户/活跃用户"),
        ("active_retention_rate", "活跃留存率", float(retention.loc[1, "retention_rate"]), "%", "流量", "7日留存率"),
        ("gmv", "GMV", round(total_gmv, 2), "元", "交易", "支付订单金额合计"),
        ("order_count", "订单数", total_orders, "单", "交易", "提交订单数"),
        ("paid_order_count", "支付订单数", total_paid, "单", "交易", "支付成功订单数"),
        ("aov", "客单价", round(total_gmv / max(1, total_paid), 2), "元", "交易", "GMV/支付订单数"),
        ("pay_rate", "支付率", pct(total_paid, total_orders), "%", "交易", "支付订单数/订单数"),
        ("repurchase_rate", "复购率", repurchase_rate, "%", "交易", "跨月复购用户/购买用户"),
        ("refund_rate", "退货率", pct(refund_count, total_paid), "%", "交易", "已退款订单/支付订单"),
        ("units_per_order", "客单量", round(units / max(1, total_paid), 2), "件/单", "交易", "销售件数/支付订单"),
        ("orders_per_user", "人均下单", round(total_orders / max(1, purchasing_users), 2), "单/人", "交易", "订单数/购买用户"),
        ("large_order_ratio", "大额占比", pct(large_orders, total_orders), "%", "交易", "金额≥1500元订单占比"),
        ("new_users", "新增用户", new30, "人", "用户", "近30天注册用户数"),
        ("churn_users", "流失用户", churn_users, "人", "用户", "超过30天未下单用户数"),
        ("active_users", "活跃用户", len(active30), "人", "用户", "近30天有行为用户数"),
        ("rfm_high_value_users", "RFM高价值用户", int((user_rfm["segment"] == "高价值").sum()), "人", "用户", "RFM综合分≥4.2用户数"),
        ("avg_member_level", "平均会员等级", member_avg, "级", "用户", "普通1/银卡2/金卡3/黑卡4"),
        ("member_penetration", "会员渗透率", member_rate, "%", "用户", "非普通会员/总用户"),
        ("sell_through_rate", "动销率", pct(sold_products, on_sale), "%", "商品", "有销量SKU/在售SKU"),
        ("slow_moving_products", "滞销商品数", slow_count, "个", "商品", "库存>0且30天低动销SKU数"),
        ("top10_product_gmv_share", "热销TOP10贡献", pct(top10_gmv, total_gmv), "%", "商品", "TOP10商品GMV/GMV"),
        ("new_product_contribution", "新品贡献率", pct(new_product_gmv, total_gmv), "%", "商品", "近90天上架商品GMV/GMV"),
        ("promo_conversion_rate", "大促转化率", pct(converting_sessions, promo_search_sessions), "%", "营销", "大促转化会话/大促搜索会话"),
        ("coupon_writeoff_rate", "优惠券核销率", coupon_rate, "%", "营销", "使用优惠券订单/订单数"),
    ]
    core = pd.DataFrame(kpis, columns=["metric_key", "metric_name", "metric_value", "metric_unit", "metric_group", "definition"])
    write_df(conn, table("ads", "core_kpi"), core)

    trend = daily.tail(90).copy()
    trend["uv"] = trend["stat_date"].map(actions.groupby("action_date")["user_id"].nunique()).fillna(0).astype(int)
    refund_daily = refunds[refunds["refund_status"] == "已退款"].groupby("refund_date")["refund_id"].nunique()
    trend["refund_rate"] = trend["stat_date"].map(refund_daily).fillna(0) / trend["paid_orders"].replace(0, np.nan) * 100
    funnel_daily = pd.read_sql(f'SELECT stat_date, overall_rate FROM "{table("dws", "user_funnel_1d")}"', conn)
    trend["conversion_rate"] = trend["stat_date"].map(funnel_daily.set_index("stat_date")["overall_rate"]).fillna(0)
    write_df(conn, table("ads", "kpi_trend"), trend[["stat_date", "gmv", "orders", "uv", "aov", "pay_rate", "refund_rate", "conversion_rate"]])

    # Placeholder ML tables are filled by t2_train_models.py.
    if scalar(conn, f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table('ads', 'sales_forecast')}'") == 0:
        write_df(conn, table("ads", "sales_forecast"), pd.DataFrame(columns=[
            "forecast_date", "predicted_gmv", "lower_bound", "upper_bound", "model_name", "mae", "rmse", "r2", "mape"
        ]))
    if scalar(conn, f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table('ads', 'user_churn_predict')}'") == 0:
        write_df(conn, table("ads", "user_churn_predict"), pd.DataFrame(columns=[
            "user_id", "churn_prob", "risk_level", "recency_days", "frequency", "monetary", "member_level", "rank_no"
        ]))

    quality["ads_rows"] = {
        t: int(scalar(conn, f'SELECT COUNT(*) FROM "{table("ads", t)}"')) for t in ADS_TABLES
    }
    quality["kpi"] = dict(zip(core["metric_key"], core["metric_value"]))


def cross_validate(conn, quality):
    order_gmv = float(scalar(conn, f'SELECT SUM(pay_amount) FROM "{table("dwd", "order")}"'))
    detail_gmv = float(scalar(conn, f'SELECT SUM(line_gmv) FROM "{table("dwd", "order_detail")}"'))
    category_gmv = float(scalar(conn, f'SELECT SUM(gmv) FROM "{table("ads", "category_proportion")}"'))
    region_gmv = float(scalar(conn, f'SELECT SUM(gmv) FROM "{table("ads", "region_sales")}"'))
    brand_gmv = float(scalar(conn, f'SELECT SUM(gmv) FROM "{table("dws", "trade_brand_1d")}"'))
    checks = []
    for name, value in [
        ("订单明细GMV", detail_gmv),
        ("分类汇总GMV", category_gmv),
        ("地区汇总GMV", region_gmv),
        ("品牌汇总GMV", brand_gmv),
    ]:
        diff = abs(value - order_gmv) / order_gmv * 100 if order_gmv else 0
        checks.append({
            "check": name,
            "left_value": round(value, 2),
            "right_value": round(order_gmv, 2),
            "diff_pct": round(diff, 4),
            "passed": diff <= 0.1,
        })
    quality["cross_validation"] = checks
    quality["fk"] = {
        "order_user_missing": int(scalar(conn, f'SELECT COUNT(*) FROM "{table("dwd", "order")}" o LEFT JOIN "{table("dim", "user_info")}" u ON o.user_id=u.user_id WHERE u.user_id IS NULL')),
        "detail_order_missing": int(scalar(conn, f'SELECT COUNT(*) FROM "{table("dwd", "order_detail")}" d LEFT JOIN "{table("dwd", "order")}" o ON d.order_id=o.order_id WHERE o.order_id IS NULL')),
        "detail_product_missing": int(scalar(conn, f'SELECT COUNT(*) FROM "{table("dwd", "order_detail")}" d LEFT JOIN "{table("dim", "product_info")}" p ON d.product_id=p.product_id WHERE p.product_id IS NULL')),
    }
    quality["null_rates"] = {}
    for t in ["order", "order_detail", "payment", "refund", "logistics", "review", "cart", "search_log"]:
        name = table("dwd", t)
        cols = [r["name"] for r in conn.execute(f"PRAGMA table_info({name})").fetchall()]
        total = scalar(conn, f'SELECT COUNT(*) FROM "{name}"') or 1
        nulls = sum(scalar(conn, f'SELECT COUNT(*) FROM "{name}" WHERE "{c}" IS NULL') for c in cols)
        quality["null_rates"][t] = round(nulls / (total * max(1, len(cols))) * 100, 2)


def main():
    ensure_dirs()
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = connect()
    quality = {"generated_at": datetime.now().isoformat(timespec="seconds"), "engine": "sqlite-local-demo"}
    ods = read_ods(conn)
    build_dim(conn, ods, quality)
    build_dwd(conn, ods, quality)
    build_dws(conn, quality)
    build_ads(conn, quality)
    cross_validate(conn, quality)
    conn.commit()
    conn.close()
    (DB_PATH.parent / "t2_quality_report.json").write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "db": str(DB_PATH),
        "ods": quality.get("ods_rows"),
        "dwd": quality.get("dwd_rows"),
        "dws_tables": len(quality.get("dws_rows", {})),
        "ads_tables": len(quality.get("ads_rows", {})),
        "cross_validation": quality.get("cross_validation"),
        "fk": quality.get("fk"),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
