<div align="center">

# 🍅 pomodoro-cli

**A pretty, zero-dependency ASCII Pomodoro timer for your terminal.**
One file. Linux · macOS · Windows. It figures out the rest.

[![CI](https://github.com/YOUR_USERNAME/pomodoro-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/pomodoro-cli/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Platforms](https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey)
![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

**English** · [Українська](README.uk.md)

</div>

```text
                                     \|/
                                  .-"""""-.
                                 /         \
                                |    ò_ó    |
                                 \         /
                                  `-.....-'

                       FOCUS  ·  Write the thesis intro

                      ██████  ██████      ██████  ██████
                      ██  ██  ██  ██  ██      ██  ██  ██
                      ██  ██  ██████      ██████  ██  ██
                      ██  ██      ██  ██      ██  ██  ██
                      ██████  ██████      ██████  ██████

              ███████████████████████████░░░░░░░░░░░░░░░░░   62%
                                  ●  ●  ○  ○
                           session: 2 · focus: 50m
                   today: 4 · streak: 5d · 7 days: ▄·▅█▆▃▅

                            One task. One tomato.
[space] pause  [s] next  [r] reset  [+/-] time  [t] theme  [m] sound  [q] quit
```

```text
                                     ( (
                                    ) )
                                 .---------.
                                 |         |)
                                 |         |)
                                  \       /
                                   `-----'

                    SHORT BREAK  ·  Write the thesis intro

                      ██████  ██████      ██  ██  ██████
                      ██  ██      ██  ██  ██  ██  ██
                      ██  ██  ██████      ██████  ██████
                      ██  ██  ██      ██      ██      ██
                      ██████  ██████          ██  ██████

              ███████████████████░░░░░░░░░░░░░░░░░░░░░░░░░   44%
                                  ●  ●  ○  ○
                           session: 2 · focus: 50m
                   today: 4 · streak: 5d · 7 days: ▄·▅█▆▃▅

                              Drink some water.
[space] pause  [s] next  [r] reset  [+/-] time  [t] theme  [m] sound  [q] quit
```

> The tomato **ripens from green to red** as your focus session progresses, and turns into a steaming coffee cup on breaks.

## ✨ Features

- **Big, jitter-free clock**: fixed-width block digits, a progress bar and cycle dots (`● ● ○ ○`).
- **Classic Pomodoro cycle**: focus → short break → … → long break every N pomodoros.
- **Asks first**: how long to focus, how long to rest and what you're working on. It remembers your answers for next time.
- **Native notifications and sounds** on every OS (details below), plus a little **confetti** when a pomodoro is done 🎉
- **Stats that stick**: today's count, daily **streak** and a 7-day sparkline (`▄·▅█▆▃▅`), stored locally.
- **5 colour themes** you can switch live: `classic`, `ocean`, `matrix`, `sunset`, `mono`.
- **Live adjustments**: `+` / `-` change the current phase by a minute, pause, reset or skip at any time.
- Remaining time in the **terminal / taskbar title**, so you can see it from another window.
- **English and Ukrainian UI** (auto-detected), and hotkeys work with the Ukrainian keyboard layout too.
- Adapts to small terminals (drops the art when there isn't enough room).
- A single file with **no dependencies**: only the Python standard library.

## 📦 Install

**Just run it** (nothing to install):

```bash
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/pomodoro-cli/main/pomodoro.py
python pomodoro.py
```

**Or install a `pomodoro` command:**

```bash
pipx install git+https://github.com/YOUR_USERNAME/pomodoro-cli
# or: pip install git+https://github.com/YOUR_USERNAME/pomodoro-cli
pomodoro
```

Requires Python 3.10+. On Windows, use Windows Terminal or any terminal with ANSI support (Windows 10+).

## 🚀 Usage

```bash
pomodoro                         # interactive: asks for focus / break / task
pomodoro --yes                   # reuse last settings, no questions
pomodoro --work 50 --short 10    # custom lengths (minutes)
pomodoro --task "Write thesis"   # show what you're working on
pomodoro --manual                # wait for [space] before each phase
pomodoro --theme ocean           # pick a colour theme
pomodoro --stats                 # last 7 days
```

### ⌨️ Controls

| Key | Action |
| --- | --- |
| `space` | pause / resume |
| `s` | skip to the next phase (an unfinished pomodoro is **not** counted) |
| `r` | restart the current phase |
| `+` / `-` | add / remove one minute |
| `t` | cycle colour theme |
| `m` | mute / unmute |
| `q` | quit (`Ctrl+C` works too) |

### 🔧 Options

| Option | Description |
| --- | --- |
| `--work N` | focus length in minutes (default `25`) |
| `--short N` | short break in minutes (default `5`) |
| `--long N` | long break in minutes (default 3× short) |
| `--cycles N` | pomodoros before a long break (default `4`) |
| `--task TEXT` | what you're working on |
| `--theme NAME` | `classic` · `ocean` · `matrix` · `sunset` · `mono` |
| `--lang en\|uk` | interface language (default: auto-detected, then remembered) |
| `--yes` | skip the questions, reuse last settings |
| `--manual` | wait for `space` before each phase starts |
| `--no-sound` | disable sounds |
| `--stats` | print the last 7 days and exit |
| `--version` | print the version |

## 🖥️ How it adapts to your OS

| | Linux | macOS | Windows |
| --- | --- | --- | --- |
| Keyboard input | `termios` | `termios` | `msvcrt` |
| Notifications | `notify-send` | `osascript` | PowerShell toast |
| Sound | `paplay` / `pw-play` / `canberra` | `afplay` | `winsound` |
| Data directory | `~/.local/share/pomodoro-cli` | `~/Library/Application Support/pomodoro-cli` | `%APPDATA%\pomodoro-cli` |

If a notifier or sound player isn't available, the app silently falls back to the terminal bell.
Settings and stats live in a small `stats.json` in the data directory. Delete it to reset everything.

> **Testing note:** developed and tested on Linux. macOS and Windows code paths are covered by CI (syntax and startup), but notifications on those systems have had less real-world testing. Issues and PRs are very welcome!

## ❓ FAQ

**The digits look broken or misaligned.**
Use a terminal font with box-drawing / block characters (almost any monospace font works).

**No notification appears on Linux.**
Install `libnotify` (`notify-send`) and make sure a notification daemon is running.

**Can I change the colours?**
Press `t` while running, or start with `--theme`. Themes are simple dictionaries at the top of `pomodoro.py`.

## 🤝 Contributing

Ideas, bug reports and PRs are welcome. The goal is to stay **one file, no dependencies**.
Ideas: more themes, custom sound files, a `--long-every` per-session override, a weekly summary.

## 📄 License

[MIT](LICENSE)
