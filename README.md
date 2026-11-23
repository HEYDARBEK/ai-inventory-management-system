# AI Inventory Management System

> AI-ready inventory operations dashboard for local Windows workflows.

Yerel çalışan bir stok yönetimi MVP’si. Ürün CRUD, CSV/XLSX içe aktarma, ürün bazlı minimum stok eşikleri, düşük stok uyarıları, dashboard metrikleri ve gerçek envanter verisine dayalı yönetim özeti içerir.

## Kurulum

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Tarayıcıda `http://127.0.0.1:8000` adresini açın. Örnek veri için dashboard'dan `sample_inventory.csv` dosyasını yükleyin.

## Veri formatı

CSV/XLSX sütunları: `sku`, `name`, `quantity`, `minimum_stock`, `unit_cost`; isteğe bağlı `category`, `supplier`. Aynı SKU tekrar içe aktarılırsa mevcut kayıt güncellenir.

## İsteğe bağlı AI özeti

API anahtarı olmadan deterministik özet çalışır. LLM özeti için `.env` değişkenlerini ayarlayıp uygulamayı yeniden başlatın. LLM'e yalnızca uygulamanın oluşturduğu envanter özeti gönderilir; ürün verisi uydurulmaması sistem talimatıyla sınırlandırılır.

## Test

```powershell
pytest -q
```

## Varsayımlar ve sonraki adımlar

MVP tek kullanıcı ve yerel SQLite içindir; kimlik doğrulama, stok hareketleri ve rol yönetimi kapsam dışıdır. Üretim sürümünde audit log, stok giriş/çıkış hareket tablosu, kimlik doğrulama ve tedarikçi sipariş akışı eklenebilir.
