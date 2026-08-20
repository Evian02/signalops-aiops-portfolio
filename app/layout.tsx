import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000",
  ),
  title: "SignalOps | AIOps Log Intelligence",
  description:
    "A small learning demo for structured log analysis, baseline comparison, and rule-based alerts.",
  openGraph: {
    title: "SignalOps | AIOps Log Intelligence",
    description:
      "A learning demo using synthetic logs, static baselines, and readable detection rules.",
    type: "website",
    images: [{ url: "/og.png", width: 1200, height: 630, alt: "SignalOps - AIOps Log Intelligence" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "SignalOps | AIOps Log Intelligence",
    description:
      "A learning demo using synthetic logs, static baselines, and readable detection rules.",
    images: ["/og.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
