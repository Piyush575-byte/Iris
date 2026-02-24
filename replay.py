import time
from storage import load_session

def replay_session(trace_file):
    session = load_session(trace_file)
        
    for event in session.get('events', []):
        print(f"$ {event['command']}")
        if event['output']:
            print(event['output'])
        time.sleep(0.5)
