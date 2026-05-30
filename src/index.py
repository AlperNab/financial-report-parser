#!/usr/bin/env python3
"""
financial-report-parser — annual reports, 10-K, earnings releases →
structured JSON with key metrics, ratios, segment data, YoY changes
"""
import anthropic, base64, json, re, sys
from pathlib import Path

SYSTEM = """You are a senior equity research analyst and CFA charterholder.
Extract all financial metrics from this report into structured, comparable JSON.

Rules:
- Standardize all amounts to millions USD (convert from thousands/billions as needed)
- Calculate ratios where underlying data is present
- Flag any restatements, discontinued operations, or one-time items
- Note the fiscal year end date
- Return ONLY valid JSON — no markdown, no explanation.

{
  "company_name": "string",
  "ticker": "string or null",
  "report_type": "annual_report|10-K|10-Q|earnings_release|press_release|other",
  "fiscal_year_end": "YYYY-MM-DD or null",
  "fiscal_year": "FY2024 or null",
  "currency": "USD|GBP|EUR|EGP|...",
  "amounts_in": "millions",
  "income_statement": {
    "revenue": number_or_null,
    "revenue_yoy_pct": number_or_null,
    "gross_profit": number_or_null,
    "gross_margin_pct": number_or_null,
    "operating_income": number_or_null,
    "operating_margin_pct": number_or_null,
    "ebitda": number_or_null,
    "ebitda_margin_pct": number_or_null,
    "net_income": number_or_null,
    "net_margin_pct": number_or_null,
    "eps_basic": number_or_null,
    "eps_diluted": number_or_null,
    "shares_basic": number_or_null,
    "shares_diluted": number_or_null
  },
  "balance_sheet": {
    "cash_and_equivalents": number_or_null,
    "total_current_assets": number_or_null,
    "total_assets": number_or_null,
    "total_current_liabilities": number_or_null,
    "total_debt": number_or_null,
    "net_debt": number_or_null,
    "total_equity": number_or_null,
    "book_value_per_share": number_or_null
  },
  "cash_flow": {
    "operating_cash_flow": number_or_null,
    "capex": number_or_null,
    "free_cash_flow": number_or_null,
    "dividends_paid": number_or_null,
    "buybacks": number_or_null
  },
  "ratios": {
    "current_ratio": number_or_null,
    "quick_ratio": number_or_null,
    "debt_to_equity": number_or_null,
    "debt_to_ebitda": number_or_null,
    "roe_pct": number_or_null,
    "roa_pct": number_or_null,
    "roic_pct": number_or_null,
    "asset_turnover": number_or_null,
    "inventory_days": number_or_null,
    "receivables_days": number_or_null
  },
  "segments": [
    {
      "name": "segment name",
      "revenue": number_or_null,
      "revenue_pct_of_total": number_or_null,
      "operating_income": number_or_null,
      "operating_margin_pct": number_or_null,
      "yoy_growth_pct": number_or_null
    }
  ],
  "guidance": {
    "next_quarter_revenue_low": number_or_null,
    "next_quarter_revenue_high": number_or_null,
    "full_year_revenue_low": number_or_null,
    "full_year_revenue_high": number_or_null,
    "full_year_eps_low": number_or_null,
    "full_year_eps_high": number_or_null
  },
  "notable_items": [
    {
      "type": "restructuring|acquisition|divestiture|restatement|one_time_charge|other",
      "description": "string",
      "amount": number_or_null,
      "impact": "positive|negative|neutral"
    }
  ],
  "management_highlights": ["key quotes or themes from MD&A or earnings call"],
  "risks_mentioned": ["key risks highlighted in the report"],
  "analyst_notes": "brief synthesis of financial health and key metrics",
  "confidence": 0.0
}"""

def parse(source: str) -> dict:
    client = anthropic.Anthropic()
    path = Path(source)

    if path.exists() and source.endswith(".pdf"):
        data = base64.standard_b64encode(path.read_bytes()).decode("ascii")
        content = [
            {"type":"document","source":{"type":"base64","media_type":"application/pdf","data":data}},
            {"type":"text","text":"Extract all financial metrics from this report."}
        ]
    elif path.exists():
        text = path.read_text(encoding="utf-8",errors="replace")[:60000]
        content = [{"type":"text","text":f"Extract financial metrics:\n\n{text}"}]
    else:
        content = [{"type":"text","text":f"Extract financial metrics:\n\n{source[:60000]}"}]

    resp = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=4096, system=SYSTEM,
        messages=[{"role":"user","content":content}]
    )
    raw = re.sub(r'^```(?:json)?\s*','',resp.content[0].text.strip(),flags=re.MULTILINE)
    raw = re.sub(r'\s*```$','',raw,flags=re.MULTILINE)
    return json.loads(raw)

