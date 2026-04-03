const API = "/api";
const MAX_PICK = 5;

const el = (id) => document.getElementById(id);

const state = {
    universities: [],
    programs: [],      // programs текущего университета + фильтр
    picked: [],        // items для расчёта
};

function readScores() {
    const get = (id, max) => {
        const v = Number(el(id).value || 0);
        if (!Number.isFinite(v) || v < 0 || v > max) return null;
        return Math.floor(v);
    };

    const scores = {
        math: get("s-math", 100),
        rus: get("s-rus", 100),
        phys: get("s-phys", 100),
        inf: get("s-inf", 100),
        eng: get("s-eng", 100),
        ach: get("s-ach", 10),
    };

    if (Object.values(scores).some(v => v === null)) return null;
    return scores;
}

function totalScore(scores) {
    return Object.values(scores).reduce((a, b) => a + b, 0);
}

function setStatus(text, ok = true) {
    const p = el("pill-status");
    p.textContent = text;
    p.style.borderColor = ok ? "" : "rgba(255,77,77,.5)";
    p.style.color = ok ? "" : "var(--bad)";
}

function saveToLocal(scores) {
    localStorage.setItem("scores", JSON.stringify(scores));
    setStatus("Сохранено в браузере ✅");
}

function loadFromLocal() {
    try {
        const raw = localStorage.getItem("scores");
        if (!raw) return;
        const s = JSON.parse(raw);

        el("s-math").value = s.math ?? "";
        el("s-rus").value = s.rus ?? "";
        el("s-phys").value = s.phys ?? "";
        el("s-inf").value = s.inf ?? "";
        el("s-eng").value = s.eng ?? "";
        el("s-ach").value = s.ach ?? "";

        setStatus("Загружено из браузера ✅");
    } catch {
    }
}

function resetAll() {
    ["s-math", "s-rus", "s-phys", "s-inf", "s-eng", "s-ach"].forEach(id => el(id).value = "");
    localStorage.removeItem("scores");
    state.picked = [];
    renderPicked();
    renderResults([]);
    setStatus("Данные не сохранены");
}

async function apiGet(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return res.json();
}

async function apiPost(url, body) {
    const res = await fetch(url, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(body),
    });
    if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || `${res.status} ${res.statusText}`);
    }
    return res.json();
}

function fillSelect(selectEl, items, getValue, getLabel, placeholder = "Выберите…") {
    selectEl.innerHTML = "";
    const opt0 = document.createElement("option");
    opt0.value = "";
    opt0.textContent = placeholder;
    selectEl.appendChild(opt0);

    for (const it of items) {
        const o = document.createElement("option");
        o.value = getValue(it);
        o.textContent = getLabel(it);
        selectEl.appendChild(o);
    }
}

function renderPicked() {
    el("picked-count").textContent = state.picked.length.toString();
    const box = el("picked");
    box.innerHTML = "";

    for (const it of state.picked) {
        const chip = document.createElement("div");
        chip.className = "chip";
        chip.innerHTML = `<b>${it.university}</b> — ${it.program} <span class="muted">(мин: ${it.min_score})</span>`;

        const btn = document.createElement("button");
        btn.title = "Удалить";
        btn.textContent = "✕";
        btn.onclick = () => {
            state.picked = state.picked.filter(x => x.id !== it.id);
            renderPicked();
            updateButtons();
        };

        chip.appendChild(btn);
        box.appendChild(chip);
    }
}

function badgeClass(chance) {
    if (chance >= 75) return ["good", "Высокие"];
    if (chance >= 45) return ["mid", "Средние"];
    return ["bad", "Низкие"];
}

function renderResults(results, total = null) {
    el("errors").textContent = "";
    el("results").innerHTML = "";

    if (total !== null) el("total-score").textContent = String(total);

    for (const r of results) {
        const [cls, label] = badgeClass(r.chance);

        const row = document.createElement("div");
        row.className = "result";
        row.innerHTML = `
      <div>
        <div><b>${r.university}</b>${r.code ? ` <span class="muted">(${r.code})</span>` : ""}</div>
        <div>${r.program}</div>
        <div class="muted">Проходной: <b>${r.min_score}</b></div>
      </div>
      <div class="badge ${cls}">${label}: ${r.chance}%</div>
    `;
        el("results").appendChild(row);
    }

    if (results.length === 0) {
        el("results").innerHTML = `<div class="muted">Пока пусто. Выбери программы и нажми “Рассчитать”.</div>`;
    }
}

