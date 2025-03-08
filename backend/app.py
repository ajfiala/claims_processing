from dotenv import load_dotenv
from fastapi import FastAPI, Body, File, UploadFile, Form
import tempfile
import base64
from models import (
    LossDescription,
    EventType,
    ElementType,
    ClassificationResponse,
    QuestionAnswer,
    AutoAnswers,
    ImageAnalysisResponse,
    QUESTIONS,
    get_relevant_questions,
)
import logging
import time
from starlette.middleware import Middleware
import asyncio
from openai import OpenAI
import instructor
from typing import Any, List, Dict, Optional
import os
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.requests import Request

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = instructor.from_openai(openai_client)
model = "gpt-4-turbo"
CLOUDFRONT_DOMAIN = os.getenv("CLOUDFRONT_DOMAIN", "claims.bangkok.solutions")
STATIC_MODE = os.getenv("STATIC", "false").lower() == "true"


CLASSIFY_SEMAPHORE = asyncio.Semaphore(5)
QUESTIONS_BATCH_SEMAPHORE = asyncio.Semaphore(10)

# Get the directory of the frontend build folder
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ui", "dist")

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:8080", "https://claims.bangkok.solutions"],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
]

app = FastAPI(
    title="Lean Innovation Labs Claims Helper",
    description="Minimal backend using instructor for question-based extraction.",
    version="0.0.1",
    middleware=middleware,
)

async def classify_event_type(description: str) -> EventType:
    async with CLASSIFY_SEMAPHORE:
        classify_prompt = f"""
Classify the following text into one of the provided eventTypes based on their definitions and examples:

Event Types and Definitions:

1. towing-only: 
   Incident involves only the towing of a vehicle, without collision or other damage.
   Example: "My car broke down and required towing."

2. collision:
   Incident involving a vehicle colliding with another vehicle or object.
   Example: "My car hit another car at an intersection."

3. injured-as-pedestrian:
   The policyholder or claimant was injured while walking as a pedestrian.
   Example: "I was hit by a vehicle while crossing the street."

4. injured-a-pedestrian:
   A vehicle injured another person who was a pedestrian.
   Example: "My car struck a person crossing the road."

5. damage-caused-by-weather:
   Vehicle damaged due to weather-related incidents like hail, floods, storms, etc.
   Example: "My car was damaged by hail during a storm."

6. damage-caused-by-fire:
   Vehicle damage explicitly caused by fire.
   Example: "My car caught fire due to an electrical fault."

7. damage-caused-by-animals:
   Vehicle damage resulting from collisions or interactions with animals.
   Example: "a monkey destroyed the glove box."

8. vehicle-vandalized:
   Intentional malicious damage inflicted upon the vehicle by vagrants or others.
   Example: "Someone scratched graffiti onto my car."

9. vehicle-broken-into-or-stolen:
   Vehicle was either broken into, resulting in theft or damage, or the vehicle itself was stolen.
   Example: "My car was stolen overnight." or "My car window was broken, and personal items were stolen."

10. other-vehicle-damage:
    Any other form of vehicle damage not fitting into the above categories.
    Example: "My windshield cracked for an unknown reason."

Text to classify:
{description}

Classify the following text into one of these eventTypes, keeping in mind their descriptions above: 
{[e.value for e in EventType]}
Respond ONLY with a single exact event type from the above list. If unclear or not listed, respond with 'other-vehicle-damage'.
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
            
        return EventType(event_type_str)

async def process_questions_batch(
    description: str,
    event_type: EventType,
    questions: List[Any],
    batch_size: int = 3
) -> Dict[str, str]:
    results = {}
    batches = [questions[i:i + batch_size] for i in range(0, len(questions), batch_size)]
    
    async def process_batch(batch):
        batch_tasks = []
        for q in batch:
            batch_tasks.append(
                get_question_answer(
                    description=description,
                    event_type=event_type,
                    question=q
                )
            )
        batch_results = await asyncio.gather(*batch_tasks)
        return {q.id: batch_results[i] for i, q in enumerate(batch)}
    
    batch_tasks = []
    for batch in batches:
        batch_tasks.append(process_batch(batch))
    
    batch_results = await asyncio.gather(*batch_tasks)
    
    for result_dict in batch_results:
        results.update(result_dict)
    
    return results

async def get_question_answer(
    description: str,
    event_type: EventType,
    question: Any
) -> str:
    async with QUESTIONS_BATCH_SEMAPHORE:
        prompt_text = f"""
