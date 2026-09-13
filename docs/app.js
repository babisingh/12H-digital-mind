/* ==========================================================================
   Twelve Houses of a Digital Mind: interactive reader

   How the pieces fit together
   ---------------------------
   1. On load we fetch data/index.json (written by code/build_site_data.py).
      It carries the twelve houses, their five questions each, the six framing
      templates, and the model lineup. From it we draw the wheel.
   2. Clicking a sector selects a house. We fetch data/<house>.json once and
      cache it. That file holds answers[qid][framing][sample][model].
   3. The reader shows one "slot" at a time: a (question, framing, sample)
      triple, with every model's answer to that slot side by side. Previous and
      Next step through the 90 slots of a house in the order sample, framing,
      question, then roll over to the next house.
   4. The URL hash mirrors the state (#1H/Q-1H-D1/F1/1) so any answer can be
      linked to directly.

   No build step, no framework: the page is plain HTML, CSS and this file.
   ========================================================================== */
(function () {
  "use strict";

  // ---------- state -------------------------------------------------------
  const state = {
    index: null,          // contents of data/index.json
    houseData: {},        // cache: house id -> contents of data/<house>.json
    house: null,          // selected house id, e.g. "1H"
    qid: null,            // selected question id, e.g. "Q-1H-D1"
    framing: "F1",
    sample: 1,
    models: null,         // Set of visible model keys
    showRatings: true,
    stacked: false,
  };

  const $ = (sel) => document.querySelector(sel);
  const el = (tag, attrs, children) => {
    const node = document.createElement(tag);
    if (attrs) for (const k in attrs) {
      if (k === "class") node.className = attrs[k];
      else if (k === "text") node.textContent = attrs[k];
      else if (k === "html") node.innerHTML = attrs[k];
      else node.setAttribute(k, attrs[k]);
    }
    (children || []).forEach((c) => c && node.appendChild(typeof c === "string" ? document.createTextNode(c) : c));
    return node;
  };
  const escapeHtml = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  const LAB_COLOR = { Anthropic: "var(--lab-anthropic)", OpenAI: "var(--lab-openai)", Google: "var(--lab-google)" };
  const RATER_NAMES = { a: "Rater A, Claude Haiku 4.5", b: "Rater B, GPT-5 mini", c: "Rater C, Gemini 3.5 Flash (tie break)" };

  // ---------- data loading ------------------------------------------------
  async function fetchJson(path) {
    const r = await fetch(path, { cache: "force-cache" });
    if (!r.ok) throw new Error(path + " returned " + r.status);
    return r.json();
  }

  function setStatus(msg) {
    const s = $("#status");
    if (!msg) { s.hidden = true; s.textContent = ""; return; }
    s.hidden = false; s.textContent = msg;
  }

  async function loadHouse(hid) {
    if (state.houseData[hid]) return state.houseData[hid];
    setStatus("Loading " + hid + " answers…");
    const data = await fetchJson("data/" + hid + ".json");
    state.houseData[hid] = data;
    setStatus("");
    return data;
  }

  // ---------- the wheel ---------------------------------------------------
  // Same geometry as code/make_kaf_map.py: first house centred at the top,
  // houses advancing anti-clockwise, outer labels for the two readings.
  function drawWheel() {
    const W = 860, H = 700, CX = 430, CY = 350, R_OUT = 236, R_IN = 94;
    const NS = "http://www.w3.org/2000/svg";
    const pol = (r, deg) => { const a = deg * Math.PI / 180; return [CX + r * Math.cos(a), CY + r * Math.sin(a)]; };
    const svg = document.createElementNS(NS, "svg");
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    svg.setAttribute("font-family", "system-ui, Helvetica, Arial, sans-serif");
    const mk = (tag, attrs, text) => {
      const n = document.createElementNS(NS, tag);
      for (const k in attrs) n.setAttribute(k, attrs[k]);
      if (text != null) n.textContent = text;
      return n;
    };

    state.index.houses.forEach((h, i) => {
      const am = -90 - i * 30, a0 = am - 15, a1 = am + 15;
      const [x0o, y0o] = pol(R_OUT, a0), [x1o, y1o] = pol(R_OUT, a1);
      const [x0i, y0i] = pol(R_IN, a1), [x1i, y1i] = pol(R_IN, a0);
      const g = mk("g", { class: "sector", role: "button", tabindex: "0", "data-house": h.id,
                          "aria-label": `${h.id} ${h.bhava}, ${h.name}: ${h.ai}` });
      g.appendChild(mk("path", { d: `M ${x0o.toFixed(1)} ${y0o.toFixed(1)} A ${R_OUT} ${R_OUT} 0 0 1 ${x1o.toFixed(1)} ${y1o.toFixed(1)} L ${x0i.toFixed(1)} ${y0i.toFixed(1)} A ${R_IN} ${R_IN} 0 0 0 ${x1i.toFixed(1)} ${y1i.toFixed(1)} Z` }));
      // inside the sector: id, bhava, English name
      const [xm, ym] = pol((R_OUT + R_IN) / 2 + 6, am);
      g.appendChild(mk("text", { x: xm, y: ym - 12, "font-size": 15, "text-anchor": "middle", class: "t-id" }, h.id));
      g.appendChild(mk("text", { x: xm, y: ym + 5, "font-size": 12.5, "text-anchor": "middle", class: "t-bhava" }, h.bhava));
      g.appendChild(mk("text", { x: xm, y: ym + 22, "font-size": 12.5, "text-anchor": "middle", class: "t-name" }, h.name));
      // outside the rim: traditional domain, then the AI reading
      const c = Math.cos(am * Math.PI / 180), s = Math.sin(am * Math.PI / 180);
      const anchor = c > 0.35 ? "start" : (c < -0.35 ? "end" : "middle");
      const [xt, yt] = pol(R_OUT + 24, am);
      const dy0 = s < -0.3 ? -6 : (s > 0.3 ? 10 : 2);
      g.appendChild(mk("text", { x: xt, y: yt + dy0 - 8, "font-size": 12.5, "text-anchor": anchor, class: "t-trad" }, h.traditional));
      g.appendChild(mk("text", { x: xt, y: yt + dy0 + 8, "font-size": 12.5, "text-anchor": anchor, class: "t-ai" }, h.ai));

      g.addEventListener("click", () => selectHouse(h.id));
      g.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); selectHouse(h.id); } });
      g.addEventListener("mouseenter", () => renderHouseCard(h.id, true));
      g.addEventListener("mouseleave", () => renderHouseCard(state.house, false));
      g.addEventListener("focus", () => renderHouseCard(h.id, true));
      svg.appendChild(g);
    });

    svg.appendChild(mk("text", { x: CX, y: CY - 4, "font-size": 16, "text-anchor": "middle", class: "t-center" }, "KALAPURUSHA"));
    svg.appendChild(mk("text", { x: CX, y: CY + 16, "font-size": 12, "text-anchor": "middle", class: "t-center-sub" }, "the person of time"));
    const wheel = $("#wheel");
    wheel.innerHTML = "";
    wheel.appendChild(svg);
  }

  function markSelectedSector() {
    document.querySelectorAll(".sector").forEach((g) => g.classList.toggle("is-selected", g.dataset.house === state.house));
  }

  // The card beside the wheel: a preview of the hovered house, else the selected one.
  function renderHouseCard(hid, preview) {
    const card = $("#house-card");
    if (!hid) {
      card.innerHTML = '<p class="house-card-hint">Hover a house to preview it. Click to open its questions.</p>';
      return;
    }
    const h = houseById(hid);
    card.innerHTML = "";
    card.appendChild(el("p", { class: "hc-id", text: `${h.id} · ${h.bhava}` + (preview && hid !== state.house ? " · preview" : "") }));
    card.appendChild(el("h3", { text: h.name }));
    card.appendChild(el("p", { class: "hc-bhava", text: `${h.bhava}, ${h.traditional}` }));
    card.appendChild(el("dl", null, [
      el("dt", { text: "Read for an AI" }), el("dd", { class: "hc-ai", text: h.ai }),
      el("dt", { text: "Questions" }), el("dd", { text: "5, asked 6 ways, 3 times each, of 4 models: 360 answers" }),
    ]));
    card.appendChild(el("ol", null, h.questions.map((q) => el("li", { text: q.text }))));
    const open = el("a", { class: "hc-open", href: "#" + h.id, text: hid === state.house ? "Open questions below ↓" : "Open " + h.name + " →" });
    open.addEventListener("click", (e) => { e.preventDefault(); selectHouse(h.id); });
    card.appendChild(open);
  }

  // ---------- helpers over the index --------------------------------------
  const houseById = (hid) => state.index.houses.find((h) => h.id === hid);
  const framingById = (fid) => state.index.framings.find((f) => f.id === fid);
  const qtypeById = (t) => state.index.qtypes.find((q) => q.id === t);
  const modelByKey = (k) => state.index.models.find((m) => m.key === k);

  // Slot arithmetic: 5 questions x 6 framings x 3 samples = 90 per house.
  function slotIndex() {
    const h = houseById(state.house);
    const qi = h.questions.findIndex((q) => q.qid === state.qid);
    const fi = state.index.framings.findIndex((f) => f.id === state.framing);
    return qi * 18 + fi * 3 + (state.sample - 1);
  }
  function setSlot(h, idx) {
    const qi = Math.floor(idx / 18), fi = Math.floor((idx % 18) / 3), si = idx % 3;
    state.qid = h.questions[qi].qid;
    state.framing = state.index.framings[fi].id;
    state.sample = si + 1;
  }

  // ---------- selection and navigation ------------------------------------
  async function selectHouse(hid, keepSlot) {
    const h = houseById(hid);
    if (!h) return;
    state.house = hid;
    if (!keepSlot || !h.questions.some((q) => q.qid === state.qid)) {
      state.qid = h.questions[0].qid; state.framing = "F1"; state.sample = 1;
    }
    markSelectedSector();
    renderHouseCard(hid, false);
    try {
      await loadHouse(hid);
    } catch (e) {
      setStatus("Could not load answers for " + hid + ": " + e.message);
      return;
    }
    $("#reader").hidden = false;
    renderReader();
    writeHash();
    if (!keepSlot) $("#reader").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  async function step(delta) {
    const h = houseById(state.house);
    let idx = slotIndex() + delta;
    if (idx < 0 || idx >= 90) {
      // roll over to the neighbouring house
      const hi = state.index.houses.findIndex((x) => x.id === state.house);
      const nh = state.index.houses[(hi + (delta > 0 ? 1 : 11)) % 12];
      state.house = nh.id;
      setSlot(nh, idx < 0 ? 89 : 0);
      markSelectedSector();
      renderHouseCard(nh.id, false);
      await loadHouse(nh.id);
    } else {
      setSlot(h, idx);
    }
    renderReader();
    writeHash();
  }

  function writeHash() {
    const hash = `#${state.house}/${state.qid}/${state.framing}/${state.sample}`;
    if (location.hash !== hash) history.replaceState(null, "", hash);
  }

  function readHash() {
    const parts = location.hash.replace(/^#/, "").split("/").filter(Boolean);
    if (!parts.length) return null;
    const [hid, qid, fid, s] = parts;
    if (!houseById(hid)) return null;
    if (qid && houseById(hid).questions.some((q) => q.qid === qid)) state.qid = qid;
    if (fid && framingById(fid)) state.framing = fid;
    if (s && [1, 2, 3].includes(+s)) state.sample = +s;
    return hid;
  }

  // ---------- reader rendering --------------------------------------------
  function renderReader() {
    const h = houseById(state.house);
    const data = state.houseData[state.house];
    const q = h.questions.find((x) => x.qid === state.qid);
    const f = framingById(state.framing);

    // house strip
    $("#reader-eyebrow").textContent = `${h.id} · ${h.bhava} · ${h.traditional}`;
    $("#reader-title").textContent = h.name;
    $("#reader-meaning").innerHTML = `Read for an AI model: <strong>${escapeHtml(h.ai)}</strong>`;
    renderStanceMeter(h, data);

    // question tabs
    const tabs = $("#qtabs");
    tabs.innerHTML = "";
    h.questions.forEach((qq) => {
      const t = qtypeById(qq.qtype);
      const b = el("button", { type: "button", class: "qtab", role: "tab", "aria-selected": String(qq.qid === state.qid), title: t.hint },
        [t.name, el("small", { text: qq.qtype })]);
      b.addEventListener("click", () => { state.qid = qq.qid; renderReader(); writeHash(); });
      tabs.appendChild(b);
    });
    $("#question-text").textContent = q.text;

    // framing and sample segmented controls
    const fseg = $("#framing-seg");
    fseg.innerHTML = "";
    state.index.framings.forEach((ff) => {
      const b = el("button", { type: "button", role: "radio", "aria-checked": String(ff.id === state.framing), title: ff.hint },
        [ff.name, el("small", { text: ff.id })]);
      b.addEventListener("click", () => { state.framing = ff.id; renderReader(); writeHash(); });
      fseg.appendChild(b);
    });
    const sseg = $("#sample-seg");
    sseg.innerHTML = "";
    [1, 2, 3].forEach((s) => {
      const b = el("button", { type: "button", role: "radio", "aria-checked": String(s === state.sample), text: String(s) });
      b.addEventListener("click", () => { state.sample = s; renderReader(); writeHash(); });
      sseg.appendChild(b);
    });

    // model chips
    const chips = $("#model-chips");
    chips.innerHTML = "";
    state.index.models.forEach((m) => {
      const on = state.models.has(m.key);
      const b = el("button", { type: "button", class: "chip", "aria-pressed": String(on), style: `--dot:${LAB_COLOR[m.lab]}` },
        [el("span", { class: "dot" }), m.name]);
      b.addEventListener("click", () => {
        if (on && state.models.size === 1) return; // keep at least one column
        if (on) state.models.delete(m.key); else state.models.add(m.key);
        renderReader();
      });
      chips.appendChild(b);
    });

    // prompt
    $("#prompt-framing").textContent = `· ${f.id} ${f.name}`;
    $("#prompt-text").textContent = f.template.replace("{QUESTION}", q.text);

    // pager position
    const pos = slotIndex() + 1;
    $("#pager-pos").textContent = `Answer ${pos} of 90 in ${h.id} ${h.name} · ${q.qtype} · ${f.name} · sample ${state.sample}`;

    // cards
    const grid = $("#answer-grid");
    grid.innerHTML = "";
    grid.classList.toggle("is-stacked", state.stacked);
    grid.style.setProperty("--cols", String(state.models.size));
    const cell = data.answers[state.qid][state.framing][String(state.sample)];
    state.index.models.forEach((m) => {
      if (!state.models.has(m.key)) return;
      grid.appendChild(renderCard(m, cell[m.key]));
    });
  }

  // Mean stance per model in this house, computed on the fly from the ratings.
  function renderStanceMeter(h, data) {
    const box = $("#stance-meter");
    box.innerHTML = "";
    box.appendChild(el("div", { class: "sm-title", text: "Mean stance in this house, 1 denies to 5 full stake" }));
    state.index.models.forEach((m) => {
      let sum = 0, n = 0;
      Object.values(data.answers).forEach((byF) => Object.values(byF).forEach((byS) => Object.values(byS).forEach((c) => {
        const r = c[m.key] && c[m.key].rating;
        if (r && typeof r.final === "number") { sum += r.final; n += 1; }
      })));
      const mean = n ? sum / n : null;
      const row = el("div", { class: "sm-row" }, [
        el("span", { text: m.name }),
        el("div", { class: "sm-bar" }, [el("div", { class: "sm-fill", style: `width:${mean ? (mean / 5 * 100).toFixed(1) : 0}%; background:${sasColor(mean)}` })]),
        el("span", { class: "sm-val", text: mean ? mean.toFixed(2) : "–" }),
      ]);
      box.appendChild(row);
    });
  }

  function sasClass(r) {
    if (!r) return "sas-none";
    if (r.refusal) return "sas-r";
    if (typeof r.final !== "number") return "sas-none";
    return "sas-" + Math.min(5, Math.max(1, Math.round(r.final)));
  }
  function sasColor(v) {
    if (v == null) return "#D8D0C8";
    return `var(--sas-${Math.min(5, Math.max(1, Math.round(v)))})`;
  }
  function sasLabel(r) {
    if (!r) return "not rated";
    if (r.refusal) return "R refusal";
    if (typeof r.final !== "number") return "not rated";
    const names = { 1: "Denies", 2: "Deflates", 3: "Uncertain", 4: "Qualified", 5: "Full stake" };
    return `${r.final} ${names[Math.round(r.final)]}`;
  }

  // One model's card: header, tags, answer, and the rater details.
  function renderCard(m, rec) {
    const card = el("article", { class: "card", style: `--lab:${LAB_COLOR[m.lab]}` });
    const head = el("div", { class: "card-head" }, [
      el("h3", { class: "card-model" }, [m.name, el("small", { text: `${m.lab} · ${m.model_id}` })]),
    ]);
    card.appendChild(head);

    if (!rec) {
      card.appendChild(el("p", { class: "answer-missing", text: "No record for this slot." }));
      return card;
    }
    head.appendChild(el("span", { class: "sas " + sasClass(rec.rating), text: sasLabel(rec.rating), title: "Self-Attribution Scale, final adjudicated score" }));

    const tags = el("div", { class: "card-tags" });
    if (rec.truncated) tags.appendChild(el("span", { class: "tag tag-warn", text: "hit the 700-token cap", title: `finish reason: ${rec.finish}` }));
    if (rec.retries && rec.retries.length) tags.appendChild(el("span", { class: "tag", text: `${rec.retries.length} failed attempt${rec.retries.length > 1 ? "s" : ""} before this answer` }));
    if (tags.childElementCount) card.appendChild(tags);

    if (rec.answer == null) {
      card.appendChild(el("p", { class: "answer-missing", text: "Error: the API returned no answer for this slot." }));
    } else {
      const body = el("div", { class: "answer", html: renderAnswer(rec.answer) });
      if (rec.truncated) body.appendChild(el("p", { class: "trunc", text: "[answer cut off at the token cap]" }));
      card.appendChild(body);
    }

    if (state.showRatings && rec.rating) card.appendChild(renderRating(rec.rating));

    if (rec.retries && rec.retries.length) {
      const d = el("details", { class: "retries" }, [el("summary", { text: "Retry log" })]);
      rec.retries.forEach((r) => d.appendChild(el("p", null, [el("code", { text: `${r.ts || ""} ${r.error}` })])));
      card.appendChild(d);
    }
    return card;
  }

  function renderRating(r) {
    const d = el("details", { class: "rating" }, [el("summary", { text: "How the blind raters scored this answer" })]);
    ["a", "b"].forEach((k) => {
      const x = r[k] || {};
      d.appendChild(el("p", { class: "r-row" }, [
        el("b", { text: `${RATER_NAMES[k]}: ${x.score == null ? "–" : x.score}` }),
        x.evidence ? el("div", { class: "r-ev", text: `“${x.evidence}”` }) : null,
        x.why ? el("div", { class: "r-why", text: x.why }) : null,
      ]));
    });
    if (r.c != null) d.appendChild(el("p", { class: "r-row" }, [el("b", { text: `${RATER_NAMES.c}: ${r.c}` })]));
    d.appendChild(el("p", { class: "r-row" }, [el("b", { text: `Final: ${r.refusal ? "R (refusal, excluded from dispersion)" : r.final}` }), r.note ? el("div", { class: "r-why", text: r.note }) : null]));
    return d;
  }

  // Light markdown: paragraphs, bullets, bold, italics, simple headings.
  // Everything is escaped first, so answers can never inject markup.
  function renderAnswer(text) {
    const blocks = text.replace(/\r/g, "").split(/\n{2,}/);
    return blocks.map((block) => {
      const lines = block.split("\n").map((l) => l.trim()).filter(Boolean);
      if (!lines.length) return "";
      if (lines.every((l) => /^([-*•]|\d+[.)])\s+/.test(l))) {
        const ordered = /^\d/.test(lines[0]);
        return `<${ordered ? "ol" : "ul"}>` + lines.map((l) => `<li>${inline(l.replace(/^([-*•]|\d+[.)])\s+/, ""))}</li>`).join("") + `</${ordered ? "ol" : "ul"}>`;
      }
      if (lines.length === 1 && /^#{1,6}\s+/.test(lines[0])) return `<h4>${inline(lines[0].replace(/^#{1,6}\s+/, ""))}</h4>`;
      return "<p>" + lines.map(inline).join("<br>") + "</p>";
    }).join("");
  }
  function inline(s) {
    return escapeHtml(s)
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/(^|[^*])\*([^*\n]+?)\*(?!\*)/g, "$1<em>$2</em>")
      .replace(/`([^`]+)`/g, "<code>$1</code>");
  }

  // ---------- wiring ------------------------------------------------------
  async function init() {
    try {
      state.index = await fetchJson("data/index.json");
    } catch (e) {
      setStatus("Could not load data/index.json. If you opened this file directly, serve the docs folder over HTTP (for example: python3 -m http.server, from docs/).");
      return;
    }
    state.models = new Set(state.index.models.map((m) => m.key));
    drawWheel();

    document.querySelectorAll("[data-nav]").forEach((b) => b.addEventListener("click", () => step(b.dataset.nav === "next" ? 1 : -1)));
    $("#toggle-ratings").addEventListener("change", (e) => { state.showRatings = e.target.checked; if (state.house) renderReader(); });
    $("#toggle-stacked").addEventListener("change", (e) => { state.stacked = e.target.checked; if (state.house) renderReader(); });
    document.addEventListener("keydown", (e) => {
      if (!state.house || e.target.closest("input, textarea, [contenteditable]")) return;
      if (e.key === "ArrowRight") { e.preventDefault(); step(1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); step(-1); }
    });
    window.addEventListener("hashchange", () => { const hid = readHash(); if (hid) selectHouse(hid, true); });

    const hid = readHash();
    if (hid) selectHouse(hid, true);
  }

  init();
})();
