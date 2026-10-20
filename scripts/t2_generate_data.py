"""Generate the 12 ODS CSV files for group 2 (sports).

Sports-specific behaviour is injected on purpose:
* 68% male shoppers, with a male-skewed product mix;
* strong spring/autumn outdoor seasonality and winter outerwear demand;
* concentrated brands (Nike/Adidas/Li-Ning/Anta lead the shelf);
* mid-to-high AOV, 618 and Double 11 traffic/GMV spikes;
* realistic shoe sizes, colours, materials, target groups and seasons.

The row counts follow the task manual exactly (24,995 rows in total).
"""

from __future__ import annotations

import json
import math
import random
from collections import Counter
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

from t2_common import (
    END_DATE,
    GROUP_NO,
    ODS_DIR,
    ODS_TABLES,
    SEED,
    START_DATE,
    ensure_dirs,
)


RNG = random.Random(SEED)
NP_RNG = np.random.default_rng(SEED)

START = date.fromisoformat(START_DATE)
END = date.fromisoformat(END_DATE)
DAYS = (END - START).days + 1

CATEGORY_ROWS = [
    ("C001", "运动鞋", "", 1),
    ("C002", "运动服饰", "", 1),
    ("C003", "健身训练", "", 1),
    ("C004", "户外装备", "", 1),
    ("C005", "球类运动", "", 1),
    ("C006", "跑步鞋", "C001", 2),
    ("C007", "篮球鞋", "C001", 2),
    ("C008", "训练鞋", "C001", 2),
    ("C009", "足球鞋", "C001", 2),
    ("C010", "户外徒步鞋", "C001", 2),
    ("C011", "羽毛球鞋", "C001", 2),
    ("C012", "休闲运动鞋", "C001", 2),
    ("C013", "儿童运动鞋", "C001", 2),
    ("C014", "跑步T恤", "C002", 2),
    ("C015", "篮球服", "C002", 2),
    ("C016", "健身背心", "C002", 2),
    ("C017", "瑜伽服", "C002", 2),
    ("C018", "运动裤", "C002", 2),
    ("C019", "冲锋衣", "C002", 2),
    ("C020", "羽绒服", "C002", 2),
    ("C021", "运动内衣", "C002", 2),
    ("C022", "运动外套", "C002", 2),
    ("C023", "瑜伽垫", "C003", 2),
    ("C024", "哑铃", "C003", 2),
    ("C025", "跳绳", "C003", 2),
    ("C026", "跑步机", "C003", 2),
    ("C027", "动感单车", "C003", 2),
    ("C028", "护具", "C003", 2),
    ("C029", "运动手表", "C003", 2),
    ("C030", "蛋白粉", "C003", 2),
    ("C031", "帐篷", "C004", 2),
    ("C032", "登山杖", "C004", 2),
    ("C033", "骑行头盔", "C004", 2),
    ("C034", "泳镜", "C004", 2),
    ("C035", "羽毛球拍", "C005", 2),
    ("C036", "篮球", "C005", 2),
    ("C037", "足球", "C005", 2),
    ("C038", "网球拍", "C005", 2),
    ("C039", "运动包", "C005", 2),
    ("C040", "水壶", "C005", 2),
]

BRANDS = [
    ("B001", "Nike", "美国", "一线", "运动鞋", 1972, 1.00),
    ("B002", "Adidas", "德国", "一线", "运动鞋", 1949, 0.95),
    ("B003", "李宁", "中国", "一线", "运动服饰", 1990, 0.92),
    ("B004", "安踏", "中国", "一线", "运动鞋", 1991, 0.90),
    ("B005", "特步", "中国", "二线", "跑步鞋", 2001, 0.66),
    ("B006", "361°", "中国", "二线", "跑步鞋", 2003, 0.60),
    ("B007", "匹克", "中国", "二线", "篮球鞋", 1989, 0.56),
    ("B008", "乔丹", "中国", "二线", "篮球鞋", 2000, 0.52),
    ("B009", "鸿星尔克", "中国", "二线", "运动鞋", 2000, 0.48),
    ("B010", "回力", "中国", "三线", "休闲运动鞋", 1927, 0.40),
    ("B011", "斯凯奇", "美国", "二线", "休闲运动鞋", 1992, 0.55),
    ("B012", "匡威", "美国", "二线", "休闲运动鞋", 1908, 0.45),
    ("B013", "彪马", "德国", "二线", "运动鞋", 1948, 0.50),
    ("B014", "安德玛", "美国", "一线", "健身训练", 1996, 0.62),
    ("B015", "亚瑟士", "日本", "一线", "跑步鞋", 1949, 0.58),
    ("B016", "美津浓", "日本", "二线", "跑步鞋", 1906, 0.42),
    ("B017", "迪卡侬", "法国", "二线", "户外装备", 1976, 0.68),
    ("B018", "Keep", "中国", "二线", "健身训练", 2014, 0.44),
    ("B019", "北面", "美国", "一线", "户外装备", 1966, 0.54),
    ("B020", "始祖鸟", "加拿大", "高端", "户外装备", 1989, 0.32),
    ("B021", "哥伦比亚", "美国", "二线", "户外装备", 1938, 0.38),
    ("B022", "探路者", "中国", "三线", "户外装备", 1999, 0.30),
    ("B023", "骆驼", "中国", "三线", "户外装备", 2000, 0.36),
    ("B024", "沃特", "中国", "三线", "篮球鞋", 1995, 0.22),
    ("B025", "贵人鸟", "中国", "三线", "运动鞋", 1987, 0.20),
    ("B026", "尤尼克斯", "日本", "一线", "羽毛球拍", 1946, 0.28),
    ("B027", "威尔胜", "美国", "二线", "篮球", 1913, 0.26),
    ("B028", "斯伯丁", "美国", "二线", "篮球", 1876, 0.24),
    ("B029", "速比涛", "澳大利亚", "二线", "泳镜", 1928, 0.18),
    ("B030", "凯乐石", "中国", "二线", "户外装备", 2003, 0.25),
]

