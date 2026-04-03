from flask import Blueprint, request, jsonify

from ege_calculator.data.csv_repository import CSVRepository
from ege_calculator.services.scoring_service import calculate_total_score
from ege_calculator.services.admission_service import admission_probability, validate_subject_scores


api = Blueprint("api", __name__)
repo = CSVRepository()


def _norm(s: str) -> str:
    return (s or "").strip()


@api.get("/universities")
def universities():
    df = repo.get_dataframe()
    return jsonify(sorted(df["university"].dropna().unique().tolist()))


@api.get("/programs")
def programs():
    df = repo.get_dataframe()

    university = _norm(request.args.get("university"))
    q = _norm(request.args.get("q")).lower()

    if university:
        df = df[df["university"] == university]

    if q:
        df = df[df["program"].astype(str).str.lower().str.contains(q)]

    # нормализуем колонки (под твой CSV)
    # ожидаем: university, program, score (или min_score)
    if "min_score" in df.columns:
        min_col = "min_score"
    else:
        min_col = "score"  # как у нас было в парсере

    if "code" not in df.columns:
        df = df.assign(code="")

    out = []
    for _, r in df.iterrows():
        uni = str(r["university"])
        code = str(r.get("code", "") or "")
        prog = str(r["program"])
        min_score = r[min_col]
        try:
            min_score = int(min_score)
        except Exception:
            continue

        pid = f"{uni}::{code}::{prog}"
        out.append({
            "id": pid,
            "university": uni,
            "code": code,
            "program": prog,
            "min_score": min_score,
        })

    return jsonify(out)


@api.post("/calculate/batch")
def calculate_batch():
    data = request.get_json(force=True)

    scores = data.get("scores", {})
    items = data.get("items", [])

    if not validate_subject_scores(scores):
        return jsonify({
            "error": "Минимум 3 предмета (кроме достижений) должны иметь балл ≥ 40"
        }), 400

    ts = calculate_total_score(
        math=int(scores.get("math", 0)),
        rus=int(scores.get("rus", 0)),
        phys=int(scores.get("phys", 0)),
        inf=int(scores.get("inf", 0)),
        eng=int(scores.get("eng", 0)),
        ach=int(scores.get("ach", 0)),
    )

    results = []
    for it in items:
        min_score = int(it["min_score"])
        chance = admission_probability(ts, min_score)

        results.append({
            "id": it.get("id"),
            "university": it.get("university"),
            "code": it.get("code", ""),
            "program": it.get("program"),
            "min_score": min_score,
            "chance": chance,
        })

    results.sort(key=lambda x: x["chance"], reverse=True)

    return jsonify({"total_score": ts, "results": results})
