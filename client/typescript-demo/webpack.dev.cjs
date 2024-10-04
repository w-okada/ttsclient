const path = require("path");
const { merge } = require("webpack-merge");
const common = require("./webpack.common.cjs");

module.exports = merge(common, {
    mode: "development",
    devServer: {
        static: {
            directory: path.join(__dirname, "public"),
        },
        client: {
            overlay: {
                errors: false,
                warnings: false,
            },
        },
        host: "0.0.0.0",
        server: "https",
        proxy: [
            {
                context: ["/api"],
                target: "http://localhost:18000",
                changeOrigin: true,
                secure: false,
                onProxyReq: (proxyReq, req, res) => {
                    console.log(`Proxying request to: ${proxyReq.path}`);
                },
            },
            {
                context: ["/model_dir"],
                target: "http://localhost:18000",
                changeOrigin: true,
                secure: false,
                onProxyReq: (proxyReq, req, res) => {
                    console.log(`Proxying request to: ${proxyReq.path}`);
                },
            },
            {
                context: ["/voice_characters"],
                target: "http://localhost:18000",
                changeOrigin: true,
                secure: false,
                onProxyReq: (proxyReq, req, res) => {
                    console.log(`Proxying request to: ${proxyReq.path}`);
                },
            },
        ],
    },
});
