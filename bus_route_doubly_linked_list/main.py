"""MIO Bus Route - Doubly Linked List.
Run this file: it opens the browser at http://127.0.0.1:5000
(uses only the Python standard library, nothing to install)."""
import json
import os
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

from doubly_linked_list import DoublyLinkedList

HERE = os.path.dirname(os.path.abspath(__file__))
L = DoublyLinkedList()
EXAMPLE = [("Universidades", "South"), ("Unidad Deportiva", "South"), ("Tequendama", "Center"),
           ("San Bosco", "Center"), ("Chiminangos", "North"), ("Menga", "North")]


def state(msg="", path=None, highlight=None, code=None, error=False, deleting=False, clear_fields=False):
    nodes = L.to_list()
    return {"nodes": [{"name": n.name, "zone": n.zone} for n in nodes],
            "current": nodes.index(L.current) if L.current else None,
            "msg": msg, "path": path or [], "highlight": highlight, "code": code,
            "error": error, "deleting": deleting, "clear_fields": clear_fields}


def fail(msg):
    return state(msg, error=True)


def operate(op, d):
    name = (d.get("name") or "").strip()
    zone = (d.get("zone") or "").strip() or "No zone"
    try:
        idx = int(d.get("index"))
    except (TypeError, ValueError):
        idx = None
    n = L.length

    if op in ("start", "end", "insert", "search") and not name:
        return fail("Type the station name first.")
    if op in ("insert", "delete") and idx is None:
        return fail("The index must be an integer.")

    if op == "start":
        L.prepend(name, zone)
        return state(f"'{name}' added at the start: new.next = old head and head.prev = new.",
                     highlight=0, code="prepend", clear_fields=True)
    if op == "end":
        L.append(name, zone)
        return state(f"'{name}' added at the end: new.prev = old tail and tail.next = new.",
                     highlight=n, code="append", clear_fields=True)
    if op == "insert":
        if idx < 0 or idx > n:
            return fail(f"Use an index between 0 and {n}.")
        path = L.path_to(idx) if 0 < idx < n else []
        L.insert(idx, name, zone)
        return state(f"'{name}' inserted at index {idx}: leader and follower are re-linked in both directions.",
                     path=path, highlight=idx, code="insert", clear_fields=True)
    if op in ("delete", "del_first", "del_last"):
        if n == 0:
            return fail("There are no stations to delete.")
        if op == "del_first":
            idx = 0
        elif op == "del_last":
            idx = n - 1
        if idx < 0 or idx >= n:
            return fail(f"Use an index between 0 and {n - 1}.")
        path = L.path_to(idx)
        node = L.remove(idx)
        return state(f"'{node.name}' deleted: its neighbors are now linked to each other.",
                     path=path, code="remove", deleting=True)
    if op == "search":
        pos = L.search(name)
        path = list(range(n if pos < 0 else pos + 1))
        msg = f"'{name}' found at index {pos}." if pos >= 0 else f"'{name}' is not in the route."
        return state(msg, path=path, highlight=pos if pos >= 0 else None, code="search")
    if op == "forward":
        return state("Head to tail using next: " + " -> ".join(x.name for x in L.to_list()),
                     path=list(range(n)), code="traverse")
    if op == "backward":
        return state("Tail to head using prev: " + " -> ".join(x.name for x in reversed(L.to_list())),
                     path=list(range(n - 1, -1, -1)), code="traverse")
    if op == "advance":
        ok = L.next_stop()
        return state(f"The bus arrives at '{L.current.name}' (current = current.next)." if ok
                     else "End of the line: current.next is None.", code="next_stop")
    if op == "go_back":
        ok = L.prev_stop()
        return state(f"The bus goes back to '{L.current.name}' (current = current.prev)." if ok
                     else "Start of the line: current.prev is None.", code="prev_stop")
    if op == "example":
        L.empty()
        for t, z in EXAMPLE:
            L.append(t, z)
        return state("Example route loaded with 6 stations.", code="append")
    if op == "empty":
        L.empty()
        return state("Route emptied: head = tail = None.")
    return state()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def respond(self, body, kind):
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/state":
            self.respond(json.dumps(state()).encode("utf-8"), "application/json")
        elif self.path in ("/", "/index.html"):
            with open(os.path.join(HERE, "index.html"), "rb") as f:
                self.respond(f.read(), "text/html; charset=utf-8")
        else:
            self.send_error(404)

    def do_POST(self):
        op = self.path.rsplit("/", 1)[-1]
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        try:
            res = operate(op, data)
        except Exception as e:  # never crash the server
            res = fail(f"Error: {e}")
        self.respond(json.dumps(res).encode("utf-8"), "application/json")


if __name__ == "__main__":
    port = 5000
    while True:
        try:
            server = HTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            port += 1
    url = f"http://127.0.0.1:{port}"
    print(f"Open {url} in your browser (press Ctrl+C to stop)")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")
