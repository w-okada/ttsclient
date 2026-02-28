import { uploadFileChunk, concatUploadedFileChunk } from "./endpoints";

const CHUNK_SIZE = 1024 * 1024; // 1MB
const MAX_CONCURRENT = 10;

export type UploadProgressCallback = (progress: number) => void;

export const uploadFile = async (
  file: File,
  onProgress?: UploadProgressCallback,
): Promise<string> => {
  const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
  let completedChunks = 0;

  // Split file into chunks and upload with concurrency limit
  const chunkIndexes = Array.from({ length: totalChunks }, (_, i) => i);

  const uploadChunk = async (index: number) => {
    const start = index * CHUNK_SIZE;
    const end = Math.min(start + CHUNK_SIZE, file.size);
    const chunk = file.slice(start, end);
    await uploadFileChunk(chunk, file.name, index);
    completedChunks++;
    onProgress?.(completedChunks / totalChunks);
  };

  // Process chunks with concurrency limit
  const pool: Promise<void>[] = [];
  for (const index of chunkIndexes) {
    const task = uploadChunk(index);
    pool.push(task);
    if (pool.length >= MAX_CONCURRENT) {
      await Promise.race(pool);
      // Remove completed promises
      for (let i = pool.length - 1; i >= 0; i--) {
        const settled = await Promise.race([pool[i].then(() => true), Promise.resolve(false)]);
        if (settled) pool.splice(i, 1);
      }
    }
  }
  await Promise.all(pool);

  // Concat chunks
  const result = await concatUploadedFileChunk(file.name, totalChunks);
  return result.generated_filename;
};
