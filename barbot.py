# ===== barbot 完全版（randomized idle + social greeting guard） =====

import irc.bot
import irc.connection
import ssl
import random
import time
import re
import json
import threading
from pathlib import Path
import requests
from bs4 import BeautifulSoup

SERVER = "irc.libera.chat"
PORT = 6697
NICK = "barbot"
CHANNEL = "##bar-jp"

OWNER_NICK = "hype"
VERSION = "barbot 2.0.0"
BOT_STARTED_AT = time.time()

BASE = Path.home()

SEEN_FILE = BASE / "barbot_seen.json"
QUOTE_FILE = BASE / "barbot_quotes.json"
DRINK_FILE = BASE / "barbot_drinks.json"
AUTOQUOTE_FILE = BASE / "barbot_autoquote.json"
RANK_FILE = BASE / "barbot_rank.json"
FIRST_SPEAK_FILE = BASE / "barbot_first_speak.json"

seen = {}
quotes = []
drinks = []
autoquote_enabled = {}
rank_data = {}
first_speak_data = {}

recent_history = []
talk_counts = {}
last_name_response = {}
last_topic_count = {}

# Social greeting state. These values are intentionally kept in memory only;
# restarting the bot simply resets the cooldowns and reply history.
last_greeting_response_at = 0.0
last_greeting_response_by_nick = {}
greeting_reply_history = []

# JOIN-based welcome state. Only users who have actually JOINed ##bar-jp
# are eligible for a welcome, and eligibility expires after 60 seconds.
WELCOME_WINDOW = 60
welcome_candidates = {}

last_activity = time.time()

# Idle messages are scheduled 5-7 hours after the latest human message.
IDLE_SECONDS = 60 * 60
IDLE_MIN_SECONDS = 5 * 60 * 60
IDLE_MAX_SECONDS = 7 * 60 * 60
IDLE_HISTORY_SIZE = 20

idle_line_history = []
idle_state_lock = threading.Lock()
next_idle_time = time.time() + random.uniform(IDLE_MIN_SECONDS, IDLE_MAX_SECONDS)

NAME_RESPONSE_COOLDOWN = 180
TOPIC_SPAM_COOLDOWN = 30

# Greeting reactions are deliberately rare so barbot does not dominate chat.
GREETING_BASE_CHANCE = 0.15
GREETING_MEDIUM_CHANCE = 0.08
GREETING_GLOBAL_COOLDOWN = 10 * 60
GREETING_NICK_COOLDOWN = 30 * 60
GREETING_HISTORY_SIZE = 8

SOFT_DRINKS = [
    "Water - まずは水を一杯",
    "Milk - 今日は休むか",
    "Coffee ☕ - 少し目を覚まそう",
    "Tea - 静かな時間に",
    "Cola - 気楽にいこう",
    "Soda - 軽くいこう",
    "Juice - 甘いのも悪くない",
]

IDLE_LINES = [
    "琥珀色の灯りがカウンターに落ちている",
    "氷がゆっくり形を変えていく",
    "古いレコードを一枚かけよう",
    "グラスが灯りを映している",
    "少し照明を落としておこう",
    "言葉のない時間も、この店にはよく似合う",
    "針の音まで聞こえる静けさだ",
    "冷たい水をカウンターに置いておくよ",
    "窓際の席が空いている",
    "静かな余韻が残っている",
    "静かな酒には、静かな時間がよく似合う",
    "話したくなるまで、黙っていてもいい",
    "誰かを待ちながら、ゆっくりグラスを磨いている",
    "時計の針だけが静かに進んでいる",
    "カーテンがわずかに揺れた",

    "ビールは静かに冷えている",
    "次は何を注ごう",
    "もう一杯ぶんの余裕が残っている",
    "IRCの片隅に、小さなバーが灯っている",
    "コーヒーの湯気がゆっくり消えていく",
    "ラムの甘い香りが漂っている",
    "磨いたグラスが灯りを返している",
    "気が向いたら、静かに一杯どうぞ",
    "店内には低い音で音楽が流れている",
    "穏やかな影が揺れている",
    "バケツの氷が小さく音を立てた",

    "ワインの栓を抜く音が似合いそうだ",
    "音楽をほんの少しだけ大きくしよう",
    "急がなくていい。",
    "静かなインターネットに、小さなバーが灯っている",
    "グラスの底に、まだ少し余韻が残っている",
    "ウイスキーの琥珀がよく映える灯りだ",
    "好きな飲み物を片手に、ゆっくりどうぞ。",
    "流れに任せよう",
]

def schedule_next_idle(now=None):
    """Schedule the next idle line after a fresh random delay."""
    global next_idle_time
    if now is None:
        now = time.time()
    with idle_state_lock:
        next_idle_time = now + random.uniform(IDLE_MIN_SECONDS, IDLE_MAX_SECONDS)


