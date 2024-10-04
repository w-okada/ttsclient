import { openDB } from "idb";

const DB_NAME = "vcclient";
const DB_VERSION = 1;
const STORE_NAME = "client-setting-store";

export const initDB = async () => {
    openDB(DB_NAME, DB_VERSION, {
        upgrade(db) {
            db.createObjectStore(STORE_NAME);
        },
    });
};

export const setItem = async (key: string, value: any) => {
    const db = await openDB(DB_NAME, DB_VERSION);
    return db.put(STORE_NAME, value, key);
};

export const getItem = async (key: string) => {
    const db = await openDB(DB_NAME, DB_VERSION);
    return db.get(STORE_NAME, key);
};

export const removeItem = async (key: string) => {
    const db = await openDB(DB_NAME, DB_VERSION);
    return db.delete(STORE_NAME, key);
};

export const clearStore = async () => {
    const db = await openDB(DB_NAME, DB_VERSION);
    const tx = db.transaction(STORE_NAME, "readwrite");
    const store = tx.objectStore(STORE_NAME);
    await store.clear();
    await tx.done;
};

export const deleteDatabase = async () => {
    await indexedDB.deleteDatabase(DB_NAME);
};
