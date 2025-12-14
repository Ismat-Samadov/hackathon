import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Space Colonization - Build Your Galactic Empire",
  description: "An engaging space colonization strategy game. Manage resources, colonize planets, research technologies, and expand across the galaxy! No login required.",
  keywords: ["space game", "strategy game", "colonization", "browser game", "idle game"],
  authors: [{ name: "Space Colonization Team" }],
  appleWebApp: {
    capable: true,
    statusBarStyle: "black-translucent",
    title: "Space Colonization",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: "#581c87",
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
