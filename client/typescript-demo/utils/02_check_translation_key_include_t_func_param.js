// Script.2 ソースコードで使われているかキーがjsonにあるかをチェックする

const fs = require("fs");
const path = require("path");
const glob = require("glob");

// Constants
const jsonFilePath = path.join("public/assets/i18n/en/translation.json");
const srcFolderPath = path.join("src");

// Function to read JSON keys
function getJsonKeys(filePath) {
    const jsonData = JSON.parse(fs.readFileSync(filePath, "utf8"));
    return Object.keys(jsonData);
}

// Function to extract keys from source files
async function extractKeysFromFiles(folderPath) {
    const pattern = `${folderPath}/**/*.tsx`;
    const files = await glob.glob(pattern);
    const extractedKeys = new Set();
    const keyRegex = /t\(['"`]([^'"`]+)['"`]\)/g;
    files.forEach((file) => {
        const content = fs.readFileSync(file, "utf8");
        let match;
        while ((match = keyRegex.exec(content)) !== null) {
            extractedKeys.add(match[1]);
        }
    });
    // console.log("extractedKeys", extractedKeys);
    return Array.from(extractedKeys);
}

// Function to check if keys exist in JSON
function checkKeysInJson(extractedKeys, jsonKeys) {
    const missingKeys = extractedKeys.filter((key) => !jsonKeys.includes(key));

    if (missingKeys.length > 0) {
        console.log(`Missing keys in ${jsonFilePath}:`);
        missingKeys.forEach((key) => console.log(key));
    } else {
        console.log("All keys are present in the translation file.");
    }
}

// Main execution
async function main() {
    const jsonKeys = getJsonKeys(jsonFilePath);
    const extractedKeys = await extractKeysFromFiles(srcFolderPath);
    checkKeysInJson(extractedKeys, jsonKeys);
}

main().catch((err) => console.error("Error:", err));
