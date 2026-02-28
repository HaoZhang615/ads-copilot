"use client";

import { use } from "react";
import { redirect } from "next/navigation";
import { ChatInterface } from "@/components/ChatInterface";

const VALID_TOPICS = ["databricks", "fabric"] as const;
type TopicId = (typeof VALID_TOPICS)[number];

function isValidTopic(value: string): value is TopicId {
  return (VALID_TOPICS as readonly string[]).includes(value);
}

export default function SessionPage({
  params,
}: {
  params: Promise<{ topic: string }>;
}) {
  const { topic } = use(params);

  if (!isValidTopic(topic)) {
    redirect("/");
  }

  return (
    <main className="h-screen w-screen overflow-hidden" data-topic={topic}>
      <ChatInterface topic={topic} />
    </main>
  );
}
