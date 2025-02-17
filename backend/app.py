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
from models import * 
from pydantic_ai import Agent, RunContext
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

load_dotenv()

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
    description="Minimal backend for an automated FNOL processing flow using pydantic-ai.",
    version="0.0.1",
    middleware=middleware
)

#######################
# pydantic-ai Agent
#######################
agent: Agent[AutoAnswers] = Agent(
    model="openai:gpt-4",
    result_type=AutoAnswers
)

@agent.system_prompt
async def system_prompt(ctx: RunContext[None]) -> str:
    """
    A short system prompt telling the AI how to fill out the data structure.
    This is where you can instruct the model on your rules and constraints.
    """
    # We'll embed the question set in the prompt, so the model sees them.
    # For a real system, we use more robust instructions or use function calling.
    q_text = ", ".join([q.id for q in QUESTIONS])
    return (
        f"You are to return valid JSON for these question IDs: {q_text}. "
        "Fill in the best guess answers from the description. If unknown, set to null/None. "
        "Yes/no fields must be booleans: true or false. "
        "We have only one vehicle: '2023-bmw-x1'. "
        "We have only one driver: 'driver-1'."
    )

#############################
# The Single Endpoint
#############################

@app.post("/form")
async def create_form(loss: LossDescription):
    result = await agent.run(loss.description)
    return {
        'questions': QUESTIONS,
        'answers': result.data,
    }