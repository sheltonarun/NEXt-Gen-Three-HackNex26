import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
orders_path = ROOT / "data" / "raw" / "orders.csv"
orders = pd.read_csv(orders_path, dtype=str)

o = orders.drop_duplicates(subset="order_id", keep="first")
o = o[o["status"].str.strip().str.lower() == "completed"]
o = o.dropna(subset=["total"])
o["total"] = pd.to_numeric(o["total"].str.replace(",", ""), errors="coerce")
ans = round(o["total"].dropna().sum(), 2)
print(ans)