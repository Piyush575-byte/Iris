import winpty
import time
import datetime
import threading
import msvcrt
import sys
import re
from storage import save_session
from redact import build_event

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

def record():
    now = datetime.datetime.now()
    session_id = now.strftime("%Y-%m-%d_%H-%M-%S")
    trace_file = f"{session_id}.trace"
    events = []

    print(f"Starting iris recording... Saving to {trace_file}")
    print("Type 'exit' to stop.\n")

    process = winpty.PtyProcess.spawn("cmd.exe")

    current_input = ""
    current_output = ""
    cmd_start_time = time.time()
    lock = threading.Lock()
    running = True

    def read_output():
        nonlocal current_output, running
        while running:
            try:
                if not process.isalive():
                    running = False
                    break
                data = process.read()
                if data:
                    # Strip ANSI codes before printing to screen
                    display_text = clean_display(data)
                    if display_text.strip():
                        sys.stdout.write(display_text)
                        sys.stdout.flush()
                    with lock:
                        current_output += display_text
            except EOFError:
                running = False
                break
            except Exception:
                running = False
                break

    # Start background thread for reading output
    reader_thread = threading.Thread(target=read_output, daemon=True)
    reader_thread.start()

    # Wait for initial cmd.exe banner to print
    time.sleep(1)

    try:
        while running:
            if msvcrt.kbhit():
                char = msvcrt.getwch()

                # Ctrl+C
                if char == '\x03':
                    break

                with lock:
                    current_input += char

                # Enter key pressed
                if char == '\r':
                    process.write(char)
                    # Give output time to arrive
                    time.sleep(0.5)
                    with lock:
                        duration = int((time.time() - cmd_start_time) * 1000)
                        cmd_text = current_input.strip()
                        if cmd_text:
                            evt = build_event(events, current_input, current_output, duration, datetime.datetime.now().isoformat())
                            if evt:
                                events.append(evt)
                            # Check if user typed 'exit'
                            if cmd_text.lower() == 'exit':
                                running = False
                                break
                        current_input = ""
                        current_output = ""
                        cmd_start_time = time.time()
                else:
                    process.write(char)
            else:
                time.sleep(0.05)
    except KeyboardInterrupt:
        pass

    running = False
    reader_thread.join(timeout=2)

    save_session(trace_file, session_id, now, datetime.datetime.now(), events)
    print(f"\n[iris] Session saved to {trace_file}")
