import type { NextConfig } from "next";

const nextConfig: NextConfig = {
	output: process.env.DOCKER ? "standalone" : "export",
	reactCompiler: true,
};

export default nextConfig;
