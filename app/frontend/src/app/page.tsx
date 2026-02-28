import Link from "next/link";

function AzureLogo({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 96 96"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <path
        d="M33.338 6.544h26.038l-27.03 80.455a4.46 4.46 0 0 1-4.223 3.01H4.834a4.46 4.46 0 0 1-4.221-5.912L29.114 9.556a4.46 4.46 0 0 1 4.224-3.012z"
        fill="#0078D4"
      />
      <path
        d="M71.175 60.261H31.528a2.07 2.07 0 0 0-1.404 3.587l25.554 23.88a4.46 4.46 0 0 0 3.046 1.2h24.258z"
        fill="#0078D4"
      />
      <path
        d="M33.338 6.544a4.45 4.45 0 0 0-4.248 3.09L.613 84.071a4.46 4.46 0 0 0 4.221 5.917h24.088a4.54 4.54 0 0 0 3.622-2.917l5.097-14.715 17.824 16.628a4.51 4.51 0 0 0 2.72 1.004h24.182l-10.596-28.727H37.788l21.264-49.277H33.338z"
        fill="#0078D4"
        opacity="0.8"
      />
    </svg>
  );
}

function DatabricksLogo({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 36 36"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <path
        d="M18 1.44L2.16 10.44v5.04l15.84 9 15.84-9v-5.04L18 1.44z"
        fill="#FF3621"
      />
      <path
        d="M18 17.28L2.16 8.28v5.04l15.84 9 15.84-9V8.28L18 17.28z"
        fill="#FF3621"
        opacity="0.7"
      />
      <path
        d="M2.16 20.52v5.04L18 34.56l15.84-9v-5.04L18 29.52l-15.84-9z"
        fill="#FF3621"
      />
      <path
        d="M2.16 15.48v5.04L18 29.52l15.84-9v-5.04L18 23.48l-15.84-8z"
        fill="#FF3621"
        opacity="0.85"
      />
    </svg>
  );
}

function FabricLogo({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 36 36"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <defs>
        <linearGradient id="fabric-grad-landing" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#008575" />
          <stop offset="100%" stopColor="#0078D4" />
        </linearGradient>
      </defs>
      <path
        d="M18 2L32 14L18 34L4 14Z"
        fill="url(#fabric-grad-landing)"
      />
      <path
        d="M18 2L32 14H4Z"
        fill="#008575"
        opacity="0.9"
      />
      <path
        d="M4 14L18 34L18 14Z"
        fill="#0078D4"
        opacity="0.7"
      />
      <path
        d="M18 14L32 14L18 34Z"
        fill="#008575"
        opacity="0.6"
      />
    </svg>
  );
}

const TOPICS = [
  {
    id: "databricks",
    name: "Azure Databricks",
    description:
      "Design a lakehouse, streaming pipeline, ML platform, or data mesh on Azure Databricks. Covers Medallion architecture, Unity Catalog governance, and migration playbooks.",
    accent: "#FF3621",
    gradientFrom: "#FF3621",
    gradientTo: "#e02e1a",
    Logo: DatabricksLogo,
  },
  {
    id: "fabric",
    name: "Microsoft Fabric",
    description:
      "Design an end-to-end analytics platform on Microsoft Fabric. Covers OneLake lakehouses, data warehouses, real-time intelligence, Power BI, and Copilot integration.",
    accent: "#008575",
    gradientFrom: "#008575",
    gradientTo: "#006b5e",
    Logo: FabricLogo,
  },
] as const;

export default function LandingPage() {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen px-6 py-12">
      {/* Hero */}
      <div className="flex flex-col items-center text-center mb-14">
        <div className="flex items-center gap-3 mb-6">
          <AzureLogo className="w-10 h-10" />
          <span className="text-2xl text-[var(--border)] font-light select-none">
            |
          </span>
          <h1 className="text-2xl font-bold text-[var(--foreground)] tracking-tight">
            ADS Copilot
          </h1>
        </div>
        <p className="text-base text-[var(--muted)] max-w-lg leading-relaxed">
          Voice-enabled AI copilot for Architecture Design Sessions. Choose a
          topic below to start designing your solution architecture.
        </p>
      </div>

      {/* Topic cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl w-full">
        {TOPICS.map((topic) => (
          <Link
            key={topic.id}
            href={`/session/${topic.id}`}
            className="group relative flex flex-col rounded-xl border border-[var(--border)] bg-[var(--surface)] p-6 transition-all duration-200 hover:border-transparent hover:shadow-lg hover:shadow-black/20 focus:outline-none focus:ring-2 focus:ring-[var(--accent)] focus:ring-offset-2 focus:ring-offset-[var(--background)]"
            style={{
              ["--card-accent" as string]: topic.accent,
            }}
          >
            {/* Gradient top border on hover */}
            <div
              className="absolute inset-x-0 top-0 h-0.5 rounded-t-xl opacity-0 group-hover:opacity-100 transition-opacity duration-200"
              style={{
                background: `linear-gradient(to right, ${topic.gradientFrom}, ${topic.gradientTo})`,
              }}
            />

            <div className="flex items-center gap-3 mb-4">
              <div
                className="flex items-center justify-center w-10 h-10 rounded-lg"
                style={{ backgroundColor: `${topic.accent}15` }}
              >
                <topic.Logo className="w-6 h-6" />
              </div>
              <h2 className="text-lg font-semibold text-[var(--foreground)] group-hover:text-white transition-colors">
                {topic.name}
              </h2>
            </div>

            <p className="text-sm text-[var(--muted)] leading-relaxed flex-1">
              {topic.description}
            </p>

            <div className="mt-5 flex items-center gap-1.5 text-sm font-medium transition-colors" style={{ color: topic.accent }}>
              Start session
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                className="w-4 h-4 transform group-hover:translate-x-0.5 transition-transform"
              >
                <path
                  fillRule="evenodd"
                  d="M3 10a.75.75 0 0 1 .75-.75h10.638l-3.96-3.96a.75.75 0 1 1 1.06-1.06l5.25 5.25a.75.75 0 0 1 0 1.06l-5.25 5.25a.75.75 0 1 1-1.06-1.06l3.96-3.96H3.75A.75.75 0 0 1 3 10Z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
          </Link>
        ))}
      </div>

      {/* Footer tagline */}
      <p className="mt-12 text-xs text-[var(--muted)] text-center">
        Powered by GitHub Copilot SDK + Azure AI Services
      </p>
    </main>
  );
}
