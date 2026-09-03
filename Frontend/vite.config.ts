import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

/**
 * Vite config for the ATS frontend.
 * Proxies /api to the FastAPI backend during development.
 */
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
