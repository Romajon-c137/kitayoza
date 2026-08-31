# Wholesale Inventory, Sales & POS Architecture

## Project Structure

```text
backend/
  config/                 Django project settings and URL routing
  apps/
    accounts/             Users, roles, auth helpers, seed command
    core/                 Shared constants, decimal helpers, API errors
    products/             Category and Product catalog
    customers/            Simple customer model
    suppliers/            Simple supplier model
    inventory/            Stock ledger, current stock operations, adjustments
    purchases/            Stock receipt documents and posting services
    sales/                Sales, sale items, returns, cancellation, corrections
    reports/              Aggregated reporting endpoints and exports
    audit/                Immutable business audit log
frontend/
  src/app/                Next.js App Router pages
  src/components/         POS UI components
  src/lib/                API client, formatting, auth helpers
  src/types/              Shared TypeScript API shapes
```

## Main Models

- `Category`: nested product categories with `slug` and `is_active`.
- `Product`: one stock keeping unit per row, unique `sku`, Decimal prices and stock, image, unit, minimum stock.
- `InventoryMovement`: immutable stock ledger. Every stock change creates a movement.
- `StockAdjustment`: explicit manual stock correction with reason.
- `StockReceipt` / `StockReceiptItem`: draft, posted, cancelled receipt workflow.
- `Sale` / `SaleItem`: completed sale with snapshots for product name, SKU, unit, cost and regular price.
- `SaleReturn` / `SaleReturnItem`: return document linked to original sale items.
- `IdempotencyKey`: protects sale creation and critical write APIs from double submit.
- `AuditLog`: immutable old/new data record for financial, stock and permission-sensitive changes.

## Relationships

- Product belongs to Category and has many inventory movements, receipt items and sale items.
- Sale belongs to operator and optional customer; SaleItem belongs to Sale and Product.
- SaleReturn belongs to Sale; SaleReturnItem belongs to SaleReturn and original SaleItem.
- StockReceipt belongs to optional Supplier; StockReceiptItem belongs to StockReceipt and Product.
- InventoryMovement references Product and stores document identity through `reference_type` and `reference_id`.

## Business Invariants

- Money, quantity, cost, price and profit use `Decimal`/`DecimalField`, never float.
- `Product.current_stock` is cached state; `InventoryMovement` is the auditable ledger.
- Stock cannot become negative.
- Completed sales, posted receipts, movements and audit logs are not physically deleted through normal flows.
- Product cost changes never recalculate historical sale items.
- Sale totals are derived from persisted sale items on the backend.
- Client never sends authoritative cost, profit or stock-after values.
- Historical sale edits must go through a correction service with required reason and audit log.
- Returns cannot exceed remaining returnable quantity.
- Duplicate request keys must return the original result, not create a second sale.

## Critical Transactions

- Posting receipt: lock receipt and products, create `RECEIPT` movements, update stock and current cost, mark posted.
- Cancelling receipt: lock receipt and products, ensure reversal will not create negative stock, create compensating movements.
- Completing sale: lock idempotency key and products with `select_for_update`, validate stock, create sale/items/movements, decrement stock.
- Returning sale: lock sale items/products, validate remaining return quantity, create return/items/movements, update sale status.
- Cancelling sale: lock sale/products, create `SALE_CANCEL` movements, restore stock, mark cancelled.
- Correcting sale: lock sale/products, persist old/new snapshots, apply stock deltas, recalculate totals, write audit log.

## API Endpoints

```text
/api/auth/token/
/api/auth/token/refresh/
/api/auth/me/
/api/products/
/api/products/{id}/
/api/categories/
/api/inventory/movements/
/api/inventory/adjustments/
/api/purchases/receipts/
/api/purchases/receipts/{id}/post/
/api/purchases/receipts/{id}/cancel/
/api/sales/
/api/sales/{id}/
/api/sales/{id}/cancel/
/api/sales/{id}/returns/
/api/sales/{id}/correct/
/api/reports/dashboard/
/api/reports/sales/
/api/reports/products/
/api/reports/operators/
/api/schema/
/api/docs/
```

## POS Screens

- `/login`: operator/admin login.
- `/operator`: fast POS workspace with product search, cart table, quantity/unit price/line total editing, sticky sale totals and checkout.
- `/operator/sales`: allowed sale history.
- `/operator/sales/[id]`: sale document details.

## Risks And Defaults

- PostgreSQL is the production target. Local development defaults to SQLite only for easy startup; concurrency safety is still implemented through transactions and row locks where supported.
- Current cost model is intentionally simple: latest receipt may update `Product.cost_price`. This rule is isolated in purchase services for future FIFO/average-cost replacement.
- Below-cost sale policy defaults to `warn`, not deny. The backend calculates negative profit and can later enforce stricter policy centrally.
- CSV export is included first; XLSX can be added without changing report query contracts.
