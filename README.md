<div align="center">

# 🔍 Iris

**A terminal session recorder that creates searchable debugging artifacts.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)](#platform-support)
[![FOSS](https://img.shields.io/badge/100%25-FOSS-orange.svg)](#license)

*Record your terminal sessions. Search through them. Replay, summarize, and export — all from the command line.*

</div>

---

## The Problem

You're debugging a server issue at 2 AM. You run dozens of commands, scroll through walls of output, and finally fix it. The next day, your teammate asks: *"What did you do to fix it?"*

You don't remember. The terminal history is gone. The output is lost.

## The Solution

**Iris** records your entire terminal session — every command and its output — into a structured `.trace` file. These trace files are searchable, replayable, and exportable. Think of it as a flight recorder for your terminal.

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
| 🎬 **Record** | Capture full terminal sessions with timestamps and command output |
| 🔎 **Search** | Find specific commands or output across recorded sessions |
| ▶️ **Replay** | Play back sessions in real-time to review what happened |
| 📊 **Summary** | Get session stats — duration, command count, error detection |
| 📄 **Export** | Generate clean, shareable text reports from recordings |
| 🛡️ **Auto-Redact** | Automatically strips passwords, API keys, and tokens from traces |
| 🌐 **Cross-Platform** | Works on Linux, macOS, and Windows with native integrations |
| 📦 **Zero Dependencies** | No external packages needed on Linux/macOS (only `pywinpty` on Windows) |

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

### Trace File Format

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
git clone https://github.com/PiyushSharma0/Iris.git
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

### Optional: Add to PATH

**Linux / macOS:**
```bash
chmod +x iris.py
sudo ln -s $(pwd)/iris.py /usr/local/bin/iris
```

**Windows:**
Add the Iris directory to your system PATH, then use the included `iris.bat` wrapper.

---

## 📖 Usage

### Record a Session

```bash
python iris.py record
```

This spawns a new shell and records everything. Type `exit` or press `Ctrl+D` to stop. The session is saved as a `.trace` file in the current directory.

### Search a Session

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

### Replay a Session

```bash
python iris.py replay examples/demo_session.trace
```

Plays back each command and its output with a short delay, simulating the original session.

### Get Session Summary

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

### Export as Text Report

```bash
python iris.py export examples/demo_session.trace --output report.txt
```

Generates a clean, shareable plain-text report without ANSI codes or sensitive data.

---

## 🖥️ Platform Support

| Platform | Backend | Status |
|---|---|---|
| Linux | Native PTY (`pty` + `select`) | ✅ Fully supported |
| macOS | Native PTY (`pty` + `select`) | ✅ Fully supported |
| Windows | `pywinpty` | ✅ Fully supported |

---

## 🛡️ Security & Privacy

Iris automatically redacts sensitive information from recorded sessions:

- **Passwords** — `password=s3cret` → `[REDACTED]`
- **API keys** — `api_key=abc123...` → `[REDACTED]`
- **Bearer tokens** — `Authorization: Bearer eyJ...` → `[REDACTED]`
- **Long random strings** — potential secrets are caught by pattern matching

All recordings stay **100% local** — nothing is ever sent to any server.

---

## 🤝 Contributing

Contributions are welcome! Please read the [Contributing Guidelines](CONTRIBUTING.md) before submitting a PR.

See also our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ and Python. No closed-source dependencies. No telemetry. Just a simple tool that does its job.**

</div>
