"""Small Gemini proxy for Frontier Run.

Set GEMINI_API_KEY in the server environment, then run: python ai_server.py
"""
import json
import os
import time
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from google import genai

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("Set GEMINI_API_KEY in the environment before starting the server.")

client = genai.Client(api_key=API_KEY)
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
MAX_MESSAGE_CHARS = 500
RATE_LIMIT_REQUESTS = int(os.environ.get("RATE_LIMIT_REQUESTS", "20"))
RATE_LIMIT_WINDOW_SECONDS = int(os.environ.get("RATE_LIMIT_WINDOW_SECONDS", "60"))
_client_requests = defaultdict(deque)

SYSTEM_INSTRUCTION = (
    "You are Frontier Guide, a friendly AI companion inside an original, fictional "
    "open-world adventure game called Frontier Run. Give concise, helpful game tips, "
    "mission hints, exploration suggestions, and general answers suitable for teens. "
    "Do not claim to control the game or know anything not included in the supplied "
    "game context. Do not ask for personal information. Keep replies under 120 words."
)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"ok": True, "service": "frontier-run-ai", "model": MODEL})
        elif self.path == "/":
            self._send(200, {"service": "Frontier Run Gemini AI", "health": "/health", "chat": "POST /chat"})
        else:
            self._send(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/chat":
            self._send(404, {"error": "Not found"})
            return
        try:
            now = time.monotonic()
            client_ip = self.client_address[0]
            recent = _client_requests[client_ip]
            while recent and now - recent[0] > RATE_LIMIT_WINDOW_SECONDS:
                recent.popleft()
            if len(recent) >= RATE_LIMIT_REQUESTS:
                self._send(429, {"error": "Too many requests. Please wait and try again."})
                return
            recent.append(now)

            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 12000:
                self._send(413, {"error": "Invalid request size"})
                return
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            message = str(data.get("message", "")).strip()[:MAX_MESSAGE_CHARS]
            if not message:
                self._send(400, {"error": "Message is required"})
                return

            context = data.get("game_context", {})
            if not isinstance(context, dict):
                context = {}
            safe_context = {
                "current_mission": str(context.get("mission", "Unknown"))[:120],
                "cash": max(0, min(int(context.get("cash", 0)), 100000000)),
                "health": max(0, min(int(context.get("health", 100)), 100)),
                "in_vehicle": bool(context.get("in_vehicle", False)),
            }
            history = data.get("history", [])
            history_lines = []
            if isinstance(history, list):
                for item in history[-6:]:
                    if not isinstance(item, dict):
                        continue
                    role = "Player" if item.get("role") == "user" else "Guide"
                    text = str(item.get("text", "")).strip()[:500]
                    if text:
                        history_lines.append(f"{role}: {text}")

            prompt = (
                f"{SYSTEM_INSTRUCTION}\n\n"
                f"Current game state: {json.dumps(safe_context)}\n"
                f"Recent conversation:\n" + ("\n".join(history_lines) or "(none)") +
                f"\nPlayer's new message: {message}"
            )
            response = client.models.generate_content(model=MODEL, contents=prompt)
            reply = (response.text or "I couldn't think of a reply. Try asking again.").strip()
            self._send(200, {"reply": reply[:1800]})
        except json.JSONDecodeError:
            self._send(400, {"error": "Invalid JSON"})
        except Exception as exc:
            print("Gemini request failed:", type(exc).__name__)
            self._send(502, {"error": "Gemini request failed"})

    def log_message(self, format_string, *args):
        print("%s - %s" % (self.address_string(), format_string % args))


if __name__ == "__main__":
    host = os.environ.get("AI_HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", os.environ.get("AI_PORT", "8000")))
    print(f"Frontier Run Gemini proxy listening on http://{host}:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
