import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = {
  title: "AIRON Native · SYNTRIASS Labs",
  description:
    "Enterprise-Owned Sovereign Intelligence",
  icons: { icon: "/brand/syntriass-mark.png" },
};
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
