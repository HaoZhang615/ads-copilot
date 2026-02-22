import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    wsUrl:
      process.env.BACKEND_WS_URL ??
      process.env.NEXT_PUBLIC_WS_URL ??
      "ws://localhost:8000/ws",
    apiUrl:
      process.env.BACKEND_API_URL ??
      process.env.NEXT_PUBLIC_API_URL ??
      "http://localhost:8000",
  });
}