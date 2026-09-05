import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

/**
 * Vite config for the ATS frontend.
 * Proxies /api to the FastAPI backend during development.
 * base '/ATS/' so the production build works under the GitHub Pages
 * subpath (https://rabziaur77.github.io/ATS/); dev keeps BASE_URL = '/'.
 */
export default defineConfig({
  base: "/ATS/",
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
