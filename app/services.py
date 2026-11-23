import os
from collections import Counter
from sqlalchemy import func
from sqlalchemy.orm import Session
from .models import InventoryItem

def dashboard_metrics(db: Session):
    items = db.query(InventoryItem).all()
    low = [x for x in items if x.quantity <= x.minimum_stock]
    return {
        "item_count": len(items),
        "total_units": round(sum(x.quantity for x in items), 2),
        "inventory_value": round(sum(x.quantity * x.unit_cost for x in items), 2),
        "low_stock_count": len(low),
        "low_stock": sorted(low, key=lambda x: (x.quantity - x.minimum_stock, x.name)),
        "category_counts": Counter(x.category for x in items),
    }

def deterministic_summary(metrics):
    low = metrics["low_stock"]
    if not metrics["item_count"]:
        return "Envanterde henüz ürün bulunmuyor. İlk CSV/XLSX dosyanızı içe aktarın veya bir ürün ekleyin."
    summary = (f"Envanterde {metrics['item_count']} farklı ürün ve {metrics['total_units']:.0f} toplam birim bulunuyor. "
               f"Tahmini stok değeri {metrics['inventory_value']:,.2f}. ")
    if low:
        names = ", ".join(x.name for x in low[:5])
        summary += f"{len(low)} ürün minimum seviyede veya altında; öncelikli kontrol: {names}."
    else:
        summary += "Hiçbir ürün minimum stok seviyesinin altında değil; mevcut stok seviyesi izlenmeye devam edilmeli."
    return summary

def management_summary(db: Session):
    metrics = dashboard_metrics(db)
    base = deterministic_summary(metrics)
    # Optional integration: keep the core app deterministic and usable without a paid service.
    if os.getenv("OPENAI_API_KEY") and os.getenv("USE_LLM", "false").lower() == "true":
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                temperature=0.2,
                messages=[{"role": "system", "content": "Summarize inventory facts only. Do not invent data. Respond in Turkish."},
                          {"role": "user", "content": base}],
            )
            return response.choices[0].message.content.strip()
        except Exception:
            pass
    return base

