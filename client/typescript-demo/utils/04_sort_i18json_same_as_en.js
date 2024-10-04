// Script.4 英語josnと日本語jsonのキーの順番を統一する。

const fs = require("fs");
const path = require("path");
// ファイルを読み込む関数
function readJsonFile(filepath) {
    return JSON.parse(fs.readFileSync(filepath, "utf-8"));
}

// JSONオブジェクトをファイルへ書き込む関数
function writeJsonFile(filepath, data) {
    fs.writeFileSync(filepath, JSON.stringify(data, null, 2), "utf-8");
}

const jsonFilePathEn = path.join("public/assets/i18n/en/translation.json");
const jsonFilePathJa = path.join("public/assets/i18n/ja/translation.json");

// ファイルAとファイルBの内容を取得
const fileA = readJsonFile(jsonFilePathEn);
const fileB = readJsonFile(jsonFilePathJa);

// ファイルAのキーの順番に従ってファイルBを並べ替える
function reorderKeys(template, target) {
    let ordered = {};
    for (let key of Object.keys(template)) {
        if (target.hasOwnProperty(key)) {
            ordered[key] = target[key];
        }
    }
    return ordered;
}

const reorderedFileB = reorderKeys(fileA, fileB);

// 結果を新しいファイルに書き込む
writeJsonFile(jsonFilePathJa, reorderedFileB);

console.log("ファイルBがファイルAのキー順に並べ替えられ、保存されました。");
