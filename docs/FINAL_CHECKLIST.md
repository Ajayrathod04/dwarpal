# Final submission checklist — read before clicking Submit

## Deadline and cutoff

- Official deadline: **Friday, October 23, 2026, 12:00 PM PDT = Saturday, October 24, 2026, 12:30 AM IST**.
- Suggested internal code/content freeze: **October 23, 11:20 PM IST**.
- Suggested final submission target: **October 23, 11:45 PM IST**, leaving about 45 minutes for portal issues.
- After the submission period ends, Devpost rules prohibit changing submitted materials except narrow sponsor-approved remediation. Freeze early and do not rely on post-deadline edits.

## Code and demo evidence

- [ ] In the exact final folder, run `python -m compileall -q app tests`.
- [ ] Run `python -m pytest -q`; capture the actual result from your machine.
- [ ] Run `node --check app/static/app.js` if Node is installed.
- [ ] Start the app with `uvicorn app.main:app --host 127.0.0.1 --port 8000`.
- [ ] Open the homepage and `/api/health`; don't claim MCP is live unless `mcp_sdk_available` is true and an MCP client successfully lists and calls a tool.
- [ ] Demonstrate: prepare a home-service plan; show its SHA-256 action hash; attempt approval without identity and show denial; create a new plan, enable simulated identity, approve it, show the one-entry/15-minute preview; prove replay is rejected; refresh the audit trail.
- [ ] Explain that identity, approval, and access are simulated. No contractor or physical lock is connected.
- [ ] Don't show a fake AWS console, invented results, or a feature that doesn't work in the submitted build.

## Repository and Devpost

- [ ] Push the final code to a GitHub repository before the cutoff.
- [ ] Make the repo public and ensure the MIT `LICENSE` is visible, or follow the private-repo reviewer-sharing instructions in the official rules.
- [ ] Verify `README.md`, requirements files, setup instructions, tests, technical report, demo script and screenshots are included.
- [ ] Remove local SQLite files, Python bytecode/cache folders, secrets, `.env`, personal data and unused assets.
- [ ] Explain that the web simulator is the selected Alexa+ path. Do not claim native Alexa+ partner integration.
- [ ] Select **Alexa+ primary track**.
- [ ] Select **AWS Builder mini-challenge only if** a qualifying live AWS service integration was actually configured and demonstrated. Current prepared build has no verified live AWS integration.
- [ ] Select **Open Source mini-challenge only if** a qualifying additional public project/contribution was made during the hackathon window and you can provide the required contribution URL, repo URL, GitHub username and description.
- [ ] Paste a public YouTube/Vimeo demo URL; English, under 3 minutes.
- [ ] Complete product feedback for every tool/API/SDK actually used. Remove claims about integrations you did not test.
- [ ] Submit friction logs only for friction you personally experienced. Do not copy the isolated preparation environment's pip/DNS failure as your own if it did not occur for you.
- [ ] If the project existed before the hackathon period, accurately disclose what was significantly updated during the period. Do not fabricate dates or commits.

## Rules to re-read

- [Official rules](https://amazonappdev2026.devpost.com/rules): eligibility, new/significantly updated project, runtime integration, demo/video, repo visibility/license, judging, prize stacking, and post-deadline restrictions.
- [Official FAQ](https://amazonappdev2026.devpost.com/details/faqs): preview-only Alexa+ tools are unavailable to all participants; simulation path is allowed.
- [Official resources](https://amazonappdev2026.devpost.com/resources): SDKs, samples, docs and office hours.

## Stop conditions

If the app fails to start, the workflow doesn't complete, or the repo/video link is broken, fix that before adding features. If no live AWS integration is available, skip the AWS Builder mini-challenge rather than claiming it. No plan can guarantee a prize.
