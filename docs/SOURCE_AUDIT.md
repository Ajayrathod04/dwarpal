# Strict source audit — Amazon Developer Hackathon / DWARPAL

**Audit date:** 2026-10-23. This audit distinguishes source-file facts, official event requirements, historical BOND findings from prior conversation context, and unverified implementation claims.

## 1. Files inspected and how they relate

The current conversation contains two user-provided text files plus five differently sized project-backed snapshots named `Hackathon Development Plan.txt`. They are not interchangeable copies.

| Source | Contents found | Relevance to this submission |
|---|---|---|
| `Pasted text (2)(2).txt` (148 rendered lines) | The user's strict audit prompt: read official pages, list rules/prizes/judges, inspect prior art, map criteria to features, avoid copying winners, prepare a complete build and submission plan, mark unverified facts | Treated as the required review method; no unsupported winners, judging weights, or integrations are invented |
| `Pasted text(20261023-155805).txt` (353 rendered lines) | Copy of the Amazon Developer Hackathon Devpost page and rules/criteria/prizes/judges | Primary source for the track requirements, demo length, feedback/friction-log obligations, prizes and judging criteria |
| `Hackathon Development Plan.txt` (490 rendered lines in Files metadata; 489 physical lines in the mounted copy) | Earlier Mergetober and Graph Hacks strategy, WhyGraph architecture, build schedule, acceptance tests and Antigravity guidance | Historical context only; the WhyGraph/FalkorDB design is not submitted as DWARPAL and is not proof that DWARPAL is working |
| `Hackathon Development Plan.txt` (207 lines) | Mergetober/Cognee contribution guidance, Graph Hacks RECALL plan, Hack Apertus plan | Historical context only; important rule distinction: the Mergetober AI-generated PR restriction is not an Amazon hackathon rule |
| `Hackathon Development Plan.txt` (43 lines) | Earlier WhyGraph status report: unit tests passed against FakeStore; FalkorDB unavailable; repo not pushed; browser E2E not run | Used as a warning not to equate unit tests with real service verification |
| `Hackathon Development Plan.txt` (158 lines) | Earlier judge-level WhyGraph audit: FakeStore tests, real DB integration blocked, browser tests unrun, deployment/repo/video pending | Used as a checklist of credibility gaps: real service proof, E2E testing, public repo and demo evidence |
| `Hackathon Development Plan.txt` (50 lines) | Later WhyGraph snapshot says Render URL and FalkorDB Cloud health check worked, but LLM mode was offline | Conflicts with the earlier snapshot only because it is later; it still does not verify DWARPAL or any Amazon submission component |
| Uploaded UI references | Spotify summer-campaign-style typography, maximalist doodle art, peach/pink neo-brutalism, editorial cream layout, 3D type, hackathon graphics and dark neon layouts | Visual inspiration only. No Spotify logo/artwork is copied; proprietary Spotify Mix is not bundled |

**BOND/BOOND evaluation limitation:** the current uploaded text-file set does not contain a standalone original BOND judging report. The following lessons are carried over from the prior conversation summary, not re-quoted as if the original document were re-opened: AWS usage 5/10; idea/impact 5/8; execution, demo and design each 3/4; criticism of a basic serverless stack, Cedar used as a library rather than Amazon Verified Permissions, raw public S3 URL, simulated-only integration path, weak real-world validation and a post-deadline commit.

## 2. Amazon event facts grounded in the provided page and official rules

- Event: **Build, Ship, Shape: Amazon Developer Hackathon**.
- Deadline in the copied page/rules: **Friday, October 23, 2026, 12:00 PM Pacific Daylight Time**, which is **Saturday, October 24, 2026, 12:30 AM IST**.
- Primary tracks: Fire TV, Alexa+, Bee, Ring.
- Alexa+ has two permitted implementation paths: a self-hosted MCP server or Agent Skill using MCP spec 2025-11-25 or later over Streamable HTTP; alternatively, a simulated Alexa+ web experience. The official FAQ says the preview-only Alexa+ add-on tools are not available to all hackathon participants and are not required.
- Demo video: public YouTube/Vimeo, English, **under 3 minutes**.
- Required materials: project description, source repository with setup instructions, track selection, product feedback for every tool/API/SDK actually used. The public repo must visibly include an open-source license, or the private repo must be shared with the specified reviewers and testing address.
- Judging: Stage 1 pass/fail baseline viability and use of required technology; Stage 2 has four equally weighted criteria: Tech Implementation, Design, Potential Impact, Quality of the Idea.
- Friction logs are optional but can contribute **up to a 10% bonus**. Entries must document the actual task, steps, expected versus actual outcome, severity, workaround and actionable suggestion.
- One project can win at most one primary-track prize and one mini-challenge prize.
- The copied rules also say participants could request $150 AWS promotional credits by October 21, 2026 at 12:00 PM PT while supplies lasted. That request deadline has passed as of October 23; do not plan on those credits being newly available.
- Prize-page discrepancy resolved: **$138,000 is the cash total** shown on the event page; the stated **$190,000 value includes AWS credits**. The page copy lists $5,000 cash plus $5,000 AWS credits for each mini-challenge winner.

