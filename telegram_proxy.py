from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import hmac

PATH = "/api/webhooks/telegram/88396290-1f80-449e-9762-dcbebc28cf52"

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if not hmac.compare_digest(self.path, PATH):
            self.send_error(404)
            return

        size = int(self.headers.get("Content-Length", "0"))
        if size <= 0 or size > 1048576:
            self.send_error(413)
            return

        body = self.rfile.read(size)

        req = Request(
            "http://127.0.0.1:8000" + PATH,
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-Telegram-Bot-Api-Secret-Token":
                    self.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
            },
            method="POST"
        )

        try:
            with urlopen(req, timeout=10) as response:
                self.send_response(response.status)
                self.end_headers()
                self.wfile.write(response.read())
        except HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
        except Exception:
            self.send_error(502)

    def do_GET(self):
        self.send_error(404)

    def do_PUT(self):
        self.send_error(405)

    def do_DELETE(self):
        self.send_error(405)

print("Telegram webhook proxy: http://127.0.0.1:8765", flush=True)
ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
