import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = {
  title: "AIRON Native · SYNTRIASS Labs",
  description:
    "Enterprise-Owned Sovereign Intelligence",
  icons: { icon: { url: "/brand/icon.png", type: "image/png", sizes: "64x64" } },
};
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
