#!/usr/bin/env python3
"""🍅 pomodoro-cli — a pretty ASCII Pomodoro timer for your terminal.

Single file, zero dependencies. Adapts to Linux / macOS / Windows by itself.
Один файл, без залежностей. Сам підлаштовується під Linux / macOS / Windows.

    python pomodoro.py              interactive start
    python pomodoro.py --yes        reuse last settings, no questions
    python pomodoro.py --stats      last 7 days
    python pomodoro.py --lang uk    Ukrainian UI (en / uk, auto-detected from locale)
"""
import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import time
import warnings
from datetime import date, timedelta
from pathlib import Path

__version__ = "1.0.0"

WIN = sys.platform.startswith("win")
MAC = sys.platform == "darwin"

if WIN:
    import msvcrt
else:
    import select
    import termios
    import tty

# ───────────────────────────── i18n ───────────────────────────────────────────
STR = {
    "en": {
        "t_work": "FOCUS", "t_short": "SHORT BREAK", "t_long": "LONG BREAK", "t_paused": "PAUSED",
        "wq": ["One task. One tomato.", "Phone face down.", "Just this for now. The rest can wait.",
               "Small steps still move you forward.", "Deep breath — and go."],
        "bq": ["Drink some water.", "Look out the window for 20 seconds.", "Stretch your neck and shoulders.",
               "Stand up and walk around.", "Rest your eyes from the screen."],
        "hint": "[space] pause  [s] next  [r] reset  [+/-] time  [t] theme  [m] sound  [q] quit",
        "sess": "session: {done} · focus: {focus}",
        "today": "today: {n} · streak: {s}d · 7 days: {sp}",
        "hm": "{h}h {m:02d}m", "mm": "{m}m",
        "ready": "Ready? Press space.",
        "n_done_t": "🍅 Pomodoro complete!", "n_done_b": "Time for a break: {name}.",
        "n_end_t": "⏰ Break is over", "n_end_b": "Back to focus!",
        "sum": "🍅 Session: {done} pomodoros · {focus} focused. Today: {n} · streak: {s}d. Nice work!",
        "stats_h": "Last 7 days", "stats_f": "Streak: {s}d · week: {sp}",
        "tty": "An interactive terminal is required.",
        "greet": "  🍅 Pomodoro · today: {n} · streak: {s}d · 7 days: {sp}",
        "enter": "  (press Enter to keep the value in brackets)",
        "l_work": "Focus length", "l_short": "Short break", "l_long": "Long break", "unit": "min",
        "task_p": "  What are you working on? (Enter to skip): ",
        "bad": "    Enter a positive number, e.g. 25 or 7.5",
    },
    "uk": {
        "t_work": "ФОКУС", "t_short": "КОРОТКА ПЕРЕРВА", "t_long": "ДОВГА ПЕРЕРВА", "t_paused": "ПАУЗА",
        "wq": ["Одна задача. Один помідор.", "Телефон — екраном донизу.", "Зараз тільки це. Решта почекає.",
               "Маленькі кроки теж рухають вперед.", "Глибокий вдих — і далі."],
        "bq": ["Випий води.", "Подивись у вікно на 20 секунд.", "Розімни плечі та шию.",
               "Встань і пройдися.", "Дай очам відпочити від екрана."],
        "hint": "[пробіл] пауза  [s] далі  [r] скинути  [+/-] час  [t] тема  [m] звук  [q] вийти",
        "sess": "сесія: {done} · у фокусі: {focus}",
        "today": "сьогодні: {n} · серія: {s} дн · 7 днів: {sp}",
        "hm": "{h}г {m:02d}хв", "mm": "{m}хв",
        "ready": "Готовий? Натисни пробіл.",
        "n_done_t": "🍅 Помідор завершено!", "n_done_b": "Час відпочити: {name}.",
        "n_end_t": "⏰ Перерва скінчилась", "n_end_b": "Повертаємось до фокусу!",
        "sum": "🍅 Сесія: {done} помідорів · у фокусі {focus}. Сьогодні: {n} · серія: {s} дн. Гарна робота!",
        "stats_h": "Останні 7 днів", "stats_f": "Серія: {s} дн · тиждень: {sp}",
        "tty": "Потрібен інтерактивний термінал.",
        "greet": "  🍅 Pomodoro · сьогодні: {n} · серія: {s} дн · 7 днів: {sp}",
        "enter": "  (Enter — залишити значення в дужках)",
        "l_work": "Скільки хвилин заняття", "l_short": "Скільки хвилин перерви", "l_long": "Довга перерва",
        "unit": "хв",
        "task_p": "  Над чим працюємо? (Enter — пропустити): ",
        "bad": "    Введи додатнє число, наприклад 25 або 7.5",
    },
}
LANG = "en"


