"""
Supplier Performance Analytics — Data Generation
Realistic FMCG logistics supplier dataset with 12 months of order history
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

os.makedirs("data", exist_ok=True)
random.seed(42)
np.random.seed(42)

# ─── REALISTIC SUPPLIER NAMES BY COUNTRY ──────────────────────────────────────
suppliers_master = [
    # Germany
    {"id":"SUP001","name":"Müller Logistik GmbH","country":"Germany","city":"Hamburg","category":"Dry Goods","contract_sla_days":5,"contracted_price_index":1.00,"years_active":8,"iso_certified":True,"payment_terms":30},
    {"id":"SUP002","name":"Bayern Transport AG","country":"Germany","city":"Munich","category":"Chilled","contract_sla_days":3,"contracted_price_index":1.12,"years_active":5,"iso_certified":True,"payment_terms":45},
    {"id":"SUP003","name":"Rhenus Supply Chain","country":"Germany","city":"Dortmund","category":"Frozen","contract_sla_days":4,"contracted_price_index":0.98,"years_active":12,"iso_certified":True,"payment_terms":30},
    {"id":"SUP004","name":"Hellmann Worldwide","country":"Germany","city":"Osnabrück","category":"Dry Goods","contract_sla_days":6,"contracted_price_index":0.95,"years_active":15,"iso_certified":True,"payment_terms":60},
    # France
    {"id":"SUP005","name":"Geodis France SAS","country":"France","city":"Paris","category":"Dry Goods","contract_sla_days":4,"contracted_price_index":1.05,"years_active":10,"iso_certified":True,"payment_terms":30},
    {"id":"SUP006","name":"Bolloré Logistics","country":"France","city":"Lyon","category":"Chilled","contract_sla_days":3,"contracted_price_index":1.18,"years_active":7,"iso_certified":True,"payment_terms":45},
    {"id":"SUP007","name":"Norbert Dentressangle","country":"France","city":"Valence","category":"Frozen","contract_sla_days":4,"contracted_price_index":1.02,"years_active":9,"iso_certified":False,"payment_terms":30},
    {"id":"SUP008","name":"FM Logistic France","country":"France","city":"Metz","category":"Dry Goods","contract_sla_days":5,"contracted_price_index":0.97,"years_active":6,"iso_certified":True,"payment_terms":60},
    # Netherlands
    {"id":"SUP009","name":"Vos Logistics BV","country":"Netherlands","city":"Oss","category":"Dry Goods","contract_sla_days":4,"contracted_price_index":1.08,"years_active":11,"iso_certified":True,"payment_terms":30},
    {"id":"SUP010","name":"Bakker Logistiek BV","country":"Netherlands","city":"Zeewolde","category":"Chilled","contract_sla_days":2,"contracted_price_index":1.22,"years_active":4,"iso_certified":True,"payment_terms":30},
    {"id":"SUP011","name":"Jan de Rijk Logistics","country":"Netherlands","city":"Roosendaal","category":"Frozen","contract_sla_days":3,"contracted_price_index":1.15,"years_active":8,"iso_certified":True,"payment_terms":45},
    # Spain
    {"id":"SUP012","name":"Grupo Logista SA","country":"Spain","city":"Madrid","category":"Dry Goods","contract_sla_days":6,"contracted_price_index":0.88,"years_active":13,"iso_certified":True,"payment_terms":60},
    {"id":"SUP013","name":"Transportes Ochoa","country":"Spain","city":"Barcelona","category":"Chilled","contract_sla_days":5,"contracted_price_index":0.92,"years_active":6,"iso_certified":False,"payment_terms":45},
    {"id":"SUP014","name":"ID Logistics España","country":"Spain","city":"Valencia","category":"Dry Goods","contract_sla_days":5,"contracted_price_index":0.90,"years_active":4,"iso_certified":True,"payment_terms":30},
    # Italy
    {"id":"SUP015","name":"BRT Corriere Espresso","country":"Italy","city":"Bologna","category":"Dry Goods","contract_sla_days":5,"contracted_price_index":0.95,"years_active":9,"iso_certified":True,"payment_terms":60},
    {"id":"SUP016","name":"Fercam SpA","country":"Italy","city":"Bolzano","category":"Frozen","contract_sla_days":4,"contracted_price_index":1.05,"years_active":7,"iso_certified":True,"payment_terms":45},
    {"id":"SUP017","name":"GLS Italy Srl","country":"Italy","city":"Milan","category":"Chilled","contract_sla_days":3,"contracted_price_index":1.10,"years_active":5,"iso_certified":True,"payment_terms":30},
    # Belgium
    {"id":"SUP018","name":"Katoen Natie NV","country":"Belgium","city":"Antwerp","category":"Dry Goods","contract_sla_days":4,"contracted_price_index":1.08,"years_active":14,"iso_certified":True,"payment_terms":30},
    {"id":"SUP019","name":"Eurilogistic SA","country":"Belgium","city":"Liège","category":"Chilled","contract_sla_days":3,"contracted_price_index":1.14,"years_active":3,"iso_certified":False,"payment_terms":45},
    # Poland
    {"id":"SUP020","name":"ROHLIG SUUS Logistics","country":"Poland","city":"Warsaw","category":"Dry Goods","contract_sla_days":7,"contracted_price_index":0.78,"years_active":6,"iso_certified":True,"payment_terms":60},
    {"id":"SUP021","name":"Raben Group Poland","country":"Poland","city":"Poznan","category":"Frozen","contract_sla_days":6,"contracted_price_index":0.82,"years_active":8,"iso_certified":True,"payment_terms":60},
    {"id":"SUP022","name":"Pekaes SA","country":"Poland","city":"Pruszkow","category":"Dry Goods","contract_sla_days":7,"contracted_price_index":0.75,"years_active":10,"iso_certified":False,"payment_terms":90},
    # UK
    {"id":"SUP023","name":"Wincanton PLC","country":"UK","city":"London","category":"Dry Goods","contract_sla_days":4,"contracted_price_index":1.15,"years_active":12,"iso_certified":True,"payment_terms":30},
    {"id":"SUP024","name":"Culina Group Ltd","country":"UK","city":"Lutterworth","category":"Chilled","contract_sla_days":3,"contracted_price_index":1.20,"years_active":7,"iso_certified":True,"payment_terms":45},
    # Switzerland
    {"id":"SUP025","name":"Planzer Transport AG","country":"Switzerland","city":"Dietikon","category":"Dry Goods","contract_sla_days":3,"contracted_price_index":1.35,"years_active":9,"iso_certified":True,"payment_terms":30},
]

suppliers_df = pd.DataFrame(suppliers_master)

# ─── DESTINATION MARKETS ──────────────────────────────────────────────────────
destinations = [
    {"market":"France","hub":"Paris CDG"},
    {"market":"Germany","hub":"Frankfurt"},
    {"market":"Netherlands","hub":"Rotterdam"},
    {"market":"Spain","hub":"Madrid"},
    {"market":"Italy","hub":"Milan"},
    {"market":"Belgium","hub":"Brussels"},
    {"market":"Poland","hub":"Warsaw"},
]

# ─── GENERATE 12 MONTHS OF ORDER HISTORY ─────────────────────────────────────
# Each supplier has a base reliability that drifts over time
# Some suppliers deteriorate (to simulate risk), some improve

# Reliability trends — who is getting better/worse
trends = {
    "SUP001": 0.00,   # stable
    "SUP002": -0.04,  # deteriorating
    "SUP003": 0.02,   # improving
    "SUP004": 0.00,   # stable
    "SUP005": -0.06,  # significantly deteriorating
    "SUP006": 0.03,   # improving
    "SUP007": -0.08,  # high risk — major deterioration
    "SUP008": 0.01,   # slightly improving
    "SUP009": 0.00,   # stable
    "SUP010": 0.04,   # strong improvement
    "SUP011": -0.03,  # slight deterioration
    "SUP012": 0.02,   # improving
    "SUP013": -0.05,  # deteriorating
    "SUP014": 0.01,   # stable
    "SUP015": 0.00,   # stable
    "SUP016": -0.02,  # slight deterioration
    "SUP017": 0.03,   # improving
    "SUP018": 0.00,   # stable
    "SUP019": -0.07,  # high risk
    "SUP020": 0.05,   # strong improvement
    "SUP021": 0.01,   # stable
    "SUP022": -0.04,  # deteriorating
    "SUP023": 0.02,   # improving
    "SUP024": 0.00,   # stable
    "SUP025": 0.01,   # stable
}

# Base reliability per supplier
base_reliability = {
    "SUP001":0.92,"SUP002":0.88,"SUP003":0.85,"SUP004":0.94,
    "SUP005":0.90,"SUP006":0.87,"SUP007":0.82,"SUP008":0.91,
    "SUP009":0.93,"SUP010":0.80,"SUP011":0.89,"SUP012":0.86,
    "SUP013":0.84,"SUP014":0.88,"SUP015":0.91,"SUP016":0.87,
    "SUP017":0.85,"SUP018":0.93,"SUP019":0.79,"SUP020":0.83,
    "SUP021":0.86,"SUP022":0.80,"SUP023":0.91,"SUP024":0.88,
    "SUP025":0.95,
}

orders = []
base_date = datetime(2024, 1, 1)

for month in range(12):
    month_date = base_date + timedelta(days=30*month)
    month_str = month_date.strftime("%Y-%m")

    # Seasonality — Q4 stress (months 9-11 = Oct-Dec)
    q4_stress = 0.05 if month >= 9 else 0.0

    for _, supplier in suppliers_df.iterrows():
        sid = supplier["id"]

        # Orders per supplier per month — varies by category
        n_orders = random.randint(8, 25) if supplier["category"] == "Dry Goods" else random.randint(5, 15)

        # Reliability this month — base + trend + seasonality + noise
        month_reliability = base_reliability[sid] + (trends[sid] * month/11) - q4_stress + random.uniform(-0.03, 0.03)
        month_reliability = max(0.40, min(0.99, month_reliability))

        for _ in range(n_orders):
            dest = random.choice(destinations)
            order_date = month_date + timedelta(days=random.randint(0, 27))
            quantity = random.randint(50, 800)
            unit_price = supplier["contracted_price_index"] * round(np.random.lognormal(2.8, 0.5), 2)
            order_value = round(quantity * unit_price, 2)

            # Delivery performance
            on_time = random.random() < month_reliability
            delay_days = 0 if on_time else random.randint(1, 12)
            actual_days = supplier["contract_sla_days"] + delay_days

            # Quality
            quality_pass = random.random() < (month_reliability * 1.03)
            defect_rate = round(random.uniform(0, 0.03) if quality_pass else random.uniform(0.03, 0.12), 4)

            # Invoice accuracy
            invoice_ok = random.random() < (month_reliability * 1.05)

            # Temperature breach (for chilled/frozen only)
            temp_breach = False
            if supplier["category"] in ["Chilled","Frozen"]:
                temp_breach = random.random() < (1 - month_reliability) * 0.3

            orders.append({
                "order_id": f"ORD{len(orders)+1:05d}",
                "supplier_id": sid,
                "supplier_name": supplier["name"],
                "supplier_country": supplier["country"],
                "category": supplier["category"],
                "destination_market": dest["market"],
                "destination_hub": dest["hub"],
                "month": month_str,
                "month_num": month + 1,
                "order_date": order_date.strftime("%Y-%m-%d"),
                "quantity_units": quantity,
                "unit_price_eur": round(unit_price, 2),
                "order_value_eur": order_value,
                "contracted_sla_days": supplier["contract_sla_days"],
                "actual_delivery_days": actual_days,
                "on_time_delivery": int(on_time),
                "delay_days": delay_days,
                "quality_pass": int(quality_pass),
                "defect_rate_pct": round(defect_rate * 100, 2),
                "invoice_accurate": int(invoice_ok),
                "temperature_breach": int(temp_breach),
                "payment_terms_days": supplier["payment_terms"],
            })

orders_df = pd.DataFrame(orders)
orders_df.to_csv("data/orders.csv", index=False)
suppliers_df.to_csv("data/suppliers.csv", index=False)

print(f"Generated {len(orders_df):,} orders across {len(suppliers_df)} suppliers")
print(f"Months: {orders_df['month'].nunique()} | Markets: {orders_df['destination_market'].nunique()}")
print(f"Categories: {orders_df['category'].value_counts().to_dict()}")
print(f"On-time rate overall: {orders_df['on_time_delivery'].mean():.1%}")
