import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const DEFAULT_API_URL = "http://localhost:8000";

function getBackendUrl(): string {
  return (
    process.env.BACKEND_API_URL ??
    process.env.NEXT_PUBLIC_API_URL ??
    DEFAULT_API_URL
  );
}

export async function POST(request: NextRequest) {
  const body = await request.json();

  const backendUrl = getBackendUrl();

  try {
    const response = await fetch(`${backendUrl}/api/send-email`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      { detail: "Failed to reach backend email service." },
      { status: 502 }
    );
  }
}
