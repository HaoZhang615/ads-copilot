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
    <svg viewBox="0 0 250 250" xmlns="http://www.w3.org/2000/svg" fill="none" className={className} aria-label="Databricks" role="img">
      <path fill="#FF3621" d="M215 170.861V136.65l-3.77-2.092-85.739 48.513-81.412-46.057.017-19.838 81.395 45.538L215 112.575V78.883l-3.77-2.092-85.739 48.513-78.06-44.172 78.06-43.896 63.032 35.438 4.725-2.646v-3.943L125.491 28 36 78.313v4.963l89.491 50.279 81.413-45.765v20.063l-81.413 46.058-85.72-48.496L36 107.507V141.7l89.491 50.14 81.413-45.608v19.942l-81.413 46.058-85.72-48.514L36 165.811v5.05L125.491 221 215 170.861Z"/>
    </svg>
  );
}

function FabricLogo({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" className={className} aria-label="Microsoft Fabric" role="img">
      <path fill="url(#fp-a)" fillRule="evenodd" d="m5.64 31.6-.586 2.144c-.218.685-.524 1.693-.689 2.59a5.629 5.629 0 0 0 4.638 7.588c.792.114 1.688.108 2.692-.04l4.613-.636a2.924 2.924 0 0 0 2.421-2.127l3.175-11.662L5.64 31.599Z" clipRule="evenodd"/>
      <path fill="url(#fp-b)" d="M10.14 32.152c-4.863.753-5.861 4.423-5.861 4.423l4.656-17.11 24.333-3.292-3.318 12.052a1.706 1.706 0 0 1-1.388 1.244l-.136.022-18.423 2.684.137-.023Z"/>
      <path fill="url(#fp-c)" fillOpacity=".8" d="M10.14 32.152c-4.863.753-5.861 4.423-5.861 4.423l4.656-17.11 24.333-3.292-3.318 12.052a1.706 1.706 0 0 1-1.388 1.244l-.136.022-18.423 2.684.137-.023Z"/>
      <path fill="url(#fp-d)" d="m12.899 21.235 26.938-3.98a1.597 1.597 0 0 0 1.323-1.17l2.78-10.06a1.595 1.595 0 0 0-1.74-2.012L16.498 7.81a7.185 7.185 0 0 0-5.777 5.193L7.013 26.438c.744-2.717 1.202-4.355 5.886-5.203Z"/>
      <path fill="url(#fp-e)" d="m12.899 21.235 26.938-3.98a1.597 1.597 0 0 0 1.323-1.17l2.78-10.06a1.595 1.595 0 0 0-1.74-2.012L16.498 7.81a7.185 7.185 0 0 0-5.777 5.193L7.013 26.438c.744-2.717 1.202-4.355 5.886-5.203Z"/>
      <path fill="url(#fp-f)" fillOpacity=".4" d="m12.899 21.235 26.938-3.98a1.597 1.597 0 0 0 1.323-1.17l2.78-10.06a1.595 1.595 0 0 0-1.74-2.012L16.498 7.81a7.185 7.185 0 0 0-5.777 5.193L7.013 26.438c.744-2.717 1.202-4.355 5.886-5.203Z"/>
      <path fill="url(#fp-g)" d="M12.899 21.236c-3.901.706-4.87 1.962-5.514 3.932L4.279 36.577s.992-3.633 5.796-4.41l18.352-2.673.136-.022a1.707 1.707 0 0 0 1.388-1.244l2.73-9.915-19.782 2.923Z"/>
      <path fill="url(#fp-h)" fillOpacity=".2" d="M12.899 21.236c-3.901.706-4.87 1.962-5.514 3.932L4.279 36.577s.992-3.633 5.796-4.41l18.352-2.673.136-.022a1.707 1.707 0 0 0 1.388-1.244l2.73-9.915-19.782 2.923Z"/>
      <path fill="url(#fp-i)" fillRule="evenodd" d="M10.075 32.167c-4.06.657-5.392 3.345-5.71 4.164a5.629 5.629 0 0 0 4.638 7.59c.792.114 1.688.108 2.692-.039l4.613-.637a2.924 2.924 0 0 0 2.421-2.127l2.894-10.633-11.547 1.683-.001-.001Z" clipRule="evenodd"/>
      <defs>
        <linearGradient id="fp-a" x1="12.953" x2="12.953" y1="44.001" y2="29.457" gradientUnits="userSpaceOnUse"><stop offset=".056" stopColor="#2AAC94"/><stop offset=".155" stopColor="#239C87"/><stop offset=".372" stopColor="#177E71"/><stop offset=".588" stopColor="#0E6961"/><stop offset=".799" stopColor="#095D57"/><stop offset="1" stopColor="#085954"/></linearGradient>
        <linearGradient id="fp-b" x1="31.331" x2="17.286" y1="33.448" y2="18.173" gradientUnits="userSpaceOnUse"><stop offset=".042" stopColor="#ABE88E"/><stop offset=".549" stopColor="#2AAA92"/><stop offset=".906" stopColor="#117865"/></linearGradient>
        <linearGradient id="fp-c" x1="-3.182" x2="10.183" y1="32.706" y2="28.148" gradientUnits="userSpaceOnUse"><stop stopColor="#6AD6F9"/><stop offset="1" stopColor="#6AD6F9" stopOpacity="0"/></linearGradient>
        <linearGradient id="fp-d" x1="7.013" x2="42.589" y1="15.219" y2="15.219" gradientUnits="userSpaceOnUse"><stop offset=".043" stopColor="#25FFD4"/><stop offset=".874" stopColor="#55DDB9"/></linearGradient>
        <linearGradient id="fp-e" x1="7.013" x2="39.06" y1="10.247" y2="25.128" gradientUnits="userSpaceOnUse"><stop stopColor="#6AD6F9"/><stop offset=".23" stopColor="#60E9D0"/><stop offset=".651" stopColor="#6DE9BB"/><stop offset=".994" stopColor="#ABE88E"/></linearGradient>
        <linearGradient id="fp-f" x1="9.978" x2="27.404" y1="13.031" y2="16.885" gradientUnits="userSpaceOnUse"><stop stopColor="#fff" stopOpacity="0"/><stop offset=".459" stopColor="#fff"/><stop offset="1" stopColor="#fff" stopOpacity="0"/></linearGradient>
        <linearGradient id="fp-g" x1="15.756" x2="16.168" y1="27.96" y2="15.74" gradientUnits="userSpaceOnUse"><stop offset=".205" stopColor="#063D3B" stopOpacity="0"/><stop offset=".586" stopColor="#063D3B" stopOpacity=".237"/><stop offset=".872" stopColor="#063D3B" stopOpacity=".75"/></linearGradient>
        <linearGradient id="fp-h" x1="2.81" x2="17.701" y1="26.744" y2="29.545" gradientUnits="userSpaceOnUse"><stop stopColor="#fff" stopOpacity="0"/><stop offset=".459" stopColor="#fff"/><stop offset="1" stopColor="#fff" stopOpacity="0"/></linearGradient>
        <linearGradient id="fp-i" x1="13.567" x2="10.662" y1="39.97" y2="25.764" gradientUnits="userSpaceOnUse"><stop offset=".064" stopColor="#063D3B" stopOpacity="0"/><stop offset=".17" stopColor="#063D3B" stopOpacity=".135"/><stop offset=".562" stopColor="#063D3B" stopOpacity=".599"/><stop offset=".85" stopColor="#063D3B" stopOpacity=".9"/><stop offset="1" stopColor="#063D3B"/></linearGradient>
      </defs>
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