SHOPS = [
    ("S001", "京东运动自营旗舰店", "自营", "北京", "北京", 4.92, "2015-03-18"),
    ("S002", "Nike京东官方旗舰店", "品牌旗舰", "上海", "上海", 4.88, "2016-06-01"),
    ("S003", "Adidas京东官方旗舰店", "品牌旗舰", "上海", "上海", 4.87, "2016-06-01"),
    ("S004", "李宁京东官方旗舰店", "品牌旗舰", "北京", "北京", 4.86, "2017-02-14"),
    ("S005", "安踏京东官方旗舰店", "品牌旗舰", "福建", "泉州", 4.85, "2017-03-22"),
    ("S006", "特步跑步专营店", "品牌专营", "福建", "泉州", 4.78, "2018-01-08"),
    ("S007", "361°运动专营店", "品牌专营", "福建", "泉州", 4.76, "2018-05-20"),
    ("S008", "匹克篮球装备店", "品牌专营", "福建", "泉州", 4.74, "2018-08-12"),
    ("S009", "迪卡侬户外旗舰店", "品牌旗舰", "上海", "上海", 4.83, "2015-11-11"),
    ("S010", "北面户外旗舰店", "品牌旗舰", "北京", "北京", 4.89, "2017-09-01"),
    ("S011", "Keep健身器械旗舰店", "品牌旗舰", "北京", "北京", 4.72, "2019-04-18"),
    ("S012", "尤尼克斯羽毛球专营店", "品牌专营", "江苏", "南京", 4.81, "2018-03-15"),
    ("S013", "运动潮流集合店", "多品牌集合", "浙江", "杭州", 4.65, "2019-07-07"),
    ("S014", "户外探险装备店", "多品牌集合", "四川", "成都", 4.60, "2020-03-10"),
    ("S015", "京东运动好物工厂店", "工厂店", "广东", "广州", 4.55, "2021-01-20"),
]

PROVINCES = [
    ("广东", ["广州", "深圳", "东莞", "佛山"], 0.15, "一线"),
    ("江苏", ["南京", "苏州", "无锡"], 0.10, "新一线"),
    ("浙江", ["杭州", "宁波", "温州"], 0.10, "新一线"),
    ("山东", ["济南", "青岛", "烟台"], 0.08, "二线"),
    ("北京", ["北京"], 0.09, "一线"),
    ("上海", ["上海"], 0.09, "一线"),
    ("河南", ["郑州", "洛阳"], 0.06, "二线"),
    ("四川", ["成都", "绵阳"], 0.06, "新一线"),
    ("湖北", ["武汉", "宜昌"], 0.05, "新一线"),
    ("福建", ["厦门", "福州", "泉州"], 0.05, "二线"),
    ("河北", ["石家庄", "唐山"], 0.04, "二线"),
    ("湖南", ["长沙", "株洲"], 0.04, "新一线"),
    ("安徽", ["合肥", "芜湖"], 0.035, "二线"),
    ("陕西", ["西安", "咸阳"], 0.035, "新一线"),
    ("辽宁", ["沈阳", "大连"], 0.03, "二线"),
    ("江西", ["南昌", "赣州"], 0.025, "二线"),
    ("重庆", ["重庆"], 0.025, "新一线"),
    ("云南", ["昆明", "曲靖"], 0.02, "二线"),
    ("广西", ["南宁", "桂林"], 0.02, "二线"),
    ("山西", ["太原", "大同"], 0.015, "二线"),
]

CITY_LEVEL = {"北京": "一线", "上海": "一线", "广州": "一线", "深圳": "一线"}
for province, cities, _, _ in PROVINCES:
    for city in cities:
        CITY_LEVEL.setdefault(city, "新一线" if province in {"江苏", "浙江", "四川", "湖北", "湖南", "陕西", "重庆"} else "二线")

SURNAMES = list("赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳鲍史唐费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卞齐康伍余元卜顾孟平黄和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝董梁杜阮蓝闵席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍虞万支柯管卢莫经房裘缪干解应宗丁宣贲邓郁单杭洪包诸左石崔吉纽龚程嵇邢滑裴陆荣翁荀羊於惠甄曲家封芮羿储靳汲邴糜松井段富巫乌焦巴弓牧隗山谷车侯宓蓬全郗班仰秋仲伊宫宁仇栾暴甘钭厉戎祖武符刘景詹束龙叶幸司韶郜黎蓟薄印宿白怀蒲邰从鄂索咸籍赖卓蔺屠蒙池乔阴胥能苍双闻莘党翟谭贡劳逄姬申扶堵冉宰郦雍却璩桑桂濮牛寿通边扈燕冀郏浦尚农温别庄晏柴瞿阎充慕连茹习宦艾鱼容向古易慎戈廖庾终暨居衡步都耿满弘匡国文寇广禄阙东欧殳沃利蔚越夔隆师巩厍聂晁勾敖融冷訾辛阚那简饶空曾毋沙乜养鞠须丰巢关蒯相查后荆红游竺权逯盖益桓公")
GIVEN = ["伟", "强", "磊", "洋", "勇", "军", "杰", "涛", "超", "明", "刚", "平", "辉", "鹏", "华", "飞", "鑫", "波", "斌", "宇", "浩", "凯", "健", "俊", "帆", "帅", "婷", "静", "丽", "娜", "敏", "艳", "芳", "燕", "玲", "霞", "萍", "红", "梅", "琳", "雪", "倩", "悦", "欣", "颖", "露", "萌", "洁", "慧", "佳"]