def tr(key, **kw):
    s = STR[LANG][key]
    return s.format(**kw) if kw else s


def detect_lang():
    for var in ("LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"):
        v = os.environ.get(var, "")
        if v:
            return "uk" if v.lower().startswith(("uk", "ua")) else "en"
    try:
        import locale
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            loc = (locale.getdefaultlocale()[0] or "").lower()
        return "uk" if loc.startswith(("uk", "ukrainian")) else "en"
    except Exception:
        return "en"


# ───────────────────────────── look & feel ────────────────────────────────────
FONT = {
    "0": ["███", "█ █", "█ █", "█ █", "███"],
    "1": [" █ ", "██ ", " █ ", " █ ", "███"],
    "2": ["███", "  █", "███", "█  ", "███"],
    "3": ["███", "  █", "███", "  █", "███"],
    "4": ["█ █", "█ █", "███", "  █", "  █"],
    "5": ["███", "█  ", "███", "  █", "███"],
    "6": ["███", "█  ", "███", "█ █", "███"],
    "7": ["███", "  █", "  █", "  █", "  █"],
    "8": ["███", "█ █", "███", "█ █", "███"],
    "9": ["███", "█ █", "███", "  █", "███"],
    ":": [" ", "█", " ", "█", " "],
}

THEMES = {
    "classic": {"work": 203, "short": 78, "long": 75, "paused": 245},
    "ocean": {"work": 39, "short": 49, "long": 141, "paused": 245},
    "matrix": {"work": 46, "short": 34, "long": 40, "paused": 240},
    "sunset": {"work": 208, "short": 213, "long": 177, "paused": 245},
    "mono": {"work": 255, "short": 250, "long": 247, "paused": 243},
}
RIPE = [71, 107, 143, 179, 209, 203, 196]  # the tomato ripens: green → red
FACES = {"work": "ò_ó", "short": "^‿^", "long": "^‿^", "paused": "-_-"}

RESET, DIM, BOLD = "\x1b[0m", "\x1b[2m", "\x1b[1m"


def fg(code):
    return f"\x1b[38;5;{code}m"


def big(text):
    """5 rows of IDENTICAL width, so the clock never jitters when digits change."""
    rows = [[] for _ in range(5)]
    for ch in text:
        for i in range(5):
            rows[i].append("".join(c * 2 for c in FONT[ch][i]))
    return ["  ".join(r) for r in rows]


def tomato(face, frame):
    leaf = ["\\|/", "/|\\"][frame % 2]
    return [
        f"     {leaf}     ",
        "  .-\"\"\"\"\"-.  ",
        " /         \\ ",
        f"|    {face}    |",
        " \\         / ",
        "  `-.....-'  ",
    ]


def cup(frame):
    steam = ["  ( (  ", " ) )   "] if frame % 2 else ["  ) )  ", "  ( (  "]
    return [
        steam[0].center(13),
        steam[1].center(13),
        " .---------. ",
        " |         |)",
        " |         |)",
        "  \\       /  ",
        "   `-----'   ",
    ]


def spark(vals):
    bars = "▁▂▃▄▅▆▇█"
    m = max(vals) or 1
    return "".join(bars[min(7, int(v / m * 7))] if v else "·" for v in vals)


