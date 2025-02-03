import type { NextConfig } from "next";

const nextConfig: NextConfig = {
	/* config options here */
	transpilePackages: ["geist"],
	async rewrites() {
		return [
			{
				source: "/api/:path*",
				destination: `http://localhost:8000/api/:path*`,
			},
		];
	},
	images: {
		formats: ["image/avif", "image/webp"],
		remotePatterns: [
			{
				protocol: "https",
				hostname: "exitocol.vtexassets.com",
				port: "",
				pathname: "/arquivos/**",
			},
		],
	},
};

export default nextConfig;
