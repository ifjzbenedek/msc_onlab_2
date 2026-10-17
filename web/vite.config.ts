import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const BACKEND_URL = "http://127.0.0.1:8000";
const DEV_SERVER_PORT = 5000;

export default defineConfig({
    plugins: [react()],
    server: {
        port: DEV_SERVER_PORT,
        strictPort: true,
        proxy: {
            "/ask": BACKEND_URL,
            "/health": BACKEND_URL,
        },
    },
});
