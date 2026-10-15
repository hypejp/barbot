"""日本の料理・食品についての簡潔な英語説明。"""

FOOD_DESCRIPTIONS = {
    "寿司": "Japanese dish of vinegared rice served with seafood or other ingredients",
    "刺身": "thinly sliced raw fish or seafood",
    "天ぷら": "seafood or vegetables coated in a light batter and deep-fried",
    "うどん": "thick Japanese wheat noodles",
    "ラーメン": "Japanese noodle soup with Chinese-style wheat noodles",
    "焼きそば": "Japanese stir-fried noodles with vegetables and meat",
    "焼きうどん": "stir-fried udon noodles with vegetables and meat",
    "おでん": "Japanese simmered dish with various ingredients in a savory broth",
    "親子丼": "rice bowl topped with chicken and egg",
    "牛丼": "rice bowl topped with thinly sliced beef and onions",
    "カツ丼": "rice bowl topped with a breaded pork cutlet and egg",
    "茶碗蒸し": "Japanese savory steamed egg custard",
    "餃子": "Chinese-origin dumplings, commonly pan-fried in Japan",
    "焼売": "Chinese-style steamed dumplings",
    "たこ焼き": "Japanese snack made of batter balls filled with octopus",
    "お好み焼き": "Japanese savory pancake with cabbage and other ingredients",
    "唐揚げ": "Japanese-style deep-fried meat or other ingredients",
    "とんかつ": "Japanese breaded and deep-fried pork cutlet",
    "肉じゃが": "Japanese simmered dish of meat, potatoes, and vegetables",
    "味噌汁": "Japanese soup made with miso paste and dashi broth",
    "大福": "soft rice cake filled with sweet bean paste",
    "どら焼き": "Japanese sweet made of two small pancakes filled with sweet bean paste",
    "たい焼き": "fish-shaped Japanese cake usually filled with sweet bean paste",
    "蕎麦": "Japanese noodles made primarily from buckwheat flour",
}


def get_food_description(word):
    """JMdictの見出し語に対応する食品の説明を返す。"""
    return FOOD_DESCRIPTIONS.get(word)

