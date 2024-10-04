const { execSync } = require("child_process");
const fs = require("fs");

// license-checker を使用してライセンス情報を取得
let rawData;
try {
    rawData = execSync("npx license-checker --json", { encoding: "utf-8" });
} catch (error) {
    console.error("Error executing license-checker:", error);
    process.exit(1);
}

const licenses = JSON.parse(rawData);

// 上書き処理
overwrite = [
    {
        targetModule: "tree-dump",
        correctedLicense: "Apache-2.0",
        licenseURL: "https://github.com/streamich/tree-dump/blob/master/LICENSE",
    },
    {
        targetModule: "thingies",
        correctedLicense: "MIT",
        licenseURL: "https://github.com/streamich/thingies/blob/main/LICENSE",
    },
];

for (let item of overwrite) {
    targetModule = item.targetModule;
    correctedLicense = item.correctedLicense;
    licenseURL = item.licenseURL;
    Object.keys(licenses).forEach((packageName) => {
        if (packageName.includes(targetModule)) {
            licenses[packageName].licenses = correctedLicense;
            licenses[packageName].licenseURL = licenseURL;
        }
    });
}

// ライセンスごとに依存関係をソート
const sortedLicenses = {};
Object.keys(licenses).forEach((packageName) => {
    const licenseType = licenses[packageName].licenses;
    if (!sortedLicenses[licenseType]) {
        sortedLicenses[licenseType] = [];
    }
    sortedLicenses[licenseType].push({
        name: packageName,
        version: licenses[packageName].version,
        repository: licenses[packageName].repository || "",
        licenseURL: licenses[packageName].licenseURL || "",
    });
});

fs.writeFileSync("public/licenses-js.json", JSON.stringify(sortedLicenses, null, 2));
