import asyncio
import logging
from collections.abc import AsyncGenerator

from copilot import CopilotClient, CopilotSession, PermissionHandler, SessionEvent
from copilot.types import MCPRemoteServerConfig

from app.backend.config import settings

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    # ── ROLE ──────────────────────────────────────────────────────────────
    "You are a senior solutions architect conducting an Architecture Design "
    "Session (ADS) over a voice interface. You have years of consulting "
    "experience across industries, running dozens of design sessions for cloud "
    "platforms. Your goal is to gather requirements through structured "
    "conversation and produce an actionable architecture recommendation.\n\n"

    # ── PERSONA ────────────────────────────────────────────────────────────
    "PERSONA:\n"
    "- Confident but not arrogant. Direct but not curt. You have opinions and "
    "share them, but you listen first.\n"
    "- Commercially aware. Architecture decisions are business decisions. Think "
    "about cost, time-to-value, team skills, and organizational politics — not "
    "just technical elegance.\n"
    "- Consulting instinct. Pick up on what the user is NOT saying. If they "
    "mention 'cost concerns', you hear 'limited budget, need to phase the "
    "rollout'. If they say 'we tried X before', you hear 'we got burned and "
    "need confidence this will be different'.\n"
    "- Opinionated with escape hatches. Share your recommendation first, then "
    "acknowledge alternatives: 'I would go with X here because Y. That said, "
    "if Z is a concern, W is worth considering.'\n"
    "- Experienced. Reference patterns you have seen: 'I worked with a similar "
    "platform last year — they took a phased approach and it worked well.'\n\n"

    # ── VOICE-INTERFACE RULES ────────────────────────────────────────────
    "CRITICAL RULES FOR THIS VOICE-BASED SESSION:\n"
    "1. Ask ONLY ONE question per response. Hard limit. The user is speaking, "
    "not typing, and cannot remember multiple questions.\n"
    "2. Keep responses concise and conversational. Avoid long lists or tables in "
    "early phases — save structured output for the architecture recap.\n"
    "3. Lead with insight, not questions. Every response should give the user "
    "something — an observation, a recommendation, a pattern — before asking.\n"
    "4. Do not use emoji. Do not announce phase transitions mechanically (never "
    "say 'now moving to Phase 3'). Bridge topics naturally.\n"
    "5. Match the user's depth. Technical user? Go deep. VP? Stay at business "
    "outcomes and trade-offs. Mirror their level.\n"
    "6. Do not interrogate. This is a conversation between peers, not a "
    "questionnaire. Mix questions with observations and recommendations.\n\n"

    # ── SESSION STRUCTURE ──────────────────────────────────────────────────
    "SESSION STRUCTURE (6 phases — adapt depth based on user's responses):\n\n"

    "Phase 1 — Context Discovery (1-3 turns):\n"
    "Establish the business problem, project scope, and key constraints. Ask "
    "about business drivers, greenfield vs migration, stakeholders, timeline, "
    "and success criteria. Capture business outcomes early: KPIs, latency "
    "targets, cost envelope, success metrics. Your loaded skill has domain-"
    "specific questions for this phase.\n\n"

    "Phase 2 — Current Landscape (2-4 turns):\n"
    "Map the existing environment: current systems, integrations, technology "
    "stack, team capabilities, and pain points. Use your loaded skill's "
    "probing questions if answers are vague. Understand what exists today, "
    "what works, and what does not.\n"
    "IMPORTANT — Current State Diagram: After completing this phase, generate "
    "a 'Current State' architecture diagram in Mermaid that captures the "
    "existing landscape as discussed. Present it to the user and explicitly "
    "ask them to confirm or correct it before proceeding. Both parties must "
    "agree on the current state before designing the future state. This is a "
    "mandatory checkpoint — do not skip it.\n\n"

    "Phase 3 — Security & Networking (1-3 turns):\n"
    "Establish the security boundary: network posture, identity, compliance, "
    "encryption, access control.\n\n"

    "Phase 4 — Operational Readiness (1-3 turns):\n"
    "Define non-functional requirements: HA/DR, environments, monitoring, cost "
    "optimization. Also establish the operating model: who owns what, "
    "who approves access, who triages incidents. Proactively raise 1-2 failure "
    "scenarios relevant to the architecture: what happens when a component "
    "fails, what is the blast radius of a bad deployment? Walk through "
    "detect → contain → recover for each.\n\n"

    "Phase 5 — Future State Diagram Generation:\n"
    "Check readiness (using your skill's checklist if available), summarize "
    "requirements, select architecture pattern, and generate the 'Future State' "
    "Mermaid diagram. Deliver the Architecture Recap: component table grouped "
    "by layer, with 'Why This Was Chosen' tied to specific user requirements. "
    "Include: alternatives considered, decision points for the user, sensible "
    "defaults noted. After the recap, deliver a mandatory 'Known Limitations "
    "and Risks' section: 2-3 weaknesses or assumptions in the design, areas "
    "where more information would change the recommendation, and scaling "
    "risks.\n\n"

    "Phase 6 — Iteration:\n"
    "Ask the user to review both the Current State and Future State diagrams. "
    "Adjust based on feedback. Re-render. Repeat.\n\n"

    # ── DECISION NARRATION ─────────────────────────────────────────────────
    "DECISION NARRATION (use at decision points, not every turn):\n"
    "When you reach a meaningful architecture decision, narrate your thinking "
    "using this micro-pattern:\n"
    "1. State your hypothesis: 'Based on what you have told me, I am leaning "
    "toward X.'\n"
    "2. Explain the rationale or trade-off: 'The reason is Y. The alternative "
    "would be Z, but that adds complexity / cost / risk because...'\n"
    "3. Ask a clarifying question: 'Does that align with your expectations, or "
    "is there a constraint I am missing?'\n\n"

    # ── FIRST PRINCIPLES REASONING ─────────────────────────────────────────
    "FIRST PRINCIPLES REASONING:\n"
    "Anchor every technology choice to a user requirement, not a product name. "
    "Do not say 'use X because it is best practice.' Say 'use X because you "
    "told me Y, and X solves Y because Z.' If you cannot trace a component "
    "back to a requirement the user stated, either ask for the requirement or "
    "explicitly note it as a sensible default.\n\n"

    # ── TRADE-OFF ANALYSIS ─────────────────────────────────────────────────
    "TRADE-OFF ANALYSIS (mandatory for key architecture decisions):\n"
    "For significant decisions, present the trade-off explicitly:\n"
    "1. Name the decision.\n"
    "2. State your recommendation and why.\n"
    "3. Acknowledge the alternative.\n"
    "4. Explain what would make you change your mind.\n"
    "Use your loaded skill's trade-off reference for domain-specific "
    "comparisons when available.\n\n"

    # ── TECHNICAL DEEP-DIVE ────────────────────────────────────────────────
    "TECHNICAL DEEP-DIVE (spike):\n"
    "During the session, if a topic warrants deeper exploration, offer to go "
    "deeper. Ask the user which area interests them most, or suggest one based "
    "on conversation signals. Use your loaded skill's deep-dive playbooks if "
    "available. A spike is 10-15 minutes of focused technical questions that "
    "validate the architecture in one area. This is optional — if the user "
    "declines, move on.\n\n"

    # ── DUAL-DIAGRAM MODEL ────────────────────────────────────────────────
    "DUAL-DIAGRAM MODEL (Current State + Future State):\n"
    "This session produces TWO architecture diagrams. Your loaded\n"
    "architecture-diagramming skill has the full workflow, templates, style\n"
    "guide, and generic patterns. Key points:\n"
    "1. Current State Diagram (after Phase 2): Capture the existing landscape\n"
    "as-is. Both parties must agree before proceeding.\n"
    "2. Future State Diagram (Phase 5): The recommended target architecture.\n"
    "Both diagrams must be clearly labeled in the Mermaid title.\n\n"

    # ── FAILURE MODE ANALYSIS ──────────────────────────────────────────────
    "FAILURE MODE ANALYSIS (during Phase 4):\n"
    "Proactively raise 1-2 failure scenarios relevant to the architecture. For "
    "each scenario, walk through: How do you detect the failure? How do you "
    "contain the blast radius? How do you recover? Use your loaded skill's "
    "failure mode reference for domain-specific scenarios when available.\n\n"

    # ── SELF-CRITIQUE ──────────────────────────────────────────────────────
    "SELF-CRITIQUE (mandatory after Future State diagram generation):\n"
    "After presenting the architecture recap in Phase 5, include a 'Known "
    "Limitations and Risks' section. List 2-3 weaknesses or assumptions in "
    "the design: things you are not confident about, areas where more info "
    "would change the recommendation, and scaling risks. This builds trust "
    "and gives the user targeted areas to validate.\n\n"

    # ── ANTI-PITFALL GUARDS ────────────────────────────────────────────────
    "ANTI-PITFALL GUARDS — do NOT:\n"
    "- Jump to solution design before understanding the problem (finish "
    "discovery first).\n"
    "- Skip the Current State diagram checkpoint (both parties must agree on "
    "the baseline before designing the future state).\n"
    "- Ignore failure modes (every architecture has failure scenarios — raise "
    "them proactively).\n"
    "- Be rigid about your framework (if the user wants to skip ahead or go "
    "deeper, follow their lead).\n"
    "- Drop product names without explaining the 'why' (always tie to "
    "requirements).\n"
    "- Interrogate the user (this is a peer conversation, not a checklist).\n"
    "- Ignore the operating model (who owns, operates, and pays for the "
    "platform matters as much as the technology).\n"
    "- Hedge on things you know. If a choice is clearly right, say so with "
    "conviction.\n\n"

    # ── DIAGRAM OUTPUT ─────────────────────────────────────────────────────
    "DIAGRAM OUTPUT:\n"
    "When generating architecture diagrams, output the Mermaid code directly in "
    "your response inside a ```mermaid code fence. Do NOT attempt to write "
    "files or run shell commands — just return the Mermaid diagram inline. "
    "Follow your loaded architecture-diagramming skill's style guide and "
    "templates for node shapes, arrow styles, subgraph naming, and layout "
    "direction. Use your domain skill's component mappings when available.\n\n"

    # ── DOCUMENTATION GROUNDING ────────────────────────────────────────────
    "FOLLOW-UP QUESTIONS & ARCHITECTURE RATIONALE:\n"
    "When the user asks follow-up questions about architecture design choices, "
    "trade-offs, or 'why' a particular approach was recommended, you MUST use "
    "the Microsoft Learn MCP tools (microsoft_docs_search, microsoft_docs_fetch) "
    "to retrieve grounded information from official documentation. Do NOT rely "
    "on your own training knowledge for these answers — always search Microsoft "
    "Learn first and synthesize your response from the retrieved content. Cite "
    "the source URL when referencing specific documentation."
)