Official sources: [Rules](https://amazonappdev2026.devpost.com/rules), [FAQ](https://amazonappdev2026.devpost.com/details/faqs), [Resources](https://amazonappdev2026.devpost.com/resources), [Alexa+ MCP quickstart](https://www.developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-quickstart), [MCP Python SDK v1 documentation](https://py.sdk.modelcontextprotocol.io/v1/), [MCP ASGI mounting and lifespan guidance](https://py.sdk.modelcontextprotocol.io/run/asgi/).

## 3. Judge panel and what the published information supports

The supplied page lists judges across the Amazon Devices leadership, Fire TV, Alexa, Bee, Ring, AWS, and developer tooling ecosystems. Named entries include Jon Kirk (VP, Amazon Devices); Joshua Danovitz (VP, Fire TV Experience); Dawn Martyniuk (Senior Manager, Fire TV Voice & AI); Macy Armstrong (Director, Fire TV Devices); Karthik Ragubathy and Saylee Joshi (Senior Solutions Architects, Alexa); Emerson Sklar (Chief Evangelist, Alexa); Maria de Lourdes Zollo and Ethan Sutin (Bee co-founders/leaders); Kourtney Meiss (Developer Evangelist); Alex Clausen, Roman Alekseenkov and Harish Komaragiri (Ring roles); Brittney Hurst and Chris Melissinos (AWS roles); Mike Grabowski (Vega OS/Callstack); and Mo Gorhom (Senior Software Development Engineer).

The defensible inference from the published roles and official rubric is that the submission must be technically credible, easy to understand, tied to a specific customer workflow, and honest about platform integration. Individual judge preferences, private discussions, or unpublished scoring tendencies were not verified; no personal preferences are attributed to these judges.

## 4. Criteria-to-feature mapping

| Published criterion (equal weight) | DWARPAL feature/evidence | Remaining risk |
|---|---|---|
| Tech Implementation | FastAPI application, three guarded capabilities, multi-step orchestration endpoint, SQLite event receipts, tests; optional MCP source | MCP SDK could not be installed in this preparation environment; no MCP client call or live AWS service has been verified |
| Design | Responsive campaign-style interface, oversized typography, neo-brutalist cards, approval controls, visible trace and audit trail | Must be browser-tested on the participant's machine and recorded in the final video |
| Potential Impact | Home-service scheduling and guest/contractor access are a concrete, understandable scenario; default is human review | No real home-service provider, identity provider, lock or resident is connected; impact is a prototype hypothesis, not field-validated |
| Quality of the Idea | Multi-step home workflow combines case context, proposal generation, explicit approval gate, deny-by-default policy and receipts | Needs a crisp demo that proves the orchestration and approval gate; avoid presenting it as a generic chatbot or production security system |

## 5. BOND/BOOND weaknesses and concrete corrections

| Prior BOND weakness | Correction in this build | What is still unverified |
|---|---|---|
| AWS usage scored 5/10; AVP not truly integrated | Optional AVP adapter exists and is clearly marked optional; AWS Builder is not claimed without a real API call | No policy store, schema, Cedar policy or live `IsAuthorized` result configured here |
| Simulated-only integration path | A multi-step scenario is executable locally and its simulation boundary is explicit; the optional MCP path is implemented in source | No external service or native Alexa+ account is connected; the MCP endpoint has not been smoke-tested |
| Demo lacked evidence of service interaction | Workflow response exposes each step and every policy result; SQLite audit trail persists locally | Must record a live run of this version and verify it on the participant's machine |
| Incomplete browser proof | API tests use FastAPI TestClient; app is launched and the health/home routes returned HTTP 200 in this preparation environment | No full browser automation or cross-browser E2E has been run |
| Submission timing/repository credibility | This package includes an MIT license, README, tests, demo script, feedback and friction log | User must publish the correct repo before deadline, verify license visibility, and submit public video URL |
| UI was not enough to overcome weak proof | Added an approval-aware three-step workflow rather than only visual polish | Need to keep the demo focused; do not add unverified features at the last minute |

## 6. Security and honesty review

- The UI role selector and simulated identity/approval toggles are user-controlled demo inputs. They are not authentication and must not be used for real access control.
- The local policy denies unknown actions and requires both simulated identity evidence and explicit homeowner approval for the resident allow-path.
- A maintenance proposal is recorded only; no contractor is contacted and no physical lock is operated.
- SQLite is a local demo audit store, not tamper-proof or managed compliance storage.
- No real AWS Verified Permissions, Bedrock, Strands, Ring, Bee, Fire TV, or native Alexa+ integration is claimed.
- Product feedback and friction log entries must be edited if the participant's actual environment differs. Never claim an untested SDK/API worked.

## 7. Prior art and winner analysis status

This is the first combined Amazon Devices hackathon described by the event page, so there are no prior winners from this exact event to analyze before judging. The current project gallery already contains relevant entrants (not winners); the following are a useful originality check, not a claim of their scores or final outcomes:

| Current entrant / reference | What its public page describes | Overlap risk | DWARPAL distinction that must be demonstrated |
|---|---|---|---|
| [VoiceGuard MCP](https://devpost.com/software/voiceguard-mcp-uegiqs) | Simulated Alexa+ safety checkpoint, explicit confirmation for consequential calls, hash-linked audit | High on generic safety gate + audit | Focus on the household service-handoff journey: case context → maintenance proposal → access decision → scoped one-entry/15-minute preview; don't claim tamper-proof logs |
| [SafeDesk](https://devpost.com/software/gnypcior-safedesk) | Human-gated desktop/MCP actions, hashes, scoped execution and result verification | Medium on approval gating | Home-service and contractor-entry use case, with no actual device execution claimed |
| [Alexa+ LifeOS](https://devpost.com/software/alexa-lifeos-agentic-mcp-server-life-assistant) | Multi-step personal assistant with tools, voice simulation and approval flow | Medium on multi-step assistant pattern | Narrow service-provider handoff and explicit deny-by-default access decision |
| [Steward](https://devpost.com/software/steward-a-personal-ops-agent-skill-for-alexa) | Persistent personal operations across calendar, reminders, notes and preferences | Low-to-medium on persistent assistant state | Explicitly scoped, approval-gated physical-world handoff rather than general personal productivity |

Cross-event pattern examples are available too. The WeMakeDevs First Commit recap describes Suraksha, a companion for an aging parent, and Beacon Night Shift, which diagnoses an incident, proposes an allowlisted fix, dry-runs it and waits for approval. These are winner write-ups from another event, not Amazon hackathon winners. The transferable lesson is to target a specific person and workflow, show evidence, and make approval part of the execution path—not a decorative button. [Source](https://www.wemakedevs.org/blogs/first-commit-hackathon-recap-and-whats-next).

The Amazon rules explicitly call a basic MCP wrapper or single-turn Q&A bot an obvious Alexa+ idea, and describe multi-service agentic workflows, context across sessions, and richer interaction as creative directions. The three-step DWARPAL flow moves in that direction, and its approval is bound to a persisted plan hash, but its deterministic workflow is **not an LLM agent** and no persistent personal memory is claimed. The biggest remaining competitive gap is real tool interoperability and a richer, verified assistant experience. [Official criteria](https://amazonappdev2026.devpost.com/rules).

Do not invent a winner list, score, judge quote or competitor count. The participant count in the supplied page copy is a dynamic snapshot (64,486) and should not be presented as the number of competing submissions.

## 8. Go/no-go verdict

**GO for the Alexa+ simulated-experience primary track**, because the official rules explicitly allow the web simulation route and it can be demonstrated without inaccessible preview-only tools. **NO-GO for claiming the MCP-server path until a compatible client lists and calls the tools. NO-GO for AWS Builder until a real qualifying AWS integration is configured and shown. NO-GO for Open Source mini-challenge unless an additional qualifying public contribution is actually made and the required URLs/details are ready.**

Verification in this preparation environment: `python -m compileall -q app tests` passed; `python -m pytest -q` passed 15 tests in the final run; `node --check app/static/app.js` passed; a live Uvicorn smoke test returned HTTP 200 for the homepage and health endpoint, created a workflow preview, rejected a hash mismatch, accepted a simulated approval, and rejected replay. The MCP SDK was not installed, so no MCP client or live AWS call was verified.

The solution is stronger than the original starter because it has an end-to-end three-step scenario, an exact-plan SHA-256 approval binding, a single-use approval attempt, audit persistence, tests and clearer limitations. It is not guaranteed to win; its biggest remaining risks are the absence of a verified live Amazon/AWS integration, lack of an actual LLM-driven agent in the primary simulation, and lack of user validation.
