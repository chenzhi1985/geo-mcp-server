"""
GEO MCP Server — stdio 协议级测试
===================================
直接通过 JSON-RPC 协议与 MCP Server 通信，
验证完整的 MCP 协议生命周期。

运行方式:
    python test_stdio.py

这是最底层的测试——模拟 Claude Desktop 与 Server 的通信过程。
"""
import subprocess
import json
import sys
import os
import time

SERVER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.py")

def send_request(proc, method: str, params: dict = None, req_id: int = 1) -> dict:
    """发送 JSON-RPC 请求并读取响应"""
    request = {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": method,
        "params": params or {},
    }
    payload = json.dumps(request) + "\n"
    proc.stdin.write(payload)
    proc.stdin.flush()

    # 读取响应行
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        try:
            response = json.loads(line.strip())
            if response.get("id") == req_id:
                return response
        except json.JSONDecodeError:
            # 可能是 server 的日志输出，跳过
            pass

    return {"error": "no response"}


def run_test(name: str, fn):
    """运行单个测试"""
    try:
        fn()
        print(f"  ✅ {name}")
    except AssertionError as e:
        print(f"  ❌ {name} — {e}")
    except Exception as e:
        print(f"  💥 {name} — {e}")


def main():
    print("=" * 60)
    print("🔌 GEO MCP Server — stdio 协议测试")
    print("=" * 60)
    print()

    # 启动 Server 进程
    print("📡 启动 MCP Server...")
    proc = subprocess.Popen(
        [sys.executable, SERVER_SCRIPT],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    time.sleep(0.5)

    if proc.poll() is not None:
        stderr = proc.stderr.read()
        print(f"❌ Server 启动失败:\n{stderr}")
        return 1

    print(f"   PID: {proc.pid}")
    print()

    # ── 测试1: Initialize ────────────────────────────────────
    print("── 阶段1: 初始化握手 ──")

    init_resp = send_request(proc, "initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test-client", "version": "1.0.0"},
    }, req_id=1)

    if "error" in init_resp:
        print(f"  ❌ Initialize 失败: {init_resp}")
        proc.terminate()
        return 1

    server_info = init_resp.get("result", {}).get("serverInfo", {})
    print(f"  ✅ Server: {server_info.get('name', 'unknown')}")
    print(f"     协议版本: {init_resp['result'].get('protocolVersion', 'unknown')}")
    print(f"     能力: {json.dumps(init_resp['result'].get('capabilities', {}), indent=2)}")

    # 发送 initialized 通知
    proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
    proc.stdin.flush()
    print(f"  ✅ initialized 通知已发送")
    print()

    # ── 测试2: List Tools ────────────────────────────────────
    print("── 阶段2: 列出工具 ──")

    tools_resp = send_request(proc, "tools/list", {}, req_id=2)
    tools = tools_resp.get("result", {}).get("tools", [])
    print(f"  ✅ 共 {len(tools)} 个工具:")
    for t in tools:
        schema = t.get("inputSchema", {})
        params = schema.get("properties", {})
        required = schema.get("required", [])
        print(f"     🔧 {t['name']}")
        print(f"        {t.get('description', '')[:80]}...")
        if params:
            for pname, pinfo in params.items():
                req_mark = " *required" if pname in required else ""
                print(f"        - {pname}: {pinfo.get('type', 'any')}{req_mark}")
    print()

    # ── 测试3: List Resources ─────────────────────────────────
    print("── 阶段3: 列出资源 ──")

    res_resp = send_request(proc, "resources/list", {}, req_id=3)
    resources = res_resp.get("result", {}).get("resources", [])
    print(f"  ✅ 共 {len(resources)} 个资源:")
    for r in resources:
        print(f"     📦 {r.get('uri', 'unknown')}")
        desc = r.get('description', '')
        if desc:
            print(f"        {desc[:100]}")
    print()

    # ── 测试4: Call Tool ─────────────────────────────────────
    print("── 阶段4: 调用工具 (内容评分) ──")

    call_resp = send_request(proc, "tools/call", {
        "name": "geo_content_score",
        "arguments": {"url": "https://example.com", "keywords": ""},
    }, req_id=4)

    result = call_resp.get("result", {})
    if result.get("isError"):
        print(f"  ❌ 工具返回错误: {result.get('content', [])}")
    else:
        content = result.get("content", [])
        for item in content:
            if item.get("type") == "text":
                try:
                    data = json.loads(item["text"])
                    print(f"  ✅ 调用成功!")
                    print(f"     URL: {data.get('url', 'N/A')}")
                    print(f"     Score: {data.get('total', 'N/A')}/100")
                    print(f"     Grade: {data.get('grade', 'N/A')}")
                    print(f"     Word Count: {data.get('word_count', 'N/A')}")
                except json.JSONDecodeError:
                    print(f"  ✅ 返回文本: {item['text'][:200]}...")
    print()

    # ── 测试5: Call Tool with params ──────────────────────────
    print("── 阶段5: 调用工具 (引用检测) ──")

    call2_resp = send_request(proc, "tools/call", {
        "name": "geo_check_citation",
        "arguments": {"brand": "OpenAI", "topic": "AI", "engines": "chatgpt,claude"},
    }, req_id=5)

    result2 = call2_resp.get("result", {})
    if not result2.get("isError"):
        content2 = result2.get("content", [])
        for item in content2:
            if item.get("type") == "text":
                try:
                    data = json.loads(item["text"])
                    print(f"  ✅ 调用成功!")
                    print(f"     Brand: {data.get('brand', 'N/A')}")
                    print(f"     Score: {data.get('overall_presence_score', 'N/A')}/100")
                    print(f"     Summary: {data.get('summary', 'N/A')}")
                except json.JSONDecodeError:
                    print(f"  ✅ 返回文本: {item['text'][:200]}...")
    print()

    # ── 测试6: Read Resource ──────────────────────────────────
    print("── 阶段6: 读取资源 ──")

    resource_resp = send_request(proc, "resources/read", {
        "uri": "geo://checklist",
    }, req_id=6)

    res_content = resource_resp.get("result", {}).get("contents", [])
    for item in res_content:
        text = item.get("text", "")
        line_count = len(text.split("\n"))
        print(f"  ✅ geo://checklist: {line_count} 行")
        print(f"     前3行: {text.split(chr(10))[0]}")
    print()

    print("── 阶段7: 获取提示词 ──")

    prompt_resp = send_request(proc, "prompts/get", {
        "name": "geo_optimize",
    }, req_id=7)

    prompt_result = prompt_resp.get("result", {})
    messages = prompt_result.get("messages", [])
    print(f"  ✅ geo_optimize 提示词: {len(messages)} 条消息")
    if messages:
        content = messages[0].get("content", {})
        text = content.get("text", "")
        print(f"     长度: {len(text)} 字符")
        print(f"     开头: {text[:100]}...")
    print()

    # ── 清理 ──────────────────────────────────────────────────
    print("── 清理: 关闭连接 ──")
    proc.stdin.close()
    proc.terminate()
    proc.wait(timeout=5)
    print(f"  ✅ Server 已关闭 (exit code: {proc.returncode})")
    print()

    print("=" * 60)
    print("🎉 stdio 协议测试全部完成！")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
