import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    // Enable React Compiler (optional, if you need React optimizations)
    reactCompiler: true,

    // Optional: if you want to silence Turbopack root warnings
    turbopack: {
        root: __dirname, // Sets the correct root directory
    },

    // Enable standalone output for Docker
    output: 'standalone',

};

export default nextConfig;
