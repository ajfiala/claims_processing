"""
Example FastAPI application demonstrating how to build a minimal backend
for a claims-UX First Notice of Loss (FNOL) flow using pydantic-ai for structured outputs.

We mock a single "Auto" policy from "Coconut Insurance Bangkok," with:
  - 1 named driver: "TEST TEST TEST" (driver-1)
  - 1 insured vehicle: "2023 BMW X1" (2023-bmw-x1)

We have a single endpoint, /claim, which accepts a loss description.
Then we return a JSON payload containing:
  - The questions (with dependsOn, id, type, etc.)
  - A best-guess set of answers (in the "answers" field) 
    based on the description you provided.

You can run this via:
    uv run uvicorn app:app --reload --port 8080
"""
from dotenv import load_dotenv
from fastapi import FastAPI, Body
from models import (
    LossDescription,
    EventType,
    ClassificationResponse,
    QuestionAnswer,
    AutoAnswers,
)
import logging
import time
from starlette.middleware import Middleware
import asyncio
from openai import OpenAI
import instructor 
from typing import Any 
import os
from starlette.middleware.cors import CORSMiddleware

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = instructor.from_openai(openai_client)
model = "gpt-4-turbo"


# async semaphore for parallel requests
QUESTION_SEMAPHORE = asyncio.Semaphore(30) 

# The main application
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
]

app = FastAPI(
    title="Coconut Insurance Bangkok",
    description="Minimal backend using instructor for question-based extraction.",
    version="0.0.1",
    middleware=middleware,
)

# We'll define a helper function that uses instructor to answer a single question
async def fetch_answer_for_question(
    description: str,
    event_type: EventType,
    question_id: str,
    question_label: str,
    question_type: str,
    question_description: str | None,
    possible_values: list[str] | None
) -> str:
    """
    We prompt the llm with a minimal question about the user text.
    We want a single string or 'null'.
    For yes/no, we want 'true'/'false' or 'null'.
    We'll ask the model to produce a JSON conforming to QuestionAnswer schema.
    """
    prompt_text = f"""
User text: {description}
Event Type: {event_type.value}
Policy holder: Billy Baddriver

You are an assistant for a First Notice of Loss (FNOL) flow for an insurance firm.

We have a question:
ID: {question_id}, Label: {question_label}, Type: {question_type}
Possible Values: {possible_values or []}
Question Description: {question_description or ''}

<example>
User text: I was in a car accident and my car was towed.
Policy holder: Billy Baddriver
Event Type: collision
Question: Injuries?, Answer: null                 

User text: I was rear ended and I hurt my head
Policy holder: Billy Baddriver
Event Type: collision
Question: Injuries?, Answer: true

User text: I was driving and a raccoon ate the passenger seat belt
Policy holder: Billy Baddriver
Event Type: damage-caused-by-animals
Question: Other Driver First Name, Answer: null
</example>

Answer that question accurately with a single string or 'null'. Base your answer on the policy holder's text and nothing else.
If the answer to the question cannot be deduced from the user text, respond 'null'.
If yes/no, respond 'true' or 'false' or 'null'.
"""

    # We'll do a minimal structured completion with instructor
    async with QUESTION_SEMAPHORE:
        res = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=100,
            response_model=QuestionAnswer,
        )
        logger.info(f"Question: {question_label}, Answer: {res.answer}")
        
        return res.answer

