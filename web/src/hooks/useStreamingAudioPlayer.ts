import { useState, useRef, useCallback } from "react";
import { concatWavBlobs } from "@/utils/wavConcat";

type AudioElementWithSinkId = HTMLAudioElement & { setSinkId?: (id: string) => Promise<void> };

const applySinkId = async (audio: AudioElementWithSinkId, deviceId: string) => {
  if (!deviceId || !audio.setSinkId) return;
  try {
    await audio.setSinkId(deviceId);
  } catch {
    // setSinkId is not supported in all browsers
  }
};

type Options = {
  outputDeviceId: string;
  monitorDeviceId: string;
  silenceDuration: number;
  maxTrim: number;
};

export const useStreamingAudioPlayer = ({ outputDeviceId, monitorDeviceId, silenceDuration, maxTrim }: Options) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [mergedBlob, setMergedBlob] = useState<Blob | null>(null);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const monitorAudioRef = useRef<HTMLAudioElement | null>(null);
  const queueRef = useRef<Blob[]>([]);
  const allBlobsRef = useRef<Blob[]>([]);
  const finishedRef = useRef(false);
  const playingRef = useRef(false);
  const waitingForSegmentRef = useRef(false);

  const playBlob = useCallback(
    async (blob: Blob) => {
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audioRef.current = audio;
      await applySinkId(audio as AudioElementWithSinkId, outputDeviceId);

      let monitorAudio: HTMLAudioElement | null = null;
      if (monitorDeviceId) {
        monitorAudio = new Audio(url);
        monitorAudioRef.current = monitorAudio;
        await applySinkId(monitorAudio as AudioElementWithSinkId, monitorDeviceId);
      }

      return new Promise<void>((resolve) => {
        audio.addEventListener("ended", () => {
          URL.revokeObjectURL(url);
          audioRef.current = null;
          monitorAudioRef.current = null;
          resolve();
        });
        audio.play();
        monitorAudio?.play();
      });
    },
    [outputDeviceId, monitorDeviceId],
  );

  const playNext = useCallback(async () => {
    if (queueRef.current.length === 0) {
      if (finishedRef.current) {
        playingRef.current = false;
        setIsPlaying(false);
      } else {
        waitingForSegmentRef.current = true;
      }
      return;
    }

    const blob = queueRef.current.shift()!;
    await playBlob(blob);
    playNext();
  }, [playBlob]);

  const pushSegment = useCallback(
    (blob: Blob) => {
      allBlobsRef.current.push(blob);
      queueRef.current.push(blob);

      if (!playingRef.current) {
        playingRef.current = true;
        setIsPlaying(true);
        playNext();
      } else if (waitingForSegmentRef.current) {
        waitingForSegmentRef.current = false;
        playNext();
      }
    },
    [playNext],
  );

  const finish = useCallback(async () => {
    finishedRef.current = true;
    if (allBlobsRef.current.length > 0) {
      const merged = await concatWavBlobs(allBlobsRef.current, silenceDuration, maxTrim);
      setMergedBlob(merged);
    }
    if (!playingRef.current) {
      setIsPlaying(false);
    }
  }, [silenceDuration, maxTrim]);

  const reset = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    if (monitorAudioRef.current) {
      monitorAudioRef.current.pause();
      monitorAudioRef.current = null;
    }
    queueRef.current = [];
    allBlobsRef.current = [];
    finishedRef.current = false;
    playingRef.current = false;
    waitingForSegmentRef.current = false;
    setIsPlaying(false);
    setMergedBlob(null);
  }, []);

  return { isPlaying, mergedBlob, pushSegment, finish, reset };
};