def choose_idle_line():
    """Choose an idle line not used in the previous 20 idle messages."""
    with idle_state_lock:
        available = [line for line in IDLE_LINES if line not in idle_line_history]

        # This is only a safety fallback if the message list becomes too short.
        if not available:
            idle_line_history.clear()
            available = list(IDLE_LINES)

        line = random.choice(available)
        idle_line_history.append(line)
        if len(idle_line_history) > IDLE_HISTORY_SIZE:
            del idle_line_history[:-IDLE_HISTORY_SIZE]
        return line


MOOD_LINES = [
    "Mood: low lights, quiet glasses, and a little whisky.",
    "Mood: the bar is quiet, but the door is open.",
    "Mood: slow music, cold glass, no rush.",
    "Mood: smoke, silence, and a small light at the counter.",
    "Mood: a calm place for IRC and drinks.",
    "Mood: just enough noise to feel alive.",
    "Mood: a quiet bar somewhere on the internet.",
    "Mood: whisky if you want, water if you need.",
    "Mood: soft lights and slow conversation.",
    "Mood: the kind of place where IRC feels right.",
    "Mood: グラスの音が少しだけ聞こえる",
    "Mood: 静かなバーに、少しだけ音楽が流れている",
    "Mood: 無理に話さなくてもいい",
    "Mood: カウンターの灯りはまだついている",
    "Mood: 水を一杯、そして少し休憩",
    "Mood: 今日はゆっくりでいい",
    "Mood: 誰かが戻ってくるまで、グラスを磨いている",
]

CHEERS_LINES = [
    "🍻 Cheers.",
    "乾杯 🍺",
    "Good health.",
    "グラスを上げよう",
    "Tonight is still young.",
]

FIRST_SPEAK_REPLIES = [
    "Welcome 🍺 JP/EN OK.",
    "Welcome. Grab a drink 🍷",
    "Welcome to ##bar-jp.",
    "Beer, whisky, chat. Enjoy 🍺",
    "Drinks and casual chat 🍸",
    "Make yourself comfortable 🍺",
    "Feel free to chat in JP/EN.",
    "Welcome. Drinks are optional, conversation is welcome.",
    "Hey, welcome. Take it easy.",
    "Welcome. Pull up a chair.",
    "barbot quietly nods. A seat is open.",
    "Welcome. No rush, stay awhile.",
]

GREETING_REPLIES = [
    "Hi. Take the quiet seat by the counter.",
    "Welcome back. Your corner is still here.",
    "静かな時間をどうぞ。",
    "カウンターに灯りをつけてあるよ。",
    "落ち着く一杯はどう？",
    "コーヒーもあるよ ☕",
    "やあ。ゆっくりしていって。",
    "Welcome. Stay as long as the mood suits you.",
    "Good to see you. The bar feels warmer now. 🍺",
]

NAME_RESPONSES = [
    "呼んだか？　ここにいるよ",
    "聞こえてる。音楽は小さめにしてある",
    "カウンターの灯りを空けてあるよ",
    "今、琥珀色のグラスを磨いていたところだ",
    "どうした？　ゆっくり聞かせて",
]

REGULAR_NAME_RESPONSES = [
    "おかえり。いつもの席は空いてるよ",
    "いつものを、静かに出そうか",
    "急がなくていい。灯りはまだ消さないよ",
    "話なら聞くよ。音楽も小さくしておこう",
]

REGULAR_NICKS = {"hype", "Fuwari", "Fuwari15", "rouji", "ginsenglily"}

DRINK_CATEGORIES = {
    "random": [],
    "whisky": ["Ardbeg", "Lagavulin", "Laphroaig", "Whisky", "Highball", "Brandy"],
    "whiskey": ["Ardbeg", "Lagavulin", "Laphroaig", "Whisky", "Highball", "Brandy"],
    "sake": ["Sake", "日本酒", "Plum Wine"],
    "nihonshu": ["Sake", "日本酒"],
    "beer": ["Beer"],
    "wine": ["Wine", "Champagne", "Sparkling", "Port", "Sherry"],
    "cocktail": ["Negroni", "Martini", "Margarita", "Daiquiri", "Mojito", "Fizz", "Sour"],
    "classic": ["Old Fashioned", "Martini", "Dry Martini", "Manhattan", "Sidecar", "Negroni"],
    "gin": ["Gin", "Martini", "Negroni", "French 75"],
    "rum": ["Rum", "Daiquiri", "Mojito"],
    "soft": [],
    "nonalcohol": [],
}

