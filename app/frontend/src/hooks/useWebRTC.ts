"use client";

import { useRef, useCallback } from "react";

/** Timeout (ms) for ICE candidate gathering before we send the offer anyway. */
const ICE_GATHER_TIMEOUT_MS = 10_000;

export interface IceServerConfig {
  urls: string[];
  username: string;
  credential: string;
}

interface UseWebRTCReturn {
  videoRef: React.RefObject<HTMLVideoElement | null>;
  audioRef: React.RefObject<HTMLAudioElement | null>;
  /**
   * Create a WebRTC offer with the given ICE servers.
   * Waits for ICE gathering to complete (or timeout) before resolving,
   * matching the official Azure Speech Avatar sample pattern.
   */
  createOffer: (iceServers: IceServerConfig[]) => Promise<string>;
  /** Apply the remote SDP answer from the avatar service. */
  setAnswer: (sdp: string) => Promise<void>;
  disconnect: () => void;
}

export function useWebRTC(): UseWebRTCReturn {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const pcRef = useRef<RTCPeerConnection | null>(null);

  const disconnect = useCallback(() => {
    if (pcRef.current) {
      pcRef.current.close();
      pcRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    if (audioRef.current) {
      audioRef.current.srcObject = null;
    }
  }, []);

  const createOffer = useCallback(
    async (iceServers: IceServerConfig[]): Promise<string> => {
      // Clean up any existing connection
      disconnect();

      // Create peer connection WITH ICE servers in the constructor
      // (official Azure sample pattern — never use setConfiguration after)
      const pc = new RTCPeerConnection({
        iceServers,
        iceTransportPolicy: "relay",
      });
      pcRef.current = pc;

      // Add recv-only transceivers for video and audio
      // Azure sample uses "sendrecv" to ensure the server-side sees transceiver
      pc.addTransceiver("video", { direction: "sendrecv" });
      pc.addTransceiver("audio", { direction: "sendrecv" });

      // Handle incoming tracks
      pc.ontrack = (event: RTCTrackEvent) => {
        console.log("[useWebRTC] ontrack:", event.track.kind);
        if (event.track.kind === "video" && videoRef.current) {
          videoRef.current.srcObject = event.streams[0];
        }
        if (event.track.kind === "audio" && audioRef.current) {
          audioRef.current.srcObject = event.streams[0];
        }
      };

      // Create offer and set local description
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      console.log("[useWebRTC] Local description set, waiting for ICE gathering...");

      // Wait for ICE gathering to complete (or timeout).
      // The official Azure sample waits for onicecandidate(null) with a 10s fallback.
      const localSdp = await new Promise<string>((resolve) => {
        let done = false;

        const finish = () => {
          if (done) return;
          done = true;
          // Official Azure sample: btoa(JSON.stringify(localDescription))
          // The service expects base64-encoded JSON of the full RTCSessionDescription
          const desc = pc.localDescription;
          const encoded = desc ? btoa(JSON.stringify(desc)) : "";
          console.log(
            "[useWebRTC] ICE gathering finished, encoded length:",
            encoded.length,
            "state:",
            pc.iceGatheringState
          );
          resolve(encoded);
        };

        // Primary: onicecandidate fires with null when gathering is complete
        pc.onicecandidate = (event) => {
          if (event.candidate === null) {
            finish();
          }
        };

        // Fallback: timeout in case gathering never completes
        setTimeout(() => {
          if (!done) {
            console.warn(
              "[useWebRTC] ICE gathering timeout, proceeding with current candidates"
            );
            finish();
          }
        }, ICE_GATHER_TIMEOUT_MS);
      });

      return localSdp;
    },
    [disconnect]
  );

  const setAnswer = useCallback(async (sdp: string): Promise<void> => {
    const pc = pcRef.current;
    if (!pc) {
      console.warn("[useWebRTC] setAnswer: no peer connection");
      return;
    }

    // The server SDP answer is base64-encoded JSON of RTCSessionDescription
    // (matching the official Azure Avatar sample: atob + JSON.parse)
    console.log("[useWebRTC] Setting remote description (answer), encoded length:", sdp.length);
    const decoded = JSON.parse(atob(sdp)) as RTCSessionDescriptionInit;
    console.log("[useWebRTC] Decoded answer type:", decoded.type, "SDP length:", decoded.sdp?.length);
    await pc.setRemoteDescription(new RTCSessionDescription(decoded));
    console.log("[useWebRTC] Remote description set, connection state:", pc.connectionState);
  }, []);

  return { videoRef, audioRef, createOffer, setAnswer, disconnect };
}
