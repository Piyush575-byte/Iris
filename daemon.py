import os
import sys
import time
import json
import socket
import threading
import datetime
from storage import save_session

SIGNAL_DIR = os.path.join(os.path.expanduser("~"), ".iris")
STOP_SIGNAL = os.path.join(SIGNAL_DIR, "stop.signal")
RECORDING_LOCK = os.path.join(SIGNAL_DIR, "recording.lock")
DAEMON_PORT_FILE = os.path.join(SIGNAL_DIR, "daemon.port")

class IrisDaemon:
    def __init__(self):
        self.events = []
        self.server_socket = None
        self.running = False
        self.start_time = datetime.datetime.now()
        self.session_id = self.start_time.strftime("%Y-%m-%d_%H-%M-%S")
        self.trace_file = os.path.join(os.getcwd(), f"{self.session_id}.trace")
        self.lock = threading.Lock()
        
    def start(self):
        os.makedirs(SIGNAL_DIR, exist_ok=True)
        for f in [STOP_SIGNAL, RECORDING_LOCK, DAEMON_PORT_FILE]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except OSError:
                    pass

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('127.0.0.1', 0))
        self.server_socket.listen(5)
        
        port = self.server_socket.getsockname()[1]
        
        with open(DAEMON_PORT_FILE, 'w') as f:
            f.write(str(port))
            
        with open(RECORDING_LOCK, 'w') as f:
            f.write(str(os.getpid()))

        self.running = True
        print(f"Iris multi-terminal recording daemon started.")
        print(f"Waiting for terminals to attach... (Port: {port})")
        print(f"Run 'iris shell' in any new terminal to record it.")
        print(f"Run 'iris stop' to end the recording session.\n")

        accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
        accept_thread.start()

        try:
            while self.running:
                if os.path.exists(STOP_SIGNAL):
                    print("Stop signal received. Shutting down daemon...")
                    self.running = False
                    break
                time.sleep(0.5)
        except KeyboardInterrupt:
            self.running = False

        self._shutdown()

    def _accept_loop(self):
        self.server_socket.settimeout(1.0)
        while self.running:
            try:
                client_sock, addr = self.server_socket.accept()
                client_thread = threading.Thread(target=self._handle_client, args=(client_sock,), daemon=True)
                client_thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Accept error: {e}")

    def _handle_client(self, client_sock):
        client_sock.settimeout(1.0)
        buffer = b""
        
        try:
            while self.running:
                try:
                    data = client_sock.recv(4096)
                    if not data:
                        break
                    buffer += data
                except socket.timeout:
                    break
            
            while b'\n' in buffer:
                line, buffer = buffer.split(b'\n', 1)
                if not line.strip():
                    continue
                try:
                    event = json.loads(line.decode('utf-8'))
                    with self.lock:
                        event['id'] = len(self.events) + 1
                        self.events.append(event)
                except json.JSONDecodeError:
                    pass
                    
            if buffer.strip():
                try:
                    event = json.loads(buffer.decode('utf-8'))
                    with self.lock:
                        event['id'] = len(self.events) + 1
                        self.events.append(event)
                except json.JSONDecodeError:
                    pass

        except Exception as e:
            pass
        finally:
            try:
                client_sock.close()
            except Exception:
                pass

    def _shutdown(self):
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass

        for f in [STOP_SIGNAL, RECORDING_LOCK, DAEMON_PORT_FILE]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except OSError:
                    pass

        end_time = datetime.datetime.now()
        save_session(self.trace_file, self.session_id, self.start_time, end_time, self.events)
        print(f"\n[iris] Multi-terminal session saved to {self.trace_file}")
        print(f"[iris] Captured {len(self.events)} total commands across all terminals.")

def run_daemon():
    daemon = IrisDaemon()
    daemon.start()

def send_event_to_daemon(event):
    if not os.path.exists(DAEMON_PORT_FILE):
        return False
        
    try:
        with open(DAEMON_PORT_FILE, 'r') as f:
            port = int(f.read().strip())
            
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2.0)
            s.connect(('127.0.0.1', port))
            message = json.dumps(event) + '\n'
            s.sendall(message.encode('utf-8'))
            return True
    except Exception:
        return False
