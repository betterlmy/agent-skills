#!/usr/bin/env python3
"""Tavily 网页数据检索工具（纯标准库，无第三方依赖，Python 3.9+）。

子命令：
  check                          校验 TAVILY_API_KEY 与端点可达性（消耗 1 次 search 额度）
  search <query> [--depth D] [--topic T] [--days N] [--max-results N] [--include-answer]
  extract <url> [<url> ...] [--include-images]
  map <url>
  crawl <url> [--max-depth N] [--max-breadth N]
  research <query> [--model pro] [--no-wait]
  research-status <job-id>
  research-poll <job-id> [--timeout S] [--interval S]

凭据只从环境变量 TAVILY_API_KEY 读取；本工具永不打印、持久化或回显密钥本身
（输出中只可能出现脱敏形式 ***<末4位>）。端点基地址可用环境变量
TAVILY_BASE_URL 覆盖（默认 https://api.tavily.com）。

退出码：0 成功；2 配置错误（缺 TAVILY_API_KEY）；3 API 错误（401/403/429/5xx 或任务失败）；
4 网络错误。
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

KEY_ENV = "TAVILY_API_KEY"
BASE_URL_ENV = "TAVILY_BASE_URL"
DEFAULT_BASE_URL = "https://api.tavily.com"

EXIT_OK = 0
EXIT_CONFIG = 2
EXIT_API = 3
EXIT_NETWORK = 4

RESEARCH_DONE_STATUSES = {"completed", "complete", "done", "success", "succeeded"}
RESEARCH_FAILED_STATUSES = {"failed", "failure", "error", "cancelled", "canceled"}
CRAWL_DONE_MARKERS = ("data", "results", "urls", "crawled_pages")


def mask_key(key):
    """返回脱敏形式，任何输出路径只允许出现该形式。"""
    if not key or len(key) < 4:
        return "*****"
    return "***" + key[-4:]


def setup_guide():
    return (
        "未检测到 {env}。配置方法：\n"
        "  1. 在 https://app.tavily.com 获取 API key（新账号有免费月度额度）；\n"
        "  2. 在当前 shell 执行 export {env}=\"tvly-...\"（建议写入 shell 配置；\n"
        "     切勿提交到仓库，也不要打印到任何输出）；\n"
        "  可选：export {base_env}=\"https://api.tavily.com\" 覆盖端点基地址。\n"
        "配置完成后重新运行本工具。"
    ).format(env=KEY_ENV, base_env=BASE_URL_ENV)


def api_call(endpoint, payload=None, api_key=None, method=None, timeout=120):
    """发起一次 Tavily REST 调用，返回 (http_status, parsed_body)。

    网络失败时返回 (0, {"error": ...})。本函数是唯一网络出口，便于测试替换。
    """
    base = os.environ.get(BASE_URL_ENV, DEFAULT_BASE_URL).rstrip("/")
    url = base + endpoint
    m = method
    if m is None:
        m = "POST" if payload is not None else "GET"
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=m)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "replace")
            return resp.status, _parse_body(body)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        return e.code, _parse_body(body)
    except urllib.error.URLError as e:
        return 0, {"error": "network: %s" % e.reason}
    except (TimeoutError, OSError) as e:
        return 0, {"error": "network: %s" % e}


def _parse_body(body):
    try:
        return json.loads(body) if body.strip() else {}
    except (ValueError, TypeError):
        return {"raw": body}


def require_key():
    """返回 api_key；缺失时打印配置指引并以退出码 2 终止。"""
    key = os.environ.get(KEY_ENV, "").strip()
    if not key:
        print(setup_guide())
        sys.exit(EXIT_CONFIG)
    return key


def print_json(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def finish_api_call(status, data, what):
    """统一处理一次 API 调用的结果；返回 None 表示成功。"""
    if status == 0:
        print_json(data)
        sys.exit(EXIT_NETWORK)
    if status in (401, 403):
        print("鉴权失败（HTTP %d）：TAVILY_API_KEY 无效或已过期，请核对后重试。" % status)
        print_json(data)
        sys.exit(EXIT_API)
    if status == 429:
        print("触发限流（HTTP 429）：请稍后重试，或降低调用频率 / 减少 max-results。")
        print_json(data)
        sys.exit(EXIT_API)
    if status >= 500:
        print("服务端错误（HTTP %d）：%s，可稍后重试一次。" % (status, what))
        print_json(data)
        sys.exit(EXIT_API)
    if 200 <= status < 300:
        return None
    print("非预期响应（HTTP %d）：%s" % (status, what))
    print_json(data)
    sys.exit(EXIT_API)


def cmd_check(args):
    key = require_key()
    status, data = api_call("/search", {"query": "tavily", "max_results": 1}, key)
    finish_api_call(status, data, "check")
    print("Tavily 连接正常。")
    print("  端点: %s" % os.environ.get(BASE_URL_ENV, DEFAULT_BASE_URL))
    print("  密钥: %s（脱敏）" % mask_key(key))
    return EXIT_OK


def cmd_search(args):
    key = require_key()
    payload = {
        "query": args.query,
        "max_results": args.max_results,
        "search_depth": args.depth,
        "topic": args.topic,
    }
    if args.days is not None:
        payload["days"] = args.days
    if args.include_answer:
        payload["include_answer"] = True
    status, data = api_call("/search", payload, key)
    finish_api_call(status, data, "search")
    print_json(data)
    return EXIT_OK


def cmd_extract(args):
    key = require_key()
    payload = {"urls": args.urls}
    if args.include_images:
        payload["include_images"] = True
    status, data = api_call("/extract", payload, key)
    finish_api_call(status, data, "extract")
    print_json(data)
    return EXIT_OK


def cmd_map(args):
    key = require_key()
    payload = {"url": args.url}
    if args.max_depth is not None:
        payload["max_depth"] = args.max_depth
    status, data = api_call("/map", payload, key)
    finish_api_call(status, data, "map")
    print_json(data)
    return EXIT_OK


def _job_id_from(data, names):
    if not isinstance(data, dict):
        return None
    for n in names:
        v = data.get(n)
        if isinstance(v, str) and v:
            return v
    return None


def cmd_crawl(args):
    key = require_key()
    # 实测 /crawl 为同步返回（results 直接含在首次响应中）；轮询仅为防御性兑底。
    payload = {"url": args.url}
    if args.max_depth is not None:
        payload["max_depth"] = args.max_depth
    if args.max_breadth is not None:
        payload["max_breadth"] = args.max_breadth
    status, data = api_call("/crawl", payload, key)
    finish_api_call(status, data, "crawl")
    # 同步返回结果则直接输出；实测 /crawl 为同步返回，下方轮询仅为防御性兑底。
    # 已验证的完成标志字段：data/results/urls/crawled_pages（2026-09-10）。
    if isinstance(data, dict) and any(m in data for m in CRAWL_DONE_MARKERS):
        print_json(data)
        return EXIT_OK
    job_id = _job_id_from(data, ("id", "job_id", "crawl_id"))
    if not job_id:
        print_json(data)
        return EXIT_OK
    print("crawl 任务已创建: %s，开始轮询（最长 %ds）…" % (job_id, args.timeout), file=sys.stderr)
    return _poll("crawl", job_id, key, args.timeout, args.interval)


def _poll(resource, job_id, key, timeout, interval):
    """轮询 <resource>/<job_id> 直到完成或超时；超时时输出最后一次结果。"""
    deadline = time.time() + timeout
    last = {}
    while True:
        status, data = api_call(
            "/%s/%s" % (resource, urllib.parse.quote(job_id)), None, key, method="GET"
        )
        finish_api_call(status, data, "%s status" % resource)
        last = data if isinstance(data, dict) else {}
        state = str(last.get("status", "")).lower()
        if state in RESEARCH_DONE_STATUSES:
            print_json(last)
            return EXIT_OK
        if state in RESEARCH_FAILED_STATUSES:
            print_json(last)
            return EXIT_API
        if time.time() >= deadline:
            print("轮询超时（%ds），输出最后一次结果；可用 research-status 稍后继续查询。" % timeout, file=sys.stderr)
            print_json(last)
            return EXIT_API
        time.sleep(interval)


def cmd_research(args):
    key = require_key()
    # 实测 /research 入参字段为 input（非 query），model 可选 mini/pro/auto。
    payload = {"input": args.query}
    if args.model:
        payload["model"] = args.model
    status, data = api_call("/research", payload, key)
    finish_api_call(status, data, "research")
    if args.no_wait:
        print_json(data)
        return EXIT_OK
    job_id = _job_id_from(data, ("request_id", "id", "job_id", "research_id"))
    if not job_id:
        print_json(data)
        return EXIT_OK
    print("research 任务已创建: %s，开始轮询 GET /research/%s（最长 %ds）…" % (job_id, job_id, args.timeout), file=sys.stderr)
    return _poll("research", job_id, key, args.timeout, args.interval)


def cmd_research_status(args):
    key = require_key()
    status, data = api_call("/research/%s" % urllib.parse.quote(args.job_id), None, key, method="GET")
    finish_api_call(status, data, "research status")
    print_json(data)
    return EXIT_OK


def cmd_research_poll(args):
    key = require_key()
    return _poll("research", args.job_id, key, args.timeout, args.interval)


def build_parser():
    p = argparse.ArgumentParser(prog="tavily.py", description="Tavily 网页数据检索工具（凭据读 TAVILY_API_KEY 环境变量）")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("check", help="校验密钥与端点可达性（消耗 1 次 search 额度）")
    sp.set_defaults(func=cmd_check)

    sp = sub.add_parser("search", help="实时网页搜索")
    sp.add_argument("query")
    sp.add_argument("--depth", choices=["basic", "advanced"], default="basic")
    sp.add_argument("--topic", choices=["general", "news"], default="general")
    sp.add_argument("--days", type=int, default=None, help="news 话题下限定最近 N 天")
    sp.add_argument("--max-results", type=int, default=5)
    sp.add_argument("--include-answer", action="store_true", help="附带 Tavily 生成的摘要答案")
    sp.set_defaults(func=cmd_search)

    sp = sub.add_parser("extract", help="已知 URL 的正文抽取")
    sp.add_argument("urls", nargs="+")
    sp.add_argument("--include-images", action="store_true")
    sp.set_defaults(func=cmd_extract)

    sp = sub.add_parser("map", help="站点 URL 结构发现")
    sp.add_argument("url")
    sp.add_argument("--max-depth", type=int, default=None)
    sp.set_defaults(func=cmd_map)

    sp = sub.add_parser("crawl", help="站点章节批量爬取（同步返回，自动兑底轮询）")
    sp.add_argument("url")
    sp.add_argument("--max-depth", type=int, default=None)
    sp.add_argument("--max-breadth", type=int, default=None)
    sp.add_argument("--timeout", type=int, default=300, help="兑底轮询超时秒数")
    sp.add_argument("--interval", type=int, default=5, help="兑底轮询间隔秒数")
    sp.set_defaults(func=cmd_crawl)

    sp = sub.add_parser("research", help="多源带引用研究（异步任务自动轮询）")
    sp.add_argument("query")
    sp.add_argument("--model", choices=["mini", "pro", "auto"], default=None)
    sp.add_argument("--no-wait", action="store_true", help="只创建任务并输出任务 JSON，不轮询")
    sp.add_argument("--timeout", type=int, default=300, help="轮询超时秒数")
    sp.add_argument("--interval", type=int, default=10, help="轮询间隔秒数")
    sp.set_defaults(func=cmd_research)

    sp = sub.add_parser("research-status", help="查询一次 research 任务状态")
    sp.add_argument("job_id")
    sp.set_defaults(func=cmd_research_status)

    sp = sub.add_parser("research-poll", help="继续轮询一个已创建的 research 任务")
    sp.add_argument("job_id")
    sp.add_argument("--timeout", type=int, default=300)
    sp.add_argument("--interval", type=int, default=10)
    sp.set_defaults(func=cmd_research_poll)

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
