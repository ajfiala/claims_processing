# app.py
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
    DamageReportEnglish,
    DamageReportThai
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
async def check_car_angle(angle_check_req: CarAngleCheckRequest, file: UploadFile = File(...)):
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


async def analyze_single_image_english(angle, temp_path, semaphore):
    async with semaphore:
        with open(temp_path, "rb") as f:
            image_bytes = f.read()
        mime_type = mimetypes.guess_type(temp_path)[0] or "image/jpeg"
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")

        prompt_text = (
            f"Analyze this car image at the angle '{angle}'. "
            f"Identify any visible damage. If there is damage, "
            f"describe it concisely in English and also in Thai."
        )

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

async def analyze_single_image_thai(angle, temp_path, semaphore):
    async with semaphore:
        with open(temp_path, "rb") as f:
            image_bytes = f.read()
        mime_type = mimetypes.guess_type(temp_path)[0] or "image/jpeg"
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")

        prompt_text = (
            f"โปรดวิเคราะห์ภาพถ่ายรถยนต์จากมุม '{angle}' อย่างละเอียด "
            "ระบุความเสียหายที่มองเห็นได้อย่างชัดเจน หากพบความเสียหาย "
            "ให้บรรยายลักษณะความเสียหายโดยละเอียดในรูปแบบที่ผู้สำรวจภัยประกันภัยรถยนต์ใช้ "
            "สำคัญ: คำอธิบายความเสียหายต้องเป็นภาษาไทยเท่านั้น"
        )

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
    
    # Read and store all uploaded files
    for angle, upload_file in files_map.items():
        temp_filename = os.path.join(TEMP_IMAGE_DIR, f"{uuid.uuid4()}_{upload_file.filename}")
        with open(temp_filename, "wb") as f:
            file_content = await upload_file.read()
            f.write(file_content)
        temp_files[angle] = temp_filename
    
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    tasks_en = []
    tasks_th = []
    for angle, temp_path in temp_files.items():
        task_en = analyze_single_image_english(angle, temp_path, semaphore)
        task_th = analyze_single_image_thai(angle, temp_path, semaphore)
        tasks_en.append(task_en)
        tasks_th.append(task_th)
    
    try:
        damage_results_en = await asyncio.gather(*tasks_en)
        damage_results_th = await asyncio.gather(*tasks_th)
    except Exception as e:
        # Clean up temp files
        for _, fp in temp_files.items():
            try:
                os.remove(fp)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Damage analysis failed: {str(e)}")
    
    # Process English damage items
    damage_items_en = []
    for res in damage_results_en:
        if res.is_damage:
            angle_label = res.angle.value.replace("_", " ")
            item_text = f"{angle_label.title()}: {res.damage_description}"
            damage_items_en.append(item_text)
    
    # Process Thai damage items
    damage_items_th = []
    for res in damage_results_th:
        if res.is_damage:
            # Convert angle names to Thai if you have translations
            # For now using the same structure as English
            angle_label = res.angle.value.replace("_", " ")
            item_text = f"{angle_label.title()}: {res.damage_description}"
            damage_items_th.append(item_text)
    
    # Create English report
    if not damage_items_en:
        report_en = DamageReportEnglish(
            insured_name=insured_name,
            vehicle_make=vehicle_make,
            vehicle_model=vehicle_model,
            damage_items=[],
            summary="No damage detected."
        )
    else:
        report_en = DamageReportEnglish(
            insured_name=insured_name,
            vehicle_make=vehicle_make,
            vehicle_model=vehicle_model,
            damage_items=damage_items_en,
            summary="Damage has been detected as listed above. Please contact the insurance provider for further repairs."
        )
    
    # Create Thai report
    if not damage_items_th:
        report_th = DamageReportThai(
            insured_name=insured_name,
            vehicle_make=vehicle_make,
            vehicle_model=vehicle_model,
            damage_items=[],
            summary="ไม่พบความเสียหายใดๆ"
        )
    else:
        report_th = DamageReportThai(
            insured_name=insured_name,
            vehicle_make=vehicle_make,
            vehicle_model=vehicle_model,
            damage_items=damage_items_th,
            summary="พบความเสียหายตามรายการด้านบน โปรดติดต่อบริษัทประกันภัยเพื่อดำเนินการซ่อมแซม"
        )
    
    # Clean up temp files
    for _, fp in temp_files.items():
        try:
            os.remove(fp)
        except:
            pass
    
    # Return both reports
    return JSONResponse(
        content={
            "english_report": report_en.to_markdown(),
            "thai_report": report_th.to_markdown()
        }
    )