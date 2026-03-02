#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
从 URL 列表下载商品图片（绕过 CDN 防盗链）

用法:
    # 从命令行参数下载
    uv run download_images.py -o /tmp/store-teardown/images \
        "https://img.alicdn.com/xxx/1.jpg" \
        "https://img.alicdn.com/xxx/2.jpg"

    # 从文件读取 URL 列表（每行一个 URL）
    uv run download_images.py -o /tmp/store-teardown/images -f urls.txt

    # 从 maishou CSV 输出提取 picUrl 并下载
    uv run download_images.py -o /tmp/store-teardown/images --csv maishou_output.csv

关键技巧: 必须设置 Accept header 为 image/* 格式，否则 alicdn.com 会返回 1x1 GIF。
"""

import argparse
import csv
import os
import sys
import urllib.request
from pathlib import Path


BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://www.taobao.com/",
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def download_image(url: str, output_path: Path, timeout: int = 15) -> bool:
    """下载单张图片，返回是否成功"""
    try:
        req = urllib.request.Request(url, headers=BROWSER_HEADERS)
        resp = urllib.request.urlopen(req, timeout=timeout)
        data = resp.read()

        # 检查是否为 1x1 GIF（防盗链占位图）
        if len(data) < 200:
            print(f"  SKIP {output_path.name}: 防盗链拦截 ({len(data)} bytes)", flush=True)
            return False

        with open(output_path, "wb") as f:
            f.write(data)

        ct = resp.headers.get_content_type() or "unknown"
        print(f"  OK   {output_path.name}: {len(data):,} bytes ({ct})", flush=True)
        return True
    except Exception as e:
        print(f"  FAIL {output_path.name}: {e}", flush=True)
        return False


def main():
    parser = argparse.ArgumentParser(description="下载商品图片（绕过 CDN 防盗链）")
    parser.add_argument("urls", nargs="*", help="图片 URL 列表")
    parser.add_argument("-o", "--output", default="/tmp/store-teardown/images",
                        help="输出目录")
    parser.add_argument("-f", "--file", help="从文件读取 URL（每行一个）")
    parser.add_argument("--csv", dest="csv_file", help="从 maishou CSV 提取 picUrl")
    parser.add_argument("--max", type=int, default=15, help="最多下载几张（默认 15）")
    args = parser.parse_args()

    # 收集所有 URL
    urls = list(args.urls)

    if args.file:
        with open(args.file) as f:
            for line in f:
                line = line.strip()
                if line and line.startswith("http"):
                    urls.append(line)

    if args.csv_file:
        with open(args.csv_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                pic_url = row.get("picUrl", "").strip()
                if pic_url and pic_url.startswith("http"):
                    urls.append(pic_url)

    if not urls:
        # 也尝试从 stdin 读取
        if not sys.stdin.isatty():
            for line in sys.stdin:
                line = line.strip()
                if line.startswith("http"):
                    urls.append(line)

    if not urls:
        print("错误: 没有提供图片 URL。用 --help 查看用法。")
        sys.exit(1)

    urls = urls[:args.max]
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[download] 下载 {len(urls)} 张图片到 {output_dir}")
    ok = 0
    for i, url in enumerate(urls):
        # 根据 URL 猜测扩展名
        ext = ".jpg"
        if ".png" in url:
            ext = ".png"
        elif ".webp" in url:
            ext = ".webp"

        filename = f"product_{i+1:02d}{ext}"
        path = output_dir / filename

        if download_image(url, path):
            ok += 1

    print(f"[download] 完成: {ok}/{len(urls)} 张下载成功")


if __name__ == "__main__":
    main()
