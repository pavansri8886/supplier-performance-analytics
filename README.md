# 📦 Supplier Performance Analytics

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat&logo=python)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-green?style=flat&logo=pandas)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-purple?style=flat)
![Domain](https://img.shields.io/badge/Domain-FMCG%20Logistics-orange?style=flat)
![Suppliers](https://img.shields.io/badge/Suppliers-25-blue?style=flat)
![Orders](https://img.shields.io/badge/Orders%20Analysed-4%2C054-red?style=flat)

> **12-month European logistics supplier scorecard — 25 suppliers · 7 origin countries · 7 destination markets · 4,054 orders · trend analysis · risk flagging · lane performance**

---

## 🧠 The Problem This Solves

Procurement and logistics teams at global FMCG companies review supplier performance every quarter. Most of those reviews happen on static spreadsheets that show where a supplier stands **today** — not where they are **heading**.

A supplier scoring 88% on-time looks fine until you realise they were at 97% six months ago and dropping fast. That is the gap this project addresses.

---

## 📊 Results at a Glance

| Metric | Value |
|---|---|
| 📦 Total orders analysed | 4,054 |
| 🏭 Suppliers tracked | 25 |
| 🌍 Origin countries | 7 |
| 🚚 Destination markets | 7 |
| 📅 Period covered | Jan – Dec 2024 |
| ✅ Overall on-time rate | 86.8% |
| ⭐ Preferred partners identified | 10 |
| 🔴 High risk suppliers flagged | 11 |

---

## 🔍 Key Findings

### 📉 Finding 1 — Q4 Stress is Real and Measurable
On-time rates drop from ~89% in September to **81.5% in October** — a 7.5 percentage point collapse that maps directly to peak season volume pressure. Procurement teams should pre-negotiate buffer stock or dual-sourcing agreements **before October**.

### 📈 Finding 2 — Trend Matters More Than Snapshot
**Planzer Transport AG** scores 97.2 overall — the highest in the dataset. But they are dropping **7.4 percentage points over 6 months** and are flagged HIGH RISK. A static scorecard would miss this entirely. Trend direction is the signal that actually drives decisions.

### ❄️ Finding 3 — Cold Chain Carries Disproportionate Risk
**Bayern Transport** and **Bakker Logistiek** both show temperature breach rates above 7% alongside declining on-time performance. In a food or pharmaceutical supply chain, this combination triggers immediate escalation — not a quarterly review note.

---

## 🏗️ Architecture

```
generate_data.py
  ├── 25 named European suppliers with realistic SLA contracts
  ├── 4,054 orders with delivery, quality and invoice outcomes
  ├── Individual reliability trends per supplier (improving / stable / deteriorating)
  └── Q4 seasonality stress built into the simulation
          │
          ▼
analysis.py
  ├── Overall scorecard (on-time · quality · invoice accuracy)
  ├── 6-month trend analysis (H1 vs H2 delta per supplier)
  ├── Risk flag detection (multi-signal automated alerting)
  ├── Lane heatmap (origin country → destination market)
  ├── Seasonality analysis (monthly pattern across 12 months)
  └── Category breakdown (Dry Goods · Chilled · Frozen)
          │
          ▼
output/
  ├── supplier_scorecard.csv       → Procurement team
  ├── monthly_trends.csv           → Performance tracking
  ├── lane_analysis.csv            → Logistics planning
  ├── seasonality.csv              → Capacity planning
  ├── category_performance.csv     → Category management
  └── supplier_dashboard.html      → Management review
```

---

## 📐 Scoring Methodology

| Metric | Weight | Rationale |
|---|---|---|
| On-time delivery rate | **40%** | Direct impact on production and shelf availability |
| Quality pass rate | **35%** | Core compliance — defects trigger costly returns |
| Invoice accuracy | **25%** | AP overhead and dispute management cost |

**Tier classification:**

| Score | Tier |
|---|---|
| 90 – 100 | ⭐ Preferred Partner |
| 82 – 89 | 🟢 Performing |
| 75 – 81 | 🟡 Needs Improvement |
| < 75 | ⚠️ At Risk |

---

## 🚩 Risk Flag Logic

A supplier is flagged **HIGH RISK** if any of the following are detected:

- 📉 Performance trend dropping more than 5pp over 6 months
- ⏱️ On-time rate below 80%
- ❌ Quality pass rate below 85%
- 🌡️ Temperature breach rate above 5% (cold chain only)
- ⏳ Average delay exceeding 4 days over contracted SLA

Multiple flags on a single supplier trigger immediate escalation recommendation.

---

## 🌍 Supplier Dataset

Real-named European logistics companies across 7 countries:

| Country | Suppliers | Example |
|---|---|---|
| 🇩🇪 Germany | 4 | Müller Logistik, Rhenus Supply Chain |
| 🇫🇷 France | 4 | Geodis France, Bolloré Logistics |
| 🇳🇱 Netherlands | 3 | Vos Logistics, Bakker Logistiek |
| 🇪🇸 Spain | 3 | Grupo Logista, Transportes Ochoa |
| 🇮🇹 Italy | 3 | BRT Corriere Espresso, Fercam |
| 🇵🇱 Poland | 3 | ROHLIG SUUS, Raben Group |
| 🇧🇪 Belgium | 2 | Katoen Natie, Eurilogistic |
| 🇬🇧 UK | 2 | Wincanton, Culina Group |
| 🇨🇭 Switzerland | 1 | Planzer Transport |

---

## 📂 Project Structure

```
supplier-performance-analytics/
│
├── 📁 data/
│   ├── suppliers.csv          # 25 supplier master records with SLA contracts
│   └── orders.csv             # 4,054 orders with full delivery and quality data
│
├── 📁 output/
│   ├── supplier_scorecard.csv
│   ├── monthly_trends.csv
│   ├── lane_analysis.csv
│   ├── seasonality.csv
│   ├── category_performance.csv
│   └── supplier_dashboard.html   ← open this
│
├── generate_data.py           # Realistic data generation with trend simulation
├── analysis.py                # Scorecard, trends, risk flags, dashboard
└── README.md
```

---

## 🚀 How to Run

```bash
pip install pandas numpy
python3 generate_data.py
python3 analysis.py
```

Then open `output/supplier_dashboard.html` in your browser.

---

## 🔭 What I Would Build Next

The natural extension is connecting this to actual purchase order data from an ERP system (SAP, Oracle) and running the trend detection automatically on a weekly schedule. The risk flag logic is already parameterised — in production you would trigger a Jira ticket or Slack alert when a supplier crosses a threshold rather than waiting for the quarterly review.

A **Separation of Duties check** across invoice approval and delivery confirmation would be the next governance layer — ensuring the same person cannot approve both the delivery and the payment for high-value orders.

---

## 👤 Author

**Pavan Kumar Naganaboina**
MSc Data Management & AI — ECE Paris 2025–2026

[![LinkedIn](https://img.shields.io/badge/LinkedIn-pavankumarn01-blue?style=flat&logo=linkedin)](https://linkedin.com/in/pavankumarn01)
[![GitHub](https://img.shields.io/badge/GitHub-pavansri8886-black?style=flat&logo=github)](https://github.com/pavansri8886)

---

> *Built to demonstrate end-to-end logistics analytics — from raw order data through trend detection, risk flagging and management-ready reporting. Inspired by the real procurement challenges faced by global FMCG companies operating multi-supplier, multi-market supply chains in Europe.*
