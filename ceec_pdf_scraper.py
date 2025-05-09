#!/usr/bin/env python3
# coding: utf-8
"""
Download all PDF files from a given CEEC 'xmfile' listing (by xsmsid).
Example:
    # 歷屆學測試題：--xsmsid 0J052424829869345634
    # 歷屆分科試題：--xsmsid 0J052427633128416650
    
    # 只抓第 1 頁
    python ceec_pdf_scraper.py --xsmsid 0J052427633128416650

    # 抓第 1~3 頁
    python ceec_pdf_scraper.py --xsmsid 0J052427633128416650 --pages 1-3

    # 把整個列表 24 頁全掃（會自動停在空頁）
    python ceec_pdf_scraper.py --xsmsid 0J052427633128416650 --pages all --output ceec_pdfs

    # 把 delay 調長一點，避免太快
    python ceec_pdf_scraper.py --xsmsid 0J052427633128416650 --pages all --delay 1.5
"""
import os
import re
import sys
import time
import argparse
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from typing import Optional
from pathlib import Path

BASE_URL = "https://www.ceec.edu.tw"

def iter_page_numbers(pages_arg: Optional[str]):
    """
    Yield page numbers according to --pages 參數。
    - None  → 預設只抓第 1 頁
    - 'all' → 自動掃到沒有 PDF 為止
    - '5'   → 只抓第 5 頁
    - '2-7' → 抓 2,3,4,5,6,7
    """
    if pages_arg is None:
        yield 1
        return

    pages_arg = pages_arg.lower()
    if pages_arg == "all":
        n = 1
        while True:
            yield n
            n += 1
    elif "-" in pages_arg:
        start, end = [int(x) for x in pages_arg.split("-", 1)]
        for n in range(start, end + 1):
            yield n
    else:
        yield int(pages_arg)

def download_ceec_pdfs(
    xsmsid: str,
    pages: str | None = None,
    output_dir: str = "pdfs",
    delay: float = 0.8,
):
    os.makedirs(output_dir, exist_ok=True)
    print("▶ 腳本位置      :", Path(__file__).resolve())
    print("▶ 目前工作目錄  :", Path.cwd())
    print("▶ 實際輸出資料夾:", Path(output_dir).resolve())
    session = requests.Session()
    session.headers.update(
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )

    pdf_seen = set()
    total = 0

    for page_no in iter_page_numbers(pages):
        list_url = f"{BASE_URL}/xmfile?page={page_no}&xsmsid={xsmsid}"
        print(f"[Page {page_no}] 解析 {list_url} ...", flush=True)

        resp = session.get(list_url, timeout=15)
        if resp.status_code != 200:
            print(f"  ⚠️  HTTP {resp.status_code}，跳出迴圈")
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        anchors = soup.find_all("a", href=re.compile(r"\.pdf$"))

        # 若這一頁沒有任何 PDF，視為爬完
        if not anchors:
            if pages is None or pages.lower() == "all":
                print("  （偵測不到 PDF，結束）")
            break

        for a in anchors:
            if not ("試題內容" in a.text or "非選擇題評分原則" in a.text):
                continue
            href = a["href"]
            pdf_url = href if bool(urlparse(href).netloc) else urljoin(BASE_URL, href)
            if pdf_url in pdf_seen:
                continue  # 有些頁面會重複列相同檔案
            pdf_seen.add(pdf_url)

            filename = os.path.basename(urlparse(pdf_url).path)
            filepath = os.path.join(output_dir, filename)

            print(f"    ↳ 下載 {filename} ...", end=" ", flush=True)
            try:
                r = session.get(pdf_url, timeout=30)
                r.raise_for_status()
                with open(filepath, "wb") as f:
                    f.write(r.content)
                total += 1
                print("OK")
            except Exception as e:
                print(f"失敗：{e}")

        # 若使用 --pages all，就禮貌性睡一下別把伺服器打爆
        time.sleep(delay)

    print(f"\n✅ 共下載 {total} 個 PDF，存到「{output_dir}」資料夾。")


def main():
    parser = argparse.ArgumentParser(
        description="Download CEEC xmfile PDFs by xsmsid."
    )
    parser.add_argument("--xsmsid", required=True, help="e.g. 0J052427633128416650")
    parser.add_argument(
        "--pages",
        default=None,
        help="想抓的頁碼：如 5、2-7、all；若省略則只抓第 1 頁"
    )
    parser.add_argument(
        "--output",
        default="pdfs",
        help="下載目的資料夾（預設 pdfs）"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.8,
        help="連續抓多頁時的間隔秒數（預設 0.8s）"
    )
    args = parser.parse_args()

    try:
        download_ceec_pdfs(
            xsmsid=args.xsmsid,
            pages=args.pages,
            output_dir=args.output,
            delay=args.delay,
        )
    except KeyboardInterrupt:
        sys.exit("\n中斷。")


if __name__ == "__main__":
    main()
