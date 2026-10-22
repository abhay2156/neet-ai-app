/* NEET AI — frontend logic (vanilla JS, no build step). */

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

const state = {
  meta: null,
  subjects: [],
  subject: null,
  topics: [],
  topic: null,
  quiz: null,
};

/* ------------------------------------------------------------------ helpers */

async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) {
    let msg = res.statusText;
    try { msg = (await res.json()).detail || msg; } catch (_) {}
    throw new Error(msg);
  }
  return res.json();
}

function toast(msg, ms = 2200) {
  const el = $("#toast");
  el.textContent = msg;
  el.classList.remove("hidden");
  clearTimeout(el._t);
  el._t = setTimeout(() => el.classList.add("hidden"), ms);
}

function fmtTime(sec) {
  const m = Math.floor(Math.abs(sec) / 60).toString().padStart(2, "0");
  const s = Math.floor(Math.abs(sec) % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

function showView(name) {
  ["viewTopics", "viewQuiz", "viewReview", "viewProgress"].forEach((v) =>
    $("#" + v).classList.toggle("hidden", v !== name)
  );
  window.scrollTo({ top: 0, behavior: "smooth" });
}

/* ------------------------------------------------------------------ boot */

async function init() {
  try {
    state.meta = await api("/api/meta");
  } catch (_) {
    state.meta = { demo_mode: true, model: "?", questions_in_bank: 0 };
  }
  updateModeBadge();
  state.subjects = await api("/api/subjects");
  renderSubjectTabs();
  if (state.subjects.length) {
    state.subject = state.subjects[0].id;
    renderSubjectTabs();
    await loadTopics(state.subject);
  }
  wireStaticHandlers();
  await handleDeepLink();
}

/* Deep link: /?topic=<id>&start=1&count=20&mode=practice|exam */
async function handleDeepLink() {
  const p = new URLSearchParams(location.search);
  const tid = p.get("topic");
  if (!tid) return;
  try {
    const t = await api("/api/topics/" + tid);
    state.subject = t.subject;
    renderSubjectTabs();
    await loadTopics(t.subject);
    await selectTopic(tid);
    if (p.get("start") === "1") {
      const count = parseInt(p.get("count") || "20", 10);
      const mode = p.get("mode") || "practice";
      startPractice(tid, count, mode);
    }
  } catch (_) {}
}

function updateModeBadge() {
  const b = $("#modeBadge");
  if (state.meta.demo_mode) {
    b.textContent = "Demo mode (no API key)";
    b.className = "badge badge-demo";
    b.title = "Questions come from a small built-in sample bank. Add LLM_API_KEY to generate live.";
  } else {
    b.textContent = "Live · " + state.meta.model;
    b.className = "badge badge-live";
    b.title = "Questions are generated live by your configured model.";
  }
  $("#bankBadge").textContent = "bank: " + state.meta.questions_in_bank;
}

/* ------------------------------------------------------------------ topics */

function renderSubjectTabs() {
  const wrap = $("#subjectTabs");
  wrap.innerHTML = "";
  state.subjects.forEach((s) => {
    const btn = document.createElement("button");
    btn.className = "tab" + (s.id === state.subject ? " active" : "");
    btn.textContent = `${s.name} (${s.topic_count})`;
    btn.onclick = () => { state.subject = s.id; renderSubjectTabs(); loadTopics(s.id); };
    wrap.appendChild(btn);
  });
}

async function loadTopics(subject) {
  state.topics = await api("/api/topics?subject=" + encodeURIComponent(subject));
  $("#listTitle").textContent = state.subjects.find((s) => s.id === subject)?.name + " topics";
  $("#topicCount").textContent = state.topics.length + " topics";
  const list = $("#topicList");
  list.innerHTML = "";
  state.topics.forEach((t) => {
    const el = document.createElement("div");
    el.className = "topic-item";
    el.dataset.id = t.id;
    el.innerHTML = `
      <div class="topic-item-top">
        <h3>${escapeHtml(t.title)}</h3>
        <span class="w-badge w-${t.weightage}">${t.weightage}</span>
      </div>
      <div class="unit">${escapeHtml(t.unit)}</div>`;
    el.onclick = () => selectTopic(t.id);
    list.appendChild(el);
  });
  $("#topicDetail").className = "detail-empty";
  $("#topicDetail").innerHTML =
    "<p>Pick a topic to read a short explanation and start a practice set.</p>";
}

async function selectTopic(id) {
  $$(".topic-item").forEach((el) => el.classList.toggle("active", el.dataset.id === id));
  const t = await api("/api/topics/" + id);
  state.topic = t;
  const d = $("#topicDetail");
  d.className = "detail-card";
  d.innerHTML = `
    <h2>${escapeHtml(t.title)}</h2>
    <div class="unit">${escapeHtml(t.unit)} · <span class="w-badge w-${t.weightage}">${t.weightage} weightage</span></div>
    <p class="detail-summary">${escapeHtml(t.summary)}</p>
    <ul class="key-points">${t.key_points.map((k) => `<li>${escapeHtml(k)}</li>`).join("")}</ul>
    <div class="bank-line">${t.in_bank} question(s) already in your bank for this topic.</div>
    <div class="practice-row">
      <select id="countSel" class="count-select">
        <option value="10">10 questions</option>
        <option value="20" selected>20 questions</option>
        <option value="30">30 questions</option>
      </select>
      <select id="modeSel" class="mode-select">
        <option value="practice">Practice mode</option>
        <option value="exam">Exam mode (timed)</option>
      </select>
      <button id="startBtn" class="primary-btn">Start practice</button>
    </div>`;
  $("#startBtn").onclick = () => {
    const count = parseInt($("#countSel").value, 10);
    const mode = $("#modeSel").value;
    startPractice(t.id, count, mode);
  };
}

/* ------------------------------------------------------------------ quiz */

async function startPractice(topicId, count, mode) {
  toast("Preparing your questions…", 4000);
  try {
    const data = await api("/api/practice", {
      method: "POST",
      body: JSON.stringify({ topic_id: topicId, count, difficulty: "NEET standard" }),
    });
    state.quiz = {
      topic: data.topic,
      source: data.source,
      mode,
      questions: data.questions,
      answers: new Array(data.questions.length).fill(null),
      current: 0,
      startedAt: Date.now(),
      timerId: null,
      remaining: mode === "exam" ? data.questions.length * 60 : 0,
      elapsed: 0,
    };
    $("#quizTitle").textContent = data.topic.title;
    $("#quizMeta").textContent =
      `${data.count} questions · ${mode === "exam" ? "Exam mode" : "Practice mode"} · source: ${data.source}`;
    renderQuiz();
    showView("viewQuiz");
    startTimer();
  } catch (e) {
    toast("Could not build the set: " + e.message, 4000);
  }
}

function startTimer() {
  clearInterval(state.quiz.timerId);
  const timerEl = $("#timer");
  timerEl.classList.remove("warn");
  const tick = () => {
    const q = state.quiz;
    if (q.mode === "exam") {
      q.remaining -= 1;
      timerEl.textContent = fmtTime(q.remaining);
      if (q.remaining <= 60) timerEl.classList.add("warn");
      if (q.remaining <= 0) {
        clearInterval(q.timerId);
        toast("Time up — submitting.", 2500);
        submitQuiz();
      }
    } else {
      q.elapsed = Math.floor((Date.now() - q.startedAt) / 1000);
      timerEl.textContent = fmtTime(q.elapsed);
    }
  };
  tick();
  state.quiz.timerId = setInterval(tick, 1000);
}

function renderQuiz() {
  const q = state.quiz;
  const idx = q.current;
  const item = q.questions[idx];
  $("#qCounter").textContent = `Question ${idx + 1} of ${q.questions.length}`;
  $("#qProgressFill").style.width = `${(answeredCount() / q.questions.length) * 100}%`;
  $("#qText").textContent = item.question;
  const optWrap = $("#qOptions");
  optWrap.innerHTML = "";
  const keys = ["A", "B", "C", "D"];
  item.options.forEach((opt, i) => {
    const el = document.createElement("div");
    el.className = "option" + (q.answers[idx] === i ? " selected" : "");
    el.innerHTML = `<span class="key">${keys[i]}</span><span>${escapeHtml(opt)}</span>`;
    el.onclick = () => {
      q.answers[idx] = i;
      renderQuiz();
    };
    optWrap.appendChild(el);
  });
  $("#prevBtn").disabled = idx === 0;
  $("#nextBtn").classList.toggle("hidden", idx === q.questions.length - 1);
  $("#submitBtn").classList.toggle("hidden", idx !== q.questions.length - 1);
  renderPalette();
}

function renderPalette() {
  const q = state.quiz;
  const pal = $("#palette");
  pal.innerHTML = "";
  q.questions.forEach((_, i) => {
    const b = document.createElement("button");
    b.className = "pal-btn" +
      (q.answers[i] !== null ? " answered" : "") +
      (i === q.current ? " current" : "");
    b.textContent = i + 1;
    b.onclick = () => { q.current = i; renderQuiz(); };
    pal.appendChild(b);
  });
}

function answeredCount() {
  return state.quiz.answers.filter((a) => a !== null).length;
}

/* ------------------------------------------------------------------ submit */

async function submitQuiz() {
  const q = state.quiz;
  clearInterval(q.timerId);
  const duration = q.mode === "exam"
    ? q.questions.length * 60 - Math.max(q.remaining, 0)
    : q.elapsed;

  let score = 0;
  const detail = q.questions.map((item, i) => {
    const chosen = q.answers[i];
    const correct = chosen === item.answer;
    if (correct) score++;
    return {
      question: item.question,
      options: item.options,
      chosen,
      answer: item.answer,
      correct,
      explanation: item.explanation,
    };
  });

  renderReview(score, detail, duration);
  showView("viewReview");

  try {
    await api("/api/attempts", {
      method: "POST",
      body: JSON.stringify({
        topic_id: q.topic.id,
        subject: q.topic.subject,
        mode: q.mode,
        score,
        total: q.questions.length,
        duration,
        detail,
      }),
    });
    state.meta.questions_in_bank += 0; // unchanged
  } catch (_) {
    toast("Could not save this attempt.", 3000);
  }
}

function renderReview(score, detail, duration) {
  const total = detail.length;
  const pct = Math.round((score / total) * 100);
  $("#resultTitle").textContent = `Result — ${state.quiz.topic.title}`;
  $("#resultSummary").textContent =
    `${score} of ${total} correct · ${pct}% · time ${fmtTime(duration)} · ${state.quiz.mode === "exam" ? "exam" : "practice"} mode`;

  $("#scoreRow").innerHTML = `
    <div class="stat-card"><div class="num">${score}/${total}</div><div class="lbl">Score</div></div>
    <div class="stat-card"><div class="num">${pct}%</div><div class="lbl">Accuracy</div></div>
    <div class="stat-card"><div class="num">${fmtTime(duration)}</div><div class="lbl">Time taken</div></div>`;

  const keys = ["A", "B", "C", "D"];
  const list = $("#reviewList");
  list.innerHTML = "";
  detail.forEach((d, i) => {
    const cls = d.chosen === null ? "unanswered" : d.correct ? "correct" : "wrong";
    const el = document.createElement("div");
    el.className = "review-item " + cls;
    el.innerHTML = `
      <div class="review-q">${i + 1}. ${escapeHtml(d.question)}</div>
      <div class="review-opts">
        ${d.options.map((o, oi) => {
          let c = "review-opt";
          let tag = "";
          if (oi === d.answer) { c += " correct-opt"; tag = "correct answer"; }
          if (oi === d.chosen && oi !== d.answer) { c += " chosen-wrong"; tag = "your answer"; }
          if (oi === d.chosen && oi === d.answer) tag = "your answer";
          return `<div class="${c}">${keys[oi]}. ${escapeHtml(o)}${tag ? `<span class="tag">${tag}</span>` : ""}</div>`;
        }).join("")}
      </div>
      ${d.explanation ? `<div class="review-exp"><strong>Why:</strong> ${escapeHtml(d.explanation)}</div>` : ""}`;
    list.appendChild(el);
  });
}

/* ------------------------------------------------------------------ progress */

async function loadProgress() {
  try {
    const [stats, attempts] = await Promise.all([api("/api/stats"), api("/api/attempts")]);
    $("#statRow").innerHTML = `
      <div class="stat-card"><div class="num">${stats.attempts}</div><div class="lbl">Attempts</div></div>
      <div class="stat-card"><div class="num">${stats.accuracy}%</div><div class="lbl">Overall accuracy</div></div>
      <div class="stat-card"><div class="num">${stats.questions_in_bank}</div><div class="lbl">Questions in bank</div></div>`;
    const list = $("#attemptList");
    list.innerHTML = attempts.length ? "" : "<p class='muted'>No attempts yet — start practising.</p>";
    attempts.forEach((a) => {
      const pct = a.total ? Math.round((a.score / a.total) * 100) : 0;
      const pill = pct >= 70 ? "pill-good" : pct >= 40 ? "pill-mid" : "pill-bad";
      const when = new Date(a.created_at * 1000).toLocaleString("en-IN");
      const el = document.createElement("div");
      el.className = "attempt-item";
      el.innerHTML = `
        <div>
          <div class="a-main">${escapeHtml(a.topic_id)}</div>
          <div class="a-sub">${a.subject} · ${a.mode} · ${fmtTime(a.duration)} · ${when}</div>
        </div>
        <span class="pill ${pill}">${a.score}/${a.total} (${pct}%)</span>`;
      list.appendChild(el);
    });
  } catch (e) {
    toast("Could not load progress: " + e.message);
  }
}

/* ------------------------------------------------------------------ wiring */

function wireStaticHandlers() {
  $("#navProgress").onclick = () => { loadProgress(); showView("viewProgress"); };
  $("#progressBack").onclick = () => showView("viewTopics");
  $("#prevBtn").onclick = () => { state.quiz.current--; renderQuiz(); };
  $("#nextBtn").onclick = () => { state.quiz.current++; renderQuiz(); };
  $("#submitBtn").onclick = () => {
    const un = state.quiz.questions.length - answeredCount();
    if (un > 0 && !confirm(`${un} question(s) unanswered. Submit anyway?`)) return;
    submitQuiz();
  };
  $("#quitQuiz").onclick = () => {
    if (!confirm("Quit this test? Progress will be lost.")) return;
    clearInterval(state.quiz.timerId);
    showView("viewTopics");
  };
  $("#retryBtn").onclick = () => {
    const q = state.quiz;
    startPractice(q.topic.id, q.questions.length, q.mode);
  };
  $("#backTopicsBtn").onclick = () => { showView("viewTopics"); refreshBankBadge(); };
}

async function refreshBankBadge() {
  try {
    const m = await api("/api/meta");
    state.meta.questions_in_bank = m.questions_in_bank;
    $("#bankBadge").textContent = "bank: " + m.questions_in_bank;
  } catch (_) {}
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

init();
