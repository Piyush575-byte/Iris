import winpty
import time
import datetime
import threading
import msvcrt
import sys
import os
import re
from storage import save_session
from redact import build_event
from daemon import send_event_to_daemon, DAEMON_PORT_FILE

# Signal directory for cross-terminal communication
SIGNAL_DIR = os.path.join(os.path.expanduser("~"), ".iris")
STOP_SIGNAL = os.path.join(SIGNAL_DIR, "stop.signal")
RECORDING_LOCK = os.path.join(SIGNAL_DIR, "recording.lock")

# Strip ALL ANSI/VT escape sequences before display
ANSI_ESCAPE = re.compile(r'''
    \x1B          # ESC character
    (?:           # followed by:
        \[        # CSI sequences: ESC [
        [0-?]*    # parameter bytes
        [ -/]*    # intermediate bytes
        [@-~]     # final byte
    |
        \]        # OSC sequences: ESC ]
        .*?       # any content
        (?:\x07|\x1B\\)  # terminated by BEL or ST
    |
        [()][AB012]  # Character set selection
    |
        \[[?]?[0-9;]*[a-zA-Z]  # Other CSI
    |
        [^[\]()]  # Two-character sequences (e.g., ESC =, ESC >)
    )
''', re.VERBOSE)

def clean_display(text):
    """Strip ANSI codes for clean terminal display."""
    cleaned = ANSI_ESCAPE.sub('', text)
    # Remove other common control sequences
    cleaned = re.sub(r'\x1B[=>]', '', cleaned)
    cleaned = re.sub(r'\x1B\[[\?]?[0-9;]*[a-zA-Z]', '', cleaned)
    cleaned = re.sub(r'\x1B\[[0-9;]*[hHlL]', '', cleaned)
    return cleaned

def _create_lock():
    """Create recording lock file so other terminals know we're recording."""
    os.makedirs(SIGNAL_DIR, exist_ok=True)
    # Clean up any stale stop signal
    if os.path.exists(STOP_SIGNAL):
        os.remove(STOP_SIGNAL)
    with open(RECORDING_LOCK, 'w') as f:
        f.write(str(os.getpid()))

def _check_stop_signal():
    """Check if another terminal sent a stop signal."""
    return os.path.exists(STOP_SIGNAL)

def _cleanup_signals():
    """Remove signal files on exit."""
    for f in [STOP_SIGNAL, RECORDING_LOCK]:
        try:
            if os.path.exists(f):
                os.remove(f)
        except Exception:
            pass

def record():
    now = datetime.datetime.now()
    session_id = now.strftime("%Y-%m-%d_%H-%M-%S")
    trace_file = f"{session_id}.trace"
    events = []

    is_daemon_mode = os.path.exists(DAEMON_PORT_FILE)

    if is_daemon_mode:
        print(f"Attaching terminal to central Iris recording daemon...")
    else:
        print(f"Starting standalone iris recording... Saving to {trace_file}")
    print("Type 'stop' or run 'iris stop' from any terminal to stop recording.\n")

    # Create lock file so 'iris stop' knows we're recording ONLY if standalone
    if not is_daemon_mode:
        _create_lock()

    process = winpty.PtyProcess.spawn("cmd.exe")

    current_input = ""
    current_output = ""
    cmd_start_time = time.time()
    lock = threading.Lock()
    user_stopped = False  # Only True when user explicitly stops

    def read_output():
        nonlocal current_output
        while not user_stopped:
            try:
                if not process.isalive():
                    time.sleep(0.5)
                    continue
                data = process.read()
                if data:
                    display_text = clean_display(data)
                    if display_text.strip():
                        sys.stdout.write(display_text)
                        sys.stdout.flush()
                    with lock:
                        current_output += display_text
            except EOFError:
                time.sleep(0.5)
                continue
            except Exception:
                time.sleep(0.2)
                continue

    reader_thread = threading.Thread(target=read_output, daemon=True)
    reader_thread.start()

    # Wait for initial cmd.exe banner to print
    time.sleep(1)

    try:
        while not user_stopped:
            try:
                # Check for stop signal ONLY if standalone
                if not is_daemon_mode and _check_stop_signal():
                    print("\n[iris] Stop signal received from another terminal.")
                    user_stopped = True
                    break

                if msvcrt.kbhit():
                    char = msvcrt.getwch()

                    # Ctrl+C
                    if char == '\x03':
                        user_stopped = True
                        break

                    with lock:
                        current_input += char

                    if char in ('\r', '\n'):
                        try:
                            process.write(char)
                        except Exception:
                            pass
                        time.sleep(0.5)
                        with lock:
                            duration = int((time.time() - cmd_start_time) * 1000)
                            cmd_text = current_input.strip()
                            if cmd_text:
                                evt = build_event(events, current_input, current_output, duration, datetime.datetime.now().isoformat())
                                if evt:
                                    if is_daemon_mode:
                                        if not send_event_to_daemon(evt):
                                            print("\n[iris] Daemon connection lost. Stopping recording.")
                                            user_stopped = True
                                            break
                                    else:
                                        events.append(evt)
                                if cmd_text.lower() == 'stop':
                                    user_stopped = True
                                    break
                            current_input = ""
                            current_output = ""
                            cmd_start_time = time.time()
                    else:
                        try:
                            process.write(char)
                        except Exception:
                            pass
                else:
                    time.sleep(0.05)
            except Exception:
                time.sleep(0.1)
                continue
    except KeyboardInterrupt:
        user_stopped = True

    user_stopped = True
    reader_thread.join(timeout=2)
    
    if not is_daemon_mode:
        _cleanup_signals()
        save_session(trace_file, session_id, now, datetime.datetime.now(), events)
        print(f"\n[iris] Session saved to {trace_file}")
    else:
        print(f"\n[iris] Terminal detached from recording daemon.")
