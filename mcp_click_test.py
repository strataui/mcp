#!/usr/bin/env python3
"""External MCP JSON-RPC 2.0 client driving a running Strata app via `strata-mcp`."""

import json
import os
import shutil
import subprocess
import sys
import time


def resolve_strata_mcp_bin() -> str:
    if env_bin := os.environ.get("STRATA_MCP_BIN"):
        return env_bin
    repo_root = os.path.dirname(os.path.abspath(__file__))
    for rel in (
        "../strata/target/release/strata-mcp",
        "../strata/target/debug/strata-mcp",
    ):
        cand = os.path.normpath(os.path.join(repo_root, rel))
        if os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand
    if found := shutil.which("strata-mcp"):
        return found
    return "strata-mcp"


STRATA_MCP_BIN = resolve_strata_mcp_bin()
SCREENSHOT_PATH = sys.argv[1] if len(sys.argv) > 1 else "/tmp/mcp_demo_after.png"


class McpClient:
    def __init__(self, bin_path: str):
        self.proc = subprocess.Popen(
            [bin_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self.next_id = 1

    def rpc(self, method: str, params: dict):
        req_id = self.next_id
        self.next_id += 1
        msg = {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params}
        assert self.proc.stdin is not None and self.proc.stdout is not None
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()
        while True:
            line = self.proc.stdout.readline()
            if not line:
                stderr = self.proc.stderr.read() if self.proc.stderr else ""
                raise RuntimeError(f"strata-mcp EOF waiting for {method}: {stderr}")
            line = line.strip()
            if not line:
                continue
            resp = json.loads(line)
            if resp.get("id") == req_id:
                return resp

    def call_tool(self, name: str, arguments: dict):
        resp = self.rpc("tools/call", {"name": name, "arguments": arguments})
        if "error" in resp and resp["error"] is not None:
            raise RuntimeError(f"Tool {name} failed: {resp['error']}")
        result = resp.get("result", {})
        if result.get("isError"):
            raise RuntimeError(f"Tool {name} error: {result}")
        return result

    def close(self):
        if self.proc.stdin:
            self.proc.stdin.close()
        self.proc.terminate()
        self.proc.wait(timeout=3)


def main():
    client = McpClient(STRATA_MCP_BIN)
    try:
        init = client.rpc("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "mcp_demo_driver", "version": "0.1.0"},
        })
        print("initialize:", json.dumps(init.get("result", {}), indent=2))

        tools = client.rpc("tools/list", {})
        tool_names = [t["name"] for t in tools["result"]["tools"]]
        print("tools/list:", tool_names)

        # Wait briefly for listener/session readiness
        info = None
        for _ in range(10):
            try:
                res = client.call_tool("strata_session_info", {})
                info = res["content"][0]["text"]
                break
            except Exception as e:
                time.sleep(0.25)
                last_err = e
        if info is None:
            raise RuntimeError(f"Could not connect to strata_session_info: {last_err}")
        print("session_info:", info)

        # Scan candidate coordinates, parsing inspect JSON to match actual button/input elements and use their center
        def find_element(pred, xs, ys):
            for y in ys:
                for x in xs:
                    res = client.call_tool("strata_inspect_element", {"x": x, "y": y})
                    txt = res["content"][0]["text"]
                    try:
                        data = json.loads(txt)
                    except Exception:
                        continue
                    if pred(data):
                        b = data.get("bounds") or {}
                        cx = b.get("x", x) + b.get("width", 0) * 0.5 if b else x
                        cy = b.get("y", y) + b.get("height", 0) * 0.5 if b else y
                        return cx, cy, data
            raise RuntimeError("Element not found during scan")

        inc_x, inc_y, inc_data = find_element(
            lambda d: d.get("tag") in ("button", "span") and "Increment +1" in (d.get("text") or ""),
            range(130, 260, 25),
            range(260, 340, 15),
        )
        print(f"Found Increment button at ({inc_x:.1f}, {inc_y:.1f}): tag={inc_data.get('tag')}")

        acc_x, acc_y, acc_data = find_element(
            lambda d: d.get("tag") in ("button", "span") and "Toggle Accent" in (d.get("text") or ""),
            range(280, 420, 25),
            range(260, 340, 15),
        )
        print(f"Found Toggle Accent button at ({acc_x:.1f}, {acc_y:.1f}): tag={acc_data.get('tag')}")

        inp_x, inp_y, inp_data = find_element(
            lambda d: d.get("tag") == "input",
            range(180, 480, 50),
            range(350, 440, 15),
        )
        print(f"Found Input at ({inp_x:.1f}, {inp_y:.1f}): tag={inp_data.get('tag')}")

        # Click Increment +1 three times!
        for i in range(3):
            client.call_tool("strata_mouse_click", {"x": inc_x, "y": inc_y, "button": "left"})
            time.sleep(0.08)
        print("Clicked Increment +1 x3")

        # Click Toggle Accent once!
        client.call_tool("strata_mouse_click", {"x": acc_x, "y": acc_y, "button": "left"})
        time.sleep(0.08)
        print("Clicked Toggle Accent x1")

        # Click input box and type text via MCP!
        client.call_tool("strata_mouse_click", {"x": inp_x, "y": inp_y, "button": "left"})
        time.sleep(0.08)
        client.call_tool("strata_keyboard_type", {"text": "Hello from MCP!"})
        time.sleep(0.15)
        print("Typed 'Hello from MCP!'")

        # Move pointer cleanly back onto Increment button and capture screenshot with Yaru cursor overlay
        client.call_tool("strata_mouse_move", {"x": inc_x, "y": inc_y, "smooth": True})
        time.sleep(0.25)
        shot = client.call_tool("strata_take_screenshot", {"save_path": SCREENSHOT_PATH})
        content_types = [c.get("type") for c in shot.get("content", [])]
        print("Screenshot saved to:", SCREENSHOT_PATH, "content blocks:", content_types)
    finally:
        client.close()


if __name__ == "__main__":
    main()
