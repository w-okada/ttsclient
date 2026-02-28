import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:18000",
        changeOrigin: true,
      },
      "/get_proxy": {
        target: "http://localhost:18000",
        changeOrigin: true,
      },
    },
  },
});
