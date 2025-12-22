#!/usr/bin/env python3
"""
Simple HTTP server để serve dashboard và shared_state.json
Giải quyết vấn đề CORS khi mở file trực tiếp
"""
import http.server
import socketserver
import os
import json
from pathlib import Path

PORT = 8000
BASE_DIR = Path(__file__).parent.parent

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        # Serve shared_state.json with proper content type
        if self.path == '/.mcp/shared_state.json' or self.path == '/shared_state.json':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            json_path = BASE_DIR / '.mcp' / 'shared_state.json'
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode())
            else:
                self.wfile.write(json.dumps({"error": "File not found"}).encode())
        else:
            super().do_GET()

if __name__ == "__main__":
    os.chdir(BASE_DIR)
    
    with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
        print(f"🚀 Dashboard server running on http://localhost:{PORT}")
        print(f"📊 Dashboard: http://localhost:{PORT}/.mcp/dashboard.html")
        print(f"📁 Serving from: {BASE_DIR}")
        print("\nPress Ctrl+C to stop the server...\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✅ Server stopped")
            httpd.shutdown()

