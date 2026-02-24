"use client";

import type { AvatarState } from "@/lib/ws-protocol";


const IDLE_VIDEO_URL = "/idle.mp4";

interface AvatarPanelProps {
  avatarState: AvatarState;
  videoRef: React.RefObject<HTMLVideoElement | null>;
  audioRef: React.RefObject<HTMLAudioElement | null>;
}

export function AvatarPanel({
  avatarState,
  videoRef,
  audioRef,
}: AvatarPanelProps) {
  const isSpeaking = avatarState === "speaking";
  const isConnecting = avatarState === "connecting";
  const isIdle = avatarState === "idle" || avatarState === "disconnected";
  const showLiveVideo = isSpeaking || isConnecting;
  const showIdleVideo = isIdle;

  return (
    <div className="flex flex-col items-center gap-3 w-full lg:w-80 lg:flex-shrink-0">
      <div
        className={`relative w-full overflow-hidden rounded-2xl border-2 transition-all duration-500 ${
          isSpeaking
            ? "border-[var(--accent)] shadow-[0_0_24px_rgba(0,120,212,0.3)]"
            : "border-[var(--border)]"
        }`}
        style={{ aspectRatio: "9/16" }}
      >
        <video
          ref={videoRef}
          autoPlay
          playsInline
          className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-500 ${
            showLiveVideo ? "opacity-100 z-10" : "opacity-0 z-0"
          }`}
        />

        <video
          src={IDLE_VIDEO_URL}
          autoPlay
          loop
          muted
          playsInline
          className={`absolute inset-0 w-full h-full object-cover object-top transition-opacity duration-500 ${
            showIdleVideo ? "opacity-100 z-10" : "opacity-0 z-0"
          }`}
        />

        {isConnecting && (
          <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-black/40 backdrop-blur-sm">
            <div className="w-12 h-12 rounded-full border-3 border-white/30 border-t-white animate-spin mb-3" />
            <span className="text-sm text-white font-medium">
              Connecting avatar...
            </span>
          </div>
        )}

        {isSpeaking && (
          <div className="absolute top-3 right-3 z-20 flex items-center gap-1.5 px-2 py-1 rounded-full bg-black/50 backdrop-blur-sm">
            <span className="w-2 h-2 rounded-full bg-[var(--success)] animate-pulse" />
            <span className="text-xs text-white font-medium">Live</span>
          </div>
        )}
      </div>

      <audio ref={audioRef} autoPlay style={{ display: "none" }} />
    </div>
  );
}