SEARCH_KEYWORDS = {
    "跑步": ["跑步鞋", "缓震跑鞋", "马拉松跑鞋", "跑步T恤", "运动手表", "运动腰包"],
    "篮球": ["篮球鞋", "实战篮球鞋", "篮球服", "7号篮球", "护膝", "篮球袜"],
    "健身": ["哑铃", "瑜伽垫", "跳绳", "蛋白粉", "健身背心", "筋膜枪"],
    "瑜伽": ["瑜伽服", "瑜伽垫", "瑜伽裤", "运动内衣", "泡沫轴"],
    "户外": ["冲锋衣", "徒步鞋", "帐篷", "登山杖", "户外背包", "骑行头盔"],
    "羽毛球": ["羽毛球拍", "羽毛球鞋", "羽毛球", "护腕", "运动水壶"],
    "足球": ["足球鞋", "足球", "球门", "护腿板", "足球服"],
    "网球": ["网球拍", "网球", "网球鞋", "吸汗带"],
    "游泳": ["泳镜", "泳衣", "泳帽", "浮板"],
}

PRODUCT_PATTERNS = {
    "C006": ["缓震竞速跑鞋", "轻量透气跑步鞋", "马拉松碳板跑鞋", "日常训练跑鞋", "越野跑鞋"],
    "C007": ["实战篮球鞋", "高帮缓震篮球鞋", "低帮后卫篮球鞋", "耐磨外场篮球鞋"],
    "C008": ["综合训练鞋", "力量训练鞋", "室内健身鞋", "CrossFit训练鞋"],
    "C009": ["TF碎钉足球鞋", "FG长钉足球鞋", "室内平底足球鞋", "人草足球鞋"],
    "C010": ["防水徒步鞋", "轻量登山鞋", "户外越野鞋", "冬季保暖徒步鞋"],
    "C011": ["专业羽毛球鞋", "防滑耐磨羽毛球鞋", "轻量比赛羽毛球鞋"],
    "C012": ["复古休闲运动鞋", "厚底老爹鞋", "帆布休闲鞋", "百搭板鞋"],
    "C013": ["儿童跑步鞋", "儿童篮球鞋", "魔术贴运动鞋", "青少年训练鞋"],
    "C014": ["速干跑步T恤", "冰感运动短袖", "马拉松竞速背心", "透气训练T恤"],
    "C015": ["篮球比赛服", "美式篮球套装", "透气篮球背心", "球队定制篮球服"],
    "C016": ["健身训练背心", "肌肉训练坎肩", "速干运动背心"],
    "C017": ["高腰瑜伽裤", "裸感瑜伽套装", "运动瑜伽背心", "瑜伽长袖上衣"],
    "C018": ["束脚运动裤", "速干跑步长裤", "篮球训练短裤", "加绒运动裤"],
    "C019": ["三合一冲锋衣", "防水硬壳冲锋衣", "轻薄户外风衣", "抓绒冲锋衣"],
    "C020": ["轻薄羽绒服", "户外鹅绒羽绒服", "运动保暖羽绒马甲", "防风羽绒外套"],
    "C021": ["高强度运动内衣", "瑜伽运动内衣", "跑步防震内衣"],
    "C022": ["运动连帽外套", "防风跑步夹克", "篮球热身外套", "健身开衫"],
    "C023": ["加厚防滑瑜伽垫", "天然橡胶瑜伽垫", "便携折叠瑜伽垫"],
    "C024": ["可调节哑铃", "包胶哑铃套装", "家用力量训练哑铃"],
    "C025": ["竞速跳绳", "无绳跳绳", "智能计数跳绳"],
    "C026": ["家用折叠跑步机", "智能减震跑步机", "商用级跑步机"],
    "C027": ["家用动感单车", "磁控静音动感单车", "智能骑行单车"],
    "C028": ["运动护膝", "篮球护踝", "健身护腕", "跑步髌骨带"],
    "C029": ["专业运动手表", "GPS跑步手表", "户外心率手表"],
    "C030": ["乳清蛋白粉", "分离乳清蛋白", "运动增肌粉"],
    "C031": ["双人露营帐篷", "轻量徒步帐篷", "自动速开帐篷"],
    "C032": ["碳纤维登山杖", "铝合金徒步杖", "折叠越野登山杖"],
    "C033": ["骑行头盔", "公路车头盔", "山地车防护头盔"],
    "C034": ["高清防雾泳镜", "竞速泳镜", "大框舒适泳镜"],
    "C035": ["全碳素羽毛球拍", "进攻型羽毛球拍", "入门训练羽毛球拍"],
    "C036": ["7号室内篮球", "室外耐磨篮球", "比赛级PU篮球"],
    "C037": ["5号足球", "比赛级足球", "室内训练足球"],
    "C038": ["碳素网球拍", "初学者网球拍", "专业比赛网球拍"],
    "C039": ["大容量运动包", "干湿分离健身包", "户外双肩背包"],
    "C040": ["大容量运动水壶", "保温运动水壶", "骑行水壶"],
}

COLORS = ["曜石黑", "象牙白", "海军蓝", "火焰红", "薄荷绿", "岩灰", "活力橙", "雾霾蓝", "樱花粉", "沙色"]
MATERIALS = ["飞织网面", "再生聚酯纤维", "头层牛皮", "EVA中底", "天然橡胶", "棉氨混纺", "铝合金", "碳纤维", "TPU", "抓绒"]
TARGET_GROUPS = ["男", "女", "中性", "儿童"]
SEASONS = ["春夏", "秋冬", "四季"]


def weighted_choice(items, weights):
    return RNG.choices(items, weights=weights, k=1)[0]


def random_datetime(day: date, peak: bool = False) -> str:
    if peak:
        hour = RNG.choice([0, 0, 1, 10, 20, 21, 22, 23])
    else:
        hour = int(np.clip(NP_RNG.normal(20, 3.2), 7, 23))
    minute = RNG.randint(0, 59)
    second = RNG.randint(0, 59)
    return datetime(day.year, day.month, day.day, hour, minute, second).strftime("%Y-%m-%d %H:%M:%S")


