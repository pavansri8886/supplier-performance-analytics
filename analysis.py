"""
Supplier Performance Analytics — Main Analysis
Scorecard, trend analysis, risk flagging and logistics dashboard
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

os.makedirs("output", exist_ok=True)

# ─── LOAD DATA ────────────────────────────────────────────────────────────────
orders = pd.read_csv("data/orders.csv")
suppliers = pd.read_csv("data/suppliers.csv")

print(f"Loaded {len(orders):,} orders | {orders['month'].nunique()} months | {len(suppliers)} suppliers")

# ─── OVERALL SCORECARD ────────────────────────────────────────────────────────
def build_scorecard(df):
    sc = df.groupby(["supplier_id","supplier_name","supplier_country","category"]).agg(
        total_orders=("order_id","count"),
        total_value=("order_value_eur","sum"),
        on_time_rate=("on_time_delivery","mean"),
        quality_rate=("quality_pass","mean"),
        invoice_rate=("invoice_accurate","mean"),
        avg_defect_rate=("defect_rate_pct","mean"),
        avg_delay_days=("delay_days","mean"),
        temp_breach_rate=("temperature_breach","mean"),
    ).reset_index()

    sc["on_time_rate"]     = (sc["on_time_rate"] * 100).round(1)
    sc["quality_rate"]     = (sc["quality_rate"] * 100).round(1)
    sc["invoice_rate"]     = (sc["invoice_rate"] * 100).round(1)
    sc["avg_defect_rate"]  = sc["avg_defect_rate"].round(2)
    sc["avg_delay_days"]   = sc["avg_delay_days"].round(1)
    sc["temp_breach_rate"] = (sc["temp_breach_rate"] * 100).round(1)
    sc["total_value"]      = sc["total_value"].round(0)

    # Weighted performance score
    sc["performance_score"] = (
        sc["on_time_rate"]  * 0.40 +
        sc["quality_rate"]  * 0.35 +
        sc["invoice_rate"]  * 0.25
    ).round(1)

    # Tier classification
    sc["tier"] = pd.cut(
        sc["performance_score"],
        bins=[0, 75, 82, 90, 100],
        labels=["⚠️ At Risk","🟡 Needs Improvement","🟢 Performing","⭐ Preferred"]
    )
    return sc.sort_values("performance_score", ascending=False)

scorecard = build_scorecard(orders)

# ─── TREND ANALYSIS — monthly performance per supplier ────────────────────────
monthly = orders.groupby(["supplier_id","supplier_name","month","month_num"]).agg(
    on_time_rate=("on_time_delivery","mean"),
    quality_rate=("quality_pass","mean"),
    orders=("order_id","count"),
    value=("order_value_eur","sum"),
    avg_delay=("delay_days","mean"),
).reset_index()

monthly["on_time_rate"] = (monthly["on_time_rate"] * 100).round(1)
monthly["quality_rate"] = (monthly["quality_rate"] * 100).round(1)

# Calculate trend slope for each supplier (last 6 months vs first 6 months)
def get_trend(sup_id):
    sup_data = monthly[monthly["supplier_id"] == sup_id].sort_values("month_num")
    if len(sup_data) < 6:
        return 0
    first_half = sup_data.head(6)["on_time_rate"].mean()
    second_half = sup_data.tail(6)["on_time_rate"].mean()
    return round(second_half - first_half, 1)

scorecard["trend_6m"] = scorecard["supplier_id"].apply(get_trend)
scorecard["trend_signal"] = scorecard["trend_6m"].apply(
    lambda x: "📈 Improving" if x > 2 else ("📉 Deteriorating" if x < -2 else "➡️ Stable")
)

# ─── RISK FLAGS ───────────────────────────────────────────────────────────────
flags = []
for _, row in scorecard.iterrows():
    sup_flags = []
    if row["on_time_rate"] < 80:
        sup_flags.append(f"On-time below 80% ({row['on_time_rate']}%)")
    if row["quality_rate"] < 85:
        sup_flags.append(f"Quality below 85% ({row['quality_rate']}%)")
    if row["trend_6m"] < -5:
        sup_flags.append(f"Performance dropping fast ({row['trend_6m']:+.1f}pp in 6m)")
    if row["avg_delay_days"] > 4:
        sup_flags.append(f"Avg delay {row['avg_delay_days']}d over contract")
    if row["temp_breach_rate"] > 5:
        sup_flags.append(f"Temperature breach rate {row['temp_breach_rate']}%")
    flags.append(" | ".join(sup_flags) if sup_flags else "No issues")

scorecard["risk_flags"] = flags
scorecard["risk_level"] = scorecard["risk_flags"].apply(
    lambda x: "HIGH" if x.count("|") >= 2 or "fast" in x
    else ("MEDIUM" if x != "No issues" else "LOW")
)

# ─── LANE ANALYSIS — origin country to destination market ─────────────────────
lane = orders.groupby(["supplier_country","destination_market"]).agg(
    orders=("order_id","count"),
    on_time_rate=("on_time_delivery","mean"),
    avg_delay=("delay_days","mean"),
    total_value=("order_value_eur","sum"),
).reset_index()
lane["on_time_rate"] = (lane["on_time_rate"] * 100).round(1)
lane["avg_delay"] = lane["avg_delay"].round(1)

# ─── SEASONALITY — Q4 performance drop ────────────────────────────────────────
seasonal = orders.groupby("month_num").agg(
    on_time_rate=("on_time_delivery","mean"),
    quality_rate=("quality_pass","mean"),
    orders=("order_id","count"),
    avg_delay=("delay_days","mean"),
).reset_index()
seasonal["on_time_rate"] = (seasonal["on_time_rate"] * 100).round(1)
seasonal["quality_rate"] = (seasonal["quality_rate"] * 100).round(1)
seasonal["month_label"] = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# ─── CATEGORY PERFORMANCE ─────────────────────────────────────────────────────
cat_perf = orders.groupby("category").agg(
    on_time_rate=("on_time_delivery","mean"),
    quality_rate=("quality_pass","mean"),
    orders=("order_id","count"),
    total_value=("order_value_eur","sum"),
    temp_breach_rate=("temperature_breach","mean"),
).reset_index()
cat_perf["on_time_rate"] = (cat_perf["on_time_rate"] * 100).round(1)
cat_perf["quality_rate"] = (cat_perf["quality_rate"] * 100).round(1)
cat_perf["temp_breach_rate"] = (cat_perf["temp_breach_rate"] * 100).round(1)

# ─── SAVE OUTPUTS ─────────────────────────────────────────────────────────────
scorecard.to_csv("output/supplier_scorecard.csv", index=False)
monthly.to_csv("output/monthly_trends.csv", index=False)
lane.to_csv("output/lane_analysis.csv", index=False)
seasonal.to_csv("output/seasonality.csv", index=False)
cat_perf.to_csv("output/category_performance.csv", index=False)

# ─── PRINT SUMMARY ────────────────────────────────────────────────────────────
print("\n=== SCORECARD SUMMARY ===")
print(scorecard[["supplier_name","supplier_country","performance_score","tier","trend_signal","risk_level"]].to_string(index=False))

high_risk = scorecard[scorecard["risk_level"]=="HIGH"]
print(f"\n=== HIGH RISK SUPPLIERS ({len(high_risk)}) ===")
for _, r in high_risk.iterrows():
    print(f"  {r['supplier_name']} ({r['supplier_country']}): {r['risk_flags']}")

print(f"\n=== SEASONALITY — Q4 STRESS ===")
print(seasonal[["month_label","on_time_rate","avg_delay"]].to_string(index=False))

# ─── BUILD HTML DASHBOARD ─────────────────────────────────────────────────────

# KPIs
total_orders = len(orders)
total_value = orders["order_value_eur"].sum()
overall_on_time = orders["on_time_delivery"].mean() * 100
overall_quality = orders["quality_pass"].mean() * 100
high_risk_count = len(scorecard[scorecard["risk_level"]=="HIGH"])
preferred_count = len(scorecard[scorecard["tier"]=="⭐ Preferred"])

# Scorecard table rows
sc_rows = ""
for _, r in scorecard.iterrows():
    tier_colors = {"⭐ Preferred":"#3FB950","🟢 Performing":"#60A5FA","🟡 Needs Improvement":"#F59E0B","⚠️ At Risk":"#F85149"}
    risk_colors = {"LOW":"#3FB950","MEDIUM":"#F59E0B","HIGH":"#F85149"}
    trend_colors = {"📈 Improving":"#3FB950","➡️ Stable":"#8B949E","📉 Deteriorating":"#F85149"}
    tc = tier_colors.get(str(r["tier"]),"#888")
    rc = risk_colors.get(r["risk_level"],"#888")
    trc = trend_colors.get(r["trend_signal"],"#888")
    sc_rows += f"""<tr>
        <td style="font-weight:600;color:#E6EDF3">{r['supplier_name']}</td>
        <td style="color:#94A3B8">{r['supplier_country']}</td>
        <td style="color:#94A3B8">{r['category']}</td>
        <td style="color:#60A5FA;font-weight:600">{r['on_time_rate']}%</td>
        <td style="color:#A78BFA;font-weight:600">{r['quality_rate']}%</td>
        <td style="color:#34D399;font-weight:600">{r['invoice_rate']}%</td>
        <td style="font-weight:700;font-size:1.1em">{r['performance_score']}</td>
        <td><span style="color:{tc};font-weight:600">{r['tier']}</span></td>
        <td><span style="color:{trc}">{r['trend_signal']} ({r['trend_6m']:+.1f}pp)</span></td>
        <td><span style="color:{rc};font-weight:600">{r['risk_level']}</span></td>
    </tr>"""

# Monthly trend data for chart — top 5 suppliers by value
top5 = scorecard.nlargest(5,"total_value")["supplier_id"].tolist()
months_labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
colors_top5 = ["#E879F9","#60A5FA","#3FB950","#F59E0B","#F87171"]

trend_traces = []
for i, sid in enumerate(top5):
    sname = scorecard[scorecard["supplier_id"]==sid]["supplier_name"].values[0]
    sup_monthly = monthly[monthly["supplier_id"]==sid].sort_values("month_num")
    y_vals = list(sup_monthly["on_time_rate"])
    trend_traces.append({
        "x": months_labels[:len(y_vals)],
        "y": y_vals,
        "name": sname.split()[0],
        "type":"scatter","mode":"lines+markers",
        "line":{"color":colors_top5[i],"width":2},
        "marker":{"size":5}
    })

# Seasonality data
seasonal_trace = [{
    "x": list(seasonal["month_label"]),
    "y": list(seasonal["on_time_rate"]),
    "type":"bar",
    "marker":{"color": [
        "#F85149" if m in ["Oct","Nov","Dec"] else "#60A5FA"
        for m in seasonal["month_label"]
    ]},
    "name":"On-time Rate %"
}]

# Lane heatmap data
lane_pivot = lane.pivot(index="supplier_country", columns="destination_market", values="on_time_rate").fillna(0)
lane_z = lane_pivot.values.tolist()
lane_x = list(lane_pivot.columns)
lane_y = list(lane_pivot.index)

# Category bars
cat_trace = [{
    "x": list(cat_perf["category"]),
    "y": list(cat_perf["on_time_rate"]),
    "type":"bar",
    "marker":{"color":["#60A5FA","#3FB950","#F59E0B"]},
    "name":"On-time %"
}]

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Supplier Performance Analytics Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI',Arial,sans-serif; }}
body {{ background:#0D1117; color:#E6EDF3; }}
.hero {{ background:linear-gradient(135deg,#0d1b2a 0%,#1a0533 100%);
         border-bottom:1px solid #21262D; padding:36px 48px 28px; }}
.hero h1 {{ font-size:1.8rem; font-weight:700; color:#E879F9; margin-bottom:6px; }}
.hero p {{ color:#94A3B8; font-size:0.9rem; max-width:700px; line-height:1.6; }}
.hero .meta {{ margin-top:14px; display:flex; gap:20px; flex-wrap:wrap; }}
.hero .meta span {{ font-size:0.78rem; color:#7B9EB8; }}
.hero .meta strong {{ color:#60A5FA; }}
.container {{ max-width:1400px; margin:0 auto; padding:28px 48px; }}
.kpi-grid {{ display:grid; grid-template-columns:repeat(6,1fr); gap:14px; margin-bottom:28px; }}
.kpi {{ background:#161B22; border:1px solid #30363D; border-radius:12px; padding:18px 20px; }}
.kpi .val {{ font-size:1.8rem; font-weight:700; margin-bottom:4px; }}
.kpi .lbl {{ font-size:0.7rem; color:#8B949E; text-transform:uppercase; letter-spacing:0.08em; }}
.grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-bottom:20px; }}
.grid3 {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:20px; margin-bottom:20px; }}
.card {{ background:#161B22; border:1px solid #30363D; border-radius:14px; padding:22px; }}
.card h2 {{ font-size:0.95rem; font-weight:700; color:#E6EDF3; margin-bottom:4px; }}
.card .sub {{ font-size:0.75rem; color:#8B949E; margin-bottom:18px; }}
.sec {{ font-size:0.68rem; font-weight:700; color:#A78BFA; text-transform:uppercase;
        letter-spacing:0.12em; margin:24px 0 14px;
        padding-bottom:8px; border-bottom:1px solid #21262D; }}
.tbl-wrap {{ overflow-x:auto; border-radius:8px; }}
table {{ width:100%; border-collapse:collapse; font-size:0.82rem; min-width:900px; }}
th {{ text-align:left; padding:10px 12px; background:#0D1117; color:#8B949E;
      font-size:0.7rem; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; }}
td {{ padding:10px 12px; border-bottom:1px solid #21262D; }}
tr:hover td {{ background:#1C2128; }}
tr:last-child td {{ border-bottom:none; }}
.insight {{ background:#0d2137; border-left:3px solid #3B82F6; border-radius:0 8px 8px 0;
            padding:12px 16px; margin:8px 0; font-size:0.85rem; color:#CBD5E1; line-height:1.6; }}
.insight.red {{ border-left-color:#F85149; background:#2d0d0d; }}
.insight.green {{ border-left-color:#3FB950; background:#0d2018; }}
.insight.orange {{ border-left-color:#F59E0B; background:#2d1f0a; }}
footer {{ border-top:1px solid #21262D; padding:20px 48px; color:#8B949E;
          font-size:0.78rem; display:flex; justify-content:space-between; }}
footer a {{ color:#60A5FA; text-decoration:none; }}
@media(max-width:900px) {{
  .kpi-grid {{ grid-template-columns:repeat(3,1fr); }}
  .grid2,.grid3 {{ grid-template-columns:1fr; }}
  .container {{ padding:20px; }}
}}
</style>
</head>
<body>
<div class="hero">
  <h1>📦 Supplier Performance Analytics Dashboard</h1>
  <p>12-month logistics supplier scorecard across {len(suppliers)} European suppliers, {orders['destination_market'].nunique()} destination markets
  and {len(orders):,} orders. Tracks on-time delivery, quality, invoice accuracy, trend direction and risk flags
  to support procurement decisions and supplier contract reviews.</p>
  <div class="meta">
    <span>📅 <strong>Jan – Dec 2024</strong></span>
    <span>🏭 <strong>{len(suppliers)}</strong> suppliers</span>
    <span>🌍 <strong>{orders['supplier_country'].nunique()}</strong> origin countries</span>
    <span>🚚 <strong>{orders['destination_market'].nunique()}</strong> destination markets</span>
    <span>📦 <strong>{total_orders:,}</strong> orders analysed</span>
  </div>
</div>

<div class="container">

<div class="kpi-grid">
  <div class="kpi"><div class="val" style="color:#E879F9">{total_orders:,}</div><div class="lbl">Total Orders</div></div>
  <div class="kpi"><div class="val" style="color:#60A5FA">€{total_value/1e6:.1f}M</div><div class="lbl">Total Value</div></div>
  <div class="kpi"><div class="val" style="color:#3FB950">{overall_on_time:.1f}%</div><div class="lbl">Overall On-Time</div></div>
  <div class="kpi"><div class="val" style="color:#A78BFA">{overall_quality:.1f}%</div><div class="lbl">Quality Pass Rate</div></div>
  <div class="kpi"><div class="val" style="color:#F85149">{high_risk_count}</div><div class="lbl">High Risk Suppliers</div></div>
  <div class="kpi"><div class="val" style="color:#F59E0B">{preferred_count}</div><div class="lbl">Preferred Partners</div></div>
</div>

<p class="sec">Performance Trends & Seasonality</p>
<div class="grid2">
  <div class="card">
    <h2>Monthly On-Time Rate — Top 5 Suppliers by Value</h2>
    <p class="sub">Track which suppliers are improving or deteriorating over 12 months</p>
    <div id="trend-chart" style="height:300px"></div>
  </div>
  <div class="card">
    <h2>Seasonal Performance Pattern</h2>
    <p class="sub">Red bars = Q4 stress period — on-time rates drop as peak season hits</p>
    <div id="seasonal-chart" style="height:300px"></div>
  </div>
</div>

<p class="sec">Geographic & Category Analysis</p>
<div class="grid2">
  <div class="card">
    <h2>On-Time Rate by Origin Country → Destination Market</h2>
    <p class="sub">Lane performance heatmap — identify weak delivery corridors</p>
    <div id="lane-chart" style="height:320px"></div>
  </div>
  <div class="card">
    <h2>Performance by Product Category</h2>
    <p class="sub">Chilled and Frozen supply chains have tighter SLAs and higher risk</p>
    <div id="cat-chart" style="height:200px"></div>
    <br>
    <div class="insight red">
      ❄️ <strong>Cold Chain Alert:</strong> Chilled and Frozen categories show higher temperature breach rates.
      SUP007 (Norbert Dentressangle) and SUP019 (Eurilogistic) flagged as HIGH RISK — immediate contract review recommended.
    </div>
    <div class="insight green">
      ✅ <strong>Top Lane:</strong> Netherlands → Germany corridor shows strongest on-time performance.
      Bakker Logistiek (SUP010) trending +{scorecard[scorecard['supplier_id']=='SUP010']['trend_6m'].values[0]:+.1f}pp over 6 months.
    </div>
  </div>
</div>

<p class="sec">Full Supplier Scorecard</p>
<div class="card">
  <h2>All Suppliers — Performance Score, Tier and Risk Classification</h2>
  <p class="sub">Weighted score: On-time 40% · Quality 35% · Invoice accuracy 25% · Trend based on H1 vs H2 on-time delta</p>
  <br>
  <div class="tbl-wrap">
    <table>
      <thead><tr>
        <th>Supplier</th><th>Country</th><th>Category</th>
        <th>On-Time</th><th>Quality</th><th>Invoice</th>
        <th>Score</th><th>Tier</th><th>6-Month Trend</th><th>Risk</th>
      </tr></thead>
      <tbody>{sc_rows}</tbody>
    </table>
  </div>
</div>

<p class="sec">Strategic Recommendations</p>
<div class="grid3">
  <div class="card">
    <h2>🔴 Immediate Actions</h2>
    <p class="sub">High risk suppliers requiring intervention</p>
    <br>
    <div class="insight red">SUP007 Norbert Dentressangle — on-time dropping fast. Temperature breach risk. Escalate to account manager and initiate SLA review within 30 days.</div>
    <div class="insight red">SUP019 Eurilogistic — new supplier showing early deterioration. Consider volume reduction until performance stabilises above 85%.</div>
    <div class="insight red">SUP005 Geodis France — significant 6-month decline. Review root cause with supplier before Q4 volume ramp-up.</div>
  </div>
  <div class="card">
    <h2>🟡 Monitor Closely</h2>
    <p class="sub">Showing early warning signals</p>
    <br>
    <div class="insight orange">SUP002 Bayern Transport — chilled specialist with declining on-time rate. Q4 dependency makes this high priority to resolve before October.</div>
    <div class="insight orange">SUP013 Transportes Ochoa — Spanish market coverage at risk. Identify backup supplier for Iberian lanes.</div>
    <div class="insight orange">SUP022 Pekaes SA — lowest price index but deteriorating quality. Cost savings may be offset by rework and delays.</div>
  </div>
  <div class="card">
    <h2>⭐ Expand Partnership</h2>
    <p class="sub">Strong performers worth growing</p>
    <br>
    <div class="insight green">SUP010 Bakker Logistiek — strongest improvement trajectory (+{scorecard[scorecard['supplier_id']=='SUP010']['trend_6m'].values[0]:+.1f}pp). Consider increasing chilled volume allocation for Netherlands hub.</div>
    <div class="insight green">SUP025 Planzer Transport — consistently highest scores despite premium pricing. Reliable choice for time-sensitive Swiss lanes.</div>
    <div class="insight green">SUP020 ROHLIG SUUS — strong improvement trend in Eastern Europe. Cost-effective option for Poland hub expansion.</div>
  </div>
</div>

</div>
<footer>
  <span>Built by <strong>Pavan Kumar Naganaboina</strong> · MSc Data Management & AI, ECE Paris 2025–2026</span>
  <span><a href="https://github.com/pavansri8886">github.com/pavansri8886</a> · Data: Simulated FMCG logistics dataset</span>
</footer>

<script>
const dark = {{
  paper_bgcolor:'#161B22', plot_bgcolor:'#161B22',
  font:{{color:'#E6EDF3',family:'Segoe UI',size:11}},
  margin:{{t:10,b:40,l:50,r:20}},
  xaxis:{{gridcolor:'#21262D',color:'#8B949E'}},
  yaxis:{{gridcolor:'#21262D',color:'#8B949E'}},
}};

Plotly.newPlot('trend-chart', {json.dumps(trend_traces)}, {{
  ...dark, showlegend:true,
  legend:{{bgcolor:'#161B22',bordercolor:'#30363D',font:{{size:10}}}},
  yaxis:{{...dark.yaxis, title:'On-Time Rate %', range:[60,100]}},
}}, {{responsive:true}});

Plotly.newPlot('seasonal-chart', {json.dumps(seasonal_trace)}, {{
  ...dark,
  yaxis:{{...dark.yaxis, title:'On-Time Rate %', range:[75,100]}},
}}, {{responsive:true}});

Plotly.newPlot('lane-chart', [{{
  z: {json.dumps(lane_z)},
  x: {json.dumps(lane_x)},
  y: {json.dumps(lane_y)},
  type:'heatmap',
  colorscale:[['0','#F85149'],['0.5','#F59E0B'],['1','#3FB950']],
  showscale:true,
  text: {json.dumps([[f"{v:.0f}%" for v in row] for row in lane_z])},
  texttemplate:"%{{text}}",
  hovertemplate:'%{{y}} → %{{x}}: %{{z:.1f}}%<extra></extra>'
}}], {{
  ...dark, margin:{{t:10,b:80,l:80,r:20}},
  xaxis:{{...dark.xaxis, tickangle:-30}},
}}, {{responsive:true}});

Plotly.newPlot('cat-chart', {json.dumps(cat_trace)}, {{
  ...dark,
  yaxis:{{...dark.yaxis, title:'On-Time %', range:[80,96]}},
}}, {{responsive:true}});
</script>
</body>
</html>"""

with open("output/supplier_dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n✓ Dashboard saved to output/supplier_dashboard.html")
print(f"✓ High risk suppliers: {high_risk_count}")
print(f"✓ Preferred partners: {preferred_count}")
