import pathlib, re, time, urllib.parse, requests, tqdm, hashlib
from urllib.parse import urlencode, urljoin, urlparse
from bs4 import BeautifulSoup

BASE_URL  = "https://miele.kenk.com.tw"
API_PATH  = "/download-list-load"
PARAMS    = {"GroupSEO": "", "Source": "", "SEO": "manual",
             "SubcategorySEO": "", "SortBy": "", "Sort": ""}  # loadPage 另填
SAVE_DIR  = pathlib.Path("miele_manuals")
TIMEOUT   = 15
SLEEP     = 0.3
HEADERS   = {
    "User-Agent": "Mozilla/5.0 (MieleCrawler/2025-06-26)",
    "Referer": f"{BASE_URL}/download/manual",
    "X-Requested-With": "XMLHttpRequest",
}

# --- 正則 ---
UUID_RE = re.compile(
    r"[/]?file-(?:preview|download)/download/"
    r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"
)

# --- 組 URL 下載 ---
def try_download(uuid: str, session: requests.Session, retries=3) -> bool:
    for prefix in ("file-download", "file-preview"):
        url = f"{BASE_URL}/{prefix}/download/{uuid}"   # 直接加「/」
        ...


def fetch_page(session: requests.Session, page: int, retries=3) -> str:
    params = PARAMS | {"loadPage": page}
    url    = f"{BASE_URL}{API_PATH}?{urlencode(params)}"
    for i in range(retries):
        try:
            r = session.get(url, timeout=TIMEOUT)
            r.raise_for_status()
            return r.text
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(1)
    return ""

def collect_uuids() -> set[str]:
    uuids, page, last_hash = set(), 1, None
    with requests.Session() as s:
        s.headers.update(HEADERS)
        while True:
            html = fetch_page(s, page)
            if not html.strip():
                break
            h = hashlib.md5(html.encode()).hexdigest()
            if h == last_hash:          # 內容重複 -> 結束
                break
            last_hash = h
            found = {m.group(1) for m in UUID_RE.finditer(html)}
            print(f"page {page:<2d}: 抓到 {len(found):3d} 筆")
            uuids |= found
            page  += 1
            time.sleep(SLEEP)
    return uuids

def filename_from_cd(cd: str, fallback: str) -> str:
    m = re.search(r'filename="?([^";]+)"?', cd or "")
    return urllib.parse.unquote(m.group(1)) if m else fallback + ".pdf"

def try_download(uuid: str, session: requests.Session, retries=3) -> bool:
    for prefix in ("file-download", "file-preview"):
        url = f"{BASE_URL}/{prefix}/download/{uuid}"
        for _ in range(retries):
            try:
                with session.get(url, stream=True, timeout=TIMEOUT) as r:
                    if r.status_code != 200:
                        raise Exception(f"HTTP {r.status_code}")
                    r.raw.decode_content = True
                    head = r.raw.read(8192)
                    if b"%PDF-" not in head[:8]:
                        raise Exception("Not PDF")
                    fname = filename_from_cd(r.headers.get("Content-Disposition"),
                                             f"{uuid}.pdf")
                    path  = SAVE_DIR / fname
                    if path.exists():
                        print(f"✓ 已存在 {fname}")
                        return True
                    total = int(r.headers.get("Content-Length", 0))
                    bar   = tqdm.tqdm(total=total or None, unit="B", unit_scale=True,
                                      desc=fname[:30], leave=False)
                    with open(path, "wb") as f:
                        f.write(head); bar.update(len(head))
                        for chunk in r.iter_content(4096):
                            f.write(chunk); bar.update(len(chunk))
                    bar.close()
                    print(f"✔ 下載完成 {fname}")
                    return True
            except Exception as e:
                time.sleep(1)
                continue
    print(f"× 無法取得 {uuid}")
    return False

def main():
    SAVE_DIR.mkdir(exist_ok=True, parents=True)
    uuids = collect_uuids()
    print(f"\n總計偵測 {len(uuids)} 份說明書\n")

    sess = requests.Session(); sess.headers.update(HEADERS)
    ok = sum(try_download(uid, sess) for uid in sorted(uuids))
    print(f"\n完成！成功 {ok} 份，失敗 {len(uuids)-ok} 份")
    print("PDF 位置：", SAVE_DIR.resolve())
    
if __name__ == "__main__":
    main()