def date_weight(day: date) -> float:
    month_weight = {5: 0.82, 6: 1.30, 7: 0.86, 8: 0.80, 9: 1.02, 10: 1.10, 11: 1.55}[day.month]
    weekend = 1.15 if day.weekday() >= 5 else 1.0
    promo = 1.0
    if date(2025, 6, 15) <= day <= date(2025, 6, 18):
        promo = 3.0
    if date(2025, 11, 8) <= day <= date(2025, 11, 11):
        promo = 4.0
    if day == date(2025, 6, 18):
        promo = 4.2
    if day == date(2025, 11, 11):
        promo = 5.0
    return month_weight * weekend * promo


def build_categories() -> pd.DataFrame:
    rows = []
    path_map = {}
    for cid, name, parent, level in CATEGORY_ROWS:
        if parent:
            path = f"{path_map[parent]}/{name}"
        else:
            path = name
        path_map[cid] = path
        rows.append(
            {
                "category_id": cid,
                "category_name": name,
                "parent_id": parent,
                "category_level": level,
                "category_path": path,
                "sort_no": int(cid[1:]),
            }
        )
    return pd.DataFrame(rows)


def build_brands() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "brand_id": bid,
                "brand_name": name,
                "brand_country": country,
                "brand_level": level,
                "main_category": main,
                "establish_year": year,
            }
            for bid, name, country, level, main, year, _ in BRANDS
        ]
    )


def build_shops() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "shop_id": sid,
                "shop_name": name,
                "shop_type": shop_type,
                "province": province,
                "city": city,
                "rating": rating,
                "open_date": open_date,
            }
            for sid, name, shop_type, province, city, rating, open_date in SHOPS
        ]
    )