DRINK_ALIASES = {
    "coffee": "Coffee ☕ - 作業のお供",
    "tea": "Tea - 静かな時間に",
    "water": "Water - まずは水を一杯",
    "milk": "Milk - 今日は休むか",
    "cola": "Cola - 気楽にいこう",
    "juice": "Juice - 甘いのも悪くない",
    "soda": "Soda - 軽くいこう",
    "beer": "Beer 🍺 - とりあえず一杯",
    "whisky": "Highball - 気楽にいこう",
    "whiskey": "Highball - 気楽にいこう",
    "highball": "Highball - 気楽にいこう",
    "wine": "Wine - ゆっくりいこう",
    "sake": "Sake - しみじみいこう",
    "nihonshu": "Sake - しみじみいこう",
    "rum": "Rum - 甘く深く",
    "gin": "Gin and Tonic - すっきりいこう",
}

CATEGORY_KEYWORDS = {
    "体調": [
        "疲れ", "つかれ", "眠い", "眠", "しんどい", "だるい",
        "腰", "肩", "首", "頭痛", "痛い", "病院", "薬", "休む",
        "体調", "具合", "寝不足", "風邪", "熱", "歯", "口内炎"
    ],
    "開発": [
        "Python", "Swift", "Xcode", "Git", "GitHub", "コード",
        "デバッグ", "ビルド", "エラー", "バグ", "実装",
        "プログラミング", "iPhone", "macOS", "キーボード拡張",
        "IME", "アプリ", "サーバー", "VPS", "Linux", "Debian",
        "systemd", "ssh", "scp", "cron", "API", "JSON", "bot",
        "VS Code", "nano", "ターミナル", "terminal"
    ],
    "音楽": [
        "YouTube", "youtu.be", "Spotify", "Apple Music", "曲", "音楽",
        "ギター", "シンセ", "volca", "DJ", "ライブ", "配信",
        "シティポップ", "AOR", "ジャズ", "カバー", "原曲",
        "アルバム", "プレイリスト", "歌", "演奏", "ピアノ",
        "ベース", "ドラム", "レコード"
    ],
    "酒": [
        "酒", "飲む", "飲みたい", "ビール", "ウイスキー",
        "ハイボール", "ラム", "ワイン", "日本酒", "焼酎",
        "カクテル", "酔", "乾杯", "ストレート", "ロック",
        "アードベッグ", "ラフロイグ", "ラガヴーリン", "ジン",
        "ブランデー", "バー", "一杯", "サッポロ", "黒ラベル"
    ],
    "IRC": [
        "IRC", "Libera", "ZNC", "The Lounge", "Textual",
        "IRCCloud", "チャンネル", "nick", "ChanServ",
        "join", "part", "quit", "##bar-jp", "クライアント"
    ],
    "Apple": [
        "Mac", "MacBook", "iMac", "iPhone", "iPad",
        "Apple", "Safari", "ミュージック", "iOS", "iPadOS",
        "macOS", "App Store", "HomePod", "Apple TV", "Time Machine",
        "Xcode"
    ],
    "日常": [
        "ご飯", "食事", "ラーメン", "散歩", "寝る", "起きた",
        "買い物", "暑い", "寒い", "雨", "天気", "朝", "夜",
        "昼", "夕食", "風呂", "歯磨き", "コーヒー", "お茶",
        "眠る", "起きる", "外", "家", "部屋",
        "猫", "犬", "ペット", "動物",
        "おはよう", "こんにちは", "こんばんは",
        "ただいま", "おかえり", "よろしく",
        "仕事", "会社", "学校", "昼寝", "休憩"
    ],
}

def load_json(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text())
    except Exception:
        pass
    return default

def save_json(path, data):
    try:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception:
        pass


def fix_mojibake(text):
    if not isinstance(text, str):
        return text

    # Repair common UTF-8 text decoded as Latin-1, e.g. ããã°ãã¯
    if any(mark in text for mark in ("ã", "Â", "ð", "�")):
        try:
            repaired = text.encode("latin-1").decode("utf-8")
            return repaired
        except Exception:
            return text

    return text

def load_all():
    global seen, quotes, drinks, autoquote_enabled, rank_data, first_speak_data
    seen = load_json(SEEN_FILE, {})
    quotes = load_json(QUOTE_FILE, [])
    drinks = load_json(DRINK_FILE, ["Beer 🍺 - とりあえず一杯"])
    autoquote_enabled = load_json(AUTOQUOTE_FILE, {})
    rank_data = load_json(RANK_FILE, {})
    first_speak_data = load_json(FIRST_SPEAK_FILE, {})

def quote_text(q):
    if isinstance(q, dict):
        text = q.get("text", "")
        nick = q.get("nick", "?")
        qtime = q.get("time", "")
        return f"💬 「{text}」 - {nick} ({qtime})"
    return str(q)