def fmt_total(seconds):
    m = int(seconds // 60)
    return tr("hm", h=m // 60, m=m % 60) if m >= 60 else tr("mm", m=m)


# ───────────────────────────── platform glue ──────────────────────────────────
def enable_ansi():
    if WIN:
        try:
            import ctypes
            k = ctypes.windll.kernel32
            h = k.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            if k.GetConsoleMode(h, ctypes.byref(mode)):
                k.SetConsoleMode(h, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
        except Exception:
            pass
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# Ukrainian layout aliases: й/і/к/ь/е sit on the same physical keys as q/s/r/m/t
ALIASES = {"й": "q", "і": "s", "ы": "s", "к": "r", "ь": "m", "е": "t", "\x03": "q", "=": "+", "_": "-"}


class Keys:
    """Non-blocking key reader: termios on Linux/macOS, msvcrt on Windows."""

    def __enter__(self):
        if not WIN:
            self.fd = sys.stdin.fileno()
            self.old = termios.tcgetattr(self.fd)
            tty.setcbreak(self.fd)
        return self

    def __exit__(self, *exc):
        if not WIN:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)

    def get(self, timeout):
        if WIN:
            end = time.monotonic() + timeout
            while True:
                if msvcrt.kbhit():
                    ch = msvcrt.getwch()
                    if ch in ("\x00", "\xe0"):  # arrows / F-keys: swallow
                        msvcrt.getwch()
                        return ""
                    break
                if time.monotonic() >= end:
                    return None
                time.sleep(0.02)
        else:
            if not select.select([sys.stdin], [], [], timeout)[0]:
                return None
            chunk = os.read(self.fd, 32).decode(errors="ignore")
            if not chunk or chunk[0] == "\x1b":  # escape sequences (arrows): ignore
                return ""
            ch = chunk[0]
        ch = ch.lower()
        return ALIASES.get(ch, ch)


def data_dir():
    if WIN:
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    elif MAC:
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return base / "pomodoro-cli"


def _run(cmd):
    kw = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if WIN:
        kw["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    subprocess.Popen(cmd, **kw)


def notify(title, body, sound=True):
    try:
        if MAC:
            esc = lambda s: s.replace("\\", "\\\\").replace('"', '\\"')
            _run(["osascript", "-e", f'display notification "{esc(body)}" with title "{esc(title)}"'])
        elif WIN:
            q = lambda s: s.replace("'", "''")
            ps = (
                "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null;"
                "$x = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02);"
                "$t = $x.GetElementsByTagName('text');"
                f"$t.Item(0).AppendChild($x.CreateTextNode('{q(title)}')) | Out-Null;"
                f"$t.Item(1).AppendChild($x.CreateTextNode('{q(body)}')) | Out-Null;"
                "$n = [Windows.UI.Notifications.ToastNotification]::new($x);"
                "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("
                "'{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe').Show($n)"
            )
            _run(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps])
        elif shutil.which("notify-send"):
            _run(["notify-send", "-a", "Pomodoro", "-i", "appointment-soon", title, body])
    except Exception:
        pass
    if sound:
        play_sound()


def play_sound():
    try:
        if WIN:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
            return
        if MAC:
            _run(["afplay", "/System/Library/Sounds/Glass.aiff"])
            return
        for path in ("/usr/share/sounds/freedesktop/stereo/complete.oga",
                     "/usr/share/sounds/freedesktop/stereo/bell.oga"):
            if os.path.exists(path):
                for player in ("paplay", "pw-play"):
                    if shutil.which(player):
                        _run([player, path])
                        return
        if shutil.which("canberra-gtk-play"):
            _run(["canberra-gtk-play", "-i", "complete"])
            return
    except Exception:
        pass
    sys.stdout.write("\a")
    sys.stdout.flush()


# ───────────────────────────── stats & settings ───────────────────────────────
class Store:
    def __init__(self):
        self.path = data_dir() / "stats.json"
        self.data = {"settings": {}, "days": {}}
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                self.data["settings"] = loaded.get("settings") or {}
                self.data["days"] = loaded.get("days") or {}
        except Exception:
            pass

    def save(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.data, ensure_ascii=False, indent=1), encoding="utf-8")
            tmp.replace(self.path)
        except Exception:
            pass

    def _day(self, d):
        v = self.data["days"].get(d.isoformat())
        return v if isinstance(v, dict) else {}

    def pomos(self, d):
        return int(self._day(d).get("pomodoros", 0))

    def minutes(self, d):
        return float(self._day(d).get("minutes", 0))

    def add(self, pomodoros=0, minutes=0.0):
        d = self.data["days"].setdefault(date.today().isoformat(), {"pomodoros": 0, "minutes": 0})
        d["pomodoros"] = int(d.get("pomodoros", 0)) + pomodoros
        d["minutes"] = round(float(d.get("minutes", 0)) + minutes, 1)

    def week(self):
        today = date.today()
        return [self.pomos(today - timedelta(days=i)) for i in range(6, -1, -1)]

    def streak(self):
        d, n = date.today(), 0
        if self.pomos(d) == 0:
            d -= timedelta(days=1)
        while self.pomos(d) > 0:
            n += 1
            d -= timedelta(days=1)
        return n


def print_stats(store):
    print(f"\n  🍅 {tr('stats_h')}\n")
    today = date.today()
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        n = store.pomos(d)
        print(f"  {d.isoformat()}  {'█' * n:<12} {n:>2}  ({fmt_total(store.minutes(d) * 60)})")
    print(f"\n  {tr('stats_f', s=store.streak(), sp=spark(store.week()))}\n")


# ───────────────────────────── drawing ────────────────────────────────────────
class State:
    def __init__(self, durations, task):
        self.durations = durations
        self.task = task
        self.mode = "work"
        self.paused = False
        self.done = 0
        self.focus = 0.0
        self.flushed = 0.0
        self.frame = 0
        self.total = self.remaining = durations["work"]
        self.quote = random.choice(STR[LANG]["wq"])

    def switch(self, mode, paused=False):
        self.mode, self.paused = mode, paused
        self.total = self.remaining = self.durations[mode]
        self.quote = tr("ready") if paused else random.choice(STR[LANG]["wq" if mode == "work" else "bq"])


def draw(st, theme, store, cycles):
    cols, rows = shutil.get_terminal_size((80, 24))
    key = "paused" if st.paused else st.mode
    color = fg(THEMES[theme][key])
    progress = min(1.0, max(0.0, 1 - st.remaining / st.total)) if st.total else 1.0

    body = []

    def add(text="", style=""):
        body.append((text[:cols], style))

    def block(lines, style, target):
        w = max(len(l) for l in lines)
        for l in lines:
            target.append((l.ljust(w), style))  # equal widths → centred as one block

    title = tr("t_" + key) + (f"  ·  {st.task}" if st.task else "")
    add(title, BOLD + color)
    add()
    block(big("{:02d}:{:02d}".format(*divmod(int(st.remaining + 0.999), 60))), color, body)
    add()
    width = 44
    filled = int(width * progress)
    add("█" * filled + "░" * (width - filled) + f"  {int(progress * 100):3d}%", color)
    add("  ".join("●" if i < st.done % cycles else "○" for i in range(cycles)), color)
    add(tr("sess", done=st.done, focus=fmt_total(st.focus)), DIM)
    add(tr("today", n=store.pomos(date.today()), s=store.streak(), sp=spark(store.week())), DIM)
    add()
    add(st.quote, DIM)
    add(tr("hint"), DIM)

    art = []
    if st.mode == "work":
        art_color = fg(245) if st.paused else fg(RIPE[min(len(RIPE) - 1, int(progress * len(RIPE)))])
        block(tomato(FACES[key], st.frame), art_color, art)
    else:
        block(cup(st.frame), color, art)
    art.append(("", ""))

    lines = body
    if rows >= len(body) + len(art) + 1:  # tiny terminal → drop the art
        lines = art + body

    top = max(0, (rows - len(lines)) // 2)
    out = ["\x1b[H"] + ["\x1b[K\n"] * top
    for text, style in lines:
        pad = max(0, (cols - len(text)) // 2)
        out.append(f"\x1b[K{' ' * pad}{style}{text}{RESET}\n")
    out.append("\x1b[J")
    sys.stdout.write("".join(out))
    sys.stdout.flush()


def confetti():
    cols, rows = shutil.get_terminal_size((80, 24))
    palette = [196, 208, 226, 46, 51, 201]
    pieces = [[random.randrange(cols), random.randrange(-rows, rows // 2),
               random.choice("*+o.x~"), random.choice(palette)] for _ in range(max(30, cols // 2))]
    for _ in range(20):
        buf = ["\x1b[2J"]
        for p in pieces:
            p[1] += random.choice((1, 1, 2))
            if 0 <= p[1] < rows:
                buf.append(f"\x1b[{p[1] + 1};{p[0] + 1}H{fg(p[3])}{p[2]}")
        sys.stdout.write("".join(buf) + RESET)
        sys.stdout.flush()
        time.sleep(0.07)
    sys.stdout.write("\x1b[2J")


# ───────────────────────────── main ───────────────────────────────────────────
def ask_minutes(label, default):
    while True:
        raw = input(f"  {tr(label)} ({tr('unit')}) [{default:g}]: ").strip().replace(",", ".")
        if not raw:
            return default
        try:
            val = float(raw)
            if val > 0:
                return val
        except ValueError:
            pass
        print(tr("bad"))


def good(v, default):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0 else default


def main():
    global LANG
    enable_ansi()
    ap = argparse.ArgumentParser(prog="pomodoro", description="A pretty ASCII Pomodoro timer for your terminal.")
    ap.add_argument("--work", type=float, help="focus length, minutes")
    ap.add_argument("--short", type=float, help="short break, minutes")
    ap.add_argument("--long", type=float, help="long break, minutes (default: 3x short)")
    ap.add_argument("--cycles", type=int, default=4, help="pomodoros before a long break (default: 4)")
    ap.add_argument("--task", help="what you are working on")
    ap.add_argument("--theme", choices=list(THEMES), help="colour theme")
    ap.add_argument("--lang", choices=list(STR), help="interface language (default: auto)")
    ap.add_argument("--yes", action="store_true", help="skip the questions, reuse last settings")
    ap.add_argument("--manual", action="store_true", help="wait for [space] before every phase")
    ap.add_argument("--no-sound", action="store_true", help="disable sounds")
    ap.add_argument("--stats", action="store_true", help="show the last 7 days and exit")
    ap.add_argument("--version", action="version", version=f"pomodoro-cli {__version__}")
    args = ap.parse_args()

    store = Store()
    saved = store.data["settings"]
    LANG = args.lang or (saved.get("lang") if saved.get("lang") in STR else detect_lang())
    if args.lang:
        saved["lang"] = args.lang

    if args.stats:
        print_stats(store)
        return
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        sys.exit(tr("tty"))

    work = args.work or good(saved.get("work"), 25)
    short = args.short or good(saved.get("short"), 5)
    long_ = args.long or good(saved.get("long"), round(short * 3, 2))
    theme = args.theme or (saved.get("theme") if saved.get("theme") in THEMES else "classic")
    sound_on = not args.no_sound and bool(saved.get("sound", True))
    task = args.task or ""

    if not args.yes:
        print("\n" + tr("greet", n=store.pomos(date.today()), s=store.streak(), sp=spark(store.week())))
        print(tr("enter") + "\n")
        work = ask_minutes("l_work", work)
        short = ask_minutes("l_short", short)
        long_ = ask_minutes("l_long", args.long or round(short * 3, 2))
        if not args.task:
            task = input(tr("task_p")).strip()
    elif not args.long and "long" not in saved:
        long_ = short * 3

    saved.update(work=work, short=short, long=long_, theme=theme)
    store.save()

    st = State({"work": work * 60, "short": short * 60, "long": long_ * 60}, task)
    if args.manual:
        st.paused, st.quote = True, tr("ready")

    def flush():
        delta = st.focus - st.flushed
        if delta >= 1:
            store.add(minutes=delta / 60)
            st.flushed = st.focus
        store.save()

    sys.stdout.write("\x1b[?1049h\x1b[?25l\x1b[2J")  # alt screen + hide cursor
    try:
        with Keys() as keys:
            last = last_frame = last_save = time.monotonic()
            last_title = ""
            while True:
                now = time.monotonic()
                dt, last = now - last, now
                if not st.paused:
                    st.remaining -= dt
                    if st.mode == "work":
                        st.focus += dt
                if now - last_frame >= 0.8:
                    st.frame += 1
                    last_frame = now
                if now - last_save >= 60:
                    flush()
                    last_save = now

                nxt = None
                if st.remaining <= 0:
                    if st.mode == "work":
                        st.done += 1
                        store.add(pomodoros=1)
                        flush()
                        nxt = "long" if st.done % args.cycles == 0 else "short"
                        notify(tr("n_done_t"), tr("n_done_b", name=tr("t_" + nxt).lower()), sound_on)
                        confetti()
                    else:
                        nxt = "work"
                        notify(tr("n_end_t"), tr("n_end_b"), sound_on)
                    last = time.monotonic()

                k = keys.get(0.1)
                if k == "q":
                    break
                elif k == " ":
                    st.paused = not st.paused
                elif k == "r":
                    st.remaining = st.total
                elif k == "s":  # skipping an unfinished pomodoro does not count it
                    nxt = "short" if st.mode == "work" else "work"
                elif k == "+":
                    st.remaining += 60
                    st.total += 60
                elif k == "-" and st.remaining > 60:
                    st.remaining -= 60
                    st.total -= 60
                elif k == "t":
                    names = list(THEMES)
                    theme = names[(names.index(theme) + 1) % len(names)]
                elif k == "m":
                    sound_on = not sound_on

                if nxt:
                    st.switch(nxt, paused=args.manual)

                draw(st, theme, store, args.cycles)
                title = "🍅 {:02d}:{:02d} · {}".format(*divmod(int(st.remaining + 0.999), 60), tr("t_" + st.mode))
                if title != last_title:
                    sys.stdout.write(f"\x1b]0;{title}\x07")  # terminal / taskbar title
                    last_title = title
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\x1b]0;\x07\x1b[?25h\x1b[?1049l")
        sys.stdout.flush()
        flush()
        saved["theme"] = theme
        if not args.no_sound:
            saved["sound"] = sound_on
        store.save()
        print(tr("sum", done=st.done, focus=fmt_total(st.focus), n=store.pomos(date.today()), s=store.streak()))


def cli():
    """Console-script entry point (handles Ctrl+C at the prompts too)."""
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()


if __name__ == "__main__":
    cli()