# fill out AutoAnswers from the question results
def fill_auto_answers(
    event_type_str: str,
    answers_map: dict[str, str | None],
) -> AutoAnswers:
    """
    Convert from the dictionary of question_id -> answer string
    into the final AutoAnswers object.
    We'll parse booleans, etc. 
    """
    # build a dict we can pass to AutoAnswers
    fields: dict[str, Any] = {}
    # eventType is special
    fields["eventType"] = event_type_str or None

    # do a small map from question_id -> field_name in AutoAnswers
    # e.g. "wasVehicleTowed" -> "wasVehicleTowed"
    for qid, val in answers_map.items():
        if qid in AutoAnswers.model_fields:
            # We parse booleans if the question is yes/no or yes/no-or-unknown
            # but we haven't stored question_type here, so let's do a naive parse
            # if it's 'true' or 'false' we store a bool, else store the string or None
            if qid in ["wasVehicleTowed","wasVehicleGlassDamaged","wereFatalities","wereInjuries","isVehicleDrivable"]:
                if val == "true":
                    fields[qid] = True
                elif val == "false":
                    fields[qid] = False
                else:
                    fields[qid] = None
            elif qid in ["injuredParty"]:
                # If it's a list, or "none", or something
                # We'll do a naive parse: if val is "none" -> empty list
                # if it's a comma separated list -> split
                if val and val.lower() != "none":
                    splitted = [v.strip() for v in val.split(",")]
                    fields[qid] = splitted
                else:
                    fields[qid] = []
            else:
                # numeric?
                if qid == "numOtherVehicles":
                    if val and val.isdigit():
                        fields[qid] = val  # store the string integer
                    else:
                        fields[qid] = None
                else:
                    # store as string
                    fields[qid] = val
        else:
            # unknown question id
            pass

    return AutoAnswers(**fields)



def format_answers_for_ui(answers: AutoAnswers) -> dict[str, Any]:
    """
    Convert each field in `answers` into the shape the React UI expects,
    precisely matching the DUMMY_RES format.

    - For checkbox questions, we return an array of objects: [ {"value": x}, ... ].
    - For every other question type, we return a single object: { "value": answer }.
    """
    from models import QUESTIONS, ELEMENT

    qtype_map = {q.id: q.type for q in QUESTIONS}
    raw = answers.model_dump()
    formatted = {}
    for field_name, field_value in raw.items():
        question_type = qtype_map.get(field_name)

        if question_type == ELEMENT.CHECKBOX:
            if field_value is None:
                formatted[field_name] = []  # Empty array for null checkbox values
            else:
                formatted[field_name] = [{"value": v} for v in field_value] # Array of objects for checkboxes
        else:
            formatted[field_name] = {"value": field_value} # Wrap other types in {"value": ...}
    return formatted

@app.post("/form")
async def create_form(loss: LossDescription = Body(...)):
    """
    1) Classify the event type
    2) For each relevant question, fetch an answer in parallel with instructor
    3) Build final AutoAnswers
    4) Format for the UI
    """
    start_time = time.time()

    # 1) classify
    classify_prompt = f"""
Classify the following text into one of these eventTypes: 
{[e.value for e in EventType]}
Text: {loss.description}
Only respond with a single valid value from the list, or 'other-vehicle-damage' if unknown.
"""
    classification = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": classify_prompt}],
        response_model=ClassificationResponse,
        max_tokens=100,
        temperature=0,
    )

    event_type_str = classification.event_type.strip()
    if event_type_str not in [e.value for e in EventType]:
        event_type_str = EventType.OTHER_VEHICLE_DAMAGE.value

    # 2) for each question, build tasks
    from models import QUESTIONS
    tasks = []
    for q in QUESTIONS:
        tasks.append(
            fetch_answer_for_question(
                description=loss.description,
                event_type=EventType(event_type_str),
                question_id=q.id,
                question_label=q.label or "",
                question_type=q.type.value,
                question_description=q.description,
                possible_values=[lov.value for lov in q.lovs] if q.lovs else []
            )
        )
    results = await asyncio.gather(*tasks)
    qid_to_ans = {q.id: results[i] for i, q in enumerate(QUESTIONS)}

    # 3) build final AutoAnswers
    auto_answers = fill_auto_answers(event_type_str, qid_to_ans)

    # 4) shape for UI
    shaped_answers = format_answers_for_ui(auto_answers)

    end_time = time.time()
    logger.info(f"Request processed in {end_time - start_time:.2f} seconds")

    return {
        "questions": QUESTIONS,
        "answers": shaped_answers,
    }
