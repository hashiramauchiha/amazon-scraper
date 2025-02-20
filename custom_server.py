from http.server import SimpleHTTPRequestHandler, HTTPServer

class CustomHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Disable caching
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

if __name__ == "__main__":
    server_address = ("", 8000)  # Host on port 8000
    httpd = HTTPServer(server_address, CustomHandler)
    print("Serving on http://localhost:8000")
    httpd.serve_forever()
