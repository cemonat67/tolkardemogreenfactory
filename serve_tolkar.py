#!/usr/bin/env python3
import json, time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

TOKEN="demo-token-001"

def j(obj): return json.dumps(obj, ensure_ascii=False).encode("utf-8")

LINES = [
  {"id":"L1","name":"Metal & Şase","wip":18,"oee":85,"status":"running"},
  {"id":"L2","name":"Boya","wip":6,"oee":72,"status":"stopped"},
  {"id":"L3","name":"Montaj","wip":15,"oee":89,"status":"running"},
  {"id":"L4","name":"Final Test","wip":4,"oee":91,"status":"running"},
  {"id":"L5","name":"Paketleme & Sevkiyat","wip":7,"oee":87,"status":"running"},
]
STATIONS = [
  {"id":"S1","line_id":"L1","name":"Metal Kesim","oee":88,"state":"running"},
  {"id":"S2","line_id":"L2","name":"Boya Kabini","oee":82,"state":"running"},
  {"id":"S3","line_id":"L3","name":"Montaj","oee":90,"state":"running"},
]
ORDERS = [{"id":"O-1001","sku":"Smartex Miracle","qty":210,"done":96,"status":"active"}]
EVENTS = [{"ts":int(time.time())-120,"type":"info","msg":"Demo server online"}]

def ok_headers(h):
  h.send_header("Cache-Control","no-store")
  h.send_header("Access-Control-Allow-Origin","*")
  h.send_header("Access-Control-Allow-Headers","Content-Type, Authorization")
  h.send_header("Access-Control-Allow-Methods","GET, POST, OPTIONS")

class H(SimpleHTTPRequestHandler):
  def log_message(self, fmt, *args):
    print('[HTTP]', fmt % args)

  def _send(self, code=200, ctype="application/json; charset=utf-8", body=b"{}"):
    self.send_response(code)
    self.send_header("Content-Type", ctype)
    ok_headers(self)
    self.end_headers()
    if body:
      self.wfile.write(body)

  def do_OPTIONS(self):
    return self._send(204, body=b"")

  def do_GET(self):
    p = urlparse(self.path).path
    qs = parse_qs(urlparse(self.path).query)

    if p in ("/api/v1/status", "/api/status"):
      return self._send(200, body=j({"health":"ok","reason":"demo-safe","ts":int(time.time())}))

    if p == "/api/v1/lines":
      return self._send(200, body=j({"lines": LINES}))

    if p == "/api/v1/stations":
      return self._send(200, body=j({"stations": STATIONS}))

    if p == "/api/v1/orders":
      return self._send(200, body=j({"orders": ORDERS}))

    if p.startswith("/api/v1/events"):
      lim = int(qs.get("limit",[200])[0])
      return self._send(200, body=j({"events": EVENTS[-lim:]}))

    if p == "/api/state":
      # dashboard.html içinde okunan shape: {stations:[] ...}
      return self._send(200, body=j({
        "stations": STATIONS,
        "lines": LINES,
        "orders": ORDERS,
        "last_sync": int(time.time())
      }))

    if p.startswith("/api/telemetry"):
      # boş da olsa array bekleniyor
      return self._send(200, body=j({"rows": []}))

    if p == "/api/me":
      return self._send(200, body=j({"ok": True, "user":{"id":"admin","role":"Admin"}}))

    # static fallback
    return super().do_GET()

  def _read_body(self):
    try:
      n = int(self.headers.get("Content-Length","0") or "0")
      raw = self.rfile.read(n) if n>0 else b""
      ct = (self.headers.get("Content-Type","") or "").lower()

      # JSON
      if "application/json" in ct:
        import json
        try:
          return json.loads((raw.decode("utf-8", errors="ignore") or "{}"))
        except Exception:
          return {}

      # x-www-form-urlencoded
      if "application/x-www-form-urlencoded" in ct:
        from urllib.parse import parse_qs
        qs = parse_qs(raw.decode("utf-8", errors="ignore"))
        return {k:(v[0] if isinstance(v,list) and v else "") for k,v in qs.items()}

      # multipart/form-data (basit fallback: içinde username/password geçen düz metin)
      txt = raw.decode("utf-8", errors="ignore")
      if "username" in txt or "password" in txt:
        # çok basit çıkarım: yine de AUTH tarafı genelde urlencoded kullanır
        pass

      # son çare: önce json dene, olmazsa urlencoded dene
      import json
      try:
        return json.loads(txt or "{}")
      except Exception:
        from urllib.parse import parse_qs
        qs = parse_qs(txt)
        return {k:(v[0] if isinstance(v,list) and v else "") for k,v in qs.items()}

    except Exception:
      return {}

  def do_POST(self):
    p = urlparse(self.path).path
    body = self._read_body()
    ct = self.headers.get('Content-Type','')
    print('[POST]', p, 'CT=', ct, 'BODY=', body)

    # LOGIN catch-all
    if p in ("/api/login", "/api/v1/login", "/api/auth/login"):
      u = body.get("username") or body.get("user") or body.get("u") or ""
      pw = body.get("password") or body.get("pass") or body.get("p") or ""
      # demo: her şeyi kabul et, ama boşsa 401
      if not u or not pw:
        return self._send(401, body=j({"ok": False, "message":"Eksik kullanıcı adı/şifre"}))
      return self._send(200, body=j({"ok": True, "token": TOKEN, "user":{"id":u,"role":"Admin"}}))

    # action endpoints
    if p in ("/api/reset","/api/shock","/api/kaizen"):
      EVENTS.append({"ts":int(time.time()),"type":"action","msg":f"{p} applied"})
      return self._send(200, body=j({"ok": True, "message": f"{p} ok"}))

    return self._send(404, body=j({"ok": False, "message": "not found", "path": p}))

if __name__ == "__main__":
  srv = ThreadingHTTPServer(("0.0.0.0", 8084), H)
  print("Serving on http://0.0.0.0:8084")
  srv.serve_forever()
