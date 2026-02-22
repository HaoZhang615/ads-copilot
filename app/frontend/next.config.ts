import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  // Disable StrictMode to prevent double-mount of effects that create
  // WebSocket connections and AudioContext instances.
  reactStrictMode: false,
};

export default nextConfig;
