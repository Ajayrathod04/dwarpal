# Architecture and threat model

## Trust boundary
The browser or MCP client is untrusted. Tool arguments are untrusted. The policy adapter is the decision point. Unknown actions and unavailable AVP calls deny by default. Tool handlers return a reason and log a decision.

## Security invariants
1. No external side effect exists in this demo.
2. `request_access` is simulated and denied unless both simulated identity evidence and explicit homeowner approval are present for the resident persona.
3. Maintenance tool creates a proposal, not a dispatch.
4. Every policy evaluation made by the service is logged to SQLite.
5. Unknown actions fail closed.
6. AWS AVP failures fail closed.

## Limitations
- Local role strings are caller-supplied, not authenticated identity claims. This is acceptable only for a local simulation.
- SQLite is not tamper-proof; a production design would use authenticated identity, AVP with a Cognito/OIDC identity source, durable centralized audit storage, key management, monitoring, and least-privilege IAM.
- The current AVP adapter uses illustrative entity type names. Map these to the exact Cedar schema in the deployed policy store before enabling `POLICY_MODE=aws_avp`.
- No real door, external service, native Alexa+ account, or resident data is connected.


## Submission-path decision

The safe primary path is the hackathon's simulated Alexa+-style web experience. The optional MCP server is not counted as verified until a compatible client can list and call the tools. When mounted into FastAPI, the host app explicitly starts the MCP session manager in its lifespan; mounted sub-app lifespan hooks do not automatically run. AWS Builder is not claimed until a live AWS API call is captured.
