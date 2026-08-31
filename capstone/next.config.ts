import type { NextConfig } from "next";

const isProd = process.env.NODE_ENV === "production";
const internalHost = process.env.TAURI_DEV_HOST || "localhost";

const nextConfig: NextConfig = {
  // Resolve assets from the LAN/TUN host when developing on a physical device.
  // https://v2.tauri.app/start/frontend/nextjs/
  assetPrefix: isProd ? undefined : `http://${internalHost}:3000`,
};

export default nextConfig;
