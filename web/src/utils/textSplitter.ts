import type { CutMethod, LanguageType } from "@/types";

const SPLITS = new Set(["，", "。", "？", "！", ",", ".", "?", "!", "~", ":", "：", "—", "…"]);
const PUNCTUATION = new Set(["!", "?", "…", ",", ".", "-", " "]);
const CUT5_PUNCTS = new Set([",", ".", ";", "?", "!", "、", "，", "。", "？", "！", "；", "：", "…"]);

/** Split text at punctuation boundaries, normalizing "……"→"。" and "——"→"，". */
export function splitAtPunctuation(text: string): string[] {
  let todo = text.replace(/……/g, "。").replace(/——/g, "，");
  if (todo.length === 0) return [];
  if (!SPLITS.has(todo[todo.length - 1])) {
    todo += "。";
  }

  const result: string[] = [];
  let tail = 0;
  for (let head = 0; head < todo.length; head++) {
    if (SPLITS.has(todo[head])) {
      result.push(todo.slice(tail, head + 1));
      tail = head + 1;
    }
  }
  return result;
}

function isPunctuationOnly(text: string): boolean {
  for (const ch of text) {
    if (!PUNCTUATION.has(ch)) return false;
  }
  return true;
}

/** cut0: No slicing. Return text as single element. */
export function cut0(input: string): string[] {
  const trimmed = input.replace(/^\n+|\n+$/g, "");
  return trimmed.length > 0 ? [trimmed] : [];
}

/** cut1: Group every 4 sentences. */
export function cut1(input: string): string[] {
  const inp = input.replace(/^\n+|\n+$/g, "");
  const segments = splitAtPunctuation(inp);

  if (segments.length <= 4) {
    return isPunctuationOnly(inp) ? [] : [inp];
  }

  const result: string[] = [];
  for (let i = 0; i < segments.length; i += 4) {
    const group = segments.slice(i, i + 4).join("");
    if (group.length > 0 && !isPunctuationOnly(group)) {
      result.push(group);
    }
  }
  return result;
}

/** cut2: Split roughly every 50 characters. */
export function cut2(input: string): string[] {
  const inp = input.replace(/^\n+|\n+$/g, "");
  const segments = splitAtPunctuation(inp);

  if (segments.length < 2) {
    return inp.length > 0 ? [inp] : [];
  }

  const result: string[] = [];
  let sum = 0;
  let tmp = "";
  for (const seg of segments) {
    sum += seg.length;
    tmp += seg;
    if (sum > 50) {
      sum = 0;
      result.push(tmp);
      tmp = "";
    }
  }
  if (tmp !== "") {
    result.push(tmp);
  }

  // If last segment is too short, merge with previous
  if (result.length > 1 && result[result.length - 1].length < 50) {
    result[result.length - 2] += result[result.length - 1];
    result.pop();
  }

  return result.filter((item) => !isPunctuationOnly(item));
}

/** cut3: Split by Chinese period "。". */
export function cut3(input: string): string[] {
  const inp = input.replace(/^\n+|\n+$/g, "");
  const stripped = inp.replace(/^。+|。+$/g, "");
  if (stripped.length === 0) return [];
  const parts = stripped.split("。");
  return parts.filter((item) => item.length > 0 && !isPunctuationOnly(item));
}

/** cut4: Split by English period "." (with decimal protection). */
export function cut4(input: string): string[] {
  const inp = input.replace(/^\n+|\n+$/g, "");
  const stripped = inp.replace(/^\.+|\.+$/g, "");
  if (stripped.length === 0) return [];
  // Split by "." that is NOT between digits (decimal protection)
  const parts = stripped.split(/(?<!\d)\.(?!\d)/);
  return parts.filter((item) => item.length > 0 && !isPunctuationOnly(item));
}

/** cut5: Split by every punctuation (with decimal protection). */
export function cut5(input: string): string[] {
  const inp = input.replace(/^\n+|\n+$/g, "");
  if (inp.length === 0) return [];

  const merged: string[] = [];
  let items: string[] = [];

  for (let i = 0; i < inp.length; i++) {
    const char = inp[i];
    if (CUT5_PUNCTS.has(char)) {
      if (char === "." && i > 0 && i < inp.length - 1 && isDigit(inp[i - 1]) && isDigit(inp[i + 1])) {
        // Decimal point: don't split
        items.push(char);
      } else {
        items.push(char);
        merged.push(items.join(""));
        items = [];
      }
    } else {
      items.push(char);
    }
  }

  if (items.length > 0) {
    merged.push(items.join(""));
  }

  return merged.filter((item) => !isPunctuationOnly(item));
}

function isDigit(ch: string): boolean {
  return ch >= "0" && ch <= "9";
}

/** Filter null/empty/whitespace-only texts. Throw if all empty. */
export function processText(texts: (string | null)[]): string[] {
  if (texts.every((text) => text == null || text === " " || text === "\n" || text === "")) {
    throw new Error("All texts are empty");
  }
  return texts.filter((text): text is string => text != null && text !== " " && text !== "") as string[];
}

/** Merge segments shorter than threshold with adjacent segments. */
export function mergeShortText(texts: string[], threshold: number = 5): string[] {
  if (texts.length < 2) return texts;

  const result: string[] = [];
  let text = "";
  for (const ele of texts) {
    text += ele;
    if (text.length >= threshold) {
      result.push(text);
      text = "";
    }
  }
  if (text.length > 0) {
    if (result.length === 0) {
      result.push(text);
    } else {
      result[result.length - 1] += text;
    }
  }
  return result;
}

/** Ensure each segment ends with appropriate punctuation. */
export function ensureEndingPunctuation(texts: string[], language: LanguageType): string[] {
  const endPunct = language === "en" ? "." : "。";
  return texts.map((text) => {
    if (text.length === 0) return text;
    const lastChar = text[text.length - 1];
    if (SPLITS.has(lastChar)) return text;
    return text + endPunct;
  });
}

type CutFunction = (input: string) => string[];

const CUT_FUNCTIONS: Record<CutMethod, CutFunction> = {
  "No slice": cut0,
  "Slice once every 4 sentences": cut1,
  "Slice per 50 characters": cut2,
  "Slice by Chinese punct": cut3,
  "Slice by English punct": cut4,
  "Slice by every punct": cut5,
};

/**
 * Main API: Split text using the specified cut method.
 * Returns an array of text segments ready for TTS.
 */
export function splitText(text: string, cutMethod: CutMethod, language: LanguageType): string[] {
  const cutFn = CUT_FUNCTIONS[cutMethod];
  const segments = cutFn(text);
  const processed = processText(segments);
  const merged = mergeShortText(processed);
  const withPunctuation = ensureEndingPunctuation(merged, language);
  return withPunctuation;
}
