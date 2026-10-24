/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The browser only ever talks to this dev server, which proxies /api to the backend (same-origin
// from the browser's point of view). That keeps cookies working and means the frontend needs no
// knowledge of backend topology — see docs/adr/0001.
export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173,
    // Preview/sandbox hosts are proxied; the dev server must accept their Host header.
    allowedHosts: true,
    proxy: {
      "/api": {
        target: process.env.TALIMGO_API_TARGET ?? "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  preview: {
    host: "0.0.0.0",
    port: 4173,
    allowedHosts: true,
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test-setup.ts"],
    include: ["src/**/*.test.{ts,tsx}"],
  },
});
