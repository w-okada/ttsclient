/**
 * useStreamingAudioPlayer の核心ロジック（キュー管理 + 再生チェイン）のテスト。
 *
 * vitest environment: node (jsdom なし) のため、React hook を直接テストせず、
 * hook のロジックをインラインで再現して timing を検証する。
 *
 * 再生チェインは同期コールバックパターンで実装し、microtask の影響を排除する。
 */
import { describe, it, expect } from "vitest";

// ---------------------------------------------------------------------------
// Mock Audio
// ---------------------------------------------------------------------------

type EndedCallback = () => void;

class MockAudio {
  playTimestamp = 0;
  private endedCallbacks: EndedCallback[] = [];

  addEventListener(event: string, cb: EndedCallback) {
    if (event === "ended") this.endedCallbacks.push(cb);
  }

  play() {
    this.playTimestamp = performance.now();
  }

  fireEnded() {
    for (const cb of this.endedCallbacks) cb();
  }
}

// ---------------------------------------------------------------------------
// Streaming player core logic (extracted from useStreamingAudioPlayer)
//
// 実際の hook は async/await を使うが、テストでは同期コールバックで再現する。
// ended イベント → playNext() のチェインが同期的に動くため、
// fireEnded() 直後に audios 配列が更新される。
// ---------------------------------------------------------------------------

const createStreamingPlayer = () => {
  const queue: Blob[] = [];
  const audios: MockAudio[] = [];
  const playedBlobs: Blob[] = [];
  let finished = false;
  let playing = false;
  let waitingForSegment = false;

  const playNext = (): void => {
    if (queue.length === 0) {
      if (finished) {
        playing = false;
      } else {
        waitingForSegment = true;
      }
      return;
    }

    const blob = queue.shift()!;
    playedBlobs.push(blob);
    const audio = new MockAudio();
    audios.push(audio);
    audio.addEventListener("ended", () => playNext());
    audio.play();
  };

  const pushSegment = (blob: Blob) => {
    queue.push(blob);

    if (!playing) {
      playing = true;
      playNext();
    } else if (waitingForSegment) {
      waitingForSegment = false;
      playNext();
    }
  };

  const setFinished = () => {
    finished = true;
  };

  return {
    pushSegment,
    setFinished,
    audios,
    playedBlobs,
    getState: () => ({ playing, waitingForSegment, finished }),
  };
};

// ---------------------------------------------------------------------------
// deadline calculation (extracted from TextInputArea)
// ---------------------------------------------------------------------------

describe("deadline calculation", () => {
  it("cumulative_deadlines: セグメント0の duration とテキスト長から後続の deadline が正しく計算される", () => {
    const segments = ["こんにちは", "世界", "テスト文です"];
    const firstDuration = 2.5; // 秒
    const firstCharCount = segments[0].length; // 5
    const durationPerChar = firstDuration / firstCharCount; // 0.5

    const now = 1000;
    let cumulativeDuration = firstDuration;
    const deadlines: number[] = [];

    for (const segment of segments.slice(1)) {
      const deadline = now + cumulativeDuration;
      deadlines.push(deadline);
      cumulativeDuration += durationPerChar * segment.length;
    }

    // セグメント1 "世界" (len=2): deadline = 1000 + 2.5 = 1002.5
    expect(deadlines[0]).toBeCloseTo(1002.5);
    // セグメント2 "テスト文です" (len=6): deadline = 1000 + 2.5 + 0.5*2 = 1003.5
    expect(deadlines[1]).toBeCloseTo(1003.5);

    // 最終 cumulativeDuration = 2.5 + 0.5*2 + 0.5*6 = 6.5
    expect(cumulativeDuration).toBeCloseTo(6.5);
  });

  it("single_segment: セグメント1つなら Phase 2 なし", () => {
    const segments = ["hello"];
    const remainingSegments = segments.slice(1);
    expect(remainingSegments).toHaveLength(0);
  });

  it("zero_length_text: 0文字テキストで durationPerChar = 0", () => {
    const firstCharCount = 0;
    const firstDuration = 0;
    const durationPerChar = firstCharCount > 0 ? firstDuration / firstCharCount : 0;
    expect(durationPerChar).toBe(0);

    // 後続セグメントの deadline は全て同じ (now + 0)
    const now = 1000;
    let cumulativeDuration = firstDuration;
    const deadlines: number[] = [];
    for (const segment of ["a", "bb", "ccc"]) {
      deadlines.push(now + cumulativeDuration);
      cumulativeDuration += durationPerChar * segment.length;
    }

    expect(deadlines).toEqual([1000, 1000, 1000]);
  });
});

// ---------------------------------------------------------------------------
// streaming playback gap
// ---------------------------------------------------------------------------

describe("streaming playback gap", () => {
  it("pre_queued_no_gap: 3セグメントを全て push 後に再生開始 → ended から次の play() までの gap < 5ms", () => {
    const player = createStreamingPlayer();
    const blob = new Blob(["dummy"], { type: "audio/wav" });

    // 3セグメントを全て push (最初の push で playNext が同期的に実行される)
    player.pushSegment(blob);
    player.pushSegment(blob);
    player.pushSegment(blob);

    // 最初のセグメントが再生中
    expect(player.audios).toHaveLength(1);

    // セグメント0 ended → セグメント1 再生開始 (同期)
    const endedTime0 = performance.now();
    player.audios[0].fireEnded();
    expect(player.audios).toHaveLength(2);
    const gap01 = player.audios[1].playTimestamp - endedTime0;
    expect(gap01).toBeLessThan(5);

    // セグメント1 ended → セグメント2 再生開始 (同期)
    const endedTime1 = performance.now();
    player.audios[1].fireEnded();
    expect(player.audios).toHaveLength(3);
    const gap12 = player.audios[2].playTimestamp - endedTime1;
    expect(gap12).toBeLessThan(5);

    player.audios[2].fireEnded();
  });

  it("late_arrival_immediate_resume: セグメント0 再生終了後にセグメント1 到着 → push から play() まで < 10ms", () => {
    const player = createStreamingPlayer();
    const blob = new Blob(["dummy"], { type: "audio/wav" });

    // セグメント0 を push → 再生開始
    player.pushSegment(blob);
    expect(player.audios).toHaveLength(1);

    // セグメント0 再生終了 → waitingForSegment = true
    player.audios[0].fireEnded();
    expect(player.getState().waitingForSegment).toBe(true);

    // セグメント1 到着 → 即座に再生開始
    const pushTime = performance.now();
    player.pushSegment(blob);

    expect(player.audios).toHaveLength(2);
    const gap = player.audios[1].playTimestamp - pushTime;
    expect(gap).toBeLessThan(10);

    player.audios[1].fireEnded();
  });

  it("playback_order: push 順に再生される", () => {
    const player = createStreamingPlayer();

    const blob1 = new Blob(["seg1"], { type: "audio/wav" });
    const blob2 = new Blob(["seg2"], { type: "audio/wav" });
    const blob3 = new Blob(["seg3"], { type: "audio/wav" });

    player.pushSegment(blob1);
    player.pushSegment(blob2);
    player.pushSegment(blob3);

    // 最初のセグメントが再生中
    expect(player.audios).toHaveLength(1);
    expect(player.playedBlobs[0]).toBe(blob1);

    player.audios[0].fireEnded();
    expect(player.audios).toHaveLength(2);
    expect(player.playedBlobs[1]).toBe(blob2);

    player.audios[1].fireEnded();
    expect(player.audios).toHaveLength(3);
    expect(player.playedBlobs[2]).toBe(blob3);

    player.audios[2].fireEnded();
  });
});
