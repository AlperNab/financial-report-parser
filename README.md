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