def quote_short(q):
    if isinstance(q, dict):
        return q.get("text", "")
    return str(q)

def today_string():
    return time.strftime("%Y-%m-%d")

def format_uptime(seconds):
    seconds = int(seconds)
    days = seconds // 86400
    seconds %= 86400
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes or not parts:
        parts.append(f"{minutes}m")
    return " ".join(parts)

def check_first_speak(nick):
    global first_speak_data

    if nick == NICK:
        return False

    today = today_string()
    if first_speak_data.get("date") != today:
        first_speak_data = {"date": today, "nicks": []}

    nicks = set(first_speak_data.get("nicks", []))
    if nick in nicks:
        return False

    nicks.add(nick)
    first_speak_data["nicks"] = sorted(nicks)
    save_json(FIRST_SPEAK_FILE, first_speak_data)

    return random.random() < 0.35

def format_time_ago(seconds):
    if seconds < 60:
        return "たった今"
    if seconds < 3600:
        return f"{seconds // 60}分前"
    if seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}時間前" if minutes == 0 else f"{hours}時間{minutes}分前"
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    return f"{days}日前" if hours == 0 else f"{days}日{hours}時間前"

def seen_message(target, diff):
    t = format_time_ago(diff)

    if diff < 60:
        choices = [
            f"{target} was last seen {t}. 今そこにいるな 🍻",
            f"{target} was last seen {t}. 目の前にいるじゃないか",
            f"{target} was last seen {t}. カウンターにいるよ",
        ]
    elif diff < 600:
        choices = [
            f"{target} was last seen {t}. まだこの辺にいるはずだ",
            f"{target} was last seen {t}. グラスはまだ片付けてない",
            f"{target} was last seen {t}. すぐ戻ってくるかもな",
            f"{target} was last seen {t}. まだ席は温かいよ",
        ]
    elif diff < 10800:
        choices = [
            f"{target} was last seen {t}. さっきまでいたよ",
            f"{target} was last seen {t}. まだ遠くには行ってないだろう",
            f"{target} was last seen {t}. もう一杯飲みに戻るかもな",
            f"{target} was last seen {t}. まだこの近くにいるかもな",
        ]
    elif diff < 86400:
        choices = [
            f"{target} was last seen {t}. しばらく見てないね",
            f"{target} was last seen {t}. もう別の店に移ったかもしれない",
            f"{target} was last seen {t}. どこかで飲んでるかもな",
            f"{target} was last seen {t}. また顔を出すといいな",
        ]
    else:
        choices = [
            f"{target} was last seen {t}. だいぶ見てないね",
            f"{target} was last seen {t}. また来るといいな",
            f"{target} was last seen {t}. 長い夜だったのかもしれない",
            f"{target} was last seen {t}. 席はまだ空けてあるよ",
        ]

    return random.choice(choices)

def categories_for_message(msg):
    cats = []
    lower = msg.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(k.lower() in lower for k in keywords):
            cats.append(category)
    return cats

def topic_counts():
    freq = {}
    for nick, msg, ts in recent_history[-20:]:
        for category in categories_for_message(msg):
            key = (nick, category)
            last = last_topic_count.get(key, 0)
            if ts - last < TOPIC_SPAM_COOLDOWN:
                continue
            last_topic_count[key] = ts
            freq[category] = freq.get(category, 0) + 1
    return freq

def generate_topic():
    freq = topic_counts()
    if not freq:
        return "No clear topic. Just a quiet night."
    top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:6]
    return "Topics: " + ", ".join([f"{w}({c})" for w, c in top])

def dominant_topic():
    freq = topic_counts()
    if not freq:
        return None
    return sorted(freq.items(), key=lambda x: x[1], reverse=True)[0][0]

def compress_history(items):
    compressed = []
    for nick, msg, ts in items:
        if compressed and compressed[-1]["nick"] == nick and compressed[-1]["msg"] == msg:
            compressed[-1]["count"] += 1
        else:
            compressed.append({"nick": nick, "msg": msg, "count": 1})

    parts = []
    for item in compressed:
        text = f"<{item['nick']}> {item['msg'][:40]}"
        if item["count"] > 1:
            text += f" ×{item['count']}"
        parts.append(text)
    return " | ".join(parts)

def category_drinks(category):
    category = category.lower()

    if category == "random":
        return drinks

    if category in ("soft", "nonalcohol"):
        return SOFT_DRINKS

    keys = DRINK_CATEGORIES.get(category)
    if not keys:
        return []

    matched = []
    for drink in drinks:
        lower = drink.lower()
        if any(key.lower() in lower for key in keys):
            matched.append(drink)

    return matched