def fmt(v, suffix=""):
    if v is None: return "N/A"
    if isinstance(v, float): return f"{v:,.1f}{suffix}"
    return f"{v:,}{suffix}"

def print_report(r: dict):
    inc = r.get("income_statement",{})
    bal = r.get("balance_sheet",{})
    cf = r.get("cash_flow",{})
    rat = r.get("ratios",{})
    curr = r.get("currency","USD")
    unit = r.get("amounts_in","millions")

    print(f"\n{'═'*60}")
    print(f"  {r.get('company_name','?')} ({r.get('ticker','?')}) — {r.get('fiscal_year','?')}")
    print(f"  {r.get('report_type','?')} | {curr} {unit}")
    print(f"{'═'*60}")

    print(f"\n  INCOME STATEMENT")
    print(f"  Revenue:         {curr}{fmt(inc.get('revenue'))}M", end="")
    if inc.get("revenue_yoy_pct") is not None: print(f"  ({'+' if inc['revenue_yoy_pct']>=0 else ''}{inc['revenue_yoy_pct']:.1f}% YoY)", end="")
    print()
    print(f"  Gross margin:    {fmt(inc.get('gross_margin_pct'),'%')}")
    print(f"  EBITDA:          {curr}{fmt(inc.get('ebitda'))}M  ({fmt(inc.get('ebitda_margin_pct'),'%')} margin)")
    print(f"  Net income:      {curr}{fmt(inc.get('net_income'))}M  ({fmt(inc.get('net_margin_pct'),'%')} margin)")
    print(f"  EPS (diluted):   {fmt(inc.get('eps_diluted'))}")

    print(f"\n  BALANCE SHEET")
    print(f"  Cash:            {curr}{fmt(bal.get('cash_and_equivalents'))}M")
    print(f"  Net debt:        {curr}{fmt(bal.get('net_debt'))}M")
    print(f"  Total equity:    {curr}{fmt(bal.get('total_equity'))}M")

    print(f"\n  CASH FLOW")
    print(f"  Operating CF:    {curr}{fmt(cf.get('operating_cash_flow'))}M")
    print(f"  CapEx:           {curr}{fmt(cf.get('capex'))}M")
    print(f"  Free cash flow:  {curr}{fmt(cf.get('free_cash_flow'))}M")

    print(f"\n  KEY RATIOS")
    print(f"  ROE: {fmt(rat.get('roe_pct'),'%')}  ROIC: {fmt(rat.get('roic_pct'),'%')}  D/EBITDA: {fmt(rat.get('debt_to_ebitda'),'x')}")
    print(f"  Current ratio: {fmt(rat.get('current_ratio'),'x')}  D/E: {fmt(rat.get('debt_to_equity'),'x')}")

    segs = r.get("segments",[])
    if segs:
        print(f"\n  SEGMENTS")
        for s in segs:
            pct = f" ({s.get('revenue_pct_of_total',0):.0f}%)" if s.get("revenue_pct_of_total") else ""
            mgn = f" | {s.get('operating_margin_pct',0):.1f}% margin" if s.get("operating_margin_pct") else ""
            yoy = f" | {'+' if (s.get('yoy_growth_pct',0) or 0)>=0 else ''}{s.get('yoy_growth_pct',0):.1f}% YoY" if s.get("yoy_growth_pct") is not None else ""
            print(f"  {s.get('name','?'):<25} {curr}{fmt(s.get('revenue'))}M{pct}{mgn}{yoy}")

    guidance = r.get("guidance",{})
    if guidance.get("full_year_revenue_low"):
        print(f"\n  GUIDANCE")
        print(f"  FY Revenue: {curr}{fmt(guidance.get('full_year_revenue_low'))}–{fmt(guidance.get('full_year_revenue_high'))}M")
        if guidance.get("full_year_eps_low"):
            print(f"  FY EPS:     {fmt(guidance.get('full_year_eps_low'))}–{fmt(guidance.get('full_year_eps_high'))}")

    notable = r.get("notable_items",[])
    if notable:
        print(f"\n  NOTABLE ITEMS")
        for n in notable:
            amt = f" ({curr}{fmt(n.get('amount'))}M)" if n.get("amount") else ""
            print(f"  • {n.get('type','?').upper()}: {n.get('description','')}{amt}")

    if r.get("analyst_notes"): print(f"\n  Analysis: {r['analyst_notes']}")
    print(f"\n  Confidence: {int(r.get('confidence',0)*100)}%")
    print(f"{'═'*60}\n")

if __name__ == "__main__":
    if len(sys.argv)<2: print("Usage: python -m financial_report_parser <report.pdf|.txt> [--json]"); sys.exit(0)
    r = parse(sys.argv[1])
    if "--json" in sys.argv: print(json.dumps(r,indent=2,ensure_ascii=False))
    else: print_report(r)
