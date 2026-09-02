import React from "react";
import type { Metadata } from "next";


import "./globals.css";

export const metadata: Metadata = {
  title: "RecoverAI - Autonomous Payment Recovery System",
  description: "Autonomous payment recovery engine with AI recommendations and human approval",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className="h-full antialiased"
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col" suppressHydrationWarning>{children}</body>
    </html>
  );
}
