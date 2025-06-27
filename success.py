import pathlib, re, time, urllib3, requests, sys
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from tqdm import tqdm  # 進度條

# === 使用者可調整 ===
TARGETS      = [("113080", 113)]          # (考試代碼, 民國年)
FILTER_TYPES = ["Q"]                      # 只抓題本；加 "M" 抓詳解
SAVE_DIR     = pathlib.Path("moex_papers")
TIMEOUT      = 30
SCAN_BYTES   = 64 * 1024
# ====================

BASE = "https://wwwq.moex.gov.tw"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
session = requests.Session()
session.verify = False
session.headers.update({"User-Agent": "Mozilla/5.0 (MoexCrawler/Progress)"})
SAVE_DIR.mkdir(exist_ok=True, parents=True)

# ---------- 工具 ----------
def choose_fname(url, resp=None):
    m = re.search(r"[^/]+\.pdf$", url, re.I)
    if m:
        return m.group(0)
    if resp:
        cd = resp.headers.get("Content-Disposition", "")
        for pat in (r'filename\*=UTF-8\'\'([^\s;]+)', r'filename="?([^";]+)"?'):
            m2 = re.search(pat, cd)
            if m2:
                return m2.group(1)
    q = parse_qs(urlparse(url).query)
    return f"{q.get('code',['x'])[0]}_{q.get('c',[''])[0]}_{q.get('s',[''])[0]}_q{q.get('q',[''])[0]}.pdf"

def header_is_pdf(resp):
    ct = resp.headers.get("Content-Type", "").lower()
    if any(k in ct for k in ("pdf", "octet-stream", "x-download", "force-download")):
        return True
    return ".pdf" in resp.headers.get("Content-Disposition", "").lower()

# ---------- 下載 ----------
def download(url, referer):
    with session.get(url, headers={"Referer": referer}, stream=True, timeout=TIMEOUT) as r:
        r.raise_for_status()

        trusted = header_is_pdf(r)
        buf = b""

        # 若標頭不可信 → 先掃描
        if not trusted:
            for chunk in r.iter_content(4096):
                buf += chunk
                if b"%PDF-" in buf or len(buf) >= SCAN_BYTES:
                    break
            if b"%PDF-" not in buf:
                print("  ⚠  檔案尚未公布，跳過", url)
                return
        else:
            buf = next(r.iter_content(4096))

        fname = choose_fname(url, r)
        path  = SAVE_DIR / fname
        if path.exists():
            print("  ✔ 已存在", fname)
            return

        # --- 進度條設定 ---
        total = int(r.headers.get("Content-Length", 0))
        if total:
            pbar = tqdm(total=total, unit="B", unit_scale=True, desc=fname, leave=False)
        else:
            pbar = tqdm(total=None, desc=fname, leave=False)

        with open(path, "wb") as f:
            f.write(buf)
            pbar.update(len(buf))
            for chunk in r.iter_content(4096):
                f.write(chunk)
                pbar.update(len(chunk))
        pbar.close()
        print("  ✔ 下載完成", fname)

# ---------- 主流程 ----------
def crawl(exam_code, roc_year):
    referer = f"{BASE}/exam/wFrmExamQandASearch.aspx?e={exam_code}&y={roc_year}"
    soup = BeautifulSoup(session.get(referer, timeout=TIMEOUT).text, "html.parser")

    links = set()
    for a in soup.select("a[href*='wHandExamQandA_File.ashx']"):
        href = a["href"]
        if not any(f"t={t}" in href for t in FILTER_TYPES):
            continue
        if href.startswith("wHandExam"):     # 補 /exam/
            href = "/exam/" + href
        links.add(urljoin(BASE, href))

    print(f"{roc_year} 年 {exam_code} → 偵測 {len(links)} 條連結")
    for link in sorted(links):
        try:
            download(link, referer)
        except Exception as e:
            print("  × 失敗", link, e)

# ---------- 執行 ----------
if __name__ == "__main__":
    for code, yr in TARGETS:
        crawl(code, yr)
    print("全部下載完成 →", SAVE_DIR.resolve())






