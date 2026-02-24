import datetime
from storage import load_session

def summarize_session(trace_file):
    session = load_session(trace_file)
        
    events = session.get('events', [])
    err_count = sum(1 for e in events if e.get('exit_code', 0) != 0)
    
    try:
        start = datetime.datetime.fromisoformat(session['start_time'])
        end = datetime.datetime.fromisoformat(session['end_time'])
        dur_sec = int((end - start).total_seconds())
    except Exception:
        dur_sec = sum(e.get('duration_ms', 0) for e in events) // 1000
        
    print(f"Session: {session.get('session_id')}")
    print(f"Host: {session.get('hostname')}")
    print(f"Duration: {dur_sec} seconds")
    print(f"Total commands: {len(events)}")
    print(f"Errors detected: {err_count}")
