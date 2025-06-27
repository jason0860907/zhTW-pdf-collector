# zhTW-pdf-collector (台灣公開資訊 PDF 下載)

本專案包含一系列 Python 腳本，用於從台灣相關的公開資訊網站下載 PDF 文件。

## 專案設定與執行

本專案使用 [uv](https://github.com/astral-sh/uv) 作為套件管理及虛擬環境工具。

### 1. 安裝 uv

如果您尚未安裝 `uv`，請參考其官方文件進行安裝。例如，透過 pipx (建議方式) 或 pip：

### 2. 設定虛擬環境並安裝依賴

- **建立虛擬環境**:
   在專案根目錄執行以下指令以建立虛擬環境。此處指定使用 Python 3.12，您可以根據您的環境調整版本。

   ```bash
   uv venv -p 3.12 --seed
   source .venv/bin/activate
   uv sync
   ```
   這會在專案根目錄建立一個名為 `.venv` 的虛擬環境資料夾，並安裝對應套件，需注意 Windows 進入虛擬環境的方式不一樣。

完成以上步驟後，您就可以執行專案中的腳本了。

## 工具列表

1.  **CEEC PDF Scraper (`scrapers/ceec_pdf_scraper.py`)**: 從大考中心（CEEC）網站下載歷屆試題等 PDF 文件。
2.  **TWSE PDF Scraper (`scrapers/twse_pdf_scraper.py`)**: 從台灣證券交易所（TWSE）公開資訊觀測站下載公司財報等 PDF 文件。
3.  **MOEX PDF Scraper (`scrapers/moex_pdf_scraper.py`)**: 從台灣考選部（MOEX）下載歷屆試題 PDF。

---

## 1. CEEC PDF Scraper

從大考中心（CEEC）的 `xmfile` 列表頁面下載 PDF 檔案。

### 使用方法

```bash
python scrapers/ceec_pdf_scraper.py --xsmsid <XSMSID> [OPTIONS]
```

### 主要參數

*   `--xsmsid <XSMSID>`: **(必要)** CEEC 網站列表的 ID。
    *   例如：歷屆學測試題 `0J052424829869345634`
    *   例如：歷屆分科試題 `0J052427633128416650`
*   `--pages <PAGES>`: 想抓取的頁碼。
    *   省略此參數：預設只抓取第 1 頁。
    *   `all`: 自動掃描所有頁面，直到沒有新的 PDF 為止。
    *   `5`: 只抓取第 5 頁。
    *   `2-7`: 抓取第 2 到第 7 頁。
*   `--output <DIRECTORY>`: 下載 PDF 的目的資料夾。 (預設: `pdfs`)
*   `--delay <SECONDS>`: 連續抓取多頁時的間隔秒數。 (預設: `0.8`)

### 範例

*   **抓取指定 `xsmsid` 列表的第一頁：**
    ```bash
    python scrapers/ceec_pdf_scraper.py --xsmsid 0J052427633128416650
    ```

*   **抓取指定 `xsmsid` 列表的第 1 到 3 頁：**
    ```bash
    python scrapers/ceec_pdf_scraper.py --xsmsid 0J052427633128416650 --pages 1-3
    ```

*   **抓取指定 `xsmsid` 列表的所有頁面，並儲存到 `ceec_exam_pdfs` 資料夾：**
    ```bash
    python scrapers/ceec_pdf_scraper.py --xsmsid 0J052427633128416650 --pages all --output ceec_exam_pdfs
    ```

*   **調整請求間隔為 1.5 秒：**
    ```bash
    python scrapers/ceec_pdf_scraper.py --xsmsid 0J052427633128416650 --pages all --delay 1.5
    ```

---

## 2. TWSE PDF Scraper

此 Python 工具讓您能自動從[台灣證券交易所公開資訊觀測站](https://mops.twse.com.tw/mops/#/web/t57sb01_q1)（財務報告書）下載公司揭露的 PDF 文件。它使用 **Selenium** 處理基於 JavaScript 的導航，並使用 **requests** 高效下載 PDF 檔案。

### 環境需求 (TWSE Scraper 特定)

*   Python 3.7+ (專案整體建議使用 `pyproject.toml` 中指定的版本，例如 3.12)
*   已安裝 Google Chrome 瀏覽器
*   ChromeDriver (版本必須與您的 Chrome 瀏覽器匹配)

您同時必須已安裝 **ChromeDriver** 並將其設定在系統路徑中。

> 您可以從此處下載 ChromeDriver: [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads) (請注意，自 Chrome 115 版起，ChromeDriver 的發布已整合至 Chrome 本身的發布流程中，請參考 [Chrome for Testing availability dashboard](https://googlechromelabs.github.io/chrome-for-testing/))

### 設定 (TWSE Scraper 特定)

1.  確保 `chromedriver` 已安裝且您的 Chrome 瀏覽器為最新版本。
2.  (依賴套件已透過上述 `uv pip sync` 統一安裝)

### 使用方法

```bash
python scrapers/twse_pdf_scraper.py --co_id <公司代號> --year <民國年份> [OPTIONS]
```

### 範例

```bash
python scrapers/twse_pdf_scraper.py --co_id 1101 --year 110
```

此指令將會：

*   抓取**公司代號 `1101`** (例如：台泥)
*   於**民國 `110` 年** (即西元 2021 年)
*   所有的公開揭露 PDF 文件，並儲存至預設的 `./pdfs` 資料夾

### 可選參數

| 參數            | 描述                                  | 預設值      |
| --------------- | ------------------------------------- | ----------- |
| `--output`      | 下載 PDF 的輸出資料夾                 | `./pdfs`    |
| `--no-headless` | 顯示瀏覽器視窗 (用於偵錯)             | headless 模式開啟 |

### 範例 (自訂資料夾，顯示瀏覽器)：

```bash
python scrapers/twse_pdf_scraper.py --co_id 2330 --year 111 --output tsmc_2022 --no-headless
```

### 輸出

所有下載的 PDF 檔案將儲存於指定的資料夾 (預設: `./pdfs/`)。每個檔案將根據證交所的命名慣例命名 (例如: `202101_1101_AI1_20250505_160800.pdf`)。

### 注意事項

*   此腳本會處理證交所網站透過 `window.open()` 開啟的**彈出視窗**。它會在每次下載 PDF 後自動切換視窗並返回。
*   請避免過快發送請求；腳本內建的延遲有助於控制請求頻率。

---

## 3. MOEX PDF Scraper

此工具可自動從[台灣考選部（MOEX）](https://wwwq.moex.gov.tw)下載歷屆試題 PDF 檔案。

### 使用方法

```bash
python scrapers/moex_pdf_scraper.py --exam <考試代碼> --year <民國年> [OPTIONS]
```

### 主要參數

*   `--exam <考試代碼>`: **(必要)** 考試代碼，可多個。
    *   例如：`113080`、`113060`
*   `--year <民國年>`: **(必要)** 民國年（如 113）。
*   `--type <檔案類型>`: 指定要下載的檔案類型，可多個。
    *   `Q`: 題本（預設）
    *   `M`: 詳解
    *   範例：`--type Q M` 只抓題本與詳解
*   `--output <資料夾名稱>`: 輸出資料夾名稱（預設 `moex_papers`）。

### 範例

*   **下載 113 年 113080 考試的題本：**
    ```bash
    python scrapers/moex_pdf_scraper.py --exam 113080 --year 113
    ```

*   **下載多個考試代碼：**
    ```bash
    python scrapers/moex_pdf_scraper.py --exam 113080 113060 --year 113
    ```

*   **只抓題本與詳解：**
    ```bash
    python scrapers/moex_pdf_scraper.py --exam 113080 --year 113 --type Q M
    ```

*   **指定輸出資料夾：**
    ```bash
    python scrapers/moex_pdf_scraper.py --exam 113080 --year 113 --output my_moex_pdfs
    ```

### 輸出

所有下載的 PDF 檔案將儲存於指定的資料夾（預設：`./pdfs/moex_papers/`）。如檔案已存在則自動跳過。

### 注意事項

*   若檔案尚未公布，腳本會自動跳過該檔案。
*   支援多考試代碼與多檔案類型同時下載。
*   下載時會顯示進度條。