# Wholesale Inventory, Sales & POS

Production-oriented MVP for wholesale inventory, stock receipts, POS sales, gross profit reporting and auditability.

## What Is Implemented

- Django + DRF backend with modular apps under `backend/apps`.
- Django Unfold admin for catalog, stock, purchases, sales and audit logs.
- Product catalog with Decimal prices/stock, units, images and unique SKU.
- Immutable `InventoryMovement` ledger and cached `Product.current_stock`.
- Stock receipt posting/cancellation services.
- Atomic sale completion with `select_for_update`, idempotency key protection and SaleItem cost/price snapshots.
- Returns, sale cancellation and historical correction service with audit logging.
- Product/operator/dashboard reports and CSV export.
- JWT auth, permission-aware DRF routes and OpenAPI docs.
- Next.js POS at `/operator` with product search, cart editing and checkout.
- Automated tests for critical inventory/sales/correction/snapshot flows.

## Backend Setup

```bash
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_dev
.venv/bin/python manage.py runserver 8000
```

Local dev users:

- `admin` / `admin12345`
- `operator` / `operator12345`

Admin: `http://localhost:8000/admin/`
API docs: `http://localhost:8000/api/docs/`

## PostgreSQL

SQLite is used automatically when `POSTGRES_DB` is not set. For PostgreSQL:

```bash
docker compose up -d postgres
cd backend
cp .env.example .env
export POSTGRES_DB=wholesale POSTGRES_USER=wholesale POSTGRES_PASSWORD=wholesale POSTGRES_HOST=localhost
.venv/bin/python manage.py migrate
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

POS: `http://localhost:3000/operator`

## Verification

```bash
cd backend
.venv/bin/python -m pytest
.venv/bin/python manage.py check
```

```bash
cd frontend
npm run build
```
