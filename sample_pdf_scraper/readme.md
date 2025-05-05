# TWSE PDF Scraper

This Python tool allows you to automatically download company disclosure PDFs from the [Taiwan Stock Exchange (TWSE) Document Center](https://mops.twse.com.tw/mops/#/web/t57sb01_q1) (財務報告書). It uses **Selenium** to handle JavaScript-based navigation and **requests** to download PDF files efficiently.

## Requirements

* Python 3.7+
* Google Chrome browser installed
* ChromeDriver (version must match your Chrome browser)

## Dependencies

Install required Python packages with:

```bash
pip install -r requirements.txt
```

Or manually install:

```bash
pip install selenium requests
```

You must also have **ChromeDriver** installed and available in your system path.

> You can download ChromeDriver from: [https://sites.google.com/chromium.org/driver/](https://sites.google.com/chromium.org/driver/)


## Setup

1. Clone this repository or download the script.
2. Make sure `chromedriver` is installed and your Chrome browser is up to date.
3. Install the dependencies listed above.


## Usage

```bash
python twse_pdf_scraper.py --co_id <COMPANY_ID> --year <ROC_YEAR>
```

### Example

```bash
python twse_pdf_scraper.py --co_id 1101 --year 110
```

This will:

* Scrape all disclosures for **company ID `1101`** (e.g., 台泥)
* From **ROC year 110** (i.e., **2021**)
* Save all PDFs to the default `./pdfs` folder


### Optional Flags

| Flag            | Description                             | Default     |
| --------------- | --------------------------------------- | ----------- |
| `--output`      | Output directory for downloaded PDFs    | `./pdfs`    |
| `--no-headless` | Show the browser window (for debugging) | headless on |

### Example (custom folder, visible browser):

```bash
python twse_pdf_scraper.py --co_id 2330 --year 111 --output tsmc_2022 --no-headless
```


## Output

All downloaded PDF files will be saved to the specified folder (default: `./pdfs/`). Each file is named based on the TWSE naming convention (e.g., `202101_1101_AI1_20250505_160800.pdf`).


## Notes

* This script navigates **popup windows** opened by TWSE using `window.open()`. It will automatically switch windows and return after each PDF download.
* Please avoid making requests too fast; rate-limiting is handled by built-in delays.


## Author

Built by James Tu – feel free to adapt, extend, or contribute.