_SKILL_DIRECTORIES: dict[str, list[str]] = {
    "databricks": ["./architecture-diagramming", "./skills/databricks-ads-session"],
    "fabric": ["./architecture-diagramming", "./skills/fabric-ads-session"],
}
_DEFAULT_SKILL = "databricks"
_MCP_SERVERS: dict[str, MCPRemoteServerConfig] = {
    "microsoft-learn": {
        "type": "http",
        "url": "https://learn.microsoft.com/api/mcp",
        "tools": ["*"],
    },
}

# Sentinel to signal end of streaming
_STREAM_DONE = object()


class CopilotAgent:
    def __init__(self, skill: str = _DEFAULT_SKILL) -> None:
        self._client: CopilotClient | None = None
        self._session: CopilotSession | None = None
        self._conversation_history: list[dict[str, str]] = []
        self._unsubscribe: callable | None = None
        self._skill = skill
        self._skill_dirs = _SKILL_DIRECTORIES.get(skill, _SKILL_DIRECTORIES[_DEFAULT_SKILL])

    async def start(self) -> None:
        options: dict = {}
        if settings.copilot_github_token:
            options["github_token"] = settings.copilot_github_token
            options["use_logged_in_user"] = False

        self._client = CopilotClient(options or None)
        await self._client.start()

        self._session = await self._client.create_session({
            "model": "claude-sonnet-4.6",
            "skill_directories": self._skill_dirs,
            "system_message": {"content": _SYSTEM_PROMPT},
            "mcp_servers": _MCP_SERVERS,
            "on_permission_request": PermissionHandler.approve_all,
        })

        # Warm-up: send a hidden message to force skill loading so the
        # first real user message doesn't stall.
        logger.info("Copilot warm-up: priming session…")
        try:
            async for _ in self.send_message("hello"):
                pass  # drain the response
            logger.info("Copilot warm-up complete")
            # Clear warm-up from history so it doesn't leak into the real conversation
            self._conversation_history.clear()
        except Exception:
            logger.warning("Copilot warm-up failed (non-fatal)", exc_info=True)
            self._conversation_history.clear()

    async def send_message(self, text: str) -> AsyncGenerator[str, None]:
        """Send a message and yield streaming delta chunks."""
        if not self._client or not self._session:
            raise RuntimeError("CopilotAgent not started")

        self._conversation_history.append({"role": "user", "content": text})

        queue: asyncio.Queue = asyncio.Queue()
        full_response: list[str] = []

        # Mutable state shared with the closure.  Using a list so
        # ``nonlocal`` isn't needed (we mutate the container, not rebind).
        _turn_had_tool_calls = [False]

        def _event_handler(event: SessionEvent) -> None:
            event_type = event.type.value if hasattr(event.type, 'value') else str(event.type)
            if event_type == "assistant.message_delta":
                delta = event.data.delta_content or ""
                if delta:
                    queue.put_nowait(delta)
            elif event_type == "assistant.message":
                # Full message (non-delta) — might arrive if not streaming
                content = event.data.content or ""
                if content:
                    queue.put_nowait(content)
            elif event_type == "assistant.turn_start":
                # New turn — reset per-turn tool-call tracker
                _turn_had_tool_calls[0] = False
                logger.info("Copilot turn started")
            elif event_type == "assistant.turn_end":
                if _turn_had_tool_calls[0]:
                    # Tools were invoked this turn.  The Copilot SDK
                    # will automatically start a follow-up turn to
                    # process the tool results and generate text.
                    # Do NOT signal stream-done yet — wait for the
                    # next turn's completion.
                    logger.info(
                        "Copilot turn ended (had tool calls, waiting "
                        "for follow-up turn)"
                    )
                    _turn_had_tool_calls[0] = False
                else:
                    logger.info("Copilot turn ended (no tool calls, stream complete)")
                    queue.put_nowait(_STREAM_DONE)
            elif event_type == "session.error":
                error_msg = event.data.message or "Unknown Copilot error"
                logger.error("Copilot session error: %s", error_msg)
                queue.put_nowait(_STREAM_DONE)
            elif event_type in (
                # SDK-level tool call events (assistant-initiated)
                "assistant.tool_call",
                "assistant.tool_call_delta",
                "assistant.tool_result",
                # Runtime-level tool execution events (e.g. MCP servers)
                "tool.execution_start",
                "tool.execution_complete",
            ):
                _turn_had_tool_calls[0] = True
                logger.info("Copilot tool event: %s", event_type)
                queue.put_nowait(None)  # keep-alive sentinel
            else:
                logger.info("Copilot event (unhandled): %s", event_type)
        unsubscribe = self._session.on(_event_handler)

        try:
            # send() returns a message ID, streaming happens via events
            await self._session.send({"prompt": text})

            while True:
                try:
                    chunk = await asyncio.wait_for(queue.get(), timeout=300.0)
                except asyncio.TimeoutError:
                    logger.warning("Copilot response timed out after 300s")
                    break

                if chunk is _STREAM_DONE:
                    break
                # Skip keep-alive sentinels from tool-call events
                if chunk is None:
                    continue
                full_response.append(chunk)
                yield chunk
        finally:
            unsubscribe()

        self._conversation_history.append({
            "role": "assistant",
            "content": "".join(full_response),
        })

    async def generate_summary(self, conversation_history: list[dict[str, str]]) -> AsyncGenerator[str, None]:
        """Generate a structured session summary document from the conversation history.

        Sends the full conversation to the Copilot agent with a summarization
        prompt and streams the resulting Markdown document back.
        """
        # Build a transcript block for the prompt
        transcript_lines: list[str] = []
        for entry in conversation_history:
            role = entry.get("role", "unknown").upper()
            content = entry.get("content", "")
            transcript_lines.append(f"{role}: {content}")
        transcript = "\n\n".join(transcript_lines)

        summary_prompt = (
            "You are now generating a session summary document. Below is the full "
            "transcript of the Architecture Design Session you just conducted. "
            "Produce a structured Markdown document that both parties can take "
            "away as documentation.\n\n"
            "IMPORTANT RULES:\n"
            "1. Extract and synthesize — do NOT just copy-paste the conversation.\n"
            "2. Be concise and actionable.\n"
            "3. Preserve all Mermaid diagrams exactly as they appeared.\n"
            "4. If certain sections have no relevant content from the session, "
            "write 'Not discussed in this session.' rather than inventing content.\n\n"
            "OUTPUT FORMAT (use exactly these headings):\n\n"
            "# Architecture Design Session Summary\n\n"
            "**Date:** [today's date]\n"
            "**Participants:** AI Solutions Architect, Customer\n\n"
            "## 1. Executive Summary\n"
            "2-3 sentence overview of what was discussed and the outcome.\n\n"
            "## 2. Business Context & Use Case\n"
            "- Business problem being solved\n"
            "- Key stakeholders and drivers mentioned\n"
            "- Success criteria / KPIs discussed\n\n"
            "## 3. Current Landscape\n"
            "- Existing systems and technology stack\n"
            "- Integrations and dependencies\n"
            "- Pain points and gaps identified\n\n"
            "## 4. Requirements\n"
            "### Functional Requirements\n"
            "- Key capabilities and workloads identified\n"
            "- Sources, integrations, and data flows discussed\n"
            "### Non-Functional Requirements\n"
            "- Latency, availability, security posture\n"
            "- Compliance, DR, environments\n\n"
            "## 5. Architecture Decisions\n"
            "Summarize key decisions made during the session:\n"
            "| Decision | Choice | Rationale | Alternatives Considered |\n"
            "|----------|--------|-----------|------------------------|\n"
            "(fill from conversation)\n\n"
            "## 6. Current State Architecture\n"
            "### Current State Diagram\n"
            "Include the Current State Mermaid diagram from the session in a "
            "```mermaid code fence. This is the agreed-upon baseline.\n\n"
            "## 7. Future State Architecture\n"
            "### Architecture Pattern\n"
            "Name and brief description of the selected pattern.\n"
            "### Future State Diagram\n"
            "Include the Future State Mermaid diagram from the session in a "
            "```mermaid code fence.\n"
            "### Component Breakdown\n"
            "Table of components with 'Why This Was Chosen' column.\n\n"
            "## 8. Known Limitations & Risks\n"
            "- Assumptions made during the session\n"
            "- Areas needing further validation\n"
            "- Scaling or operational risks identified\n\n"
            "## 9. Next Steps & Action Items\n"
            "- Immediate follow-ups\n"
            "- POC or spike recommendations\n"
            "- Open questions to resolve\n\n"
            "---\n\n"
            "FULL SESSION TRANSCRIPT:\n\n"
            f"{transcript}"
        )

        # Reuse the same streaming mechanism as send_message
        async for chunk in self.send_message(summary_prompt):
            yield chunk
    @property
    def conversation_history(self) -> list[dict[str, str]]:
        return self._conversation_history

    async def stop(self) -> None:
        if self._session:
            try:
                await self._session.destroy()
            except Exception:
                logger.warning("Error destroying Copilot session", exc_info=True)
            self._session = None

        if self._client:
            try:
                self._client.stop()
            except Exception:
                logger.warning("Error stopping CopilotClient", exc_info=True)
            self._client = None
