import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "QuizVeda Admin",
  description: "Secure content operations console for QuizVeda",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
