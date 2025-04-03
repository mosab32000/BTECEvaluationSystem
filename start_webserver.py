"""
خادم ويب بسيط لعرض ملف index.html
"""

import http.server
import socketserver

PORT = 3000
DIRECTORY = "."

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def main():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"خادم الويب يعمل على المنفذ {PORT}...")
        print(f"يمكنك الوصول إلى الموقع من خلال العنوان: http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    main()