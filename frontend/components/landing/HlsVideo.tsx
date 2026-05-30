"use client";

import { useEffect, useRef } from "react";
import Hls from "hls.js";

interface HlsVideoProps {
  src: string;
  className?: string;
}

/**
 * Background video that plays an HLS (.m3u8) stream. Uses hls.js where MSE is
 * available, otherwise falls back to native HLS (Safari/iOS).
 */
export default function HlsVideo({ src, className }: HlsVideoProps) {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    let hls: Hls | undefined;

    if (Hls.isSupported()) {
      hls = new Hls({ enableWorker: true });
      hls.loadSource(src);
      hls.attachMedia(video);
    } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
      video.src = src;
    }

    const tryPlay = () => video.play().catch(() => {});
    video.addEventListener("canplay", tryPlay);

    return () => {
      video.removeEventListener("canplay", tryPlay);
      hls?.destroy();
    };
  }, [src]);

  return (
    <video ref={videoRef} autoPlay muted loop playsInline className={className} />
  );
}
