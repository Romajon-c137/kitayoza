export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type Product = {
  id: number;
  sku: string;
  name: string;
  brand: string;
  model: string;
  size: string;
  unit: string;
  unit_display: string;
  image_url: string;
  cost_price: string;
  sale_price: string;
  current_stock: string;
  is_active: boolean;
};

export type SaleLineInput = {
  product_id: number;
  quantity: string;
  unit_price?: string;
  total_price?: string;
};

export type Sale = {
  id: number;
  number: string;
  total: string;
  total_cost: string;
  profit: string;
  status: string;
};

export type ApiError = {
  code: string;
  message: unknown;
  details: Record<string, unknown>;
};
