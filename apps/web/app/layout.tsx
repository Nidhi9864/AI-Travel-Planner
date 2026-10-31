import type { Metadata } from "next";
import { Geist } from "next/font/google";

import { Providers } from "@/components/shell/Providers";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Travel Planner",
  description:
    "Describe a trip and get a day-by-day, costed itinerary you can edit. Plans are drafts with labelled estimates.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${geistSans.variable} h-full antialiased`}>
      <body className="min-h-full">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
