import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const frontendPort = Number(env.FRONTEND_PORT ?? 5173);
  const backendPort = Number(env.BACKEND_PORT ?? 8000);
  const backendHost = env.BACKEND_HOST ?? "127.0.0.1";
  const backendUrl = env.BACKEND_URL ?? `http://${backendHost}:${backendPort}`;

  return {
    plugins: [react()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
      host: env.FRONTEND_HOST ?? "127.0.0.1",
      port: frontendPort,
      strictPort: false,
      proxy: {
        "/api": {
          target: backendUrl,
          changeOrigin: false,
        },
      },
    },
  };
});
