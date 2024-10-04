const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const CopyPlugin = require("copy-webpack-plugin");
const webpack = require("webpack");
const { VanillaExtractPlugin } = require("@vanilla-extract/webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = {
    entry: "./src/index.tsx",
    resolve: {
        extensions: [".ts", ".tsx", ".js", ".mjs"],
        fallback: { buffer: false },
    },
    module: {
        rules: [
            {
                test: [/\.ts$/, /\.tsx$/],
                use: [
                    {
                        loader: "babel-loader",
                        options: {
                            presets: ["@babel/preset-env", "@babel/preset-react", "@babel/preset-typescript"],
                            plugins: ["@babel/plugin-transform-runtime"],
                        },
                    },
                ],
            },
            {
                test: /\.html$/,
                loader: "html-loader",
            },
            {
                test: /\.css$/,
                use: [MiniCssExtractPlugin.loader, "css-loader"],
                use: ["style-loader", { loader: "css-loader", options: { importLoaders: 1 } }],
            },
        ],
    },
    output: {
        filename: "index.js",
        path: path.resolve(__dirname, "../../web_front"),
    },
    plugins: [
        new webpack.ProvidePlugin({
            Buffer: ["buffer", "Buffer"],
        }),
        new HtmlWebpackPlugin({
            template: path.resolve(__dirname, "public/index.html"),
            filename: "./index.html",
        }),
        new VanillaExtractPlugin(),
        new MiniCssExtractPlugin({
            filename: "static/chunks/[contenthash].css",
            chunkFilename: "static/chunks/[contenthash].css",
        }),
        new CopyPlugin({
            patterns: [{ from: "public/assets", to: "assets" }],
        }),
        new CopyPlugin({
            patterns: [{ from: "public/favicon.ico", to: "." }],
        }),
        new CopyPlugin({
            patterns: [{ from: "public/licenses-js.json", to: "." }],
        }),
    ],
};
