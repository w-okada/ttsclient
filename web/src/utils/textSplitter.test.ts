import {
  splitAtPunctuation,
  cut0,
  cut1,
  cut2,
  cut3,
  cut4,
  cut5,
  processText,
  mergeShortText,
  ensureEndingPunctuation,
  splitText,
} from "./textSplitter";

// =============================================================
// splitAtPunctuation
// =============================================================

describe("splitAtPunctuation", () => {
  it("should split at basic punctuation", () => {
    expect(splitAtPunctuation("こんにちは。世界。")).toEqual(["こんにちは。", "世界。"]);
  });

  it("should split at multiple punctuation types", () => {
    expect(splitAtPunctuation("hello,world.foo!")).toEqual(["hello,", "world.", "foo!"]);
  });

  it("should replace '……' with '。'", () => {
    expect(splitAtPunctuation("テスト……次")).toEqual(["テスト。", "次。"]);
  });

  it("should replace '——' with '，'", () => {
    expect(splitAtPunctuation("テスト——次")).toEqual(["テスト，", "次。"]);
  });

  it("should add ending punctuation if missing", () => {
    expect(splitAtPunctuation("テスト")).toEqual(["テスト。"]);
  });

  it("should not add extra punctuation if already ends with one", () => {
    expect(splitAtPunctuation("テスト。")).toEqual(["テスト。"]);
  });

  it("should handle empty string", () => {
    expect(splitAtPunctuation("")).toEqual([]);
  });
});

// =============================================================
// cut0
// =============================================================

describe("cut0", () => {
  it("should return text as single element", () => {
    expect(cut0("hello world")).toEqual(["hello world"]);
  });

  it("should strip leading/trailing newlines", () => {
    expect(cut0("\nhello\n")).toEqual(["hello"]);
  });

  it("should return empty array for empty input", () => {
    expect(cut0("")).toEqual([]);
    expect(cut0("\n\n")).toEqual([]);
  });
});

// =============================================================
// cut1
// =============================================================

describe("cut1", () => {
  it("should group every 4 sentences", () => {
    const input = "一。二。三。四。五。六。七。八。";
    const result = cut1(input);
    expect(result).toEqual(["一。二。三。四。", "五。六。七。八。"]);
  });

  it("should return single group if 4 or fewer sentences", () => {
    const input = "一。二。三。";
    const result = cut1(input);
    expect(result).toEqual(["一。二。三。"]);
  });

  it("should filter punctuation-only segments", () => {
    const input = "テスト。";
    const result = cut1(input);
    expect(result).toEqual(["テスト。"]);
  });
});

// =============================================================
// cut2
// =============================================================

describe("cut2", () => {
  it("should split roughly every 50 characters", () => {
    // Build a string with segments totaling ~60 chars, then ~60 more
    const seg = "あいうえおかきくけこ。"; // 11 chars each
    const input = seg.repeat(10); // 110 chars total
    const result = cut2(input);
    expect(result.length).toBeGreaterThanOrEqual(2);
    for (const r of result) {
      expect(r.length).toBeGreaterThan(0);
    }
  });

  it("should merge last short segment with previous", () => {
    // Create input where last segment would be short
    const long = "a".repeat(48) + "。";
    const short = "b" + "。";
    const result = cut2(long + short);
    expect(result.length).toBe(1);
    expect(result[0]).toContain("b");
  });

  it("should return single element for short input", () => {
    expect(cut2("短い。")).toEqual(["短い。"]);
  });
});

// =============================================================
// cut3
// =============================================================

describe("cut3", () => {
  it("should split by Chinese period", () => {
    expect(cut3("第一句。第二句。第三句")).toEqual(["第一句", "第二句", "第三句"]);
  });

  it("should strip leading/trailing '。'", () => {
    expect(cut3("。テスト。")).toEqual(["テスト"]);
  });

  it("should handle no Chinese periods", () => {
    expect(cut3("hello world")).toEqual(["hello world"]);
  });
});

// =============================================================
// cut4
// =============================================================

describe("cut4", () => {
  it("should split by English period", () => {
    expect(cut4("First sentence.Second sentence.Third")).toEqual([
      "First sentence",
      "Second sentence",
      "Third",
    ]);
  });

  it("should protect decimal points (3.14)", () => {
    // "3.14.Done" - the second "." is preceded by digit "4", so lookbehind (?<!\d) fails, no split
    expect(cut4("The value is 3.14.Done")).toEqual(["The value is 3.14.Done"]);
    // But "end.Next" splits normally since no digit before "."
    expect(cut4("end.Next")).toEqual(["end", "Next"]);
  });

  it("should handle no periods", () => {
    expect(cut4("hello world")).toEqual(["hello world"]);
  });

  it("should strip leading/trailing periods", () => {
    expect(cut4(".hello.")).toEqual(["hello"]);
  });
});

// =============================================================
// cut5
// =============================================================

