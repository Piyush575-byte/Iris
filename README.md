# 🔍 Iris
**A terminal session recorder that creates searchable debugging artifacts.**

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-green.svg)
![FOSS](https://img.shields.io/badge/FOSS-100%25-brightgreen.svg)

Record your terminal sessions. Search through them. Replay, summarize, and export — all from the command line.

---

## The Problem

You're debugging a server issue at 2 AM. You run dozens of commands, scroll through walls of output, and finally fix it. The next day, your teammate asks: *"What did you do to fix it?"*

You don't remember. The terminal history is gone. The output is lost.

---

### Who is actually suffering — and why they need to switch

**1. The junior developer who can't explain what happened.**

Ravi has been debugging for 3 hours. He ran 40 commands, tried 6 different fixes, and finally got it working — but he has no idea which step actually solved it. When his senior asks for a bug report, Ravi pastes 3 scattered screenshots and writes a paragraph from memory. His senior spends another hour trying to reproduce the same environment. Neither of them has time for this.

*Ravi needs to switch because his current tools — shell history and screenshots — don't capture what actually happened. `history` shows commands but no output. Screenshots show one moment but not the sequence. He is reconstructing a crime scene from memory.*

**2. The senior developer drowning in "it doesn't work on my machine."**

Amit receives 5 Slack messages a day that all look like this: "bhai ye error aa raha hai" followed by a blurry screenshot of half a terminal. He asks follow-up questions. The junior runs more commands. More screenshots. 20 minutes of back-and-forth to understand a 30-second problem.

*Amit needs to switch because no current tool gives him the full sequence in one shot. He either jumps on a call — expensive — or plays 20-questions over Slack — slow. There is no async way to share a complete debugging session right now.*

**3. The open source maintainer who can't reproduce bugs.**

Every week someone opens a GitHub issue that says "crashes on startup" with zero context. The maintainer asks for logs. The user pastes partial output. The maintainer asks for more. The user disappears. The issue sits open for months.

*The maintainer needs to switch because asking users to manually collect and share terminal context is too much friction. Users don't know what to copy. They copy the wrong thing. A single `.trace` file attachment would contain everything — but no standard tool creates one.*

---

### Why everything you're already using fails

**Shell history (`history` command):** Shows commands. Zero output. Zero exit codes. Zero timestamps. You know *what* you ran. You have no idea *what happened* when you ran it.

**Screenshots:** Capture one frozen moment. A debugging session is 40 moments in sequence. You would need 40 screenshots to tell the full story — and they still wouldn't be searchable.

**`script` command (Linux built-in):** Dumps everything to a file — but "everything" includes ANSI color codes, terminal resize events, cursor movements, and raw control characters. The output looks like this: `^[[0m^[[01;34m`. Unreadable by humans, unparseable by machines.

**asciinema:** Records a video of your terminal. You can watch it. You cannot search it, grep it, or query it programmatically. Finding one error in a 20-minute recording means scrubbing through video like it's YouTube.

**Pasting into ChatGPT:** You share one error. One moment. ChatGPT has no idea what you tried before, what worked, what didn't. It gives generic advice because it only sees the crash site — not the flight path that led there.

**None of these tools were built for the "share your debugging journey" use case. They were built for other things and developers have been awkwardly force-fitting them ever since.**

---

### Why Iris is worth switching to

Iris does one thing none of the above can do: it captures the **complete, structured, searchable sequence** of what happened — not a video, not a raw dump, not a partial history — a clean JSON artifact where every command, every output, every exit code, and every timestamp is a separate queryable field.

The switching cost is exactly one command: `iris record`. Nothing to configure. Nothing to install on the receiving end. The person you send the `.trace` file to only needs Python — which they already have.

The switching benefit is immediate: the next time something breaks and someone asks what happened, you send one file instead of writing three paragraphs from memory.

*That is a switch worth making.*

---

## The Solution

```
┌─────────────────────────────────────────────────┐
│  $ iris record                                  │
│                                                 │
│  🔴 Recording...                                │
│  $ kubectl get pods                             │
│  $ docker logs api-server --tail 50             │
│  $ vim /etc/nginx/nginx.conf                    │
│  $ systemctl restart nginx                      │
│  $ exit                                         │
│                                                 │
│  ✅ Session saved to 2026-02-24_14-30-00.trace  │
└─────────────────────────────────────────────────┘
```

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎬 Record | Capture full terminal sessions with timestamps and command output |
| 🔎 Search | Find specific commands or output across recorded sessions |
| ▶️ Replay | Play back sessions in real-time to review what happened |
| 📊 Summary | Get session stats — duration, command count, error detection |
| 📄 Export | Generate clean, shareable text reports from recordings |
| 🛡️ Auto-Redact | Automatically strips passwords, API keys, and tokens from traces |
| 🌐 Cross-Platform | Works on Linux, macOS, and Windows with native integrations |
| 📦 Zero Dependencies | No external packages needed on Linux/macOS (only pywinpty on Windows) |

---

## 🏗️ Architecture

```
iris.py                   ← CLI entry point & argument parser
│
├── recorder_unix.py      ← Linux/macOS recorder (pty + select)
├── recorder_windows.py   ← Windows recorder (pywinpty + threads)
│
├── redact.py             ← ANSI stripping, sensitive data redaction, event builder
├── storage.py            ← JSON trace file I/O
│
├── search.py             ← Full-text search across trace events
├── replay.py             ← Terminal playback engine
├── summary.py            ← Session statistics & error counting
└── export.py             ← Clean text report generator
```

---

## Trace File Format

Sessions are stored as structured JSON (`.trace` files):

```json
{
  "session_id": "2026-02-24_14-30-00",
  "start_time": "2026-02-24T14:30:00",
  "end_time": "2026-02-24T14:32:15",
  "hostname": "dev-machine",
  "events": [
    {
      "id": 1,
      "type": "command",
      "timestamp": "2026-02-24T14:30:05",
      "command": "echo Hello from Iris!",
      "output": "Hello from Iris!",
      "exit_code": 0,
      "duration_ms": 120
    }
  ]
}
```

---

## 🚀 Installation

```bash
git clone https://github.com/piyush1910dtu-dot/Iris.git
cd Iris
```

**Linux / macOS** — no extra dependencies:
```bash
python3 iris.py --help
```

**Windows** — install the PTY adapter:
```bash
pip install -r requirements.txt
python iris.py --help
```

**Optional: Add to PATH**

Linux / macOS:
```bash
chmod +x iris.py
sudo ln -s $(pwd)/iris.py /usr/local/bin/iris
```

Windows: Add the Iris directory to your system PATH, then use the included `iris.bat` wrapper.

---

## 📖 Usage

**Record a Session**
```bash
python iris.py record
```
This spawns a new shell and records everything. Type `exit` or press `Ctrl+D` to stop. The session is saved as a `.trace` file in the current directory.

**Search a Session**
```bash
python iris.py search "error" examples/demo_session.trace
```
```
Searching for 'error' in examples/demo_session.trace...

[2026-02-24T14:31:30] Event #5 (Exit: 1)
$ curl https://api.example.com/status
Connection refused
----------------------------------------
Found 1 matching events.
```

**Replay a Session**
```bash
python iris.py replay examples/demo_session.trace
```
Plays back each command and its output with a short delay, simulating the original session.

**Get Session Summary**
```bash
python iris.py summary examples/demo_session.trace
```
```
Session: 2026-02-24_14-30-00
Host: dev-machine
Duration: 135 seconds
Total commands: 5
Errors detected: 2
```

**Export as Text Report**
```bash
python iris.py export examples/demo_session.trace --output report.txt
```
Generates a clean, shareable plain-text report without ANSI codes or sensitive data.

---

## 🖥️ Platform Support

| Platform | Backend | Status |
|---|---|---|
| Linux | Native PTY (pty + select) | ✅ Fully supported |
| macOS | Native PTY (pty + select) | ✅ Fully supported |
| Windows | pywinpty | ✅ Fully supported |

---

## 🛡️ Security & Privacy

Iris automatically redacts sensitive information from recorded sessions:

- **Passwords** — `password=s3cret` → `[REDACTED]`
- **API keys** — `api_key=abc123...` → `[REDACTED]`
- **Bearer tokens** — `Authorization: Bearer eyJ...` → `[REDACTED]`
- **Long random strings** — potential secrets are caught by pattern matching

All recordings stay 100% local — nothing is ever sent to any server.

---

## 🤝 Contributing

Contributions are welcome! Please read the Contributing Guidelines before submitting a PR.

See also our Code of Conduct.

---

## 📄 License

This project is licensed under the MIT License — see the LICENSE file for details.

---

*Built with ❤️ and Python. No closed-source dependencies. No telemetry. Just a simple tool that does its job.*
