const form = document.getElementById("checkinForm");
const statusEl = document.getElementById("status");
const resultCard = document.getElementById("resultCard");
const resultEl = document.getElementById("result");
const planTextEl = document.getElementById("planText");
console.log("app.js loaded");

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (m) => ({
    "&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"
  }[m]));
}

function renderAdvice(advice) {
  const sections = ["sleep","nutrition","training","steps","recovery"];
  const planHtml = sections.map((k) => {
    const items = (advice.plan?.[k] ?? []).map(x => `<li>${esc(x)}</li>`).join("");
    return `
      <h3>${k.toUpperCase()}</h3>
      <ul>${items || "<li>(none)</li>"}</ul>
    `;
  }).join("");

  const questions = (advice.check_in_questions ?? []).map(q => `<li>${esc(q)}</li>`).join("");

  return `
    <div class="pill"><strong>Today focus:</strong> ${esc(advice.today_focus)}</div>
    ${planHtml}
    <div class="pill"><strong>One small win:</strong> ${esc(advice.one_small_win)}</div>
    <h3>Check-in questions</h3>
    <ul>${questions || "<li>(none)</li>"}</ul>
  `;
}

async function loadPlan() {
  try {
    const r = await fetch("/api/plan");
    const data = await r.json();
    planTextEl.textContent = data.health_plan ?? "";
  } catch {
    planTextEl.textContent = "(Could not load plan.)";
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  statusEl.textContent = "Thinking…";
  resultCard.hidden = true;

  const fd = new FormData(form);
  const payload = {
    sleep_hours: fd.get("sleep_hours") ? Number(fd.get("sleep_hours")) : null,
    protein_g: fd.get("protein_g") ? Number(fd.get("protein_g")) : null,
    steps: fd.get("steps") ? Number(fd.get("steps")) : null,
    training: fd.get("training") || "",
    energy_1_10: fd.get("energy_1_10") ? Number(fd.get("energy_1_10")) : null,
    mood_1_10: fd.get("mood_1_10") ? Number(fd.get("mood_1_10")) : null,
    notes: fd.get("notes") || "",
  };

  try {
    const r = await fetch("/api/checkin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(data.detail || `Request failed (${r.status})`);
    if (!data.advice) throw new Error("No advice returned.");

    resultEl.innerHTML = renderAdvice(data.advice);
    resultCard.hidden = false;
    statusEl.textContent = "Done.";
  } catch (err) {
    statusEl.textContent = `Error: ${err.message}`;
  }
});


loadPlan();
