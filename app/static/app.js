const $ = id => document.getElementById(id);

async function post(url, body) {
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  return await r.json();
}

function pretty(x) {
  return JSON.stringify(x, null, 2);
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  }[c]));
}

let currentWorkflow = null;

// Update 7-step stepper UI
function updateStepper(steps) {
  if (!steps || !steps.length) return;
  const list = $("stepperList");
  if (!list) return;

  const stepElements = list.querySelectorAll(".stepper-item");
  steps.forEach((step, idx) => {
    if (idx < stepElements.length) {
      const el = stepElements[idx];
      const chip = el.querySelector(".step-chip");
      const status = step.status || "WAITING";
      chip.className = `step-chip ${status.toLowerCase()}`;
      chip.textContent = status;

      if (status === "COMPLETED") {
        el.classList.add("completed");
        el.classList.remove("active", "blocked");
      } else if (status === "PENDING") {
        el.classList.add("active");
        el.classList.remove("completed", "blocked");
      } else if (status === "BLOCKED") {
        el.classList.add("blocked");
        el.classList.remove("active", "completed");
      } else {
        el.classList.remove("active", "completed", "blocked");
      }
    }
  });

  const allCompleted = steps.every(s => s.status === "COMPLETED");
  const anyBlocked = steps.some(s => s.status === "BLOCKED");
  const stateBadge = $("wfStateBadge");
  if (stateBadge) {
    if (allCompleted) {
      stateBadge.textContent = "ALLOW PREVIEW";
      stateBadge.className = "live-dot allow-text";
    } else if (anyBlocked) {
      stateBadge.textContent = "DENIED";
      stateBadge.className = "live-dot deny-text";
    } else {
      stateBadge.textContent = "AWAITING APPROVAL";
      stateBadge.className = "live-dot warn-text";
    }
  }
}

// Render explainable risk assessment
function renderRiskAssessment(risk) {
  const card = $("riskCard");
  if (!card || !risk) {
    if (card) card.style.display = "none";
    return;
  }
  card.style.display = "block";
  const badge = $("riskLevelBadge");
  badge.textContent = risk.risk_level || "UNKNOWN";
  badge.className = `risk-level-badge risk-${(risk.risk_level || "elevated").toLowerCase()}`;

  $("riskExplanation").textContent = risk.explanation || "";
  $("riskNextStep").textContent = risk.recommended_next_step || "";

  const factorsEl = $("riskFactors");
  factorsEl.innerHTML = (risk.risk_factors || [])
    .map(f => `<span class="risk-tag">${escapeHtml(f)}</span>`)
    .join(" ");
}

// Render Decision Provenance (P1.4)
function renderProvenance(data, isApproval = false) {
  const container = $("provenanceContent");
  if (!container) return;

  if (!data) {
    container.className = "provenance-empty";
    container.innerHTML = `<div class="provenance-icon">🔍</div><b>NO ACTIVE DECISION</b><p>Prepare and approve a plan to view the full evidence trail and facts used.</p>`;
    return;
  }

  container.className = "provenance-body";
  const status = data.status || (data.ok ? "ALLOW" : "DENY");
  const isAllow = status === "APPROVED_SIMULATED" || data.ok === true;
  const hash = data.action_hash || (data.workflow_preview ? data.workflow_preview.action_hash : "");
  const runId = data.run_id || (data.workflow_preview ? data.workflow_preview.run_id : "");
  const caseId = (data.plan ? data.plan.case_id : null) || (data.provenance ? data.provenance.case_id : "CASE-1042");
  const reasonCode = (data.access_decision ? data.access_decision.reason_code : null) || (data.provenance ? data.provenance.policy_reason_code : data.reason_code) || "EVALUATED";
  const reasonText = (data.access_decision ? data.access_decision.reason : null) || (data.provenance ? data.provenance.policy_reason : data.reason) || "Policy rules checked.";

  container.innerHTML = `
    <div class="provenance-decision-banner ${isAllow ? "allow-banner" : "deny-banner"}">
      <b>${isAllow ? "✓ ACCESS SCOPE PREVIEW ALLOWED" : "× ACCESS REQUEST DENIED"}</b>
      <span>STATUS: ${escapeHtml(status)}</span>
    </div>
    <div class="provenance-facts">
      <div class="p-fact"><span class="p-lbl">Source Case:</span> <b>${escapeHtml(caseId)}</b></div>
      <div class="p-fact"><span class="p-lbl">Workflow Run ID:</span> <code>${escapeHtml(runId)}</code></div>
      <div class="p-fact"><span class="p-lbl">Policy Reason Code:</span> <b class="chip-code">${escapeHtml(reasonCode)}</b></div>
      <div class="p-fact"><span class="p-lbl">Decision Rationale:</span> <p>${escapeHtml(reasonText)}</p></div>
      <div class="p-fact"><span class="p-lbl">Canonical Digest:</span> <code class="break-hash">${escapeHtml(hash)}</code></div>
      <div class="p-fact"><span class="p-lbl">Audit Status:</span> <b>Appended to local demo SQLite log</b></div>
      <div class="p-fact"><span class="p-lbl">Simulation Notice:</span> <em>Identity and physical entry are simulated only.</em></div>
    </div>
  `;
}

