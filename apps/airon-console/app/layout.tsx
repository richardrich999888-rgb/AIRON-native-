import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = {
  title: "AIRON Native · SYNTRIASS Labs",
  description:
    "Enterprise-Owned Sovereign Intelligence",
  manifest: "/manifest.webmanifest",
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "any" },
      { url: "/brand/icon.png", type: "image/png", sizes: "64x64" },
      { url: "/brand/icon-512.png", type: "image/png", sizes: "512x512" },
    ],
    apple: { url: "/brand/icon-180.png", sizes: "180x180" },
  },
};
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
