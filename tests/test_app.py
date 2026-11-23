import io
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base
from app.importer import import_inventory
from app.models import InventoryItem
from app.services import dashboard_metrics, management_summary

@pytest.fixture()
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try: yield session
    finally: session.close(); engine.dispose()

def test_csv_import_and_upsert(db):
    csv = b"sku,name,category,quantity,minimum_stock,unit_cost,supplier\nA-1,Test,Demo,2,5,10,Supplier\n"
    assert import_inventory(csv, "items.csv", db) == 1
    assert db.query(InventoryItem).count() == 1
    assert import_inventory(csv.replace(b",2,", b",7,"), "items.csv", db) == 1
    assert db.query(InventoryItem).one().quantity == 7

def test_dashboard_flags_low_stock_and_summary_is_grounded(db):
    db.add_all([InventoryItem(sku="LOW", name="Critical", category="Demo", quantity=2, minimum_stock=5, unit_cost=10), InventoryItem(sku="OK", name="Healthy", category="Demo", quantity=20, minimum_stock=5, unit_cost=2)])
    db.commit()
    metrics = dashboard_metrics(db)
    assert metrics["item_count"] == 2
    assert metrics["low_stock_count"] == 1
    assert metrics["inventory_value"] == 60
    summary = management_summary(db)
    assert "Critical" in summary and "2" in summary

def test_empty_inventory_has_actionable_summary(db):
    assert "CSV" in management_summary(db)
