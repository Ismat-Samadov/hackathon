import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Space Colonization - Build Your Galactic Empire",
  description: "An engaging space colonization strategy game. Manage resources, colonize planets, and expand across the galaxy!",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
