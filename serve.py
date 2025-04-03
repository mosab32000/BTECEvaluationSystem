"""
خادم ويب بسيط لعرض ملف index.html مع تحديث متواصل للصفحة
"""

import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = "."

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def main():
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"خادم الويب يعمل على المنفذ {PORT}...")
        print(f"يمكنك الوصول إلى الموقع من خلال: http://0.0.0.0:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nتم إيقاف الخادم.")

if __name__ == "__main__":
    main()