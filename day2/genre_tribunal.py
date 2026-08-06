"""Classify movie genres, then have a second model judge each call.

Two models, two jobs:
    MODEL_CLASSIFIER   picks the genre and gives a one-sentence reason
    MODEL_JUDGE         sees the overview and the predicted genre (not the
                        reason) and says whether it would have agreed

A movie is flagged needs_human_review when the judge disagrees or its
certainty drops below 70. suggested_genre is recorded for review but never
applied automatically.

Run it from the repo root:
    python3 day2/genre_tribunal.py
"""
import json
import logging
import os
import statistics
from enum import Enum
from typing import Optional

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ValidationError

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

MODEL_CLASSIFIER = "gemini-2.5-flash-lite"
MODEL_JUDGE = "gpt-5-mini"
RESULTS_PATH = "results/genre_verdicts.json"

client = OpenAI(
    base_url="https://aiapi-prod.stanford.edu/v1",
    api_key=os.getenv("STANFORD_API_KEY"),
)


class Genre(str, Enum):
    ACTION = "Action"
    ADVENTURE = "Adventure"
    ANIMATION = "Animation"
    COMEDY = "Comedy"
    CRIME = "Crime"
    DOCUMENTARY = "Documentary"
    DRAMA = "Drama"
    FAMILY = "Family"
    FANTASY = "Fantasy"
    HORROR = "Horror"
    MYSTERY = "Mystery"
    ROMANCE = "Romance"
    SCIENCE_FICTION = "Science Fiction"
    THRILLER = "Thriller"
    WAR = "War"
    WESTERN = "Western"
    OTHER = "Other"


class GenreClassification(BaseModel):
    genre: Genre
    reason: str


class JudgeVerdict(BaseModel):
    agrees: bool
    certainty: int
    reason: str
    suggested_genre: Optional[Genre] = None


classifier_system_prompt = f"""
You classify movie genres from their overview text.

Pick the single best-fitting genre from exactly this list: {", ".join(g.value for g in Genre)}.
Use "Other" only if none of the rest fit.

Also give a one-sentence reason for your choice, no more than 25 words.

Return valid JSON matching the schema exactly: {{"genre": "...", "reason": "..."}}
"""

judge_system_prompt = f"""
You are a judge reviewing a movie genre classification made by another model.

You will be given a movie overview and a predicted genre. Decide whether you
would have picked the same genre.

If you disagree, suggest an alternative from exactly this list: {", ".join(g.value for g in Genre)}.
Leave suggested_genre null when you agree.

Return valid JSON matching the schema exactly:
{{"agrees": true/false, "certainty": 0-100, "reason": "...", "suggested_genre": "..." or null}}
"""


def classify_overview(overview: str) -> GenreClassification:
    response = client.chat.completions.create(
        model=MODEL_CLASSIFIER,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": classifier_system_prompt},
            {"role": "user", "content": overview},
        ],
    )
    raw = response.choices[0].message.content
    return GenreClassification.model_validate_json(raw)


def judge_classification(overview: str, genre: Genre) -> JudgeVerdict:
    response = client.chat.completions.create(
        model=MODEL_JUDGE,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": judge_system_prompt},
            {"role": "user", "content": f"Overview: {overview}\n\nPredicted genre: {genre.value}"},
        ],
    )
    raw = response.choices[0].message.content
    return JudgeVerdict.model_validate_json(raw)


df = pd.read_csv("data/top_rated_movies.csv").head(10)

results = []
for row in df.itertuples():
    try:
        classification = classify_overview(row.overview)
        verdict = judge_classification(row.overview, classification.genre)
    except ValidationError as e:
        logger.error("%s: validation failed — %s", row.title, e)
        continue

    needs_human_review = (not verdict.agrees) or (verdict.certainty < 70)

    results.append(
        {
            "id": row.id,
            "title": row.title,
            "predicted_genre": classification.genre.value,
            "classifier_reason": classification.reason,
            "agrees": verdict.agrees,
            "certainty": verdict.certainty,
            "judge_reason": verdict.reason,
            "suggested_genre": verdict.suggested_genre.value if verdict.suggested_genre else None,
            "needs_human_review": needs_human_review,
            "classifier_model": MODEL_CLASSIFIER,
            "judge_model": MODEL_JUDGE,
        }
    )

    log = logger.warning if needs_human_review else logger.info
    log(
        "%s -> %s (judge %s, certainty %d)",
        row.title,
        classification.genre.value,
        "agrees" if verdict.agrees else f"disagrees, suggests {verdict.suggested_genre.value}",
        verdict.certainty,
    )

os.makedirs("results", exist_ok=True)
with open(RESULTS_PATH, "w") as f:
    json.dump(results, f, indent=2)
logger.info("Wrote %s", RESULTS_PATH)

n = len(results)
agree_count = sum(r["agrees"] for r in results)
certainties = sorted(r["certainty"] for r in results)
flagged_count = sum(r["needs_human_review"] for r in results)

print(f"agreement rate ........  {agree_count}/{n}  ({agree_count / n:.0%})")
print(f"certainty  min/med/max   {certainties[0]} / {int(statistics.median(certainties))} / {certainties[-1]}")
print(f"flagged for review ....  {flagged_count}/{n}")