// Refresh audit trail
async function refreshAudit() {
  try {
    const data = await (await fetch("/api/audit?limit=25")).json();
    const rows = $("auditRows");
    if (!data.events || !data.events.length) {
      rows.innerHTML = '<div class="empty-row">No events yet. Run a scenario above.</div>';
      return;
    }
    rows.innerHTML = data.events.map(e => {
      const dt = new Date(e.ts).toLocaleString();
      const decClass = e.decision === "ALLOW" ? "ALLOW" : "DENY";
      const evtType = e.event_type || e.action;
      const rCode = e.reason_code ? ` [${escapeHtml(e.reason_code)}]` : "";
      const corr = e.correlation_id ? `<br><small class="mono-tiny">ID: ${escapeHtml(e.correlation_id)}</small>` : "";
      const simBadge = e.simulated ? `<span class="sim-badge">SIM</span>` : "";
      return `
        <div class="audit-row">
          <span>${escapeHtml(dt)}${corr}</span>
          <span><b>${escapeHtml(e.principal)}</b><br><span class="action-tag">${escapeHtml(evtType)}</span> ${escapeHtml(e.resource)}</span>
          <span><i class="decision-chip ${decClass}">${escapeHtml(e.decision)}</i>${rCode}<br><small>${escapeHtml(e.reason)}</small></span>
          <span>${escapeHtml(e.engine)} ${simBadge}</span>
        </div>
      `;
    }).join("");
  } catch (e) {
    $("auditRows").innerHTML = '<div class="empty-row">API unavailable. Start the server and refresh.</div>';
  }
}

// Standalone Access Tool
$("runAccess").addEventListener("click", async () => {
  const btn = $("runAccess");
  btn.disabled = true;
  btn.textContent = "EVALUATING…";
  try {
    const d = await post("/api/access", {
      principal_role: $("role").value,
      door_id: $("door").value,
      reason: $("reason").value,
      verified_identity: false,
      homeowner_approved: false
    });
    const box = $("decision");
    box.className = "decision " + (d.decision === "ALLOW" ? "allow-result" : "deny-result");
    const scope = d.simulated_grant_preview
      ? `<p><strong>SIMULATED SCOPE:</strong> ${escapeHtml(d.simulated_grant_preview.resource_scope)} · ${d.simulated_grant_preview.max_entries} entry · ${d.simulated_grant_preview.valid_for_minutes} minutes · preview only</p>`
      : "";
    box.innerHTML = `
      <div class="decision-icon">${d.decision === "ALLOW" ? "✓" : "×"}</div>
      <div>
        <b>${escapeHtml(d.decision)} / ${escapeHtml(d.engine.toUpperCase())} [${escapeHtml(d.reason_code || "")}]</b>
        <p>${escapeHtml(d.reason)}</p>
        ${scope}
        <p><strong>Receipt:</strong> ${escapeHtml(d.audit.timestamp)} · ${escapeHtml(d.audit.decision)}</p>
        <p class="tiny-safety">${escapeHtml(d.safety_note)}</p>
      </div>`;
    await refreshAudit();
  } catch (e) {
    alert("API request failed. Check that the server is running.");
  } finally {
    btn.disabled = false;
    btn.innerHTML = "EVALUATE ACCESS <span>↗</span>";
  }
});

