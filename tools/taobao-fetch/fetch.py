#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests",
#     "beautifulsoup4",
#     "pyyaml",
# ]
# ///
"""
淘宝页面抓取工具

通过 ScraperAPI 代理访问淘宝/天猫页面，获取截图、HTML 和商品图片。
独立工具，不依赖 OpenClaw，可单独调试。

核心能力:
  1. 从嵌入的 JSON (window.staticConfig 等) 提取商品数据（免费套餐可用）
  2. 从 HTML DOM 提取 CDN 图片 URL
  3. 页面截图（需要 ScraperAPI premium 套餐）

用法:
    # 抓取淘宝首页（提取推荐商品）
    uv run fetch.py "https://www.taobao.com"

    # 抓取搜索结果
    uv run fetch.py "https://s.taobao.com/search?q=连衣裙"

    # 指定输出目录和下载图片数
    uv run fetch.py "https://www.taobao.com" -o /tmp/my-store --max-images 10

    # 只提取数据，不下载图片
    uv run fetch.py "https://www.taobao.com" --no-images

    # 输出 JSON 到 stdout（方便管道给其他工具）
    uv run fetch.py "https://www.taobao.com" --json

环境变量:
    SCRAPERAPI_KEY  — ScraperAPI 的 API Key
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
import yaml
from bs4 import BeautifulSoup


SCRAPERAPI_BASE = "https://api.scraperapi.com/"

TAOBAO_IMG_DOMAINS = [
    "img.alicdn.com",
    "gw.alicdn.com",
    "assets.alicdn.com",
    "aecpm.alicdn.com",
    "g-search1.alicdn.com",
    "g-search2.alicdn.com",
    "g-search3.alicdn.com",
    ".tbcdn.cn",
]


def log(msg: str):
    print(f"[taobao-fetch] {msg}", flush=True)


# ──────────────────────────────────────────────
# 网络层
# ──────────────────────────────────────────────

def fetch_page(api_key: str, url: str, screenshot: bool = True) -> dict:
    """通过 ScraperAPI 获取页面内容，自动降级。

    降级策略:
      Level 1: screenshot + render (需要 premium)
      Level 2: render only (可能需要 premium)
      Level 3: 纯 HTML (免费套餐可用，商品数据在嵌入 JSON 中)
    """
    modes = []
    if screenshot:
        modes.append(("截图+渲染", {"screenshot": "true", "render": "true"}))
    modes.append(("JS渲染", {"render": "true"}))
    modes.append(("纯HTML", {}))

    resp = None
    final_mode = ""

    for mode_name, extra_params in modes:
        params = {"api_key": api_key, "url": url, **extra_params}
        log(f"请求: {url} ({mode_name})")
        start = time.time()
        resp = requests.get(SCRAPERAPI_BASE, params=params, timeout=180)

        if resp.status_code == 200:
            final_mode = mode_name
            break
        if resp.status_code == 500 and b"premium" in resp.content:
            log(f"  ⚠ {mode_name}需要 premium，降级...")
            continue
        final_mode = mode_name
        break

    elapsed = time.time() - start
    result = {
        "url": url,
        "status_code": resp.status_code,
        "mode": final_mode,
        "elapsed": round(elapsed, 1),
        "html_size": len(resp.content),
        "html": resp.text,
        "screenshot_url": resp.headers.get("sa-screenshot", ""),
        "final_url": resp.headers.get("sa-final-url", url),
        "credit_cost": resp.headers.get("sa-credit-cost", "?"),
    }

    log(f"  {final_mode} → HTTP {resp.status_code}, "
        f"{len(resp.content):,} bytes, {elapsed:.1f}s, {result['credit_cost']} credits")

    if result["screenshot_url"]:
        log(f"  截图: {result['screenshot_url']}")

    return result


def download_file(url: str, path: Path, timeout: int = 30) -> bool:
    try:
        resp = requests.get(url, timeout=timeout, stream=True)
        if resp.status_code == 200:
            with open(path, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            return True
    except Exception as e:
        log(f"  下载失败: {e}")
    return False


# ──────────────────────────────────────────────
# 数据提取层
# ──────────────────────────────────────────────

def extract_embedded_items(html: str) -> list[dict]:
    """从 <script> 标签中的嵌入 JSON 提取商品数据。

    淘宝页面在 window.staticConfig / window.__INITIAL_DATA__ 等变量中
    嵌入了商品卡片的结构化数据，包含 itemId、价格、标题、800x800 白底图。
    这些数据不需要 JS 渲染就能获取。
    """
    items = []
    seen_ids = set()

    # 提取所有 window.xxx = {...} 形式的 JSON
    json_blobs = re.findall(
        r'window\.(\w+)\s*=\s*(\{.+?\})\s*;?\s*(?:\n|$)',
        html, re.DOTALL
    )

    for var_name, json_str in json_blobs:
        try:
            data = json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            continue
        _collect_items(data, items, seen_ids)

    # 也尝试提取 JSON.parse('...') 中的数据
    json_parse_blobs = re.findall(r"JSON\.parse\('(.+?)'\)", html)
    for blob in json_parse_blobs:
        try:
            blob = blob.encode().decode('unicode_escape')
            data = json.loads(blob)
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
            continue
        _collect_items(data, items, seen_ids)

    log(f"  嵌入JSON: 提取到 {len(items)} 个商品")
    return items


def _collect_items(obj, items: list, seen_ids: set, depth: int = 0):
    """递归收集含 itemId 的对象"""
    if depth > 8:
        return
    if isinstance(obj, dict):
        if "itemId" in obj and obj["itemId"] not in seen_ids:
            item = _normalize_item(obj)
            if item:
                seen_ids.add(obj["itemId"])
                items.append(item)
        for v in obj.values():
            _collect_items(v, items, seen_ids, depth + 1)
    elif isinstance(obj, list) and len(obj) < 500:
        for v in obj:
            _collect_items(v, items, seen_ids, depth + 1)


def _normalize_item(raw: dict) -> dict | None:
    """将原始商品数据标准化"""
    item_id = str(raw.get("itemId", ""))
    if not item_id:
        return None

    # 图片: itemWhiteImg > picUrl > pic_url > img_url
    img = (raw.get("itemWhiteImg") or raw.get("picUrl") or
           raw.get("pic_url") or raw.get("img_url") or "")
    if img.startswith("//"):
        img = "https:" + img

    # 标题
    title = raw.get("shortTitle") or raw.get("title") or raw.get("raw_title") or ""

    # 价格
    price = raw.get("price") or raw.get("view_price") or raw.get("reserve_price") or ""

    # 商品链接
    click_url = raw.get("clickUrl") or raw.get("detail_url") or ""
    if not click_url and item_id:
        click_url = f"https://item.taobao.com/item.htm?id={item_id}"

    # 店铺
    shop_name = raw.get("shopName") or raw.get("nick") or ""

    # 标签
    benefit = raw.get("benefit") or raw.get("tag") or ""

    return {
        "item_id": item_id,
        "title": title,
        "price": str(price),
        "image": img,
        "url": click_url,
        "shop_name": shop_name,
        "benefit": benefit,
    }


def extract_dom_images(html: str, base_url: str) -> list[dict]:
    """从 HTML DOM 的 <img> 标签提取淘宝 CDN 图片 URL"""
    soup = BeautifulSoup(html, "html.parser")
    images = []
    seen = set()

    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-lazy-src") or ""
        if not src:
            continue

        if src.startswith("//"):
            src = "https:" + src
        elif src.startswith("/"):
            src = urljoin(base_url, src)

        if not any(d in src for d in TAOBAO_IMG_DOMAINS):
            continue

        skip = ["icon", "logo", "arrow", "loading", "sprite", "pixel", "1x1", "s.gif"]
        if any(p in src.lower() for p in skip):
            continue

        dedup_key = re.sub(r'_\d+x\d+', '', src).split("?")[0]
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        images.append({
            "src": src,
            "src_hd": normalize_img_url(src),
            "alt": img.get("alt", ""),
        })

    log(f"  DOM图片: 提取到 {len(images)} 张 CDN 图片")
    return images


def normalize_img_url(url: str, size: str = "800x800") -> str:
    if not url:
        return url
    if url.startswith("//"):
        url = "https:" + url
    url = re.sub(r'_\d+x\d+q?\d*(\.\w+)', f'_{size}\\1', url)
    url = re.sub(r'\.webp$', '.jpg', url)
    return url


def extract_page_info(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    shop_name = ""
    for sel in [".shop-name", ".J_ShopName", "[class*='shopName']", ".slogo-shopname"]:
        el = soup.select_one(sel)
        if el:
            shop_name = el.get_text(strip=True)
            break

    meta_desc = ""
    meta = soup.find("meta", attrs={"name": "description"})
    if meta:
        meta_desc = meta.get("content", "")

    return {"title": title, "shop_name": shop_name, "meta_description": meta_desc[:200]}


def detect_anti_scraping(html: str) -> list[str]:
    signals = []
    checks = {
        "unusual traffic": "异常流量检测",
        "punish": "惩罚页面",
        "captcha": "验证码",
        "安全验证": "安全验证弹窗",
        "请完成验证": "验证要求",
        "bixi.alicdn.com": "反爬脚本",
    }
    html_lower = html.lower()
    for pattern, desc in checks.items():
        if pattern.lower() in html_lower:
            signals.append(desc)
    return signals


# ──────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="淘宝页面抓取工具 — 通过 ScraperAPI 获取商品数据和图片",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例:\n"
               "  uv run fetch.py 'https://www.taobao.com'\n"
               "  uv run fetch.py 'https://s.taobao.com/search?q=连衣裙' --max-images 10\n"
               "  uv run fetch.py 'https://www.tmall.com' --json\n"
    )
    parser.add_argument("url", help="淘宝/天猫页面 URL")
    parser.add_argument("--output", "-o", default="/tmp/taobao-fetch",
                        help="输出目录 (默认: /tmp/taobao-fetch)")
    parser.add_argument("--api-key", default=None,
                        help="ScraperAPI Key (也可设置 SCRAPERAPI_KEY 环境变量)")
    parser.add_argument("--no-images", action="store_true",
                        help="不下载商品图片")
    parser.add_argument("--no-screenshot", action="store_true",
                        help="不尝试获取截图（跳过 premium 降级，更快）")
    parser.add_argument("--max-images", type=int, default=20,
                        help="最多下载多少张图片 (默认: 20)")
    parser.add_argument("--image-size", default="800x800",
                        help="图片尺寸 (默认: 800x800)")
    parser.add_argument("--json", action="store_true",
                        help="输出 JSON 格式结果到 stdout")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("SCRAPERAPI_KEY")
    if not api_key:
        print("错误: 请设置 SCRAPERAPI_KEY 环境变量或使用 --api-key 参数")
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "images").mkdir(exist_ok=True)

    log(f"目标: {args.url}")
    log(f"输出: {output_dir}")

    # ── 1. 获取页面 ──
    result = fetch_page(api_key, args.url, screenshot=not args.no_screenshot)

    if result["status_code"] != 200:
        log(f"❌ 请求失败: HTTP {result['status_code']}")
        sys.exit(1)

    # ── 2. 检测反爬 ──
    anti_signals = detect_anti_scraping(result["html"])
    if anti_signals:
        log(f"⚠ 反爬信号: {', '.join(anti_signals)}")

    # ── 3. 页面信息 ──
    page_info = extract_page_info(result["html"])
    log(f"  页面: {page_info['title']}")
    if page_info["shop_name"]:
        log(f"  店铺: {page_info['shop_name']}")

    # ── 4. 保存 HTML ──
    html_path = output_dir / "page.html"
    html_path.write_text(result["html"], encoding="utf-8")

    # ── 5. 下载截图 ──
    screenshot_path = None
    if result["screenshot_url"]:
        screenshot_path = output_dir / "screenshot.png"
        if download_file(result["screenshot_url"], screenshot_path):
            size_kb = screenshot_path.stat().st_size / 1024
            log(f"  截图: {screenshot_path} ({size_kb:.0f} KB)")
        else:
            screenshot_path = None

    # ── 6. 提取商品数据（双通道） ──
    # 通道 A: 嵌入 JSON（免费模式的主要数据源）
    embedded_items = extract_embedded_items(result["html"])

    # 通道 B: DOM 图片（补充，渲染模式下更多）
    dom_images = extract_dom_images(result["html"], result["final_url"])

    # 合并：优先用嵌入 JSON 的商品图（800x800 白底图），DOM 图片作补充
    all_image_urls = []
    for item in embedded_items:
        if item["image"]:
            all_image_urls.append({
                "src": item["image"],
                "src_hd": normalize_img_url(item["image"], args.image_size),
                "alt": item["title"],
                "source": "embedded_json",
                "item_id": item["item_id"],
            })

    embedded_srcs = {img["src"] for img in all_image_urls}
    for img in dom_images:
        if img["src"] not in embedded_srcs:
            all_image_urls.append({
                "src": img["src"],
                "src_hd": img["src_hd"],
                "alt": img["alt"],
                "source": "dom",
                "item_id": "",
            })

    log(f"  合计: {len(all_image_urls)} 张图片 "
        f"({len(embedded_items)} 来自JSON, {len(dom_images)} 来自DOM)")

    # ── 7. 下载图片 ──
    downloaded = []
    if not args.no_images and all_image_urls:
        to_download = all_image_urls[:args.max_images]
        log(f"下载图片: {len(to_download)}/{len(all_image_urls)} 张")

        for i, img in enumerate(to_download):
            url = img["src_hd"] or img["src"]
            ext = ".png" if ".png" in url else ".jpg"
            filename = f"product_{i+1:02d}{ext}"
            img_path = output_dir / "images" / filename

            if download_file(url, img_path):
                size_kb = img_path.stat().st_size / 1024
                downloaded.append({
                    "filename": filename,
                    "src": img["src"],
                    "src_hd": url,
                    "alt": img["alt"],
                    "source": img["source"],
                    "item_id": img.get("item_id", ""),
                    "size_kb": round(size_kb, 1),
                })
                log(f"  [{i+1}/{len(to_download)}] {filename} "
                    f"({size_kb:.0f} KB, {img['source']})")

    # ── 8. 报告 ──
    report = {
        "fetch_result": {
            "url": args.url,
            "final_url": result["final_url"],
            "status": "success",
            "mode": result["mode"],
            "http_status": result["status_code"],
            "elapsed_seconds": result["elapsed"],
            "credits_used": result["credit_cost"],
            "anti_scraping_signals": anti_signals,
            "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "page_info": page_info,
        "screenshot": str(screenshot_path) if screenshot_path else None,
        "items": embedded_items,
        "images": {
            "from_json": len(embedded_items),
            "from_dom": len(dom_images),
            "total": len(all_image_urls),
            "downloaded": len(downloaded),
            "files": downloaded,
        },
        "output_dir": str(output_dir),
    }

    report_path = output_dir / "report.yaml"
    with open(report_path, "w", encoding="utf-8") as f:
        yaml.dump(report, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    # items 单独存一份 JSON 方便下游工具使用
    if embedded_items:
        items_path = output_dir / "items.json"
        with open(items_path, "w", encoding="utf-8") as f:
            json.dump(embedded_items, f, ensure_ascii=False, indent=2)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))

    # ── 9. 汇总 ──
    log("")
    log("=" * 50)
    log("抓取完成")
    log(f"  页面:  {page_info['title']}")
    log(f"  模式:  {result['mode']}")
    log(f"  截图:  {'✅ ' + str(screenshot_path) if screenshot_path else '❌ (需 premium)'}")
    log(f"  商品:  {len(embedded_items)} 个 (嵌入JSON)")
    log(f"  图片:  {len(downloaded)}/{len(all_image_urls)} 张已下载")
    log(f"  反爬:  {'⚠ ' + ', '.join(anti_signals) if anti_signals else '✅ 未触发'}")
    log(f"  消耗:  {result['credit_cost']} credits")
    log(f"  输出:  {output_dir}")
    log("=" * 50)


if __name__ == "__main__":
    main()
