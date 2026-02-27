import subprocess
import time
import datetime
import os
import sys
from redact import build_event
from storage import save_session
from daemon import send_event_to_daemon, DAEMON_PORT_FILE

def run_single_command(cmd_args):
    now = datetime.datetime.now()
    session_id = now.strftime("%Y-%m-%d_%H-%M-%S")
    trace_file = f"{session_id}.trace"
    events = []
    
    is_daemon_mode = os.path.exists(DAEMON_PORT_FILE)
    
    start_time = time.time()
    cmd_text = " ".join(cmd_args)
    
    output_lines = []
    
    try:
        process = subprocess.Popen(
            cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            shell=True if os.name == 'nt' else False
        )
        
        for line in iter(process.stdout.readline, ''):
            sys.stdout.write(line)
            sys.stdout.flush()
            output_lines.append(line)
            
        process.stdout.close()
        process.wait()
        exit_code = process.returncode
        
    except KeyboardInterrupt:
        process.terminate()
        output_lines.append("\n^C\n")
        exit_code = 130
    except Exception as e:
        print(f"Error running command: {e}")
        exit_code = 1
        output_lines.append(str(e))
        
    duration = int((time.time() - start_time) * 1000)
    raw_output = "".join(output_lines)
    
    evt = build_event(events, cmd_text, raw_output, duration, datetime.datetime.now().isoformat())
    if evt:
        evt['exit_code'] = exit_code
        if is_daemon_mode:
            send_event_to_daemon(evt)
        else:
            events.append(evt)
            save_session(trace_file, session_id, now, datetime.datetime.now(), events)
            print(f"\n[iris] Command session saved to {trace_file}")