User text: {description}
Event Type: {event_type.value}
Policy holder: Billy Baddriver

You are an assistant for a First Notice of Loss (FNOL) flow for an insurance firm.

We have a question:
ID: {question.id}, Label: {question.label or ""}, Type: {question.type.value}
Possible Values: {[lov.value for lov in question.lovs] if question.lovs else []}
Question Description: {question.description or ""}

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
If the user's description is about their vehicle, assume it is the primary vehicle in their policy unless they mention another car.
If the answer to the question cannot be deduced from the user text, respond 'null'.
If yes/no, respond 'true' or 'false' or 'null'.
"""
        res = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=100,
            response_model=QuestionAnswer,
        )
        logger.info(f"Question: {question.id}, Answer: {res.answer}")
        return res.answer

def fill_auto_answers(
    event_type_str: str,
    answers_map: Dict[str, Optional[str]],
) -> AutoAnswers:
    fields: Dict[str, Any] = {}
    fields["eventType"] = event_type_str or None

    for qid, val in answers_map.items():
        if qid in AutoAnswers.model_fields:
            if qid in ["wasVehicleTowed", "wasVehicleGlassDamaged", "wereFatalities", "wereInjuries", "isVehicleDrivable"]:
                if val == "true":
                    fields[qid] = True
                elif val == "false":
                    fields[qid] = False
                else:
                    fields[qid] = None
            elif qid in ["injuredParty", "insuredInjured", "whoElseWasInjured"]:
                if val and val.lower() != "none":
                    splitted = [v.strip() for v in val.split(",")]
                    fields[qid] = splitted
                else:
                    fields[qid] = []
            else:
                if qid == "numOtherVehicles":
                    if val and val.isdigit():
                        fields[qid] = val
                    else:
                        fields[qid] = None
                else:
                    fields[qid] = val

    return AutoAnswers(**fields)

def format_answers_for_ui(answers: AutoAnswers) -> Dict[str, Any]:
    qtype_map = {q.id: q.type for q in QUESTIONS}
    raw = answers.model_dump()
    formatted = {}
    
    for field_name, field_value in raw.items():
        question_type = qtype_map.get(field_name)

        if question_type == ElementType.CHECKBOX:
            if field_value is None:
                formatted[field_name] = []
            else:
                formatted[field_name] = [{"value": v} for v in field_value]
        else:
            formatted[field_name] = {"value": field_value}
            
    return formatted

def clean_questions_for_response(questions):
    """Remove dependency metadata fields from question objects for the final response"""
    clean_questions = []
    
    for q in questions:
        # Convert to dict for easier manipulation
        q_dict = q.model_dump()
        
        # Remove the metadata fields
        metadata_fields = ["dependency_type", "depends_on_event_types", "depends_on_who_driving", "depends_on_injuries"]
        for field in metadata_fields:
            if field in q_dict:
                del q_dict[field]
                
        # Add to cleaned list
        clean_questions.append(q_dict)
        
    return clean_questions

# API routes
@app.post("/api/form")
async def create_form(loss: LossDescription = Body(...)):
    start_time = time.time()

    event_type = await classify_event_type(loss.description)
    logger.info(f"Classified as: {event_type.value}")
    
    relevant_questions = get_relevant_questions(event_type)
    logger.info(f"Processing {len(relevant_questions)} relevant questions out of {len(QUESTIONS)} total")
    
    question_answers = await process_questions_batch(
        description=loss.description,
        event_type=event_type,
        questions=relevant_questions
    )
    
    auto_answers = fill_auto_answers(event_type.value, question_answers)
    shaped_answers = format_answers_for_ui(auto_answers)

    # Clean questions to remove metadata fields
    clean_questions = clean_questions_for_response(QUESTIONS)

    end_time = time.time()
    logger.info(f"Request processed in {end_time - start_time:.2f} seconds")

    return {
        "questions": clean_questions,
        "answers": shaped_answers,
    }

# Keep the original endpoint for backward compatibility
@app.post("/form")
async def create_form_legacy(loss: LossDescription = Body(...)):
    return await create_form(loss)

@app.post("/api/form-with-image")
async def create_form_with_image(
    description: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    start_time = time.time()
    image_description = None
    
    # Process image if provided
    if image:
        try:
            # Create a temporary file to store the image
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                contents = await image.read()
                temp_file.write(contents)
                temp_file_path = temp_file.name
            
            # Process the image with OpenAI Vision API
            try:
                with open(temp_file_path, "rb") as img_file:
                    # Convert image to base64
                    base64_image = base64.b64encode(img_file.read()).decode('utf-8')
                
                # Call OpenAI with the image
                image_prompt = """
                Analyze this image of a vehicle damage or incident. 
                Describe what you see in detail, focusing on:
                1. Type of damage visible
                2. Describe the state of the vehicle's glass (intact, shattered, etc.)
                3. Vehicle parts affected
                4. Any environmental factors visible (weather, road conditions)
                5. Any injuries or people visible
                
                Provide only factual descriptions of what is visible, not assumptions.
                """
                
                image_analysis = client.chat.completions.create(
                    model="gpt-4o", # Use GPT-4o for vision capabilities
                    messages=[
                        {"role": "user", "content": [
                            {"type": "text", "text": image_prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]}
                    ],
                    response_model=ImageAnalysisResponse,
                    max_tokens=300,
                    temperature=0
                )
                
                image_description = image_analysis.image_description.strip()
                logger.info(f"Image analysis: {image_description}")
                
                # Combine text description with image description
                combined_description = f"{description}\n\nImage analysis: {image_description}"
                
            except Exception as e:
                logger.error(f"Error processing image with OpenAI: {e}")
                # If image processing fails, proceed with just the text description
                combined_description = description
            finally:
                # Clean up the temporary file
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.error(f"Error deleting temporary file: {e}")
        except Exception as e:
            logger.error(f"Error processing uploaded image: {e}")
            combined_description = description
    else:
        combined_description = description

    # Use the existing classification logic with the combined description
    event_type = await classify_event_type(combined_description)
    logger.info(f"Classified as: {event_type.value}")
    
    relevant_questions = get_relevant_questions(event_type)
    logger.info(f"Processing {len(relevant_questions)} relevant questions out of {len(QUESTIONS)} total")
    
    question_answers = await process_questions_batch(
        description=combined_description,
        event_type=event_type,
        questions=relevant_questions
    )
    
    auto_answers = fill_auto_answers(event_type.value, question_answers)
    shaped_answers = format_answers_for_ui(auto_answers)

    # Clean questions to remove metadata fields
    clean_questions = clean_questions_for_response(QUESTIONS)

    end_time = time.time()
    logger.info(f"Request processed in {end_time - start_time:.2f} seconds")

    return {
        "questions": clean_questions,
        "answers": shaped_answers,
        "image_description": image_description
    }

# health check 
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Mount static files for frontend
if not STATIC_MODE and os.path.exists(FRONTEND_DIR):
    # Only serve static files if not in STATIC mode
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    @app.get("/{path:path}")
    async def serve_spa(path: str):
        # Skip API routes
        if path.startswith("api/"):
            return {"error": "Not Found"}, 404
            
        # Check if file exists
        file_path = os.path.join(FRONTEND_DIR, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Otherwise return index.html for SPA routing
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
else:
    # In STATIC mode, redirect frontend requests to CloudFront
    @app.get("/")
    async def redirect_to_frontend():
        return RedirectResponse(url=f"https://{CLOUDFRONT_DOMAIN}/")
    
    @app.get("/{path:path}")
    async def handle_frontend_routes(path: str, request: Request):
        # Skip API routes
        if path.startswith("api/"):
            return JSONResponse(content={"error": "Not Found"}, status_code=404)
        
        # Redirect frontend routes to CloudFront
        return RedirectResponse(url=f"https://{CLOUDFRONT_DOMAIN}/{path}")