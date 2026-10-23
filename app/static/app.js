const $ = id => document.getElementById(id);
async function post(url, body) {
  const r = await fetch(url, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)});
  return await r.json();
}
function pretty(x){return JSON.stringify(x,null,2)}
function escapeHtml(value){return String(value ?? "").replace(/[&<>\"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
let currentWorkflow = null;
async function refreshAudit(){
  try {
    const data=await (await fetch("/api/audit?limit=20")).json();
    const rows=$("auditRows");
    if(!data.events.length){rows.innerHTML='<div class="empty-row">No events yet. Run a scenario above.</div>';return}
    rows.innerHTML=data.events.map(e=>`<div class="audit-row"><span>${escapeHtml(new Date(e.ts).toLocaleString())}</span><span><b>${escapeHtml(e.principal)}</b><br>${escapeHtml(e.action)} · ${escapeHtml(e.resource)}</span><span><i class="decision-chip ${e.decision === "ALLOW" ? "ALLOW" : "DENY"}">${escapeHtml(e.decision)}</i><br>${escapeHtml(e.reason)}</span><span>${escapeHtml(e.engine)}</span></div>`).join("");
  } catch(e){$("auditRows").innerHTML='<div class="empty-row">API unavailable. Start the server and refresh.</div>'}
}
$("runAccess").addEventListener("click",async()=>{
  const btn=$("runAccess");btn.disabled=true;btn.textContent="EVALUATING…";
  try{
    const d=await post("/api/access",{principal_role:$("role").value,door_id:$("door").value,reason:$("reason").value,verified_identity:$("verified").checked,homeowner_approved:$("homeownerApproved").checked});
    const box=$("decision");box.className="decision "+(d.decision==="ALLOW"?"allow-result":"deny-result");
    const scope = d.simulated_grant_preview ? `<p><strong>SIMULATED SCOPE:</strong> ${escapeHtml(d.simulated_grant_preview.resource_scope)} · ${d.simulated_grant_preview.max_entries} entry · ${d.simulated_grant_preview.valid_for_minutes} minutes · preview only</p>` : "";
    box.innerHTML=`<div class="decision-icon">${d.decision==="ALLOW"?"✓":"×"}</div><div><b>${escapeHtml(d.decision)} / ${escapeHtml(d.engine.toUpperCase())}</b><p>${escapeHtml(d.reason)}</p>${scope}<p><strong>Receipt:</strong> ${escapeHtml(d.audit.timestamp)} · ${escapeHtml(d.audit.decision)}</p><p>${escapeHtml(d.safety_note)}</p></div>`;
    await refreshAudit();
  }catch(e){alert("API request failed. Check that the server is running.")}finally{btn.disabled=false;btn.innerHTML='EVALUATE ACCESS <span>↗</span>'}
});
$("runCase").addEventListener("click",async()=>{
  const d=await post("/api/case",{case_id:$("caseId").value,principal_role:"resident"});
  $("caseResult").textContent=pretty(d);await refreshAudit();
});
$("runProposal").addEventListener("click",async()=>{
  const d=await post("/api/proposal",{case_id:"CASE-1042",action:$("proposal").value,rationale:"Demo request: "+$("proposal").value,principal_role:"support_agent"});
  $("proposalResult").textContent=pretty(d);await refreshAudit();
});
$("runWorkflow").addEventListener("click",async()=>{
  const btn=$("runWorkflow");btn.disabled=true;btn.textContent="PREPARING EXACT PLAN…";
  try{
    currentWorkflow=await post("/api/workflow",{case_id:$("caseId").value,request:$("workflowRequest").value});
    $("workflowResult").textContent=pretty(currentWorkflow);
    $("approveWorkflow").disabled=!(currentWorkflow.ok && currentWorkflow.run_id && currentWorkflow.action_hash && currentWorkflow.status==="AWAITING_HUMAN_APPROVAL");
    await refreshAudit();
  }catch(e){currentWorkflow=null;$("workflowResult").textContent="Workflow preview failed. Check the local server."}
  finally{btn.disabled=false;btn.textContent="PREPARE EXACT PLAN ↗"}
});
$("approveWorkflow").addEventListener("click",async()=>{
  if(!currentWorkflow)return;
  const btn=$("approveWorkflow");btn.disabled=true;btn.textContent="CHECKING APPROVAL…";
  try{
    const decision=await post("/api/workflow/approve",{run_id:currentWorkflow.run_id,action_hash:currentWorkflow.action_hash,verified_identity:$("verified").checked});
    $("workflowResult").textContent=pretty({preview:currentWorkflow,approval:decision});
    currentWorkflow=null;await refreshAudit();
  }catch(e){$("workflowResult").textContent="Approval request failed. Check the local server."}
  finally{btn.disabled=true;btn.textContent="APPROVAL RECORDED / PREPARE NEW PLAN"}
});
$("refreshAudit").addEventListener("click",refreshAudit);
(async()=>{try{const h=await(await fetch("/api/health")).json();$("health").textContent=`API OK · POLICY ${h.policy_mode.toUpperCase()} · ${h.mcp_sdk_available ? "MCP READY" : "SIMULATOR MODE"}`;await refreshAudit()}catch(e){$("health").textContent="API OFFLINE"}})();
