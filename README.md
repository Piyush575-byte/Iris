# 🔍 Iris
**A terminal session recorder that creates searchable debugging artifacts.**

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-green.svg)
![FOSS](https://img.shields.io/badge/FOSS-100%25-brightgreen.svg)

Record your terminal sessions. Search through them. Replay, summarize, and export — all from the command line.

---

The Problem
You're debugging at 2 AM. You run 40 commands, finally fix it. Next day your teammate asks: "What did you do?"
You don't remember. Terminal history shows commands — not output. Screenshots show one moment — not the sequence. The session is gone.

Three people who feel this every single day
1. Junior developer — Ravi
Debugged for 3 hours, fixed it, has no idea which step worked. Sends his senior 3 blurry screenshots and a paragraph from memory. Senior spends another hour reproducing the same problem.
Current tools fail him: history has no output. Screenshots have no sequence. He's reconstructing a crime scene from memory.
2. Senior developer — Amit
Gets 5 Slack messages a day: "bhai error aa raha hai" + one blurry screenshot. Asks follow-up questions. More screenshots. 20 minutes of back-and-forth to understand a 30-second problem.
Current tools fail him: there is no way to share a complete debugging session asynchronously. He either jumps on a call or plays 20-questions over chat.
3. Open source maintainer
Someone opens a GitHub issue: "crashes on startup." Zero context. Maintainer asks for logs. User pastes partial output. Maintainer asks for more. User disappears. Issue sits open for months.
Current tools fail him: users don't know what to copy. They always copy the wrong thing.

Why Iris is worth switching to
One command — iris record. Every command, every output, every exit code, every timestamp — saved into one clean .trace file. Send it like any attachment. The receiver searches it, replays it, understands it — no calls, no screenshots, no memory required.
Switching cost: one command. Switching benefit: never explain a bug from memory again.
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
│  $ stop                                         │
│                                                 │
│  ✅ Session saved to 2026-02-24_14-30-00.trace  │
└─────────────────────────────────────────────────┘
```

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎬 Multi-Terminal Record | Capture sessions from multiple windows into ONE trace file using the daemon |
| ⏹️ Cross-Terminal Stop | Stop recording from any terminal with `iris stop` — no need to switch back |
| 🔎 Search | Find specific commands or output across recorded sessions |
| ▶️ Replay | Play back sessions in real-time to review what happened |
| 📊 Summary | Get session stats — duration, command count, error detection |
| 📄 Export | Generate clean, shareable text reports from recordings |
| 🛡️ Auto-Redact | Automatically strips passwords, API keys, and tokens from traces |
| 💪 Resilient Recording | Won't crash from transient errors — only stops when you say so |
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

**Optional: Add to PATH (run `iris` from any folder)**

Linux / macOS:
```bash
chmod +x iris.py
sudo ln -s $(pwd)/iris.py /usr/local/bin/iris
```

Windows (PowerShell — run once):
```powershell
$p = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$p;C:\path\to\Iris", "User")
```
Then restart your terminal. The included `iris.bat` wrapper lets you use `iris record`, `iris stop`, etc. from anywhere.

---

## 📖 Usage

**1. Start the Background Daemon**
```bash
iris start
```
This runs Iris in server mode, listening for terminals to attach.

**2. Attach Any Terminal**
```bash
iris shell
# Or just
iris record
```
Run this in *any* terminal (or multiple terminals) you want to record. Everything you type is sent to the central daemon.

**3. Run a Single Script/Command**

If you don't want a full interactive shell (or if you hit the "Terminate batch job" error in VS Code when pressing Ctrl+C), use `iris run`:
```bash
iris run python my_script.py
```
This transparently executes the command, streams the output, and saves it into the daemon's active `.trace` file (or a local file if no daemon is running).

**4. Stop the Recording**

You have three ways to stop:
```bash
# From ANY terminal (even a different one):
iris stop

# From inside a recording terminal:
stop

# Or press Ctrl+C inside a recording terminal
```
Stopping the daemon saves a single `.trace` file combining all commands from all attached terminals.

**Search a Session**
```bash
iris search "error" examples/demo_session.trace
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
iris replay examples/demo_session.trace
```
Plays back each command and its output with a short delay, simulating the original session.

**Get Session Summary**
```bash
iris summary examples/demo_session.trace
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
iris export examples/demo_session.trace --output report.txt
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
