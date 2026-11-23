from io import BytesIO
import pandas as pd
from sqlalchemy.orm import Session
from .models import InventoryItem

REQUIRED = {"sku", "name", "quantity", "minimum_stock", "unit_cost"}

def import_inventory(file_bytes: bytes, filename: str, db: Session):
    if filename.lower().endswith((".xlsx", ".xls")):
        frame = pd.read_excel(BytesIO(file_bytes))
    else:
        frame = pd.read_csv(BytesIO(file_bytes))
    frame.columns = [str(c).strip().lower().replace(" ", "_") for c in frame.columns]
    missing = REQUIRED - set(frame.columns)
    if missing:
        raise ValueError(f"Eksik sütun(lar): {', '.join(sorted(missing))}")
    count = 0
    for row in frame.fillna("").to_dict(orient="records"):
        values = {k: row.get(k, "") for k in ("sku", "name", "category", "quantity", "minimum_stock", "unit_cost", "supplier")}
        values["category"] = values["category"] or "General"
        values["quantity"] = float(values["quantity"])
        values["minimum_stock"] = float(values["minimum_stock"])
        values["unit_cost"] = float(values["unit_cost"])
        item = db.query(InventoryItem).filter_by(sku=str(values["sku"])).first()
        if item:
            for k, v in values.items(): setattr(item, k, v)
        else:
            db.add(InventoryItem(**{**values, "sku": str(values["sku"])}))
        count += 1
    db.commit()
    return count

