import { useState, useRef, useCallback } from "react";

type AudioPlayerOptions = {
  outputDeviceId?: string;
};

const applySinkId = async (audio: HTMLAudioElement, deviceId: string) => {
  if (!deviceId) return;
  try {
    await (audio as HTMLAudioElement & { setSinkId: (id: string) => Promise<void> }).setSinkId(
      deviceId,
    );
  } catch {
    // setSinkId is not supported in all browsers
  }
};

export const useAudioPlayer = (options: AudioPlayerOptions = {}) => {
  const { outputDeviceId } = options;
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const urlRef = useRef<string | null>(null);

  const play = useCallback(
    async (blob: Blob) => {
      stop();
      const url = URL.createObjectURL(blob);
      urlRef.current = url;
      const audio = new Audio(url);
      audioRef.current = audio;

      audio.addEventListener("timeupdate", () => setCurrentTime(audio.currentTime));
      audio.addEventListener("loadedmetadata", () => setDuration(audio.duration));
      audio.addEventListener("ended", () => {
        setIsPlaying(false);
        setCurrentTime(0);
      });

      if (outputDeviceId) await applySinkId(audio, outputDeviceId);
      audio.play();
      setIsPlaying(true);
    },
    [outputDeviceId],
  );

  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    if (urlRef.current) {
      URL.revokeObjectURL(urlRef.current);
      urlRef.current = null;
    }
    setIsPlaying(false);
    setCurrentTime(0);
    setDuration(0);
  }, []);

  const playUrl = useCallback(
    async (url: string) => {
      stop();
      const audio = new Audio(url);
      audioRef.current = audio;

      audio.addEventListener("timeupdate", () => setCurrentTime(audio.currentTime));
      audio.addEventListener("loadedmetadata", () => setDuration(audio.duration));
      audio.addEventListener("ended", () => {
        setIsPlaying(false);
        setCurrentTime(0);
      });

      if (outputDeviceId) await applySinkId(audio, outputDeviceId);
      audio.play();
      setIsPlaying(true);
    },
    [outputDeviceId],
  );

  return { isPlaying, currentTime, duration, play, playUrl, stop };
};