FOOD_DESCRIPTIONS.update({
    # ご飯・丼物
    "お握り": "Japanese rice ball, often filled with savory ingredients and wrapped in seaweed",
    "お結び": "Japanese rice ball, often wrapped in seaweed",
    "炊き込みご飯": "rice cooked with vegetables, meat, or seafood and seasonings",
    "赤飯": "sticky rice steamed with red beans, traditionally served at celebrations",
    "お茶漬け": "rice with tea or dashi broth poured over it",
    "雑炊": "cooked rice simmered in seasoned broth with other ingredients",
    "お粥": "Japanese rice porridge",
    "卵かけご飯": "hot rice mixed with raw egg and usually soy sauce",
    "オムライス": "Japanese omelet filled with seasoned fried rice",
    "カレーライス": "Japanese-style curry served over rice",
    "ハヤシライス": "rice topped with beef and onions in a rich tomato-based sauce",
    "天津飯": "rice topped with a Chinese-style omelet and savory sauce",
    "中華丼": "rice topped with stir-fried meat, seafood, and vegetables in thick sauce",
    "海鮮丼": "rice bowl topped with assorted raw seafood",
    "天丼": "rice bowl topped with tempura",
    "うな丼": "rice bowl topped with grilled eel and sweet soy-based sauce",
    "鉄火丼": "rice bowl topped with slices of raw tuna",

    # 麺類
    "素麺": "very thin Japanese wheat noodles, often served chilled",
    "冷や麦": "thin Japanese wheat noodles usually served cold",
    "ざる蕎麦": "chilled buckwheat noodles served with dipping sauce",
    "狐うどん": "udon noodle soup topped with sweetened fried tofu",
    "たぬきうどん": "udon topped with tempura batter crumbs",
    "カレー饂飩": "udon noodles served in Japanese curry broth",
    "鍋焼きうどん": "udon noodles simmered with ingredients in an individual pot",
    "冷やし中華": "chilled Chinese-style noodles with vegetables and other toppings",
    "つけ麺": "noodles served separately from a rich dipping broth",
    "担々麺": "spicy noodles with sesame-based broth and minced meat",
    "皿うどん": "Nagasaki-style noodles topped with vegetables and seafood in thick sauce",
    "ナポリタン": "Japanese spaghetti stir-fried with ketchup, vegetables, and sausage",

    # 肉・魚料理
    "焼き鳥": "Japanese grilled chicken skewers",
    "焼肉": "Japanese-style grilled meat, often cooked at the table",
    "すき焼き": "Japanese hot pot of thinly sliced beef and vegetables in sweet soy broth",
    "しゃぶしゃぶ": "thinly sliced meat and vegetables briefly cooked in hot broth",
    "生姜焼き": "Japanese ginger pork stir-fry",
    "ハンバーグ": "Japanese-style hamburger steak made from ground meat",
    "コロッケ": "Japanese croquette, often made with mashed potatoes",
    "メンチカツ": "breaded and deep-fried minced meat cutlet",
    "チキン南蛮": "fried chicken coated in sweet vinegar sauce, often served with tartar sauce",
    "照り焼き": "meat or fish glazed with a sweet soy-based sauce",
    "焼き魚": "Japanese grilled fish",
    "煮魚": "fish simmered in a seasoned soy-based broth",
    "西京焼き": "fish marinated in sweet white miso and grilled",
    "ローストビーフ": "roasted beef served in thin slices",

    # 煮物・惣菜
    "筑前煮": "Japanese simmered chicken and root vegetables",
    "切り干し大根": "dried daikon radish strips, often simmered in seasoned broth",
    "金平牛蒡": "burdock root and carrots stir-fried in sweet soy sauce",
    "胡麻和え": "vegetables dressed with a sesame-based sauce",
    "白和え": "vegetables dressed with seasoned mashed tofu",
    "揚げ出し豆腐": "lightly fried tofu served in savory dashi broth",
    "湯豆腐": "tofu gently simmered in hot water or kombu broth",
    "冷奴": "chilled tofu served with condiments and soy sauce",
    "卵焼き": "Japanese rolled omelet",
    "だし巻き卵": "Japanese rolled omelet flavored with dashi broth",

    # 粉物・中華料理
    "もんじゃ焼き": "Tokyo-style savory batter cooked on a griddle",
    "ねぎ焼き": "Japanese savory pancake made with plenty of green onions",
    "広島焼き": "Hiroshima-style layered savory pancake with noodles and cabbage",
    "春巻き": "Chinese-style fried spring roll",
    "小籠包": "Chinese steamed dumpling filled with meat and hot broth",
    "麻婆豆腐": "spicy Sichuan-style tofu dish with minced meat",
    "麻婆茄子": "Japanese-Chinese dish of eggplant in spicy minced meat sauce",
    "酢豚": "Chinese-style sweet-and-sour pork with vegetables",
    "回鍋肉": "Sichuan-style stir-fried pork and cabbage",
    "青椒肉絲": "Chinese-style stir-fried meat with green peppers",
    "八宝菜": "Chinese-style stir-fried vegetables, meat, and seafood in thick sauce",
    "海老チリ": "shrimp cooked in a spicy tomato and chili sauce",

    # 汁物・鍋
    "豚汁": "Japanese miso soup with pork and vegetables",
    "けんちん汁": "Japanese vegetable soup with tofu and root vegetables",
    "すまし汁": "clear Japanese soup made with dashi broth",
    "石狩鍋": "Hokkaido-style salmon and vegetable hot pot with miso",
    "ちゃんこ鍋": "hearty Japanese hot pot traditionally eaten by sumo wrestlers",
    "寄せ鍋": "Japanese hot pot with assorted seafood, meat, and vegetables",
    "もつ鍋": "Japanese hot pot with beef or pork offal and vegetables",
    "キムチ鍋": "spicy Japanese hot pot flavored with kimchi",
    "水炊き": "Japanese chicken and vegetable hot pot served with dipping sauce",
    "お雑煮": "Japanese New Year soup containing mochi rice cakes",

    # 菓子・軽食
    "団子": "Japanese dumplings made from rice flour",
    "みたらし団子": "skewered rice dumplings coated in sweet soy glaze",
    "桜餅": "pink rice cake filled with sweet bean paste and wrapped in a cherry leaf",
    "柏餅": "rice cake filled with sweet bean paste and wrapped in an oak leaf",
    "草餅": "green mochi flavored with Japanese mugwort",
    "お萩": "sweet rice balls coated with red bean paste or other toppings",
    "ぼた餅": "sweet rice cakes covered with red bean paste",
    "羊羹": "firm Japanese jelly confection made from sweet bean paste",
    "金つば": "Japanese sweet bean confection coated in a thin flour batter",
    "わらび餅": "soft jelly-like Japanese sweet traditionally made from bracken starch",
    "葛餅": "Japanese jelly-like sweet made with kudzu starch",
    "餡蜜": "Japanese dessert with agar jelly, sweet bean paste, fruit, and syrup",
    "お汁粉": "sweet red bean soup served with mochi or rice dumplings",
    "かき氷": "Japanese shaved ice topped with flavored syrup",
    "心太": "chilled agar jelly noodles served with sauce",
    "いなり寿司": "sushi rice stuffed into sweetened fried tofu pockets",
    "巻き寿司": "sushi rolls wrapped in seaweed",
    "ちらし寿司": "sushi rice topped with assorted seafood and vegetables",
})

# JMdictの英訳が長い場合に使用する簡潔な料理名。
FOOD_ENGLISH_NAMES = {
    "麻婆豆腐": "mapo tofu",
    "みたらし団子": "mitarashi dango",
    "きつねうどん": "kitsune udon",
    "狐うどん": "kitsune udon",
    "豚汁": "tonjiru",
    "冷やし中華": "hiyashi chuka",
    "卵かけご飯": "tamago kake gohan",
    "切り干し大根": "kiriboshi daikon",
    "青椒肉絲": "chinjao rosu",
    "回鍋肉": "hoikoro",
}


def get_food_english_name(word, default):
    """料理の簡潔な英語名を取得する。"""
    return FOOD_ENGLISH_NAMES.get(word, default)

# 料理以外の意味もあるため、読み方に注意が必要な食品。
AMBIGUOUS_FOOD_DESCRIPTIONS = {
    "ぜんざい": (
        "zenzai",
        "Japanese sweet red bean soup, often served with mochi",
    ),
    "もなか": (
        "monaka",
        "Japanese wafer confection filled with sweet bean paste",
    ),
    "あかしやき": (
        "akashiyaki",
        "soft egg-rich octopus dumplings served with dashi broth",
    ),
    "ちゃんぽん": (
        "champon",
        "Nagasaki-style noodle soup with pork, seafood, and vegetables",
    ),
}


def get_ambiguous_food(reading):
    """読み方から、別の意味も持つ料理の情報を取得する。"""
    return AMBIGUOUS_FOOD_DESCRIPTIONS.get(reading)