def is_quote_worthy(msg):
    if len(msg) < 15:
        return False
    if not any(p in msg for p in "。！？.!?"):
        return False
    keywords = ["人生", "楽しい", "つらい", "酒", "プログラミング", "IRC", "思う"]
    return any(k in msg for k in keywords)

def should_auto_quote(nick, msg):
    if nick == OWNER_NICK:
        return False
    if autoquote_enabled.get(nick, True) is False:
        return False
    if msg.startswith("!"):
        return False
    if "http://" in msg or "https://" in msg:
        return False
    if not is_quote_worthy(msg):
        return False
    return random.random() < 0.05

def topic_drink():
    t = dominant_topic()
    if t == "体調":
        return "Tea - 無理するなよ"
    if t == "開発":
        return "Coffee ☕ - 作業のお供"
    if t == "音楽":
        return "Highball - 音楽には軽めで"
    if t == "IRC":
        return "Highball - 深夜IRC仕様"
    if t == "日常":
        return "Tea - 日常にはこれくらいがいい"
    if t == "Apple":
        return "Coffee ☕ - Apple談義には合う"
    if t == "酒":
        return random.choice(drinks)
    return random.choice(drinks)

def fetch_title(url):
    try:
        if "youtube.com/watch" in url or "youtu.be/" in url:
            api = "https://www.youtube.com/oembed"
            r = requests.get(api, params={"url": url, "format": "json"}, timeout=5)
            r.raise_for_status()
            title = r.json().get("title")
            if title:
                return title.strip()[:120]

        r = requests.get(url, timeout=3)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "html.parser")
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
            if title and title != "- YouTube":
                return title[:100]
    except Exception:
        return None

def fetch_async(c, url):
    title = fetch_title(url)
    if title:
        c.privmsg(CHANNEL, f"Title: {title}")

def is_regular(nick):
    return nick in REGULAR_NICKS or talk_counts.get(nick, 0) >= 5

def should_name_respond(nick, msg):
    lowered = msg.lower()

    if lowered.startswith("barbot:") or lowered.startswith("barbot,"):
        return False

    if not re.search(r"\bbarbot\b", lowered):
        return False

    now = time.time()
    if nick in last_name_response and now - last_name_response[nick] < NAME_RESPONSE_COOLDOWN:
        return False

    strong_call = any(x in lowered for x in [
        "hey barbot",
        "hi barbot",
        "yo barbot",
        "おい barbot",
        "ねえ barbot",
        "なあ barbot",
    ])

    if strong_call and is_regular(nick):
        chance = 0.50
    elif is_regular(nick):
        chance = 0.25
    else:
        chance = 0.15

    if random.random() < chance:
        last_name_response[nick] = now
        return True

    return False

def name_response(nick):
    if is_regular(nick):
        return random.choice(REGULAR_NAME_RESPONSES)
    return random.choice(NAME_RESPONSES)

def welcome_key(nick):
    """Normalize a nick for the short-lived JOIN welcome candidate table."""
    return nick.lower()


def prune_welcome_candidates(now=None):
    """Remove JOIN welcome candidates whose 60-second window has expired."""
    if now is None:
        now = time.time()

    expired = [
        key for key, joined_at in welcome_candidates.items()
        if now - joined_at > WELCOME_WINDOW
    ]
    for key in expired:
        welcome_candidates.pop(key, None)


def is_welcome_candidate(nick, now=None):
    """Return True only while nick is inside its post-JOIN welcome window."""
    if now is None:
        now = time.time()

    prune_welcome_candidates(now)
    return welcome_key(nick) in welcome_candidates


def consume_welcome_candidate(nick):
    """Remove a nick after barbot has actually welcomed it."""
    welcome_candidates.pop(welcome_key(nick), None)


def is_greeting_message(msg):
    """Return True only for short, greeting-like messages."""
    normalized = re.sub(r"[!！?？。、,.]+$", "", msg.strip().lower())
    normalized = re.sub(r"\s+", " ", normalized)

    japanese_greetings = (
        "おはよう", "おはようございます",
        "こんにちは", "こんばんは",
        "やあ", "どうも",
    )
    if normalized in japanese_greetings:
        return True

    return bool(re.fullmatch(
        r"(?:hi|hello|hey|hiya|howdy|good morning|good afternoon|good evening)(?: everyone| all| folks)?",
        normalized,
    ))

def recent_human_message_count(now, seconds, exclude_current=True):
    """Count recent human messages recorded in recent_history."""
    items = recent_history[:-1] if exclude_current and recent_history else recent_history
    return sum(1 for _nick, _msg, ts in items if now - ts <= seconds)