describe("cut5", () => {
  it("should split by various punctuation", () => {
    expect(cut5("hello,world.foo!bar")).toEqual(["hello,", "world.", "foo!", "bar"]);
  });

  it("should protect decimal points", () => {
    const result = cut5("Price is 3.14,ok");
    expect(result).toEqual(["Price is 3.14,", "ok"]);
  });

  it("should handle Chinese punctuation", () => {
    expect(cut5("你好，世界。")).toEqual(["你好，", "世界。"]);
  });

  it("should filter punctuation-only segments", () => {
    expect(cut5("hello,.world")).toEqual(["hello,", "world"]);
  });

  it("should handle empty input", () => {
    expect(cut5("")).toEqual([]);
  });
});

// =============================================================
// processText
// =============================================================

describe("processText", () => {
  it("should filter null, empty, and space-only texts", () => {
    expect(processText(["hello", null, "", " ", "world"])).toEqual(["hello", "world"]);
  });

  it("should throw if all texts are empty", () => {
    expect(() => processText([null, "", " ", "\n"])).toThrow("All texts are empty");
  });

  it("should return all valid texts", () => {
    expect(processText(["a", "b"])).toEqual(["a", "b"]);
  });
});

// =============================================================
// mergeShortText
// =============================================================

describe("mergeShortText", () => {
  it("should merge short segments", () => {
    // "ab"(2) + "cd"(4) = "abcd"(4) < 5, continues; + "efghij"(10) = "abcdefghij"(10) >= 5
    expect(mergeShortText(["ab", "cd", "efghij"], 5)).toEqual(["abcdefghij"]);
    // With items that cross the threshold
    expect(mergeShortText(["abcde", "fg", "hijklmn"], 5)).toEqual(["abcde", "fghijklmn"]);
  });

  it("should append remainder to last segment", () => {
    expect(mergeShortText(["abcde", "fg"], 5)).toEqual(["abcdefg"]);
  });

  it("should handle single element", () => {
    expect(mergeShortText(["abc"], 5)).toEqual(["abc"]);
  });

  it("should handle all short segments", () => {
    expect(mergeShortText(["a", "b", "c"], 10)).toEqual(["abc"]);
  });

  it("should use default threshold of 5", () => {
    expect(mergeShortText(["ab", "cd", "efghij"])).toEqual(["abcdefghij"]);
  });
});

// =============================================================
// ensureEndingPunctuation
// =============================================================

describe("ensureEndingPunctuation", () => {
  it("should add '。' for Japanese", () => {
    expect(ensureEndingPunctuation(["テスト"], "all_ja")).toEqual(["テスト。"]);
  });

  it("should add '.' for English", () => {
    expect(ensureEndingPunctuation(["hello"], "en")).toEqual(["hello."]);
  });

  it("should not add punctuation if already present", () => {
    expect(ensureEndingPunctuation(["テスト。"], "all_ja")).toEqual(["テスト。"]);
    expect(ensureEndingPunctuation(["hello!"], "en")).toEqual(["hello!"]);
  });

  it("should handle empty strings", () => {
    expect(ensureEndingPunctuation([""], "en")).toEqual([""]);
  });
});

// =============================================================
// splitText (integration)
// =============================================================

describe("splitText", () => {
  it("should work with 'No slice'", () => {
    const result = splitText("こんにちは世界", "No slice", "all_ja");
    expect(result).toEqual(["こんにちは世界。"]);
  });

  it("should work with 'Slice once every 4 sentences'", () => {
    const input = "一。二。三。四。五。六。七。八。";
    const result = splitText(input, "Slice once every 4 sentences", "all_ja");
    expect(result.length).toBe(2);
  });

  it("should work with 'Slice by Chinese punct'", () => {
    // Use longer segments so they don't get merged by mergeShortText (threshold=5)
    const result = splitText("これは第一の文章です。これは第二の文章です。これは第三の文章", "Slice by Chinese punct", "all_ja");
    expect(result).toEqual(["これは第一の文章です。", "これは第二の文章です。", "これは第三の文章。"]);
  });

  it("should work with 'Slice by English punct'", () => {
    const result = splitText("First.Second.Third", "Slice by English punct", "en");
    expect(result).toEqual(["First.", "Second.", "Third."]);
  });

  it("should work with 'Slice by every punct'", () => {
    const result = splitText("hello,world!", "Slice by every punct", "en");
    expect(result).toEqual(["hello,", "world!"]);
  });

  it("should throw for empty text", () => {
    expect(() => splitText("", "No slice", "all_ja")).toThrow("All texts are empty");
  });

  it("should merge short segments and ensure punctuation", () => {
    // "ab,cd,efghij!" - cut5 splits to ["ab,", "cd,", "efghij!"]
    // mergeShortText(["ab,", "cd,", "efghij!"], 5) -> ["ab,cd,", "efghij!"]
    // ensureEndingPunctuation already has punctuation
    const result = splitText("ab,cd,efghij!", "Slice by every punct", "en");
    expect(result).toEqual(["ab,cd,", "efghij!"]);
  });
});
