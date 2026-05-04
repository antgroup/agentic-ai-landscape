#!/usr/bin/env python3
"""Publish a weekly report to Yuque through the local yuqueServer MCP config.

Input is a JSON object on stdin. It is intentionally compatible with
weekly_update.py's YUQUE_PUBLISH_COMMAND hook.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MCP_CONFIG = ROOT / ".mcp.json"
DEFAULT_SERVER_NAME = "yuqueServer"


class McpError(RuntimeError):
    pass


class StdioMcpClient:
    def __init__(self, command, args=None, env=None, timeout=30):
        self.command = command
        self.args = args or []
        self.timeout = timeout
        merged_env = os.environ.copy()
        merged_env.update(env or {})
        self.proc = subprocess.Popen(
            [command, *self.args],
            cwd=str(ROOT),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=1,
            env=merged_env,
        )
        self._next_id = 1
        self._stderr_lines = []
        self._stderr_thread = threading.Thread(target=self._read_stderr, daemon=True)
        self._stderr_thread.start()

    def _read_stderr(self):
        if not self.proc.stderr:
            return
        for line in self.proc.stderr:
            self._stderr_lines.append(line.rstrip())

    def close(self):
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()

    def notify(self, method, params=None):
        message = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            message["params"] = params
        self._write(message)

    def request(self, method, params=None):
        msg_id = self._next_id
        self._next_id += 1
        message = {"jsonrpc": "2.0", "id": msg_id, "method": method}
        if params is not None:
            message["params"] = params
        self._write(message)
        return self._read_response(msg_id)

    def _write(self, message):
        if self.proc.poll() is not None:
            raise McpError(f"MCP server exited early: {self._stderr_tail()}")
        assert self.proc.stdin is not None
        self.proc.stdin.write(json.dumps(message, ensure_ascii=False) + "\n")
        self.proc.stdin.flush()

    def _read_response(self, msg_id):
        assert self.proc.stdout is not None
        deadline = time.time() + self.timeout
        while time.time() < deadline:
            line = self.proc.stdout.readline()
            if not line:
                if self.proc.poll() is not None:
                    raise McpError(f"MCP server exited: {self._stderr_tail()}")
                time.sleep(0.05)
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            if data.get("id") != msg_id:
                continue
            if "error" in data:
                raise McpError(json.dumps(data["error"], ensure_ascii=False))
            return data.get("result")
        raise McpError(f"MCP request timed out: {self._stderr_tail()}")

    def _stderr_tail(self):
        return "\n".join(self._stderr_lines[-8:])


def load_server_config(server_name):
    if not MCP_CONFIG.exists():
        raise McpError(f"Missing MCP config: {MCP_CONFIG}")
    config = json.loads(MCP_CONFIG.read_text(encoding="utf-8"))
    servers = config.get("mcpServers", {})
    server = servers.get(server_name)
    if not server:
        raise McpError(f"MCP server {server_name!r} is not configured")
    return server


def initialize_client(server_name, timeout):
    server = load_server_config(server_name)
    command = server.get("command")
    if not command:
        raise McpError(f"MCP server {server_name!r} has no command")
    client = StdioMcpClient(
        command=command,
        args=server.get("args", []),
        env=server.get("env", {}),
        timeout=timeout,
    )
    client.request(
        "initialize",
        {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "llm-oss-landscape-yuque-publisher", "version": "0.1.0"},
        },
    )
    client.notify("notifications/initialized")
    return client


def list_tools(client):
    result = client.request("tools/list", {})
    return result.get("tools", []) if isinstance(result, dict) else []


def schema_properties(tool):
    schema = tool.get("inputSchema") or tool.get("input_schema") or {}
    props = schema.get("properties") or {}
    return set(props.keys())


def schema_property_map(tool):
    schema = tool.get("inputSchema") or tool.get("input_schema") or {}
    return schema.get("properties") or {}


def first_present(mapping, names):
    for name in names:
        value = mapping.get(name)
        if value:
            return value
    return None


def find_tool(tools, env_key, patterns):
    requested = os.getenv(env_key, "").strip()
    if requested:
        for tool in tools:
            if tool.get("name") == requested:
                return tool
        raise McpError(f"Requested tool {requested!r} from {env_key} was not found")

    scored = []
    for tool in tools:
        name = tool.get("name", "")
        lower = name.lower()
        for score, pattern in enumerate(patterns):
            if pattern in lower:
                scored.append((score, tool))
                break
    if not scored:
        return None
    scored.sort(key=lambda item: item[0])
    return scored[0][1]


def filter_arguments(tool, candidates):
    prop_map = schema_property_map(tool)
    props = set(prop_map.keys())
    if not props:
        return candidates
    filtered = {}
    for key, value in candidates.items():
        if key not in props or value in (None, ""):
            continue
        prop_type = prop_map.get(key, {}).get("type")
        if prop_type == "number" and isinstance(value, str):
            try:
                value = int(value) if value.isdigit() else float(value)
            except ValueError:
                pass
        elif prop_type == "integer" and isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                pass
        elif prop_type == "boolean" and isinstance(value, str):
            value = value.lower() in ("1", "true", "yes", "y")
        filtered[key] = value
    return filtered


def extract_structured_tool_result(result):
    if not isinstance(result, dict):
        return result
    if "structuredContent" in result:
        return result["structuredContent"]
    content = result.get("content")
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        text = "\n".join(part for part in text_parts if part).strip()
        if text:
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text
    return result


def extract_url(value):
    if isinstance(value, dict):
        url = first_present(value, ["url", "doc_url", "web_url", "link"])
        if url:
            return url
        data = value.get("data")
        if isinstance(data, dict):
            return extract_url(data)
    text = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
    match = re.search(r"https?://[^\s)>\"]+", text)
    return match.group(0) if match else None


def find_value(value, keys):
    """Search a nested JSON-like object for the first non-empty value matching any key."""
    if isinstance(value, dict):
        for key in keys:
            if value.get(key) not in (None, ""):
                return value[key]
        for item in value.values():
            found = find_value(item, keys)
            if found not in (None, ""):
                return found
    elif isinstance(value, list):
        for item in value:
            found = find_value(item, keys)
            if found not in (None, ""):
                return found
    return None


def call_tool(client, tool, arguments):
    result = client.request("tools/call", {"name": tool["name"], "arguments": arguments})
    return extract_structured_tool_result(result)


def exact_tool(tools, name):
    for tool in tools:
        if tool.get("name") == name:
            return tool
    return None


def resolve_parent_metadata(client, tools, payload):
    resolve_tool = exact_tool(tools, "skylark_resolve_url")
    if resolve_tool and payload.get("parent_url"):
        resolved = call_tool(client, resolve_tool, {"url": payload["parent_url"]})
        payload["book_id"] = payload.get("book_id") or find_value(resolved, ["book_id", "bookId"])
        payload["namespace"] = payload.get("namespace") or find_value(resolved, ["namespace"])
        payload["parent_doc_id"] = payload.get("parent_doc_id") or find_value(resolved, ["doc_id", "docId", "id"])
        payload["parent_slug"] = payload.get("parent_slug") or find_value(resolved, ["slug"])
        payload["parent_node_uuid"] = payload.get("parent_node_uuid") or find_value(resolved, ["node_uuid", "nodeUuid", "uuid"])
        return payload

    if payload.get("parent_uuid") or payload.get("parent_id") or payload.get("parent_node_uuid"):
        return payload

    parent_tool = find_tool(
        tools,
        "YUQUE_MCP_GET_TOOL",
        ["get_doc", "doc_get", "fetch_doc", "query_doc", "search_doc"],
    )
    if not parent_tool:
        return payload

    lookup_candidates = {
        "book_id": payload.get("book_id"),
        "namespace": payload.get("namespace"),
        "slug": payload.get("parent_slug"),
        "doc_slug": payload.get("parent_slug"),
        "title": payload.get("parent_title"),
        "path": payload.get("parent_slug"),
    }
    lookup_args = filter_arguments(parent_tool, lookup_candidates)
    if not lookup_args:
        return payload

    parent = call_tool(client, parent_tool, lookup_args)
    if isinstance(parent, dict):
        data = parent.get("data") if isinstance(parent.get("data"), dict) else parent
        parent_uuid = first_present(data, ["uuid", "id", "doc_id", "docId"])
        if parent_uuid:
            payload["parent_uuid"] = parent_uuid
            payload["parent_id"] = parent_uuid
            payload["parent_doc_id"] = parent_uuid
    return payload


def find_node_uuid_in_toc(toc, payload):
    parent_doc_id = str(payload.get("parent_doc_id") or "")
    parent_slug = payload.get("parent_slug") or ""
    parent_title = payload.get("parent_title") or ""

    def walk(node):
        if not isinstance(node, dict):
            return None
        node_doc_id = str(first_present(node, ["doc_id", "docId", "id"]) or "")
        node_slug = str(first_present(node, ["slug", "url"]) or "")
        node_title = str(first_present(node, ["title", "name"]) or "")
        node_uuid = first_present(node, ["node_uuid", "nodeUuid", "uuid"])
        if node_uuid:
            if parent_doc_id and node_doc_id == parent_doc_id:
                return node_uuid
            if parent_slug and (node_slug == parent_slug or node_slug.endswith(parent_slug)):
                return node_uuid
            if parent_title and node_title == parent_title:
                return node_uuid
        for key in ("children", "childs", "items", "toc", "data"):
            child = node.get(key)
            if isinstance(child, list):
                for item in child:
                    found = walk(item)
                    if found:
                        return found
            elif isinstance(child, dict):
                found = walk(child)
                if found:
                    return found
        return None

    if isinstance(toc, list):
        for item in toc:
            found = walk(item)
            if found:
                return found
        return None
    return walk(toc)


def add_doc_to_parent_toc(client, tools, payload, created):
    toc_update_tool = exact_tool(tools, "skylark_book_toc_update")
    if not toc_update_tool:
        return None

    book_id = payload.get("book_id")
    doc_id = find_value(created, ["doc_id", "docId", "id"])
    if not book_id or not doc_id:
        return None

    target_uuid = payload.get("parent_node_uuid")
    if not target_uuid:
        toc_tool = exact_tool(tools, "skylark_book_toc")
        if toc_tool:
            toc = call_tool(client, toc_tool, filter_arguments(toc_tool, {"book_id": book_id}))
            target_uuid = find_node_uuid_in_toc(toc, payload)

    if not target_uuid:
        return None

    args = filter_arguments(
        toc_update_tool,
        {
            "book_id": book_id,
            "action": "appendChild",
            "doc_id": doc_id,
            "target_uuid": target_uuid,
            "title": payload.get("title"),
            "type": "DOC",
            "visible": "1",
        },
    )
    return call_tool(client, toc_update_tool, args)


def publish_report(client, tools, payload):
    requested_create_tool = os.getenv("YUQUE_MCP_CREATE_TOOL", "").strip()
    if requested_create_tool:
        create_tool = exact_tool(tools, requested_create_tool)
        if not create_tool:
            raise McpError(f"Requested tool {requested_create_tool!r} was not found")
    elif payload.get("namespace"):
        create_tool = exact_tool(tools, "skylark_user_doc_create")
    else:
        create_tool = exact_tool(tools, "skylark_doc_create")
    create_tool = create_tool or find_tool(
        tools,
        "YUQUE_MCP_CREATE_TOOL",
        ["create_doc", "doc_create", "create", "publish_doc", "write_doc"],
    )
    if not create_tool:
        names = ", ".join(tool.get("name", "") for tool in tools)
        raise McpError(f"No Yuque create-doc tool found. Available tools: {names}")

    payload = resolve_parent_metadata(client, tools, payload)
    candidates = {
        "book_id": payload.get("book_id"),
        "bookId": payload.get("book_id"),
        "repo_id": payload.get("book_id"),
        "repoId": payload.get("book_id"),
        "namespace": payload.get("namespace"),
        "repo": payload.get("namespace"),
        "title": payload.get("title"),
        "slug": payload.get("slug"),
        "body": payload.get("body"),
        "content": payload.get("body"),
        "markdown": payload.get("body"),
        "format": "markdown",
        "public": payload.get("public"),
        "parent_slug": payload.get("parent_slug"),
        "parentSlug": payload.get("parent_slug"),
        "parent_title": payload.get("parent_title"),
        "parentTitle": payload.get("parent_title"),
        "parent_uuid": payload.get("parent_uuid"),
        "parentUuid": payload.get("parent_uuid"),
        "parent_id": payload.get("parent_id"),
        "parentId": payload.get("parent_id"),
    }
    arguments = filter_arguments(create_tool, candidates)
    required = {"title", "body"}
    missing = [name for name in required if name not in arguments and name in schema_properties(create_tool)]
    if missing:
        raise McpError(f"Missing required Yuque tool arguments: {', '.join(missing)}")

    result = call_tool(client, create_tool, arguments)
    toc_result = add_doc_to_parent_toc(client, tools, payload, result)
    url = extract_url(result)
    if not url and payload.get("namespace") and payload.get("slug"):
        url = f"https://yuque.antfin.com/{payload['namespace']}/{payload['slug']}"
    return {"url": url, "tool": create_tool["name"], "toc_result": toc_result, "result": result}


def build_payload(stdin_text):
    incoming = json.loads(stdin_text) if stdin_text.strip() else {}
    date_str = incoming.get("date") or time.strftime("%Y-%m-%d")
    payload = {
        "book_id": incoming.get("book_id") or os.getenv("YUQUE_BOOK_ID", ""),
        "namespace": incoming.get("namespace") or os.getenv("YUQUE_NAMESPACE", ""),
        "parent_url": incoming.get("parent_url") or os.getenv("YUQUE_PARENT_URL", ""),
        "parent_slug": incoming.get("parent_slug") or os.getenv("YUQUE_PARENT_SLUG", ""),
        "parent_title": incoming.get("parent_title") or os.getenv("YUQUE_PARENT_TITLE", ""),
        "parent_uuid": incoming.get("parent_uuid") or os.getenv("YUQUE_PARENT_UUID", ""),
        "parent_id": incoming.get("parent_id") or os.getenv("YUQUE_PARENT_ID", ""),
        "parent_doc_id": incoming.get("parent_doc_id") or os.getenv("YUQUE_PARENT_DOC_ID", ""),
        "parent_node_uuid": incoming.get("parent_node_uuid") or os.getenv("YUQUE_PARENT_NODE_UUID", ""),
        "public": incoming.get("public") or os.getenv("YUQUE_DOC_PUBLIC", ""),
        "title": incoming.get("title") or f"Agentic 每周推送 {date_str}",
        "slug": incoming.get("slug") or f"agentic-weekly-{date_str}",
        "body": incoming.get("body") or incoming.get("content") or "",
        "date": date_str,
    }
    if not payload["body"]:
        raise McpError("Missing report body")
    return payload


def main():
    parser = argparse.ArgumentParser(description="Publish a weekly report through Yuque MCP")
    parser.add_argument("--server", default=os.getenv("YUQUE_MCP_SERVER", DEFAULT_SERVER_NAME))
    parser.add_argument("--timeout", type=int, default=int(os.getenv("YUQUE_MCP_TIMEOUT", "30")))
    parser.add_argument("--list-tools", action="store_true")
    args = parser.parse_args()

    client = initialize_client(args.server, args.timeout)
    try:
        tools = list_tools(client)
        if args.list_tools:
            print(json.dumps([{"name": tool.get("name"), "inputSchema": tool.get("inputSchema")} for tool in tools], ensure_ascii=False, indent=2))
            return
        payload = build_payload(sys.stdin.read())
        result = publish_report(client, tools, payload)
        print(json.dumps(result, ensure_ascii=False))
    finally:
        client.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Yuque MCP publish failed: {exc}", file=sys.stderr)
        sys.exit(1)
