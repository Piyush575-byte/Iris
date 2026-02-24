from storage import load_session

def export_session(trace_file, output_file):
    session = load_session(trace_file)
        
    with open(output_file, 'w') as f:
        f.write(f"Iris Report: {session.get('session_id')}\n")
        f.write("=" * 40 + "\n\n")
        for event in session.get('events', []):
            f.write(f"[{event['timestamp']}] $ {event['command']}\n")
            if event['output']:
                f.write(f"{event['output']}\n")
            f.write("\n")
            
    print(f"Exported clean text report to {output_file}")