// Standalone Case Tool
$("runCase").addEventListener("click", async () => {
  const d = await post("/api/case", { case_id: $("caseId").value, principal_role: "resident" });
  $("caseResult").textContent = pretty(d);
  await refreshAudit();
});

// Standalone Proposal Tool
$("runProposal").addEventListener("click", async () => {
  const d = await post("/api/proposal", {
    case_id: "CASE-1042",
    action: $("proposal").value,
    rationale: "Demo request: " + $("proposal").value,
    principal_role: "support_agent"
  });
  $("proposalResult").textContent = pretty(d);
  await refreshAudit();
});

// Prepare Exact Plan (Workflow Step 1-3)
$("runWorkflow").addEventListener("click", async () => {
  const btn = $("runWorkflow");
  btn.disabled = true;
  btn.textContent = "PREPARING EXACT PLAN…";
  try {
    const selectedCase = $("caseSelect") ? $("caseSelect").value : "CASE-1042";
    currentWorkflow = await post("/api/workflow", {
      case_id: selectedCase,
      request: $("workflowRequest").value
    });

    $("workflowResult").textContent = pretty(currentWorkflow);

    if (currentWorkflow.ok) {
      // Update Stepper
      updateStepper(currentWorkflow.lifecycle_steps);

      // Render Risk Assessment
      renderRiskAssessment(currentWorkflow.risk_assessment);

      // Show Digest Card
      $("digestCard").style.display = "block";
      $("digestHash").textContent = currentWorkflow.action_hash;

      // Enable Approval Button
      $("approveWorkflow").disabled = false;
      $("tamperWorkflowBtn").disabled = false;
      $("approveWorkflow").textContent = "APPROVE THIS EXACT PLAN ↗";

      renderProvenance(currentWorkflow);
    } else {
      alert("Plan preparation failed: " + (currentWorkflow.reason || "Check server logs."));
    }
    await refreshAudit();
  } catch (e) {
    currentWorkflow = null;
    $("workflowResult").textContent = "Workflow preview failed. Check the local server.";
  } finally {
    btn.disabled = false;
    btn.textContent = "PREPARE EXACT PLAN ↗";
  }
});

// Approve Exact Plan (Workflow Step 4-7)
$("approveWorkflow").addEventListener("click", async () => {
  if (!currentWorkflow) return;
  const btn = $("approveWorkflow");
  btn.disabled = true;
  btn.textContent = "EVALUATING APPROVAL GATE…";

  try {
    const decision = await post("/api/workflow/approve", {
      run_id: currentWorkflow.run_id,
      action_hash: currentWorkflow.action_hash,
      verified_identity: $("verified").checked
    });

    $("workflowResult").textContent = pretty({ preview: currentWorkflow, approval: decision });

    if (decision.lifecycle_steps) {
      updateStepper(decision.lifecycle_steps);
    }
    if (decision.risk_assessment) {
      renderRiskAssessment(decision.risk_assessment);
    }

    renderProvenance(decision, true);

    currentWorkflow = null;
    await refreshAudit();
  } catch (e) {
    $("workflowResult").textContent = "Approval request failed. Check the local server.";
  } finally {
    btn.disabled = true;
    $("tamperWorkflowBtn").disabled = true;
    btn.textContent = "APPROVAL FINALIZED (PREPARE NEW PLAN)";
  }
});

// Tamper Test Button (P1.3 / P0.2)
$("tamperWorkflowBtn").addEventListener("click", async () => {
  if (!currentWorkflow) return;
  const btn = $("tamperWorkflowBtn");
  btn.disabled = true;
  btn.textContent = "SUBMITTING TAMPERED HASH…";

  try {
    // Intentionally submit an altered hash
    const tamperedHash = "f" * 64 || "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff";
    const decision = await post("/api/workflow/approve", {
      run_id: currentWorkflow.run_id,
      action_hash: tamperedHash,
      verified_identity: $("verified").checked
    });

    $("workflowResult").textContent = pretty({
      note: "Tampered hash was submitted to verify server-side rejection.",
      tampered_hash_submitted: tamperedHash,
      server_response: decision
    });

    renderProvenance(decision, true);
    currentWorkflow = null;
    await refreshAudit();
  } catch (e) {
    alert("Tamper test request failed.");
  } finally {
    btn.disabled = true;
    $("approveWorkflow").disabled = true;
  }
});

