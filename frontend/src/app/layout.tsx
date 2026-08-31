import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "POS",
  description: "Склад и продажи"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
