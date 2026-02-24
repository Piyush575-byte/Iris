import json
import os
import sys
import socket

def load_session(trace_file):
    if not os.path.exists(trace_file):
        print(f"Error: File {trace_file} not found.")
        sys.exit(1)
        
    with open(trace_file) as f:
        return json.load(f)

def save_session(trace_file, session_id, start_dt, end_dt, events):
    hostname = socket.gethostname()
    session = {
        "session_id": session_id,
        "start_time": start_dt.isoformat(),
        "end_time": end_dt.isoformat(),
        "hostname": hostname,
        "events": events
    }
    with open(trace_file, 'w') as f:
        json.dump(session, f, indent=2)