// Presets Handler (P1.3)
async function runPreset(presetName) {
  const banner = $("presetBanner");
  banner.style.display = "block";
  $("presetBannerTitle").textContent = `EXECUTING PRESET: ${presetName.toUpperCase()}`;
  $("presetBannerNarrative").textContent = "Sending real requests to backend…";

  try {
    const result = await post("/api/preset", { name: presetName });
    $("presetBannerTitle").textContent = `${result.title} · ${result.expected_decision}`;
    $("presetBannerNarrative").textContent = result.narrative;

    $("workflowResult").textContent = pretty(result);

    const wf = result.workflow_preview;
    const appr = result.approval_result || result.first_approval;

    if (appr && appr.lifecycle_steps) {
      updateStepper(appr.lifecycle_steps);
    } else if (wf && wf.lifecycle_steps) {
      updateStepper(wf.lifecycle_steps);
    }

    if (appr && appr.risk_assessment) {
      renderRiskAssessment(appr.risk_assessment);
    } else if (wf && wf.risk_assessment) {
      renderRiskAssessment(wf.risk_assessment);
    }

    if (wf) {
      $("digestCard").style.display = "block";
      $("digestHash").textContent = wf.action_hash;
    }

    renderProvenance(appr || wf, true);

    // Scroll to orchestration section smoothly
    $("workflow").scrollIntoView({ behavior: "smooth" });

    currentWorkflow = null;
    $("approveWorkflow").disabled = true;
    $("tamperWorkflowBtn").disabled = true;

    await refreshAudit();
  } catch (e) {
    $("presetBannerNarrative").textContent = "Preset request failed. Server might be offline.";
  }
}

$("presetSafe").addEventListener("click", () => runPreset("safe_approved"));
$("presetMissing").addEventListener("click", () => runPreset("missing_approval"));
$("presetTamper").addEventListener("click", () => runPreset("tampered_plan"));
$("presetReplay").addEventListener("click", () => runPreset("replayed_plan"));

$("presetReset").addEventListener("click", () => {
  $("presetBanner").style.display = "none";
  $("digestCard").style.display = "none";
  $("riskCard").style.display = "none";
  renderProvenance(null);
  currentWorkflow = null;
  $("approveWorkflow").disabled = true;
  $("tamperWorkflowBtn").disabled = true;
  $("workflowResult").textContent = "Workflow reset. Choose a preset or prepare a new plan.";

  // Reset stepper
  const list = $("stepperList");
  if (list) {
    list.querySelectorAll(".stepper-item").forEach(el => {
      el.className = "stepper-item";
      const chip = el.querySelector(".step-chip");
      chip.className = "step-chip waiting";
      chip.textContent = "READY";
    });
  }
  const stateBadge = $("wfStateBadge");
  if (stateBadge) {
    stateBadge.textContent = "READY";
    stateBadge.className = "live-dot";
  }
});

$("refreshAudit").addEventListener("click", refreshAudit);

// Initial Load & Health Check
(async () => {
  try {
    const h = await (await fetch("/api/health")).json();
    $("health").textContent = `API OK · POLICY ${h.policy_mode.toUpperCase()} · ${h.mcp_sdk_available ? "MCP STREAMABLE HTTP (2025-11-25)" : "SIMULATOR MODE"}`;

    const mcpEl = $("statusMcp");
    if (mcpEl) {
      mcpEl.textContent = h.mcp_sdk_available ? "mounted (/mcp) · Streamable HTTP (2025-11-25 verified)" : "unavailable (simulated route)";
      mcpEl.className = h.mcp_sdk_available ? "status-val allow" : "status-val muted";
    }

    const avpEl = $("statusAvp");
    if (avpEl) {
      avpEl.textContent = h.aws_avp_configured ? "configured" : "not configured";
      avpEl.className = h.aws_avp_configured ? "status-val allow" : "status-val muted";
    }

    const bedrockEl = $("statusBedrock");
    if (bedrockEl) {
      bedrockEl.textContent = h.strands_enabled ? "enabled" : "not configured";
      bedrockEl.className = h.strands_enabled ? "status-val allow" : "status-val muted";
    }

    await refreshAudit();
  } catch (e) {
    $("health").textContent = "API OFFLINE";
  }
})();
