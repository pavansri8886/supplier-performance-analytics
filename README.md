# Supplier Performance Analytics

Built this as part of my MSc in Data Management and AI at ECE Paris (2025–2026).

Procurement and logistics teams at global FMCG companies review supplier performance every quarter, but most of those reviews happen on static spreadsheets that show where a supplier stands today — not where they are heading. A supplier scoring 88% on-time looks fine until you realise they were at 97% six months ago and are dropping fast. That is the gap this project addresses.

---

## What it does

Analyses 4,054 orders across 25 European logistics suppliers over 12 months, covering 7 origin countries and 7 destination markets. The analysis goes beyond a flat scorecard — it tracks trend direction, flags suppliers whose performance is deteriorating before it becomes a crisis, and surfaces the specific delivery lanes and product categories where risk is concentrating.

**What the dashboard shows:**

- Weighted performance scorecard: on-time delivery (40%), quality pass rate (35%), invoice accuracy (25%)
- 6-month trend analysis — H1 vs H2 delta showing which suppliers are improving or declining
- Seasonal pattern analysis — Q4 stress period clearly visible in October/November data
- Lane performance heatmap — origin country to destination market on-time rates
- Category comparison — Dry Goods vs Chilled vs Frozen (cold chain shows higher breach rates)
- Risk flags — automated detection of suppliers with multiple simultaneous warning signals
- Strategic recommendations — immediate actions, monitor closely, expand partnership

---

## Key findings from the data

**Q4 stress is real and measurable.** On-time rates drop from ~89% in September to 81.5% in October — a 7.5 percentage point drop that directly correlates with peak season volume pressure. Procurement teams should pre-negotiate buffer stock or dual-sourcing agreements before October.

**Trend matters more than snapshot.** Planzer Transport AG scores 97.2 overall but is dropping 7.4 percentage points over 6 months — flagged HIGH RISK despite being the top scorer. A static scorecard would miss this entirely.

**Cold chain suppliers carry disproportionate risk.** Bayern Transport and Bakker Logistiek both show temperature breach rates above 7% alongside declining on-time performance. In a food or pharmaceutical supply chain, this combination triggers immediate escalation.

---

## Dataset

25 real-named European logistics suppliers with country-appropriate companies — Geodis, Rhenus, Bolloré, Katoen Natie, Planzer, Raben Group and others. 4,054 orders generated with realistic reliability trends including deliberate deterioration patterns to simulate real procurement scenarios.

| Metric | Value |
|---|---|
| Total orders | 4,054 |
| Suppliers | 25 |
| Origin countries | 7 |
| Destination markets | 7 |
| Period | 12 months (Jan–Dec 2024) |
| Overall on-time rate | 86.8% |
| High risk suppliers identified | 11 |
| Preferred partners | 10 |

---

## Stack

Python · pandas · NumPy · Plotly (dashboard) · HTML

---

## How to run

```bash
pip install pandas numpy
python3 generate_data.py
python3 analysis.py
```

Open `output/supplier_dashboard.html` in your browser.

---

## What I would build next

The natural extension is connecting this to actual purchase order data from an ERP system and running the trend detection automatically on a weekly schedule. The risk flag logic is already parameterised — in production you would trigger a Jira ticket or email alert when a supplier crosses a risk threshold rather than waiting for the quarterly review.

---

**Pavan Kumar Naganaboina**
MSc Data Management & AI — ECE Paris 2025–2026
[linkedin.com/in/pavankumarn01](https://linkedin.com/in/pavankumarn01) · [github.com/pavansri8886](https://github.com/pavansri8886)
