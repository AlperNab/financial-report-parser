# Financial Report Parser

This folder has been upgraded into a **standalone real GUI project**.

Run the project GUI:

```bash
./run_gui.sh
```

Windows:

```powershell
.\run_gui_windows.ps1
```

Default local URL: `http://127.0.0.1:9122`

This project includes its own FastAPI backend, browser GUI, provider settings, local/cloud LLM routing, encrypted API-key storage, file uploads, job history, exports, and a project-specific plugin configuration.

See `PROJECT_IMPLEMENTATION.md` and `project_config.json` for the applied project-specific features and customization controls.

---

## Original README

# financial-report-parser

> **Annual reports, 10-K, earnings releases → structured financial JSON.** Revenue, margins, EPS, balance sheet, cash flows, segment data, ratios, guidance — all normalized and comparable.

[![PyPI](https://img.shields.io/pypi/v/financial-report-parser?style=flat)](https://pypi.org/project/financial-report-parser/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Quickstart

```bash
pip install financial-report-parser
python -m financial_report_parser apple_10k.pdf
python -m financial_report_parser earnings_release.txt --json
```

## Extracted fields

**Income statement** — Revenue (+ YoY%), Gross/EBIT/EBITDA/Net margins, EPS basic + diluted

**Balance sheet** — Cash, Net debt, Total equity, Book value per share

**Cash flow** — Operating CF, CapEx, Free cash flow, Buybacks, Dividends

**Ratios** — ROE, ROIC, ROA, D/E, D/EBITDA, Current ratio, Asset turnover, DSO

**Segments** — Revenue, margin, YoY growth per segment

**Guidance** — Revenue and EPS range for next quarter and full year

## License
MIT © [Alper Nabil Gabra Zakher](https://github.com/AlperNab)