def recent_conversation_state(now, current_nick=None, seconds=90):
    """Classify recent human activity as quiet, solo, or conversation."""
    items = recent_history[:-1] if recent_history else recent_history
    speakers = {
        nick
        for nick, _msg, ts in items
        if now - ts <= seconds and nick != NICK
    }

    if current_nick and current_nick != NICK:
        speakers.add(current_nick)

    if not speakers:
        return "quiet"
    if len(speakers) == 1:
        return "solo"
    return "conversation"

def choose_greeting_reply():
    """Avoid repeating recently used greeting replies."""
    available = [line for line in GREETING_REPLIES if line not in greeting_reply_history]
    if not available:
        greeting_reply_history.clear()
        available = list(GREETING_REPLIES)

    line = random.choice(available)
    greeting_reply_history.append(line)
    if len(greeting_reply_history) > GREETING_HISTORY_SIZE:
        del greeting_reply_history[:-GREETING_HISTORY_SIZE]
    return line

def should_greeting_respond(nick, msg, now):
    """React rarely to greetings, and stay quiet during active conversation."""
    global last_greeting_response_at

    if ("乾杯" in msg) or ("cheers" in msg.lower()) or ("kanpai" in msg.lower()):
        return False

    if nick == NICK or not is_greeting_message(msg):
        return False

    # Let the JOIN-based welcome handler take care of recent joiners.
    if is_welcome_candidate(nick, now):
        return False

    if now - last_greeting_response_at < GREETING_GLOBAL_COOLDOWN:
        return False

    nick_last = last_greeting_response_by_nick.get(nick, 0.0)
    if now - nick_last < GREETING_NICK_COOLDOWN:
        return False

    # Do not interrupt a quick exchange already in progress.
    if recent_human_message_count(now, 30) >= 3:
        return False

    # Stay quiet when a human conversation is already in progress.
    if recent_conversation_state(now, nick) == "conversation":
        return False

    five_minute_count = recent_human_message_count(now, 5 * 60)
    if five_minute_count >= 9:
        return False
    chance = GREETING_MEDIUM_CHANCE if five_minute_count >= 3 else GREETING_BASE_CHANCE

    if random.random() >= chance:
        return False

    last_greeting_response_at = now
    last_greeting_response_by_nick[nick] = now
    return True

def drink_alias_response(msg):
    lowered = msg.lower().strip()

    if lowered.startswith("!"):
        return None

    m = re.match(r"^barbot[:,]?\s+([a-zA-Z]+)", lowered)
    if m:
        word = m.group(1)
        return DRINK_ALIASES.get(word)

    m = re.match(r"^([a-zA-Z]+)\s*(pls|please)?$", lowered)
    if m:
        word = m.group(1)
        if word in DRINK_ALIASES and (m.group(2) or word in {"coffee", "tea", "water", "beer"}):
            return DRINK_ALIASES.get(word)

    return None

