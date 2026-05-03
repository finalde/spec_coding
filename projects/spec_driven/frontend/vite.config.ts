/// <reference types="vitest" />
import { defineConfig, type ProxyOptions } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

// SPA build emits to ../backend/static so `make run-prod` serves a single process.
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: resolve(__dirname, "..", "backend", "static"),
    emptyOutDir: true,
    sourcemap: true,
  },
  server: {
    host: "127.0.0.1",
    port: 5173,
    proxy: (() => {
      const target = "http://127.0.0.1:8765";
      const rewriteOrigin: ProxyOptions = {
        target,
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on("proxyReq", (proxyReq) => {
            proxyReq.setHeader("origin", target);
          });
        },
      };
      return {
        "/api": rewriteOrigin,
        "/file": rewriteOrigin,
        "/project": rewriteOrigin,
      };
    })(),
  },
  test: {
    environment: "jsdom",
    environmentOptions: {
      jsdom: { url: "http://127.0.0.1:8765" },
    },
    globals: true,
    setupFiles: ["./test/setup.ts"],
    include: ["test/**/*.test.{ts,tsx}", "src/**/*.test.{ts,tsx}"],
  },
});
