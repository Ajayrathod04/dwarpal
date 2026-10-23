# Devpost submission pack — DWARPAL

## Project title
DWARPAL — The consent layer for AI actions

## Short description
DWARPAL is a policy-first action gateway for AI assistants. It exposes guarded capabilities through a self-hosted MCP Streamable HTTP server, evaluates requests before any action, and records an inspectable audit receipt. The browser simulator demonstrates allow/deny decisions, read-only case lookup, and human-approved maintenance proposals.

## Long description
AI assistants are moving from answering questions to taking actions across household, civic, and business systems. A single-turn chatbot can suggest a task, but it often hides the boundary between a user's intent and an action the system is actually authorized to perform.

DWARPAL makes that boundary visible. It exposes three tools over MCP: read a fictional case status, propose a maintenance action, and simulate an access request. Each request passes a policy check; unknown or unsafe actions are denied by default. The interface explains the decision and shows the audit receipt. Maintenance is only proposed, never dispatched, and no physical access device or external municipal service is connected.

The prototype runs locally without cloud credentials. Its local policy mode is explicitly labelled as a simulator. An optional Amazon Verified Permissions adapter and optional Strands/Bedrock agent are included for live integration, but they must be configured and verified before claiming them as working AWS services.

## Track selection
- Primary: Alexa+ — self-hosted MCP server / simulated Alexa+-style experience.
- AWS Builder mini-challenge: select only if you actually configure and demonstrate a live AWS service integration in the final demo and document it below.
- Open Source mini-challenge: this is a new MIT-licensed repository created during the hackathon window; only select if its timing and public repository status meet the official rules.

## Technologies
- Python, FastAPI, MCP Python SDK (Streamable HTTP), SQLite, HTML/CSS/JavaScript.
- Optional integrations: Amazon Verified Permissions via boto3; Amazon Bedrock through Strands Agents SDK.
- State exactly which optional integrations were live in the submitted build: [FILL IN].

## Product feedback
Complete `docs/PRODUCT_FEEDBACK.md` with real observations for each tool/API/SDK used. Don't submit placeholders.

## Friction log
Complete `docs/FRICTION_LOG.md` with actual friction events only. Do not fabricate issues or test outcomes.

## Demo
Public English video under 3 minutes: [PASTE YOUTUBE/VIMEO URL]
Repository: [PASTE PUBLIC GITHUB URL]
Live demo or local setup instructions: see README.

## Originality and scope
The design uses general visual references—oversized campaign typography, neon gradients, editorial bento cards and neo-brutalist borders—not copied logos, artwork or proprietary typefaces. Spotify Mix is proprietary and is not bundled. The app uses Archivo Black and Space Grotesk as substitutes.
