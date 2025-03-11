import os
import uuid
import base64
import mimetypes
import asyncio
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from instructor import from_openai
from openai import AsyncOpenAI
from models import (
    CarAngleCheckRequest,
    CarAngleCheckResponse,
    ImageDamageAnalysis,
    CarAngle,
    DamageReport
)

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set in environment variables or .env file.")

client = from_openai(AsyncOpenAI(api_key=OPENAI_API_KEY))

app = FastAPI(title="Vehicle Damage Assessment API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_IMAGE_DIR = "temp_images"
MAX_CONCURRENT_REQUESTS = 10

os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)

@app.post("/check-angle", response_model=CarAngleCheckResponse)
async def check_car_angle(
    angle_check_req: CarAngleCheckRequest,
    file: UploadFile = File(...)
):
    """
    Endpoint to verify a single uploaded image is indeed the specified angle 
    (front, front_left, front_right, etc.).
    Returns True/False along with a short reasoning in JSON.
    
    The client can decide to re-prompt user to re-upload if valid==False.
    """
    try:
        temp_filename = os.path.join(TEMP_IMAGE_DIR, f"{uuid.uuid4()}_{file.filename}")
        with open(temp_filename, "wb") as f:
            f.write(await file.read())

        with open(temp_filename, "rb") as f:
            image_bytes = f.read()
        mime_type = mimetypes.guess_type(temp_filename)[0] or "image/jpeg"
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")

        prompt_text = (
            f"Is this image a picture of a car at the angle '{angle_check_req.angle}'?\n"
            f"Answer 'yes' or 'no', and provide reasoning in short."
        )

        response = await client.chat.completions.create(
            model="gpt-4o", 
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{encoded_image}"}
                    }
                ]
            }],
            response_model=CarAngleCheckResponse,
            max_tokens=100,
            temperature=0
        )

        try:
            os.remove(temp_filename)
        except:
            raise HTTPException(status_code=500, detail="Failed to remove temp file.")

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def analyze_single_image(angle, temp_path, semaphore):
    """Helper function to analyze a single image with semaphore control"""
    async with semaphore:
        # Read and base64-encode the image
        with open(temp_path, "rb") as f:
            image_bytes = f.read()
        mime_type = mimetypes.guess_type(temp_path)[0] or "image/jpeg"
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")

        prompt_text = (
            f"Analyze this car image at the angle '{angle}'. "
            f"Identify any visible damage. If there is damage, "
            f"describe it concisely in English and also in Thai."
        )

        # Let instructor directly return the Pydantic model
        damage_analysis = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{encoded_image}"}
                    }
                ]
            }],
            response_model=ImageDamageAnalysis,
            max_tokens=300,
            temperature=0
        )
        return damage_analysis


@app.post("/analyze-images")
async def analyze_images(
    insured_name: str = Form(...),
    vehicle_make: str = Form(...),
    vehicle_model: str = Form(...),
    front: UploadFile = File(...),
    front_left: UploadFile = File(...),
    front_right: UploadFile = File(...),
    left: UploadFile = File(...),
    right: UploadFile = File(...),
    back: UploadFile = File(...),
    back_left: UploadFile = File(...),
    back_right: UploadFile = File(...)
):
    """
    Endpoint that receives 8 images for a single vehicle (one per angle).
    1) Temporarily saves them.
    2) Analyzes each image with a VLM to detect if there's damage.
    3) Produces a bilingual Thai/English damage report only for the angles that have damage.
    4) Removes the images afterwards.
    """

    files_map = {
        CarAngle.front: front,
        CarAngle.front_left: front_left,
        CarAngle.front_right: front_right,
        CarAngle.left: left,
        CarAngle.right: right,
        CarAngle.back: back,
        CarAngle.back_left: back_left,
        CarAngle.back_right: back_right,
    }

    temp_files = {}
    for angle, upload_file in files_map.items():
        temp_filename = os.path.join(TEMP_IMAGE_DIR, f"{uuid.uuid4()}_{upload_file.filename}")
        with open(temp_filename, "wb") as f:
            f.write(await upload_file.read())
        temp_files[angle] = temp_filename

    # Create a semaphore to limit concurrent API calls
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    # Create tasks for concurrent processing
    tasks = []
    for angle, temp_path in temp_files.items():
        task = analyze_single_image(angle, temp_path, semaphore)
        tasks.append(task)
    
    try:
        damage_results = await asyncio.gather(*tasks)
    except Exception as e:
        for _, fp in temp_files.items():
            try:
                os.remove(fp)
            except:
                raise HTTPException(status_code=500, detail="Failed to remove temp files.")
        raise HTTPException(status_code=500, detail=f"Damage analysis failed: {str(e)}")
    
    # 3) Generate bilingual Thai/English damage report
    # Only for images that have damage
    damage_items = []
    for res in damage_results:
        if res.is_damage:
            angle_label = res.angle.value.replace("_", " ") 
            item_text = f"{angle_label.title()}: {res.damage_description}"
            damage_items.append(item_text)

    if not damage_items:
        report = DamageReport(
            insured_name=insured_name,
            vehicle_make=vehicle_make,
            vehicle_model=vehicle_model,
            damage_items=[],
            summary_thai="ไม่พบความเสียหายใดๆ",
            summary_english="No damage detected."
        )
    else:
        report = DamageReport(
            insured_name=insured_name,
            vehicle_make=vehicle_make,
            vehicle_model=vehicle_model,
            damage_items=damage_items,
            summary_thai=(
                "พบความเสียหายตามรายการด้านบน โปรดติดต่อบริษัทประกันภัยเพื่อดำเนินการซ่อมแซม"
            ),
            summary_english=(
                "Damage has been detected as listed above. Please contact the insurance provider for further repairs."
            )
        )
    
    # Cleanup temp files
    for _, fp in temp_files.items():
        try:
            os.remove(fp)
        except:
            raise HTTPException(status_code=500, detail="Failed to remove temp files.")

    return JSONResponse(content=report.model_dump_json())