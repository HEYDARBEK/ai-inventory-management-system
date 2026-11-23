from pathlib import Path
from fastapi import Depends, FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import get_db, init_db
from .importer import import_inventory
from .models import InventoryItem
from .schemas import ItemIn
from .services import dashboard_metrics, management_summary

app = FastAPI(title="AI Inventory Management System")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

@app.on_event("startup")
def startup(): init_db()

@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    metrics = dashboard_metrics(db)
    items = db.query(InventoryItem).order_by(InventoryItem.name).all()
    return templates.TemplateResponse("index.html", {"request": request, "metrics": metrics, "items": items, "summary": management_summary(db), "error": None})

@app.post("/items")
async def create_item(request: Request, db: Session = Depends(get_db)):
    payload = await request.json() if "application/json" in request.headers.get("content-type", "") else dict(await request.form())
    item = ItemIn(**payload)
    if db.query(InventoryItem).filter_by(sku=item.sku).first():
        return {"error": "Bu SKU zaten kayıtlı."}
    db.add(InventoryItem(**item.model_dump())); db.commit()
    return RedirectResponse("/", status_code=303)

@app.post("/items/{item_id}/delete")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(InventoryItem, item_id)
    if item: db.delete(item); db.commit()
    return RedirectResponse("/", status_code=303)

@app.put("/items/{item_id}")
def update_item(item_id: int, item: ItemIn, db: Session = Depends(get_db)):
    record = db.get(InventoryItem, item_id)
    if not record:
        return {"error": "Ürün bulunamadı."}
    duplicate = db.query(InventoryItem).filter(InventoryItem.sku == item.sku, InventoryItem.id != item_id).first()
    if duplicate:
        return {"error": "Bu SKU zaten kayıtlı."}
    for key, value in item.model_dump().items():
        setattr(record, key, value)
    db.commit()
    return record

@app.post("/import", response_class=HTMLResponse)
async def upload_inventory(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    error = None
    try:
        imported = import_inventory(await file.read(), file.filename or "inventory.csv", db)
    except Exception as exc:
        imported = 0; error = str(exc)
    metrics = dashboard_metrics(db)
    items = db.query(InventoryItem).order_by(InventoryItem.name).all()
    return templates.TemplateResponse("index.html", {"request": request, "metrics": metrics, "items": items, "summary": management_summary(db), "error": error, "imported": imported})

@app.get("/api/summary")
def api_summary(db: Session = Depends(get_db)):
    return {"summary": management_summary(db), "metrics": {k: v for k, v in dashboard_metrics(db).items() if k != "low_stock"}}

