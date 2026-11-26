#!/usr/bin/env python3
import html
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

HOST = "127.0.0.1"  # Bind strictly to localhost so only your laptop can access it
PORT = 8080

def get_system_data():
    # 1. Read uptime and load average directly from /proc
    load = Path("/proc/loadavg").read_text(encoding="utf-8").split()[:3]
    uptime_raw = float(Path("/proc/uptime").read_text(encoding="utf-8").split()[0])
    uptime_hrs = round(uptime_raw / 3600, 1)

    # 2. Fetch the last 25 kernel warnings/errors from journalctl
    cmd = ["journalctl", "-k", "-p", "warning", "-n", "25", "--no-pager"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    logs = res.stdout.strip() or "No kernel warnings or errors found!"

    return " ".join(load), uptime_hrs, html.escape(logs)

class KernelDashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Only serve the root path
        if self.path != "/":
            self.send_error(404, "Page Not Found")
            return

        load, uptime, logs = get_system_data()

        # Build a dark-mode HTML page that auto-refreshes every 10 seconds
        page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="10">
    <title>Debian 13 Kernel Dashboard</title>
    <style>
        body {{ font-family: monospace; background: #121212; color: #e0e0e0; padding: 2rem; }}
        .card {{ background: #1e1e1e; border: 1px solid #333; padding: 1rem; border-radius: 6px; margin-bottom: 1rem; }}
        h1 {{ color: #d70a53; margin-top: 0; }}
        pre {{ background: #0d0d0d; padding: 1rem; overflow-x: auto; border-left: 4px solid #d70a53; }}
        .meta {{ color: #888; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <h1>Debian 13 Live Kernel Monitor</h1>
    <div class="card">
        <strong>System Uptime:</strong> {uptime} hours &nbsp;|&nbsp;
        <strong>CPU Load (1m / 5m / 15m):</strong> {load}
        <div class="meta">Auto-refreshing every 10 seconds via Python HTTP Socket ({HOST}:{PORT})</div>
    </div>
    <div class="card">
        <h3>Recent Kernel Warnings &amp; Errors</h3>
        <pre>{logs}</pre>
    </div>
</body>
</html>"""

        # Send HTTP 200 OK headers followed by the HTML payload
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(page.encode("utf-8"))

if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), KernelDashboardHandler)
    print(f"Serving Debian 13 Kernel Dashboard at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop the server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down socket cleanly.")
        server.server_close()
