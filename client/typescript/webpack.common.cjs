const path = require("path");
module.exports = {
    entry: "./src/index.ts",
    resolve: {
        extensions: [".ts", ".js"],
    },
    module: {
        rules: [
            {
                test: [/\.ts$/, /\.tsx$/],
                use: [
                    {
                        loader: "ts-loader",
                        options: {
                            configFile: "tsconfig.json",
                        },
                    },
                ],
            },
        ],
    },
    output: {
        filename: "index.mjs",
        path: path.resolve(__dirname, "dist"),
        libraryTarget: "module",
        globalObject: "typeof self !== 'undefined' ? self : this",
    },
    experiments: {
        outputModule: true,
    },
};
