import re

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

SENSITIVE_PATTERNS = [
    r'(?i)(password|passwd|pwd)\s*[=:]\s*\S+',
    r'(?i)(api_key|apikey|api-key)\s*[=:]\s*\S+',
    r'(?i)(secret|token)\s*[=:]\s*\S+',
    r'Bearer\s+[A-Za-z0-9\-._~+/]+=*',
    r'[A-Za-z0-9]{32,}',  # long random strings (API keys)
]

def strip_ansi(text):
    return ANSI_ESCAPE.sub('', text)

def redact(text):
    for pattern in SENSITIVE_PATTERNS:
        text = re.sub(pattern, '[REDACTED]', text)
    return text

def clean_command(raw_input):
    s = strip_ansi(raw_input)
    res = []
    for c in s:
        if c in ('\b', '\x7f'):
            if res:
                res.pop()
        elif ord(c) < 32 and c != '\t':
            pass
        else:
            res.append(c)
    return "".join(res).strip()

def guess_exit_code(output):
    lower_out = output.lower()
    if "error" in lower_out or "traceback" in lower_out or "exception" in lower_out or "not found" in lower_out or "failed" in lower_out:
        return 1
    return 0

def build_event(events, raw_input, raw_output, duration_ms, timestamp_iso):
    command = clean_command(raw_input)
    if not command:
        return None
        
    out_clean = strip_ansi(raw_output)
    out_clean = out_clean.replace('\r\n', '\n').replace('\r', '\n')
    lines = out_clean.split('\n')
    if lines and lines[0] == '':
        lines = lines[1:]
    if lines:
        lines = lines[:-1]
    output = '\n'.join(lines).strip()
    
    command = redact(command)
    output = redact(output)
    
    exit_code = guess_exit_code(output)
    
    return {
        "id": len(events) + 1,
        "type": "command",
        "timestamp": timestamp_iso,
        "command": command,
        "output": output,
        "exit_code": exit_code,
        "duration_ms": duration_ms
    }
