"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { LogOut, Minus, Plus, ShoppingCart, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";

import { clearTokens, createSale, getToken, searchProducts } from "@/lib/api";
import { money, quantity as formatQuantity } from "@/lib/format";
import type { ApiError, Product } from "@/types/api";

type CartItem = {
  product: Product;
  quantity: string;
  unitPrice: string;
  totalPrice: string;
};

function toNumber(value: string) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

const inputClass = "h-10 rounded-md border border-line px-2 outline-none focus:border-accent";
const mobileInputClass = "h-12 w-full rounded-md border border-line px-3 text-lg font-semibold outline-none focus:border-accent";
const belowCostInputClass =
  "h-10 rounded-md border border-danger bg-red-50 px-2 font-semibold text-danger outline-none shadow-[0_0_0_3px_rgba(180,35,24,0.14)] focus:border-danger";
const belowCostMobileInputClass =
  "h-12 w-full rounded-md border border-danger bg-red-50 px-3 text-lg font-semibold text-danger outline-none shadow-[0_0_0_3px_rgba(180,35,24,0.14)] focus:border-danger";

export default function OperatorPage() {
  const router = useRouter();
  const touchStartX = useRef<number | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    if (!getToken()) router.push("/login");
  }, [router]);

  useEffect(() => {
    const handle = window.setTimeout(async () => {
      try {
        setLoading(true);
        const data = await searchProducts("");
        setProducts(data.results);
      } catch {
        if (!getToken()) router.push("/login");
      } finally {
        setLoading(false);
      }
    }, 180);
    return () => window.clearTimeout(handle);
  }, [router]);

  const totals = useMemo(() => {
    const revenue = cart.reduce((sum, item) => sum + toNumber(item.totalPrice), 0);
    return { revenue };
  }, [cart]);

  function addProduct(product: Product) {
    setSuccess("");
    setError("");
    setCart((current) => {
      const existing = current.find((item) => item.product.id === product.id);
      if (existing) {
        return current.map((item) => {
          if (item.product.id !== product.id) return item;
          const nextQuantity = String(toNumber(item.quantity) + 1);
          return { ...item, quantity: nextQuantity, totalPrice: String(toNumber(nextQuantity) * toNumber(item.unitPrice)) };
        });
      }
      return [...current, { product, quantity: "1", unitPrice: product.sale_price, totalPrice: product.sale_price }];
    });
  }

  function updateQuantity(productId: number, value: string) {
    setCart((current) => current.map((item) => (item.product.id === productId ? { ...item, quantity: value, totalPrice: String(toNumber(value) * toNumber(item.unitPrice)) } : item)));
  }

  function stepQuantity(productId: number, delta: number) {
    setCart((current) =>
      current.map((item) => {
        if (item.product.id !== productId) return item;
        const nextQuantity = Math.max(0.001, toNumber(item.quantity) + delta);
        return { ...item, quantity: String(nextQuantity), totalPrice: String(nextQuantity * toNumber(item.unitPrice)) };
      })
    );
  }

  function updateUnitPrice(productId: number, value: string) {
    setCart((current) => current.map((item) => (item.product.id === productId ? { ...item, unitPrice: value, totalPrice: String(toNumber(item.quantity) * toNumber(value)) } : item)));
  }

  function updateTotalPrice(productId: number, value: string) {
    setCart((current) => current.map((item) => (item.product.id === productId ? { ...item, totalPrice: value, unitPrice: item.quantity === "0" ? "0" : String(toNumber(value) / toNumber(item.quantity)) } : item)));
  }

  async function checkout() {
    setCheckoutLoading(true);
    setError("");
    setSuccess("");
    try {
      const sale = await createSale(
        cart.map((item) => ({
          product_id: item.product.id,
          quantity: item.quantity,
          total_price: item.totalPrice
        }))
      );
      setSuccess(`Продажа ${sale.number} завершена. Сумма: ${money(sale.total)}`);
      setCart([]);
      const fresh = await searchProducts("");
      setProducts(fresh.results);
    } catch (err) {
      const apiError = err as ApiError;
      const message = typeof apiError.message === "string" ? apiError.message : "Не удалось завершить продажу.";
      setError(message);
    } finally {
      setCheckoutLoading(false);
    }
  }

  function logout() {
    clearTokens();
    router.push("/login");
  }

  function handleCartTouchStart(event: React.TouchEvent) {
    const target = event.target as HTMLElement;
    if (target.closest("input,button")) {
      touchStartX.current = null;
      return;
    }
    touchStartX.current = event.touches[0]?.clientX ?? null;
  }

  function handleCartTouchEnd(event: React.TouchEvent, productId: number) {
    const startX = touchStartX.current;
    touchStartX.current = null;
    if (startX === null) return;
    const endX = event.changedTouches[0]?.clientX ?? startX;
    const deltaX = endX - startX;
    if (Math.abs(deltaX) < 70) return;
    stepQuantity(productId, deltaX > 0 ? 1 : -1);
  }

  const cartRows = cart.map((item) => {
    const actualUnitPrice = toNumber(item.unitPrice);
    const costPrice = toNumber(item.product.cost_price);
    const belowCost = actualUnitPrice < costPrice;
    return { item, belowCost };
  });

  return (
    <main className="min-h-screen bg-panel pb-32 md:pb-0">
      <header className="sticky top-0 z-20 flex h-11 items-center justify-between border-b border-line bg-white px-2 md:h-14 md:px-4">
        <div className="flex items-center gap-2 font-semibold">
          <ShoppingCart size={20} />
          Касса
        </div>
        <button onClick={logout} className="inline-flex h-8 items-center gap-2 rounded-md border border-line bg-white px-2 text-sm md:h-9 md:px-3">
          <LogOut size={16} />
          Выйти
        </button>
      </header>

      <div className="grid gap-2 p-2 md:gap-4 md:p-4 lg:grid-cols-[minmax(320px,420px)_1fr]">
        <section className="overflow-hidden rounded-md border border-line bg-white">
          <div className="max-h-[31vh] overflow-auto overscroll-contain md:max-h-[calc(100vh-150px)]">
            {loading ? <div className="p-4 text-muted">Загрузка...</div> : null}
            {!loading && products.length === 0 ? <div className="p-4 text-muted">По запросу ничего не найдено</div> : null}
            {products.map((product) => (
              <button key={product.id} onClick={() => addProduct(product)} className="grid w-full grid-cols-[58px_1fr_auto] items-center gap-2 border-b border-line p-2 text-left active:bg-emerald-50 md:grid-cols-[64px_1fr] md:gap-3 md:p-3 md:hover:bg-panel">
                <div className="grid h-[58px] w-[58px] place-items-center overflow-hidden rounded-md border border-line bg-panel text-xs text-muted md:h-16 md:w-16">
                  {product.image_url ? <img src={product.image_url} alt="" className="h-full w-full object-cover" /> : "Фото"}
                </div>
                <div className="min-w-0">
                  <div className="line-clamp-1 font-semibold md:truncate">{product.name}</div>
                  <div className="text-sm text-muted">SKU: {product.sku}</div>
                  <div className="mt-0.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm">
                    <span>{formatQuantity(product.current_stock, product.unit_display)}</span>
                    <span className="font-semibold">{money(product.sale_price)}</span>
                  </div>
                </div>
                <span className="grid h-10 w-10 place-items-center rounded-full bg-accent text-white md:hidden">
                  <Plus size={20} />
                </span>
              </button>
            ))}
          </div>
        </section>

        <section className="flex min-h-[48vh] flex-col overflow-hidden rounded-md border border-line bg-white md:min-h-[calc(100vh-88px)]">
          <div className="hidden grid-cols-[1fr_110px_130px_140px_44px] gap-2 border-b border-line px-3 py-2 text-sm font-semibold text-muted md:grid">
            <span>Товар</span>
            <span>Кол-во</span>
            <span>Цена</span>
            <span>Сумма</span>
            <span />
          </div>
          <div className="flex-1 overflow-auto overscroll-contain">
            {cart.length === 0 ? <div className="p-6 text-muted">Текущая продажа пустая</div> : null}
            <div className="md:hidden">
              {cartRows.map(({ item, belowCost }) => {
                return (
                  <article
                    key={item.product.id}
                    className={`touch-pan-y border-b border-line p-2 active:bg-panel ${belowCost ? "bg-red-50/60" : ""}`}
                    onTouchStart={handleCartTouchStart}
                    onTouchEnd={(event) => handleCartTouchEnd(event, item.product.id)}
                  >
                    <div className="flex gap-3">
                      <div className="grid h-16 w-16 shrink-0 place-items-center overflow-hidden rounded-md border border-line bg-panel text-xs text-muted">
                        {item.product.image_url ? <img src={item.product.image_url} alt="" className="h-full w-full object-cover" /> : "Фото"}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="line-clamp-2 font-semibold leading-tight">{item.product.name}</div>
                        <div className="mt-1 text-sm text-muted">{item.product.sku}</div>
                        {belowCost ? <div className="mt-1 rounded-md bg-white px-2 py-1 text-xs font-semibold text-danger">Минус. Себестоимость: {money(item.product.cost_price)}</div> : null}
                      </div>
                      <button className="grid h-11 w-11 shrink-0 place-items-center rounded-md border border-line bg-white" onClick={() => setCart((current) => current.filter((row) => row.product.id !== item.product.id))} aria-label="Удалить товар">
                        <Trash2 size={18} />
                      </button>
                    </div>

                    <div className="mt-2 grid grid-cols-[44px_1fr_44px] items-end gap-2">
                      <button className="grid h-12 place-items-center rounded-md border border-line bg-white active:bg-panel" onClick={() => stepQuantity(item.product.id, -1)} aria-label="Уменьшить количество">
                        <Minus size={18} />
                      </button>
                      <label className="block text-xs font-semibold text-muted">
                        Количество
                        <input inputMode="decimal" className={mobileInputClass} value={item.quantity} onChange={(event) => updateQuantity(item.product.id, event.target.value)} />
                      </label>
                      <button className="grid h-12 place-items-center rounded-md border border-line bg-white active:bg-panel" onClick={() => stepQuantity(item.product.id, 1)} aria-label="Увеличить количество">
                        <Plus size={18} />
                      </button>
                    </div>

                    <div className="mt-2 grid grid-cols-2 gap-2">
                      <label className="block text-xs font-semibold text-muted">
                        Цена
                        <input inputMode="decimal" className={belowCost ? belowCostMobileInputClass : mobileInputClass} value={item.unitPrice} onChange={(event) => updateUnitPrice(item.product.id, event.target.value)} />
                      </label>
                      <label className="block text-xs font-semibold text-muted">
                        Сумма
                        <input inputMode="decimal" className={belowCost ? belowCostMobileInputClass : mobileInputClass} value={item.totalPrice} onChange={(event) => updateTotalPrice(item.product.id, event.target.value)} />
                      </label>
                    </div>
                  </article>
                );
              })}
            </div>
            <div className="hidden md:block">
            {cartRows.map(({ item, belowCost }) => {
              return (
                <div key={item.product.id} className={`grid grid-cols-[1fr_110px_130px_140px_44px] gap-2 border-b border-line p-3 ${belowCost ? "bg-red-50/45" : ""}`}>
                  <div className="min-w-0">
                    <div className="truncate font-medium">{item.product.name}</div>
                    <div className="text-sm text-muted">{item.product.sku}</div>
                    {belowCost ? <div className="mt-1 text-xs font-semibold text-danger">Цена ниже себестоимости: {money(item.product.cost_price)}</div> : null}
                  </div>
                  <input inputMode="decimal" className={inputClass} value={item.quantity} onChange={(event) => updateQuantity(item.product.id, event.target.value)} />
                  <input inputMode="decimal" className={belowCost ? belowCostInputClass : inputClass} value={item.unitPrice} onChange={(event) => updateUnitPrice(item.product.id, event.target.value)} />
                  <input inputMode="decimal" className={belowCost ? belowCostInputClass : inputClass} value={item.totalPrice} onChange={(event) => updateTotalPrice(item.product.id, event.target.value)} />
                  <button className="grid h-10 place-items-center rounded-md border border-line" onClick={() => setCart((current) => current.filter((row) => row.product.id !== item.product.id))}>
                    <Trash2 size={17} />
                  </button>
                </div>
              );
            })}
            </div>
          </div>
          <footer className="fixed inset-x-0 bottom-0 z-30 border-t border-line bg-white p-2 shadow-[0_-8px_24px_rgba(16,24,40,0.12)] md:sticky md:p-4 md:shadow-none">
            {error ? <div className="mb-3 rounded-md border border-danger/30 bg-red-50 p-3 text-sm text-danger">{error}</div> : null}
            {success ? <div className="mb-3 rounded-md border border-accent/30 bg-emerald-50 p-3 text-sm text-accent">{success}</div> : null}
            <div className="flex flex-wrap items-center justify-between gap-2 md:gap-3">
              <div>
                <div className="text-sm text-muted">Итого</div>
                <div className="text-2xl font-semibold md:text-3xl">{money(totals.revenue)}</div>
              </div>
              <div className="grid w-full grid-cols-[48px_1fr] gap-2 sm:w-auto sm:grid-cols-none sm:flex">
                <button onClick={() => setCart([])} disabled={cart.length === 0 || checkoutLoading} className="inline-flex h-12 items-center justify-center gap-2 rounded-md border border-line px-3 disabled:opacity-50 sm:px-4" aria-label="Очистить продажу">
                  <Minus size={18} />
                  <span className="hidden sm:inline">Очистить</span>
                </button>
                <button onClick={checkout} disabled={cart.length === 0 || checkoutLoading} className="inline-flex h-12 items-center justify-center gap-2 rounded-md bg-accent px-5 font-semibold text-white disabled:opacity-60">
                  <Plus size={18} />
                  {checkoutLoading ? "Проведение..." : "Завершить продажу"}
                </button>
              </div>
            </div>
          </footer>
        </section>
      </div>
    </main>
  );
}
