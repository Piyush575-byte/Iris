#!/usr/bin/env python3
import sys
import os

# Make imports work from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import argparse
import platform
from storage import save_session, load_session
from search import search_session
from replay import replay_session
from summary import summarize_session
from export import export_session

# Signal directory for cross-terminal communication
SIGNAL_DIR = os.path.join(os.path.expanduser("~"), ".iris")
STOP_SIGNAL = os.path.join(SIGNAL_DIR, "stop.signal")
RECORDING_LOCK = os.path.join(SIGNAL_DIR, "recording.lock")

def record_session():
    os_name = platform.system()
    if os_name == "Windows":
        try:
            from recorder_windows import record
        except ImportError:
            print("Error: 'pywinpty' is required on Windows.")
            print("Please install it using: pip install pywinpty")
            sys.exit(1)
        record()
    elif os_name in ("Linux", "Darwin"):
        from recorder_unix import record
        record()
    else:
        print(f"Unsupported OS: {os_name}")
        sys.exit(1)

def stop_recording():
    """Send stop signal to a running iris recording from any terminal."""
    os.makedirs(SIGNAL_DIR, exist_ok=True)
    if not os.path.exists(RECORDING_LOCK):
        print("No active iris recording found.")
        return
    with open(STOP_SIGNAL, 'w') as f:
        f.write("stop")
    print("Stop signal sent. Recording will save and exit shortly.")

def main():
    parser = argparse.ArgumentParser(description="iris: a terminal session recorder that creates searchable debugging artifacts.")
    subparsers = parser.add_subparsers(dest="action", required=True)
    
    subparsers.add_parser("record", help="Start recording a session")
    subparsers.add_parser("stop", help="Stop a recording from any terminal")
    
    search_p = subparsers.add_parser("search", help="Search through a recorded session")
    search_p.add_argument("query", help="Text to search for")
    search_p.add_argument("file", help="Trace file to search in (.trace)")
    
    replay_p = subparsers.add_parser("replay", help="Replay a session in terminal")
    replay_p.add_argument("file", help="Trace file to replay")
    
    summary_p = subparsers.add_parser("summary", help="Show summary of a session")
    summary_p.add_argument("file", help="Trace file to analyze")
    
    export_p = subparsers.add_parser("export", help="Export as clean shareable text")
    export_p.add_argument("file", help="Trace file to export")
    export_p.add_argument("--output", required=True, help="Output text file path")
    
    args = parser.parse_args()
    
    if args.action == "record":
        record_session()
    elif args.action == "stop":
        stop_recording()
    elif args.action == "search":
        search_session(args.file, args.query)
    elif args.action == "replay":
        replay_session(args.file)
    elif args.action == "summary":
        summarize_session(args.file)
    elif args.action == "export":
        export_session(args.file, args.output)

if __name__ == "__main__":
    main()