def build_users(n: int = 800) -> pd.DataFrame:
    rows = []
    for i in range(1, n + 1):
        province, cities, _, _ = weighted_choice(PROVINCES, [p[2] for p in PROVINCES])
        city = RNG.choice(cities)
        gender = "男" if RNG.random() < 0.68 else "女"
        age = int(np.clip(NP_RNG.normal(29, 7), 18, 55))
        surname = RNG.choice(SURNAMES)
        given = "".join(RNG.choice(GIVEN) for _ in range(RNG.choice([1, 2])))
        level = weighted_choice(["普通", "银卡", "金卡", "黑卡"], [0.48, 0.30, 0.17, 0.05])
        if RNG.random() < 0.35:
            reg = START + timedelta(days=RNG.randint(0, DAYS - 20))
        else:
            reg = START - timedelta(days=RNG.randint(30, 520))
        last = min(END, max(reg, END - timedelta(days=RNG.randint(0, 80))))
        rows.append(
            {
                "user_id": f"U{i:05d}",
                "username": surname + given,
                "gender": gender,
                "age": age,
                "phone": f"1{RNG.choice(['38', '39', '58', '66', '88', '35', '36'])}{RNG.randint(10000000, 99999999)}",
                "email": f"u{i:05d}@sports-demo.cn",
                "province": province,
                "city": city,
                "register_time": reg.strftime("%Y-%m-%d %H:%M:%S"),
                "user_level": level,
                "is_member": 1 if level != "普通" else 0,
                "last_login_time": last.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    return pd.DataFrame(rows)


def build_products(n: int = 250) -> pd.DataFrame:
    leaf_categories = [c for c in CATEGORY_ROWS if c[3] == 2]
    category_weights = []
    for cid, name, _, _ in leaf_categories:
        if cid in {"C006", "C007", "C014", "C018", "C023", "C024", "C031", "C035"}:
            category_weights.append(3.2)
        elif cid in {"C008", "C009", "C010", "C015", "C016", "C017", "C019", "C020", "C025", "C026", "C027", "C028", "C029", "C030", "C032", "C033", "C034", "C036", "C037", "C038", "C039", "C040"}:
            category_weights.append(2.0)
        else:
            category_weights.append(1.2)
    rows = []
    brand_weights = [b[6] for b in BRANDS]
    for i in range(1, n + 1):
        cid, cname, _, _ = weighted_choice(leaf_categories, category_weights)
        brand = weighted_choice(BRANDS, brand_weights)
        bid, bname, _, blevel, _, _, _ = brand
        pattern = RNG.choice(PRODUCT_PATTERNS[cid])
        model_no = f"{RNG.choice(['Pro', 'Air', 'Max', 'Lite', 'Elite', 'X', 'Plus'])}{RNG.randint(1, 9)}"
        product_name = f"{bname} {pattern} {model_no}"
        if cid in {"C006", "C007", "C008", "C009", "C010", "C011", "C012", "C013"}:
            base = {"B001": 699, "B002": 649, "B003": 499, "B004": 459, "B015": 799, "B020": 1599}.get(bid, 329)
            price = base * RNG.uniform(0.62, 1.45)
            size = RNG.choice(["36", "37", "38", "39", "40", "41", "42", "43", "44", "45"])
            material = RNG.choice(["飞织网面", "EVA中底", "天然橡胶", "TPU", "头层牛皮"])
            target = "儿童" if cid == "C013" else RNG.choice(["男", "男", "女", "中性"])
        elif cid in {"C014", "C015", "C016", "C017", "C018", "C019", "C020", "C021", "C022"}:
            base = {"B001": 329, "B002": 299, "B003": 239, "B004": 219, "B014": 349, "B019": 899, "B020": 1899}.get(bid, 169)
            price = base * RNG.uniform(0.65, 1.55)
            size = RNG.choice(["S", "M", "L", "XL", "2XL", "3XL"])
            material = RNG.choice(["棉氨混纺", "再生聚酯纤维", "抓绒", "速干聚酯纤维"])
            target = RNG.choice(["男", "男", "女", "中性"])
        elif cid in {"C023", "C024", "C025", "C028", "C029", "C030"}:
            base = {"B017": 159, "B018": 249, "B014": 399, "B001": 299}.get(bid, 129)
            price = base * RNG.uniform(0.55, 2.0)
            size = "均码" if cid in {"C023", "C025", "C028"} else RNG.choice(["标准", "小号", "大号"])
            material = RNG.choice(["天然橡胶", "TPU", "铝合金", "棉氨混纺", "聚酯纤维"])
            target = RNG.choice(["男", "女", "中性"])
        elif cid in {"C026", "C027"}:
            base = {"B001": 3999, "B017": 2499, "B018": 2199}.get(bid, 1999)
            price = base * RNG.uniform(0.65, 1.45)
            size = "标准"
            material = "铝合金"
            target = "中性"
        elif cid in {"C031", "C032", "C033", "C034"}:
            base = {"B017": 399, "B019": 899, "B020": 1599, "B030": 499, "B029": 199}.get(bid, 259)
            price = base * RNG.uniform(0.55, 1.75)
            size = "均码" if cid in {"C033", "C034"} else RNG.choice(["1人", "2人", "3-4人"])
            material = RNG.choice(["铝合金", "碳纤维", "聚酯纤维", "TPU"])
            target = RNG.choice(["男", "女", "中性"])
        else:
            base = {"B026": 699, "B027": 199, "B028": 219, "B017": 129}.get(bid, 159)
            price = base * RNG.uniform(0.55, 1.85)
            size = RNG.choice(["4号", "5号", "7号", "标准"]) if cid in {"C036", "C037"} else "均码"
            material = RNG.choice(["天然橡胶", "碳纤维", "PU", "聚酯纤维"])
            target = RNG.choice(["男", "女", "中性"])
        price = round(max(39, price), 2)
        original_price = round(price * RNG.uniform(1.05, 1.45), 2)
        shop_id = RNG.choice(["S001", "S002", "S003", "S004", "S005", "S006", "S007", "S008", "S009", "S010", "S011", "S012", "S013", "S014", "S015"])
        listing = END - timedelta(days=RNG.randint(5, 700))
        rows.append(
            {
                "product_id": f"P{i:05d}",
                "product_name": product_name,
                "category_id": cid,
                "brand_id": bid,
                "shop_id": shop_id,
                "price": price,
                "original_price": original_price,
                "stock_qty": RNG.randint(0, 520),
                "sales_qty": 0,
                "size": size,
                "color": RNG.choice(COLORS),
                "material": material,
                "target_group": target,
                "season": RNG.choice(SEASONS),
                "listing_date": listing.strftime("%Y-%m-%d"),
                "status": "在售" if RNG.random() < 0.96 else "下架",
                "image_url": f"https://img14.360buyimg.com/n1/t2-sports-{i:05d}.jpg",
            }
        )
    return pd.DataFrame(rows)


def build_orders(users: pd.DataFrame) -> list[dict]:
    user_ids = users["user_id"].tolist()
    RNG.shuffle(user_ids)
    multi_users = user_ids[:304]
    single_users = user_ids[304:]

    order_specs: list[tuple[str, date, bool]] = []
    months = [5, 6, 7, 8, 9, 10, 11]
    for uid in multi_users:
        chosen_months = RNG.sample(months, 4)
        for m in chosen_months:
            first = max(START, date(2025, m, 1))
            last = min(END, date(2025, m, 28))
            day = first + timedelta(days=RNG.randint(0, (last - first).days))
            order_specs.append((uid, day, False))
    for idx, uid in enumerate(single_users):
        m = RNG.choice(months)
        first = max(START, date(2025, m, 1))
        last = min(END, date(2025, m, 28))
        day = first + timedelta(days=RNG.randint(0, (last - first).days))
        order_specs.append((uid, day, False))
        if idx < 288:
            day2 = min(last, day + timedelta(days=RNG.randint(1, 24)))
            order_specs.append((uid, day2, False))

    # Avoid empty/low-volume days so the daily forecast and trend charts have a
    # stable signal. Move orders from very busy days into days below 6 orders.
    all_days = [START + timedelta(days=i) for i in range(DAYS)]
    counts = Counter(spec[1] for spec in order_specs)
    for day in all_days:
        while counts[day] < 6:
            donors = [i for i, spec in enumerate(order_specs) if counts[spec[1]] > 10]
            if not donors:
                break
            donor = max(donors, key=lambda i: counts[order_specs[i][1]])
            uid, old_day, _ = order_specs[donor]
            order_specs[donor] = (uid, day, False)
            counts[old_day] -= 1
            counts[day] += 1

    # Move surplus normal-day orders into two short, high-intensity promo
    # windows. This produces a clean 618 / Double 11 burst without starving
    # ordinary days of traffic.
    promo_days = {date(2025, 6, 15), date(2025, 6, 16), date(2025, 6, 17), date(2025, 6, 18),
                  date(2025, 11, 8), date(2025, 11, 9), date(2025, 11, 10), date(2025, 11, 11)}
    promo_slots = (
        [date(2025, 6, 15)] * 40 + [date(2025, 6, 16)] * 40 +
        [date(2025, 6, 17)] * 45 + [date(2025, 6, 18)] * 55 +
        [date(2025, 11, 8)] * 50 + [date(2025, 11, 9)] * 55 +
        [date(2025, 11, 10)] * 60 + [date(2025, 11, 11)] * 75
    )
    for day in promo_slots:
        donors = [
            i for i, spec in enumerate(order_specs)
            if spec[1] not in promo_days and counts[spec[1]] > 6
        ]
        if not donors:
            break
        idx = max(donors, key=lambda i: counts[order_specs[i][1]])
        uid, old_day, _ = order_specs[idx]
        order_specs[idx] = (uid, day, True)
        counts[old_day] -= 1
        counts[day] += 1

    assert len(order_specs) == 2000, len(order_specs)
    province_by_user = users.set_index("user_id")[["province", "city"]].to_dict("index")
    rows = []
    for i, (uid, day, peak) in enumerate(order_specs, start=1):
        promo = ""
        if date(2025, 6, 15) <= day <= date(2025, 6, 18):
            promo = "618"
        if date(2025, 11, 8) <= day <= date(2025, 11, 11):
            promo = "双11"
        status = weighted_choice(
            ["已完成", "已发货", "已支付", "已退款", "待支付", "已取消"],
            [0.52, 0.20, 0.22, 0.04, 0.015, 0.005],
        )
        rows.append(
            {
                "order_id": f"O{day.strftime('%y%m%d')}{i:04d}",
                "user_id": uid,
                "order_time": random_datetime(day, peak),
                "order_status": status,
                "total_amount": 0.0,
                "discount_amount": 0.0,
                "shipping_fee": 0.0 if RNG.random() < 0.78 else RNG.choice([6, 8, 10, 12]),
                "pay_amount": 0.0,
                "province": province_by_user[uid]["province"],
                "city": province_by_user[uid]["city"],
                "channel": weighted_choice(["APP", "小程序", "PC", "H5"], [0.55, 0.25, 0.15, 0.05]),
                "promo_id": promo if promo else "",
                "coupon_amount": 0.0,
                "order_date": day.isoformat(),
            }
        )
    return rows


def build_details(orders: list[dict], products: pd.DataFrame) -> list[dict]:
    counts = np.ones(len(orders), dtype=int)
    # Add exactly 3,000 extra lines, capped at 4 lines per order.
    for _ in range(3000):
        idx = RNG.randrange(len(counts))
        while counts[idx] >= 4:
            idx = RNG.randrange(len(counts))
        counts[idx] += 1
    assert sum(counts) == 5000
    product_records = products.to_dict("records")
    weights = []
    brand_weight = {b[0]: b[6] for b in BRANDS}
    for p in product_records:
        weights.append(brand_weight.get(p["brand_id"], 0.3) * (1.6 if p["season"] in {"四季", "春夏"} else 1.0))
    rows = []
    detail_id = 1
    for order, count in zip(orders, counts):
        chosen = RNG.choices(product_records, weights=weights, k=int(count))
        total = 0.0
        for p in chosen:
            qty = 1 if RNG.random() < 0.86 else 2
            unit = round(float(p["price"]) * RNG.uniform(0.92, 1.04), 2)
            line = round(unit * qty, 2)
            total += line
            rows.append(
                {
                    "detail_id": f"D{detail_id:06d}",
                    "order_id": order["order_id"],
                    "product_id": p["product_id"],
                    "quantity": qty,
                    "unit_price": unit,
                    "discount_amount": 0.0,
                    "line_amount": line,
                }
            )
            detail_id += 1
        discount = 0.0
        if order["promo_id"] == "618":
            discount = round(total * RNG.uniform(0.12, 0.28), 2)
        elif order["promo_id"] == "双11":
            discount = round(total * RNG.uniform(0.15, 0.35), 2)
        elif RNG.random() < 0.22:
            discount = round(total * RNG.uniform(0.03, 0.10), 2)
        coupon = 0.0
        if RNG.random() < 0.42:
            coupon = RNG.choice([10, 20, 30, 50, 80, 100])
        order["total_amount"] = round(total + order["shipping_fee"], 2)
        order["discount_amount"] = discount
        order["coupon_amount"] = coupon
        order["pay_amount"] = round(max(1, total + order["shipping_fee"] - discount - coupon), 2)
        if order["order_status"] not in {"已完成", "已发货", "已支付", "已退款"}:
            order["pay_amount"] = 0.0
    return rows


def build_payments(orders: list[dict]) -> list[dict]:
    rows = []
    for i, order in enumerate(orders, start=1):
        paid = order["order_status"] in {"已完成", "已发货", "已支付", "已退款"}
        base_time = datetime.strptime(order["order_time"], "%Y-%m-%d %H:%M:%S")
        pay_time = base_time + timedelta(minutes=RNG.randint(1, 45))
        rows.append(
            {
                "payment_id": f"PAY{i:06d}",
                "order_id": order["order_id"],
                "pay_time": pay_time.strftime("%Y-%m-%d %H:%M:%S"),
                "pay_amount": order["pay_amount"] if paid else 0.0,
                "pay_method": weighted_choice(["微信支付", "支付宝", "京东支付", "银行卡"], [0.38, 0.31, 0.22, 0.09]),
                "pay_status": "成功" if paid else weighted_choice(["待支付", "失败"], [0.7, 0.3]),
                "transaction_no": f"TXN{order['order_id'][1:]}{RNG.randint(1000, 9999)}",
            }
        )
    return rows


def build_refunds(orders: list[dict]) -> list[dict]:
    paid = [o for o in orders if o["order_status"] in {"已完成", "已发货", "已退款"}]
    chosen = RNG.sample(paid, 300)
    reasons = ["尺码不合适", "颜色与描述不符", "质量问题", "七天无理由", "物流破损", "拍错商品", "降价补差"]
    rows = []
    for i, order in enumerate(chosen, start=1):
        base = datetime.strptime(order["order_time"], "%Y-%m-%d %H:%M:%S")
        refund_time = base + timedelta(days=RNG.randint(1, 18), hours=RNG.randint(0, 23))
        status = weighted_choice(["已退款", "处理中", "已拒绝"], [0.60, 0.25, 0.15])
        amount = round(order["pay_amount"] * RNG.uniform(0.3, 1.0), 2) if status == "已退款" else 0.0
        rows.append(
            {
                "refund_id": f"R{i:06d}",
                "order_id": order["order_id"],
                "refund_time": refund_time.strftime("%Y-%m-%d %H:%M:%S"),
                "refund_amount": amount,
                "refund_reason": RNG.choice(reasons),
                "refund_status": status,
                "refund_type": RNG.choice(["仅退款", "退货退款"]),
            }
        )
    return rows


def build_logistics(orders: list[dict]) -> list[dict]:
    rows = []
    companies = ["顺丰速运", "京东物流", "中通快递", "圆通速递", "韵达快递", "德邦物流"]
    for i, order in enumerate(orders, start=1):
        base = datetime.strptime(order["order_time"], "%Y-%m-%d %H:%M:%S")
        ship = base + timedelta(days=RNG.randint(0, 2), hours=RNG.randint(1, 20))
        deliver = ship + timedelta(days=RNG.randint(1, 5), hours=RNG.randint(0, 12))
        sign = deliver + timedelta(days=RNG.randint(0, 2), hours=RNG.randint(0, 10))
        status = order["order_status"]
        if status in {"已完成", "已退款"}:
            logistics_status = "已签收"
        elif status == "已发货":
            logistics_status = "运输中"
        elif status == "已支付":
            logistics_status = "已发货"
        else:
            logistics_status = "待发货"
        rows.append(
            {
                "logistics_id": f"L{i:06d}",
                "order_id": order["order_id"],
                "ship_time": ship.strftime("%Y-%m-%d %H:%M:%S") if logistics_status != "待发货" else "",
                "deliver_time": deliver.strftime("%Y-%m-%d %H:%M:%S") if logistics_status in {"已签收", "运输中"} else "",
                "sign_time": sign.strftime("%Y-%m-%d %H:%M:%S") if logistics_status == "已签收" else "",
                "logistics_company": RNG.choice(companies),
                "tracking_no": f"JD{RNG.randint(10**12, 10**13 - 1)}",
                "logistics_status": logistics_status,
                "province": order["province"],
                "city": order["city"],
            }
        )
    return rows


def build_reviews(orders: list[dict], details: list[dict]) -> list[dict]:
    detail_by_order: dict[str, list[dict]] = {}
    for d in details:
        detail_by_order.setdefault(d["order_id"], []).append(d)
    eligible = [o for o in orders if o["order_status"] in {"已完成", "已发货", "已支付", "已退款"} and o["order_id"] in detail_by_order]
    chosen = RNG.sample(eligible, 1500)
    positive = ["脚感很好，缓震明显，跑步训练都合适。", "尺码标准，做工扎实，运动时很稳。", "面料透气，出汗也不闷，性价比不错。", "大促入手很划算，物流也快。", "配色好看，日常穿搭和运动都能用。"]
    neutral = ["整体还行，尺码稍微偏小，建议拍大半码。", "功能符合预期，包装一般。", "价格合适，细节还有提升空间。"]
    negative = ["尺码偏差较大，已经申请退货。", "做工有瑕疵，和页面描述不太一致。", "物流太慢，影响使用。"]
    rows = []
    for i, order in enumerate(chosen, start=1):
        d = RNG.choice(detail_by_order[order["order_id"]])
        base = datetime.strptime(order["order_time"], "%Y-%m-%d %H:%M:%S")
        review_time = base + timedelta(days=RNG.randint(3, 25))
        rating = weighted_choice([5, 4, 3, 2, 1], [0.52, 0.27, 0.12, 0.06, 0.03])
        content = RNG.choice(positive if rating >= 4 else neutral if rating == 3 else negative)
        rows.append(
            {
                "review_id": f"RV{i:06d}",
                "order_id": order["order_id"],
                "product_id": d["product_id"],
                "user_id": order["user_id"],
                "review_time": review_time.strftime("%Y-%m-%d %H:%M:%S"),
                "rating": rating,
                "review_content": content,
                "is_anonymous": 1 if RNG.random() < 0.3 else 0,
                "images_count": RNG.randint(0, 5),
            }
        )
    return rows


def build_cart(users: pd.DataFrame, products: pd.DataFrame, n: int = 6000) -> list[dict]:
    rows = []
    for i in range(1, n + 1):
        uid = RNG.choice(users["user_id"].tolist())
        pid = RNG.choice(products["product_id"].tolist())
        day = START + timedelta(days=RNG.randint(0, DAYS - 1))
        rows.append(
            {
                "cart_id": f"CA{i:07d}",
                "user_id": uid,
                "product_id": pid,
                "add_time": random_datetime(day),
                "quantity": RNG.randint(1, 3),
                "cart_status": weighted_choice(["已下单", "购物车", "已删除"], [0.36, 0.52, 0.12]),
                "source_page": weighted_choice(["搜索页", "商品详情", "推荐位", "活动页"], [0.42, 0.28, 0.18, 0.12]),
            }
        )
    return rows


def build_search(users: pd.DataFrame, n: int = 5000) -> list[dict]:
    rows = []
    scenes = list(SEARCH_KEYWORDS)
    for i in range(1, n + 1):
        uid = RNG.choice(users["user_id"].tolist())
        day = START + timedelta(days=RNG.randint(0, DAYS - 1))
        scene = weighted_choice(scenes, [3 if s in {"跑步", "篮球", "健身"} else 1 for s in scenes])
        keyword = RNG.choice(SEARCH_KEYWORDS[scene])
        clicks = RNG.choices([0, 1, 2, 3], [0.30, 0.48, 0.16, 0.06])[0]
        rows.append(
            {
                "log_id": f"SL{i:07d}",
                "user_id": uid,
                "search_time": random_datetime(day),
                "keyword": keyword,
                "scene": scene,
                "result_count": RNG.randint(18, 980),
                "click_count": clicks,
                "duration_sec": RNG.randint(3, 180),
                "device": weighted_choice(["iOS", "Android", "PC", "小程序"], [0.38, 0.42, 0.08, 0.12]),
                "session_id": f"SE{day.strftime('%y%m%d')}{RNG.randint(1, 4000):05d}",
            }
        )
    return rows


def inject_dirty_ods(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Create controlled data-quality defects kept inside referential bounds."""
    orders = data["order_info"].copy()
    # Keep every order id intact so that detail/payment/logistics references
    # remain valid at the ODS layer. The rejected rows are amount anomalies.
    bad_amount_idx = RNG.sample(range(len(orders)), 40)
    orders.loc[bad_amount_idx, "pay_amount"] = -abs(orders.loc[bad_amount_idx, "pay_amount"])
    data["order_info"] = orders

    details = data["order_detail"].copy()
    dup = RNG.sample(range(len(details)), 50)
    for i in dup:
        details.loc[i, "detail_id"] = details.loc[(i + 1) % len(details), "detail_id"]
    zero = RNG.sample([i for i in range(len(details)) if i not in dup], 50)
    details.loc[zero, "quantity"] = 0
    data["order_detail"] = details

    payments = data["payment_info"].copy()
    dup = RNG.sample(range(len(payments)), 20)
    for i in dup:
        payments.loc[i, "payment_id"] = payments.loc[(i + 1) % len(payments), "payment_id"]
    zero = RNG.sample([i for i in range(len(payments)) if i not in dup], 20)
    payments.loc[zero, "pay_amount"] = 0
    data["payment_info"] = payments

    refunds = data["refund_info"].copy()
    neg = RNG.sample(range(len(refunds)), 15)
    refunds.loc[neg, "refund_amount"] = -refunds.loc[neg, "refund_amount"].abs()
    data["refund_info"] = refunds

    logistics = data["logistics_info"].copy()
    bad = RNG.sample([i for i in range(len(logistics)) if logistics.loc[i, "ship_time"]], 60)
    for i in bad:
        base = datetime.strptime(logistics.loc[i, "ship_time"], "%Y-%m-%d %H:%M:%S")
        logistics.loc[i, "deliver_time"] = (base - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        logistics.loc[i, "logistics_status"] = "已签收"
        logistics.loc[i, "sign_time"] = (base - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
    data["logistics_info"] = logistics

    reviews = data["review_info"].copy()
    bad = RNG.sample(range(len(reviews)), 40)
    reviews.loc[bad[:20], "rating"] = 0
    reviews.loc[bad[20:], "review_content"] = ""
    data["review_info"] = reviews

    cart = data["cart_info"].copy()
    bad = RNG.sample(range(len(cart)), 70)
    cart.loc[bad, "quantity"] = 0
    data["cart_info"] = cart

    search = data["search_log"].copy()
    bad = RNG.sample(range(len(search)), 100)
    search.loc[bad[:50], "keyword"] = ""
    search.loc[bad[50:], "duration_sec"] = 0
    data["search_log"] = search
    return data


def main() -> None:
    ensure_dirs()
    for name in ODS_TABLES:
        target = ODS_DIR / f"{name}.csv"
        if target.exists():
            target.unlink()

    categories = build_categories()
    brands = build_brands()
    shops = build_shops()
    users = build_users()
    products = build_products()
    orders = build_orders(users)
    details = build_details(orders, products)
    payments = build_payments(orders)
    refunds = build_refunds(orders)
    logistics = build_logistics(orders)
    reviews = build_reviews(orders, details)
    cart = build_cart(users, products)
    search = build_search(users)

    # Product sales_qty is a shelf snapshot derived from the order facts.
    detail_df = pd.DataFrame(details)
    sales = detail_df.groupby("product_id")["quantity"].sum().to_dict()
    products["sales_qty"] = products["product_id"].map(sales).fillna(0).astype(int)

    data = {
        "user_info": users,
        "category": categories,
        "product_info": products,
        "brand_info": brands,
        "shop_info": shops,
        "order_info": pd.DataFrame(orders),
        "order_detail": detail_df,
        "payment_info": pd.DataFrame(payments),
        "refund_info": pd.DataFrame(refunds),
        "logistics_info": pd.DataFrame(logistics),
        "review_info": pd.DataFrame(reviews),
        "cart_info": pd.DataFrame(cart),
        "search_log": pd.DataFrame(search),
    }
    data = inject_dirty_ods(data)

    expected = {
        "user_info": 800,
        "category": 40,
        "product_info": 250,
        "brand_info": 30,
        "shop_info": 15,
        "order_info": 2000,
        "order_detail": 5000,
        "payment_info": 2000,
        "refund_info": 300,
        "logistics_info": 2000,
        "review_info": 1500,
        "cart_info": 6000,
        "search_log": 5000,
    }
    summary = {}
    for name in ODS_TABLES:
        df = data[name]
        assert len(df) == expected[name], f"{name}: {len(df)} != {expected[name]}"
        df.to_csv(ODS_DIR / f"{name}.csv", index=False, encoding="utf-8-sig")
        summary[name] = len(df)

    order_df = data["order_info"]
    detail_df = data["order_detail"]
    valid_paid = order_df[(order_df["pay_amount"] > 0) & order_df["order_status"].isin(["已完成", "已发货", "已支付", "已退款"])]
    total_gmv = float(valid_paid["pay_amount"].sum())
    aov = total_gmv / max(1, valid_paid["order_id"].nunique())
    male_share = round(float((users["gender"] == "男").mean() * 100), 2)
    brand_counts = detail_df.merge(products[["product_id", "brand_id"]], on="product_id")["brand_id"].value_counts()
    top5_share = round(float(brand_counts.head(5).sum() / brand_counts.sum() * 100), 2)
    promo_days = valid_paid[valid_paid["promo_id"].isin(["618", "双11"])].groupby("order_date")["pay_amount"].sum()
    normal_days = valid_paid[~valid_paid["promo_id"].isin(["618", "双11"])].groupby("order_date")["pay_amount"].sum()
    meta = {
        "group_no": GROUP_NO,
        "group_name": "运动",
        "seed": SEED,
        "period": [START_DATE, END_DATE],
        "days": DAYS,
        "rows": summary,
        "total_rows": sum(summary.values()),
        "male_share_pct": male_share,
        "gmv": round(total_gmv, 2),
        "aov": round(aov, 2),
        "paid_orders": int(valid_paid["order_id"].nunique()),
        "top5_brand_share_pct": top5_share,
        "promo_avg_daily_gmv": round(float(promo_days.mean()), 2),
        "normal_avg_daily_gmv": round(float(normal_days.mean()), 2),
        "promo_uplift": round(float(promo_days.mean() / normal_days.mean()), 2),
        "refund_rows": len(refunds),
        "approved_refund_rows": int((data["refund_info"]["refund_status"] == "已退款").sum()),
    }
    (ODS_DIR / "_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