function updateButtons() {
    const scores = readScores();
    const hasScores = !!scores;
    el("btn-calc").disabled = !(hasScores && state.picked.length > 0);
    el("btn-best").disabled = !hasScores;
}

async function loadUniversities() {
    const universities = await apiGet(`${API}/universities`);
    state.universities = universities;

    fillSelect(el("sel-university"), universities, x => x, x => x, "Выберите университет");
}

async function loadProgramsForSelectedUniversity() {
    const uni = el("sel-university").value;
    const q = el("inp-search").value.trim();

    if (!uni) {
        state.programs = [];
        fillSelect(el("sel-program"), [], () => "", () => "", "Сначала выберите университет");
        return;
    }

    const url = new URL(`${location.origin}${API}/programs`);
    url.searchParams.set("university", uni);
    if (q) url.searchParams.set("q", q);

    const programs = await apiGet(url.toString());
    state.programs = programs;

    fillSelect(
        el("sel-program"),
        programs,
        p => p.id,
        p => `${p.program} (мин: ${p.min_score})`,
        "Выберите программу"
    );
}

function addPickedFromSelected() {
    const programId = el("sel-program").value;
    if (!programId) return;

    if (state.picked.length >= MAX_PICK) {
        el("errors").textContent = `Можно выбрать максимум ${MAX_PICK} программ.`;
        return;
    }

    const prog = state.programs.find(p => p.id === programId);
    if (!prog) return;

    if (state.picked.some(p => p.id === prog.id)) {
        el("errors").textContent = "Эта программа уже добавлена.";
        return;
    }

    state.picked.push(prog);
    renderPicked();
    updateButtons();
}

async function calculatePicked() {
    const scores = readScores();
    if (!scores) {
        el("errors").textContent = "Проверь баллы: ЕГЭ 0–100, достижения 0–10.";
        return;
    }

    const payload = {
        scores,
        items: state.picked.map(p => ({
            id: p.id,
            university: p.university,
            code: p.code,
            program: p.program,
            min_score: p.min_score,
        })),
    };

    try {
        const res = await apiPost(`${API}/calculate/batch`, payload);
        renderResults(res.results, res.total_score);
    } catch (e) {
        el("errors").textContent = e.message;
        renderResults([]);
    }
}

async function bestTop10() {
    const scores = readScores();
    if (!scores) {
        el("errors").textContent = "Проверь баллы: ЕГЭ 0–100, достижения 0–10.";
        return;
    }

    try {
        // берём все программы и считаем батчем
        const all = await apiGet(`${API}/programs`);
        const items = all.slice(0, 5000); // safety: если база станет огромной

        const res = await apiPost(`${API}/calculate/batch`, {
            scores,
            items: items.map(p => ({
                id: p.id, university: p.university, code: p.code, program: p.program, min_score: p.min_score
            }))
        });

        renderResults(res.results.slice(0, 10), res.total_score);
    } catch (e) {
        el("errors").textContent = e.message;
        renderResults([]);
    }
}

function wireEvents() {
    el("btn-save").addEventListener("click", () => {
        const scores = readScores();
        if (!scores) {
            setStatus("Проверь значения (ЕГЭ 0–100, достижения 0–10) ❌", false);
            return;
        }
        saveToLocal(scores);
        updateButtons();
    });

    el("btn-reset").addEventListener("click", () => resetAll());

    ["s-math", "s-rus", "s-phys", "s-inf", "s-eng", "s-ach"].forEach(id => {
        el(id).addEventListener("input", () => updateButtons());
    });

    el("sel-university").addEventListener("change", async () => {
        await loadProgramsForSelectedUniversity();
    });

    el("inp-search").addEventListener("input", async () => {
        // лёгкий debounce
        clearTimeout(window.__t);
        window.__t = setTimeout(loadProgramsForSelectedUniversity, 180);
    });

    el("btn-add").addEventListener("click", () => addPickedFromSelected());

    el("btn-calc").addEventListener("click", () => calculatePicked());

    el("btn-best").addEventListener("click", () => bestTop10());
}

(async function init() {
    loadFromLocal();
    wireEvents();
    renderPicked();
    renderResults([]);
    updateButtons();

    try {
        await loadUniversities();
        await loadProgramsForSelectedUniversity();
    } catch (e) {
        el("errors").textContent = `Не удалось загрузить данные API: ${e.message}`;
    }
})();