export function money(value: string | number) {
  const numeric = Number(value);
  return new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 2 }).format(Number.isFinite(numeric) ? numeric : 0);
}

export function quantity(value: string | number, unit: string) {
  const numeric = Number(value);
  return `${new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 3 }).format(Number.isFinite(numeric) ? numeric : 0)} ${unit}`;
}
