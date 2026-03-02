/** Parse a WAV file and extract PCM data and format info. */
function parseWav(buffer: ArrayBuffer) {
  const view = new DataView(buffer);

  // Verify RIFF header
  const riff = String.fromCharCode(view.getUint8(0), view.getUint8(1), view.getUint8(2), view.getUint8(3));
  if (riff !== "RIFF") throw new Error("Invalid WAV: missing RIFF header");

  const wave = String.fromCharCode(view.getUint8(8), view.getUint8(9), view.getUint8(10), view.getUint8(11));
  if (wave !== "WAVE") throw new Error("Invalid WAV: missing WAVE header");

  // Find fmt and data chunks
  let offset = 12;
  let numChannels = 0;
  let sampleRate = 0;
  let bitsPerSample = 0;
  let dataOffset = 0;
  let dataSize = 0;

  while (offset < buffer.byteLength) {
    const chunkId = String.fromCharCode(
      view.getUint8(offset),
      view.getUint8(offset + 1),
      view.getUint8(offset + 2),
      view.getUint8(offset + 3),
    );
    const chunkSize = view.getUint32(offset + 4, true);

    if (chunkId === "fmt ") {
      numChannels = view.getUint16(offset + 10, true);
      sampleRate = view.getUint32(offset + 12, true);
      bitsPerSample = view.getUint16(offset + 22, true);
    } else if (chunkId === "data") {
      dataOffset = offset + 8;
      dataSize = chunkSize;
    }

    offset += 8 + chunkSize;
  }

  if (sampleRate === 0 || dataOffset === 0) {
    throw new Error("Invalid WAV: missing fmt or data chunk");
  }

  return {
    numChannels,
    sampleRate,
    bitsPerSample,
    pcmData: new Uint8Array(buffer, dataOffset, dataSize),
  };
}

/** Build a WAV file from raw PCM data. */
function buildWav(pcmData: Uint8Array, numChannels: number, sampleRate: number, bitsPerSample: number): ArrayBuffer {
  const byteRate = (sampleRate * numChannels * bitsPerSample) / 8;
  const blockAlign = (numChannels * bitsPerSample) / 8;
  const headerSize = 44;
  const buffer = new ArrayBuffer(headerSize + pcmData.byteLength);
  const view = new DataView(buffer);

  // RIFF header
  writeString(view, 0, "RIFF");
  view.setUint32(4, 36 + pcmData.byteLength, true);
  writeString(view, 8, "WAVE");

  // fmt chunk
  writeString(view, 12, "fmt ");
  view.setUint32(16, 16, true); // chunk size
  view.setUint16(20, 1, true); // PCM format
  view.setUint16(22, numChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, byteRate, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, bitsPerSample, true);

  // data chunk
  writeString(view, 36, "data");
  view.setUint32(40, pcmData.byteLength, true);
  new Uint8Array(buffer, headerSize).set(pcmData);

  return buffer;
}

function writeString(view: DataView, offset: number, str: string) {
  for (let i = 0; i < str.length; i++) {
    view.setUint8(offset + i, str.charCodeAt(i));
  }
}

// -40dB relative to 16-bit max amplitude
const SILENCE_THRESHOLD = 0.01;
// Margin to keep around detected content boundaries to avoid clipping
const MARGIN_SEC = 0.002;

/** Read a signed 16-bit little-endian sample from a Uint8Array. */
function readSample16(data: Uint8Array, byteOffset: number): number {
  let value = data[byteOffset] | (data[byteOffset + 1] << 8);
  if (value >= 0x8000) value -= 0x10000;
  return value;
}

/**
 * Find the frame index where audible content ends (exclusive).
 * Scans backwards from the end to find the last sample above the silence threshold.
 */
function findContentEndFrame(
  pcmData: Uint8Array,
  numChannels: number,
  sampleRate: number,
  bitsPerSample: number,
): number {
  const bytesPerSample = bitsPerSample / 8;
  const blockAlign = numChannels * bytesPerSample;
  const totalFrames = Math.floor(pcmData.byteLength / blockAlign);
  const maxVal = 1 << (bitsPerSample - 1);
  const threshold = SILENCE_THRESHOLD * maxVal;
  const marginFrames = Math.ceil(sampleRate * MARGIN_SEC);

  for (let frame = totalFrames - 1; frame >= 0; frame--) {
    for (let ch = 0; ch < numChannels; ch++) {
      const offset = frame * blockAlign + ch * bytesPerSample;
      if (Math.abs(readSample16(pcmData, offset)) > threshold) {
        return Math.min(totalFrames, frame + 1 + marginFrames);
      }
    }
  }
  return totalFrames;
}

/**
 * Find the frame index where audible content starts.
 * Scans forward from the beginning to find the first sample above the silence threshold.
 */
