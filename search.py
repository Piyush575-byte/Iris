from storage import load_session

def search_session(trace_file, query):
    session = load_session(trace_file)
        
    results = []
    print(f"Searching for '{query}' in {trace_file}...\n")
    for event in session.get('events', []):
        cmd = event.get('command', '')
        out = event.get('output', '')
        if query.lower() in cmd.lower() or query.lower() in out.lower():
            results.append(event)
            print(f"[{event['timestamp']}] Event #{event['id']} (Exit: {event['exit_code']})")
            print(f"$ {cmd}")
            if out:
                print(f"{out}")
            print("-" * 40)
            
    print(f"Found {len(results)} matching events.")
