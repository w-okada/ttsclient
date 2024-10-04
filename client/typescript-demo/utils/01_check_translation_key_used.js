// Script.1 jsonの中にあるkeyがソースコードで使われているかをチェックする

const fs = require("fs");
const path = require("path");
const glob = require("glob");

//  Constants
const jsonFilePath = path.join("public/assets/i18n/en/translation.json");
const srcFolderPath = path.join("src");

// Function to read JSON keys
function getJsonKeys(filePath) {
    const jsonData = JSON.parse(fs.readFileSync(filePath, "utf8"));
    return Object.keys(jsonData);
}

// Function to search for key usage in files
async function searchKeyUsageInFiles(keys, folderPath) {
    const pattern = `${folderPath}/**/*.tsx`;
    const files = await glob.glob(pattern);
    console.log(files);

    const keyUsageMap = keys.reduce((acc, key) => {
        acc[key] = false;
        return acc;
    }, {});

    files.forEach((file) => {
        const content = fs.readFileSync(file, "utf8");
        keys.forEach((key) => {
            const regex = new RegExp(`t\\(['"\`]${key}['"\`]\\)`, "g");
            if (regex.test(content)) {
                keyUsageMap[key] = true;
            }
        });
    });
    Object.entries(keyUsageMap).forEach(([key, used]) => {
        console.log(`${used ? "    " : "****"} ${key}: ${used ? "Found" : "Not Found"}`);
    });
}

// Main execution
const keys = getJsonKeys(jsonFilePath);
// console.log(keys);
searchKeyUsageInFiles(keys, srcFolderPath);