function findContentStartFrame(
  pcmData: Uint8Array,
  numChannels: number,
  sampleRate: number,
  bitsPerSample: number,
): number {
  const bytesPerSample = bitsPerSample / 8;
  const blockAlign = numChannels * bytesPerSample;
  const totalFrames = Math.floor(pcmData.byteLength / blockAlign);
  const maxVal = 1 << (bitsPerSample - 1);
  const threshold = SILENCE_THRESHOLD * maxVal;
  const marginFrames = Math.ceil(sampleRate * MARGIN_SEC);

  for (let frame = 0; frame < totalFrames; frame++) {
    for (let ch = 0; ch < numChannels; ch++) {
      const offset = frame * blockAlign + ch * bytesPerSample;
      if (Math.abs(readSample16(pcmData, offset)) > threshold) {
        return Math.max(0, frame - marginFrames);
      }
    }
  }
  return 0;
}

/**
 * Concatenate multiple WAV blobs into a single WAV blob.
 *
 * Trims trailing/leading silence at segment boundaries (up to `maxTrimSec`),
 * then inserts exactly `silenceDurationSec` of silence between segments.
 * The silence duration represents the gap between the end of audible content
 * in one segment and the start of audible content in the next.
 *
 * @param maxTrimSec - Maximum amount of silence to trim from each boundary (seconds).
 *                     Silence beyond this limit is preserved. Set to 0 to disable trimming.
 */
export async function concatWavBlobs(
  blobs: Blob[],
  silenceDurationSec: number = 0.3,
  maxTrimSec: number = 0.3,
): Promise<Blob> {
  if (blobs.length === 0) throw new Error("No blobs to concatenate");
  if (blobs.length === 1) return blobs[0];

  const parsed = await Promise.all(blobs.map((b) => b.arrayBuffer().then(parseWav)));

  // Use format from first WAV
  const { numChannels, sampleRate, bitsPerSample } = parsed[0];
  const bytesPerSample = bitsPerSample / 8;
  const blockAlign = numChannels * bytesPerSample;
  const maxTrimFrames = Math.floor(maxTrimSec * sampleRate);

  // Trim silence from segment boundaries (capped by maxTrimFrames)
  const trimmedSegments: Uint8Array[] = [];
  for (let i = 0; i < parsed.length; i++) {
    const { pcmData } = parsed[i];
    const totalFrames = Math.floor(pcmData.byteLength / blockAlign);

    let startFrame = 0;
    let endFrame = totalFrames;

    // Trim leading silence (except first segment)
    if (i > 0) {
      const contentStart = findContentStartFrame(pcmData, numChannels, sampleRate, bitsPerSample);
      startFrame = Math.min(contentStart, maxTrimFrames);
      console.debug(
        `[wavConcat] segment ${i}: leading silence=${Math.round((contentStart / sampleRate) * 1000)}ms, trimmed=${Math.round((startFrame / sampleRate) * 1000)}ms`,
      );
    }

    // Trim trailing silence (except last segment)
    if (i < parsed.length - 1) {
      const contentEnd = findContentEndFrame(pcmData, numChannels, sampleRate, bitsPerSample);
      const trailingSilenceFrames = totalFrames - contentEnd;
      const trimFrames = Math.min(trailingSilenceFrames, maxTrimFrames);
      endFrame = totalFrames - trimFrames;
      console.debug(
        `[wavConcat] segment ${i}: trailing silence=${Math.round((trailingSilenceFrames / sampleRate) * 1000)}ms, trimmed=${Math.round((trimFrames / sampleRate) * 1000)}ms`,
      );
    }

    const startByte = startFrame * blockAlign;
    const endByte = endFrame * blockAlign;
    trimmedSegments.push(pcmData.slice(startByte, endByte));
  }

  // Build silence buffer for the gap
  const silenceFrames = Math.round(silenceDurationSec * sampleRate);
  const silenceBytes = silenceFrames * blockAlign;
  const silence = new Uint8Array(silenceBytes); // zero-filled = silence

  // Calculate total size
  let totalSize = 0;
  for (let i = 0; i < trimmedSegments.length; i++) {
    totalSize += trimmedSegments[i].byteLength;
    if (i < trimmedSegments.length - 1) {
      totalSize += silenceBytes;
    }
  }

  // Merge PCM data
  const merged = new Uint8Array(totalSize);
  let offset = 0;
  for (let i = 0; i < trimmedSegments.length; i++) {
    merged.set(trimmedSegments[i], offset);
    offset += trimmedSegments[i].byteLength;
    if (i < trimmedSegments.length - 1) {
      merged.set(silence, offset);
      offset += silenceBytes;
    }
  }

  const wavBuffer = buildWav(merged, numChannels, sampleRate, bitsPerSample);
  return new Blob([wavBuffer], { type: "audio/wav" });
}
