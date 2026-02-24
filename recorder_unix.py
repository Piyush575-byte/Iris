import sys
import os
import time
import datetime
import pty
import tty
import termios
import select
from storage import save_session
from redact import build_event

def record():
    now = datetime.datetime.now()
    session_id = now.strftime("%Y-%m-%d_%H-%M-%S")
    trace_file = f"{session_id}.trace"
    
    events = []
    
    print(f"Starting iris recording... Saving to {trace_file}")
    print("Type 'exit' or press Ctrl+D to stop.")
    time.sleep(1)
    
    pid, fd = pty.fork()
    if pid == 0:
        shell = os.environ.get('SHELL', 'bash')
        os.execvp(shell, [shell])
    else:
        old_tty = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())
        
        state = "START"
        current_input = ""
        current_output = ""
        cmd_start_time = time.time()
        
        try:
            while True:
                r, w, e = select.select([sys.stdin, fd], [], [])
                if sys.stdin in r:
                    char = os.read(sys.stdin.fileno(), 1)
                    if not char:
                        break
                    
                    char_str = char.decode('utf-8', errors='replace')
                    
                    if state != "INPUT":
                        if state == "RUNNING" and current_input.strip():
                            duration = int((time.time() - cmd_start_time) * 1000)
                            evt = build_event(events, current_input, current_output, duration, datetime.datetime.now().isoformat())
                            if evt:
                                events.append(evt)
                        
                        state = "INPUT"
                        current_input = ""
                        current_output = ""
                    
                    current_input += char_str
                    os.write(fd, char)
                    
                    if char == b'\r' or char == b'\n':
                        state = "RUNNING"
                        cmd_start_time = time.time()
                        
                if fd in r:
                    try:
                        data = os.read(fd, 1024)
                    except OSError:
                        break
                    if not data:
                        break
                    
                    os.write(sys.stdout.fileno(), data)
                    
                    text = data.decode('utf-8', errors='replace')
                    if state == "RUNNING":
                        current_output += text
        except Exception as e:
            pass
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)
            
            if state == "RUNNING" and current_input.strip():
                duration = int((time.time() - cmd_start_time) * 1000)
                evt = build_event(events, current_input, current_output, duration, datetime.datetime.now().isoformat())
                if evt:
                    events.append(evt)
                    
            save_session(trace_file, session_id, now, datetime.datetime.now(), events)
            print(f"\r\n[iris] Session saved to {trace_file}")
