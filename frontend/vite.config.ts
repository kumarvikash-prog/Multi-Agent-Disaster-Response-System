import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      /* Mirror production: browser uses relative /api paths; Vite forwards to backend */
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
