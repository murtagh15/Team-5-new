from flask import Blueprint, request, jsonify, render_template
from ege_calculator.data.csv_repository import CSVRepository
from ege_calculator.services.admission_service import admission_probability

api = Blueprint("api", __name__)

repo = CSVRepository()


@api.get("/ui")
def ui():
    return render_template("calculator.html")


@api.get("/universities")
def universities():
    df = repo.get_dataframe()

    return jsonify(
        sorted(df["university"].unique())
    )


@api.get("/programs")
def programs():
    university = request.args.get("university")

    df = repo.get_dataframe()

    programs = df[df["university"] == university][
        ["program", "score"]
    ].to_dict(orient="records")

    return jsonify(programs)


@api.post("/calculate")
def calculate():
    data = request.json

    total_score = (
            data["Math"]
            + data["Rus"]
            + data["Phys"]
            + data["Inf"]
            + data["Eng"]
            + data["Ach"]
    )

    passing_score = data["minScore"]

    chance = admission_probability(total_score, passing_score)

    return jsonify({
        "chance": chance,
        "totalScore": total_score,
        "minScore": passing_score
    })