class BarBot(irc.bot.SingleServerIRCBot):
    def __init__(self):
        context = ssl.create_default_context()
        context.load_cert_chain(
            certfile=str(BASE / ".config/barbot/certs/barbot.crt"),
            keyfile=str(BASE / ".config/barbot/certs/barbot.key"),
        )
        factory = irc.connection.Factory(
            wrapper=lambda sock: context.wrap_socket(sock, server_hostname=SERVER)
        )
        super().__init__([(SERVER, PORT)], NICK, NICK, connect_factory=factory)
        self.idle_thread_started = False

    def on_welcome(self, c, e):
        print(f"barbot connected to IRC; joining {CHANNEL}", flush=True)
        c.join(CHANNEL)
        if not self.idle_thread_started:
            self.idle_thread_started = True
            threading.Thread(target=self.idle_loop, args=(c,), daemon=True).start()

    def on_join(self, c, e):
        try:
            nick = e.source.nick
            now = time.time()

            if nick == NICK:
                print(f"barbot joined {e.target}", flush=True)

            if nick != NICK:
                seen[nick] = now
                save_json(SEEN_FILE, seen)

            # Only a real JOIN creates a Welcome candidate. hype and barbot
            # are deliberately excluded.
            if welcome_key(nick) not in {
                welcome_key(OWNER_NICK),
                welcome_key(NICK),
            }:
                prune_welcome_candidates(now)
                welcome_candidates[welcome_key(nick)] = now
        except Exception:
            pass

    def idle_loop(self, c):
        while True:
            time.sleep(60)
            now = time.time()
            with idle_state_lock:
                scheduled_time = next_idle_time

            if now >= scheduled_time and now - last_activity >= IDLE_SECONDS:
                try:
                    c.privmsg(CHANNEL, choose_idle_line())
                except Exception:
                    pass
                finally:
                    schedule_next_idle(now)

    def on_disconnect(self, c, e):
        time.sleep(5)
        try:
            self.reconnect()
        except Exception:
            pass

    def on_pubmsg(self, c, e):
        global last_activity

        try:
            raw_msg = e.arguments[0].strip()
            msg = fix_mojibake(raw_msg)
            nick = e.source.nick
            now = time.time()
            last_activity = now
            schedule_next_idle(now)
            lowered = msg.lower()

            if not msg.startswith("!"):
                recent_history.append((nick, msg, now))
                talk_counts[nick] = talk_counts.get(nick, 0) + 1
                seen[nick] = now
                save_json(SEEN_FILE, seen)

                if len(recent_history) > 30:
                    recent_history.pop(0)

                first_speak_replied = False
                if is_welcome_candidate(nick, now) and check_first_speak(nick):
                    c.privmsg(CHANNEL, random.choice(FIRST_SPEAK_REPLIES))
                    consume_welcome_candidate(nick)
                    first_speak_replied = True

                if should_auto_quote(nick, msg):
                    quotes.append({
                        "text": msg,
                        "nick": nick,
                        "time": time.strftime("%Y-%m-%d %H:%M")
                    })
                    save_json(QUOTE_FILE, quotes)

                    rank_data[nick] = rank_data.get(nick, 0) + 1
                    save_json(RANK_FILE, rank_data)

            if msg == "!help":
                c.privmsg(
                    CHANNEL,
                    "!ping !menu !drink [category] !history !who !topic !quote !quote list !quote add text !quote del number(owner) !rank !seen nick !autoquote on/off/status !uptime !about !version !mood"
                )

            elif msg == "!ping":
                c.privmsg(CHANNEL, random.choice([
                    "pong 🍺",
                    "Still here.",
                    "グラスを磨いてる",
                    "生きてるよ",
                    "barbot は静かに営業中",
                ]))

            elif msg == "!uptime":
                c.privmsg(CHANNEL, f"barbot uptime: {format_uptime(time.time() - BOT_STARTED_AT)}")

            elif msg == "!about":
                c.privmsg(CHANNEL, "barbot is a small quiet IRC bar bot for ##bar-jp. Drinks, quotes, topics, history, and a little atmosphere.")

            elif msg == "!version":
                c.privmsg(CHANNEL, VERSION)

            elif msg == "!mood":
                c.privmsg(CHANNEL, random.choice(MOOD_LINES))

            elif msg == "!menu":
                c.privmsg(CHANNEL, "Drink categories: random, whisky, sake, nihonshu, beer, wine, cocktail, classic, gin, rum, soft")

            elif msg == "!drink":
                c.privmsg(CHANNEL, topic_drink())

            elif msg.startswith("!drink "):
                category = msg.split(" ", 1)[1].strip().lower()
                matched = category_drinks(category)

                if matched:
                    c.privmsg(CHANNEL, random.choice(matched))
                else:
                    alias = DRINK_ALIASES.get(category)
                    if alias:
                        c.privmsg(CHANNEL, alias)
                    else:
                        c.privmsg(CHANNEL, f"No drinks found for '{category}'. Try !menu")

            elif msg == "!history":
                if recent_history:
                    c.privmsg(CHANNEL, "Recent: " + compress_history(recent_history[-10:]))
                else:
                    c.privmsg(CHANNEL, "No history yet. The bar is quiet.")

            elif msg == "!who":
                if talk_counts:
                    top = sorted(talk_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                    c.privmsg(CHANNEL, "Top talkers: " + ", ".join([f"{n}({count})" for n, count in top]))
                else:
                    c.privmsg(CHANNEL, "No one has talked much yet.")

            elif msg == "!topic":
                c.privmsg(CHANNEL, generate_topic())

            elif msg == "!quote":
                if quotes:
                    c.privmsg(CHANNEL, quote_text(random.choice(quotes)))
                else:
                    c.privmsg(CHANNEL, "No quotes yet.")

            elif msg == "!quote list":
                if quotes:
                    start = max(1, len(quotes) - 4)
                    items = []
                    for i, q in enumerate(quotes[-5:], start=start):
                        items.append(f"#{i}: {quote_short(q)[:30]}")
                    c.privmsg(CHANNEL, "Quotes: " + " | ".join(items))
                else:
                    c.privmsg(CHANNEL, "No quotes yet.")

            elif msg.startswith("!quote add "):
                text = msg[len("!quote add "):].strip()
                if text:
                    quotes.append({
                        "text": text,
                        "nick": nick,
                        "time": time.strftime("%Y-%m-%d %H:%M")
                    })
                    save_json(QUOTE_FILE, quotes)

                    rank_data[nick] = rank_data.get(nick, 0) + 1
                    save_json(RANK_FILE, rank_data)

                    c.privmsg(CHANNEL, f"Quote saved as #{len(quotes)} 📌")

            elif msg.startswith("!quote del "):
                if nick != OWNER_NICK:
                    c.privmsg(CHANNEL, "Only hype can delete quotes.")
                else:
                    arg = msg.split(" ", 2)[2].strip()

                    if arg.isdigit():
                        num = int(arg)
                        if 1 <= num <= len(quotes):
                            deleted = quotes.pop(num - 1)
                            save_json(QUOTE_FILE, quotes)
                            text = quote_short(deleted)[:40]
                            c.privmsg(CHANNEL, f"Deleted quote #{num}: {text}")
                        else:
                            c.privmsg(CHANNEL, "No such quote number.")
                    else:
                        c.privmsg(CHANNEL, "Usage: !quote del NUMBER")

            elif msg.startswith("!quote "):
                arg = msg.split(" ", 1)[1].strip()
                if arg.isdigit():
                    num = int(arg)
                    if 1 <= num <= len(quotes):
                        c.privmsg(CHANNEL, quote_text(quotes[num - 1]))
                    else:
                        c.privmsg(CHANNEL, "No such quote number.")

            elif msg == "!rank":
                if rank_data:
                    top = sorted(rank_data.items(), key=lambda x: x[1], reverse=True)[:5]
                    c.privmsg(CHANNEL, "🏆 Quote Ranking: " + ", ".join([f"{n}({count})" for n, count in top]))
                else:
                    c.privmsg(CHANNEL, "No ranking yet.")

            elif msg.startswith("!seen "):
                target = msg.split(" ", 1)[1].strip()
                if target == NICK:
                    c.privmsg(CHANNEL, "barbot is right here, polishing glasses 🍻")
                elif target in seen:
                    diff = int(time.time() - seen[target])
                    c.privmsg(CHANNEL, seen_message(target, diff))
                else:
                    c.privmsg(CHANNEL, f"I haven't seen {target}. Maybe they slipped out quietly.")

            elif msg == "!autoquote on":
                autoquote_enabled[nick] = True
                save_json(AUTOQUOTE_FILE, autoquote_enabled)
                c.privmsg(CHANNEL, f"{nick}: AutoQuote ON")

            elif msg == "!autoquote off":
                autoquote_enabled[nick] = False
                save_json(AUTOQUOTE_FILE, autoquote_enabled)
                c.privmsg(CHANNEL, f"{nick}: AutoQuote OFF")

            elif msg == "!autoquote status":
                state = autoquote_enabled.get(nick, True)
                c.privmsg(CHANNEL, f"{nick}: AutoQuote {'ON' if state else 'OFF'}")

            elif lowered.startswith("barbot ") and (("cheers" in lowered) or ("乾杯" in msg)):
                c.privmsg(CHANNEL, random.choice(CHEERS_LINES))

            elif (("cheers" in lowered) or ("乾杯" in msg)):
                c.privmsg(CHANNEL, random.choice(CHEERS_LINES))

            elif msg.lower().startswith("barbot:") or msg.lower().startswith("barbot,"):
                if "おすすめ" in msg or "drink" in msg.lower():
                    c.privmsg(CHANNEL, topic_drink())
                elif "乾杯" in msg or "cheers" in msg.lower():
                    c.privmsg(CHANNEL, random.choice(CHEERS_LINES))
                else:
                    alias = drink_alias_response(msg)
                    if alias:
                        c.privmsg(CHANNEL, alias)
                    else:
                        c.privmsg(CHANNEL, random.choice([
                            "barbot は静かにグラスを磨いている",
                            "Hmm. もう一杯どうだい?",
                            "聞こえてるよ。カウンターの奥からね",
                        ]))

            elif (
                not msg.startswith("!")
                and not first_speak_replied
                and should_greeting_respond(nick, msg, now)
            ):
                c.privmsg(CHANNEL, choose_greeting_reply())
                consume_welcome_candidate(nick)

            elif not msg.startswith("!") and should_name_respond(nick, msg):
                c.privmsg(CHANNEL, name_response(nick))

            else:
                alias = drink_alias_response(msg)
                if alias:
                    c.privmsg(CHANNEL, alias)

            urls = re.findall(r'https?://\S+', msg)
            for u in urls:
                threading.Thread(target=fetch_async, args=(c, u), daemon=True).start()

        except Exception as ex:
            try:
                with open(BASE / "barbot.log", "a", encoding="utf-8") as f:
                    f.write(f"[ERROR] {ex}\n")
            except Exception:
                pass

load_all()
bot = BarBot()
bot.start()
