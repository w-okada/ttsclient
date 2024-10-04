// Script.3 英語josnと日本語jsonのキーの差分を出す。

const fs = require("fs");
const path = require("path");
const glob = require("glob");

//  Constants
const jsonFilePathEn = path.join("public/assets/i18n/en/translation.json");
const jsonFilePathJa = path.join("public/assets/i18n/ja/translation.json");

// Function to read JSON keys
function getJsonKeys(filePath) {
    const jsonData = JSON.parse(fs.readFileSync(filePath, "utf8"));
    return Object.keys(jsonData);
}
// Main execution
const keysEn = getJsonKeys(jsonFilePathEn);
const keysJa = getJsonKeys(jsonFilePathJa);

console.log("--- Only in English Check:");
keysEn.forEach((key) => {
    if (!keysJa.includes(key)) {
        console.log(`**** ${key}`);
    } else {
        console.log(`     ${key}`);
    }
});

console.log("--- Only in Japanese Check:");
keysJa.forEach((key) => {
    if (!keysEn.includes(key)) {
        console.log(`**** ${key}`);
    } else {
        console.log(`     ${key}`);
    }
});
