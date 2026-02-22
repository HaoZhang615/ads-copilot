"use client";

interface WaveformVisualizerProps {
  audioLevel: number;
  isActive: boolean;
}

const BAR_COUNT = 5;

export function WaveformVisualizer({
  audioLevel,
  isActive,
}: WaveformVisualizerProps) {
  if (!isActive) return null;

  return (
    <div className="flex items-center justify-center gap-1" aria-hidden="true">
      {Array.from({ length: BAR_COUNT }).map((_, i) => {
        const delay = i * 0.1;
        const baseHeight = 8;
        const maxAdditionalHeight = 24;
        const height = baseHeight + audioLevel * maxAdditionalHeight;
        const staggeredHeight =
          height * (0.5 + 0.5 * Math.sin((i / BAR_COUNT) * Math.PI));

        return (
          <div
            key={i}
            className="w-1 rounded-full bg-red-400 transition-all duration-75"
            style={{
              height: `${Math.max(baseHeight, staggeredHeight)}px`,
              animationDelay: `${delay}s`,
              opacity: 0.6 + audioLevel * 0.4,
            }}
          />
        );
      })}
    </div>
  );
}
