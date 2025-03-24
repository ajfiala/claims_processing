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
    ImageDamageAnalyses,
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
    """
    This endpoint is used to verify if the uploaded image
    matches the requested CarAngle (front, back_left, etc.)
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


async def translate_to_thai(english_description: str) -> str:
    """
    Uses GPT to translate an English description of car damage into Thai.
    Uses regular AsyncOpenAI client instead of instructor.
    Provides detailed instructions and examples to ensure valid Thai translation.
    Falls back to a default message if translation fails.
    """
    translation_prompt = (
        "คุณเป็นนักแปลมืออาชีพระดับเชี่ยวชาญในการแปลคำอธิบายความเสียหายของรถยนต์จากภาษาอังกฤษเป็นภาษาไทย "
        "หน้าที่ของคุณคือการแปลข้อความภาษาอังกฤษให้เป็นภาษาไทยที่ถูกต้องเท่านั้น "
        "คุณต้องตอบกลับเป็นภาษาไทยล้วน ไม่มีการเพิ่มข้อความภาษาอังกฤษหรือภาษาอื่นใดๆ "
        "ไม่มีคำอธิบายเพิ่มเติม ไม่มีหมายเหตุ ไม่มีแท็กพิเศษ "
        "เพียงแค่ข้อความภาษาไทยที่แปลจากภาษาอังกฤษเท่านั้น \n\n"
        
        "กฎที่สำคัญมาก: \n"
        "1. ตอบเป็นภาษาไทยเท่านั้น ห้ามมีภาษาอังกฤษ \n"
        "2. ไม่ต้องมีคำอธิบายใดๆ ทั้งสิ้น \n"
        "3. ไม่ต้องใส่เครื่องหมายคำพูดหรือเครื่องหมายอ้างอิงใดๆ \n"
        "4. แปลให้เป็นภาษาไทยที่เป็นธรรมชาติ ถูกต้องตามหลักภาษา \n"
        "5. ห้ามเพิ่มเติมหรือลดทอนความหมายจากต้นฉบับ \n\n"
        
        f"ข้อความที่ต้องแปล: \"{english_description}\" \n\n"
        
        "ตัวอย่างการแปลที่ถูกต้อง: \n"
        "ภาษาอังกฤษ: \"The front left side of the car shows significant damage. The bumper is detached, and the hood is crumpled and lifted.\" \n"
        "ภาษาไทย: ด้านหน้าซ้ายของรถมีความเสียหายอย่างมาก กันชนหลุดออก และฝากระโปรงหน้ายุบและยกขึ้น \n\n"
        
        "ภาษาอังกฤษ: \"The front right side of the car shows significant damage. The hood is bent upwards, and the front bumper is misaligned.\" \n"
        "ภาษาไทย: ด้านหน้าขวาของรถมีความเสียหายอย่างมาก ฝากระโปรงหน้างอขึ้น และกันชนหน้าไม่ตรงแนว \n\n"
        
        "ภาษาอังกฤษ: \"The rear bumper has multiple scratches and a small dent on the right corner.\" \n"
        "ภาษาไทย: กันชนหลังมีรอยขีดข่วนหลายจุดและมีรอยบุบเล็กที่มุมด้านขวา \n\n"
        
        "โปรดแปลข้อความให้เป็นภาษาไทยที่ถูกต้องและเป็นธรรมชาติ เหมาะสำหรับการใช้งานจริงในบริบทของการประเมินความเสียหายของรถยนต์ "
        "ตอบเฉพาะเนื้อหาภาษาไทยที่แปลแล้วเท่านั้น ไม่มีข้อความอื่นใด"
    )

    try:
        openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": translation_prompt}],
            max_tokens=500,
            temperature=0.6,
        )
        
        translated_text = response.choices[0].message.content.strip()
        
        print(f"Translated text: {translated_text}")

        if translated_text and len(translated_text.strip()) > 0:
            return translated_text
        else:
            raise ValueError("Empty translation received")
            
    except Exception as e:
        print(f"Translation failed with error: {e}")
        return f"พบความเสียหาย: {english_description}"

async def analyze_single_image_english(angle: CarAngle, temp_path: str, semaphore: asyncio.Semaphore) -> ImageDamageAnalyses:
    async with semaphore:
        with open(temp_path, "rb") as f:
            image_bytes = f.read()
        mime_type = mimetypes.guess_type(temp_path)[0] or "image/jpeg"
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")

        english_prompt = (
            f"Analyze this car image at the angle '{angle}'. "
            f"Identify any visible damage in English. "
            f"Be concise and factual, but note if damage is found or not."
        )

        english_result = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": english_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{encoded_image}",
                                      "detail": "high"},
                    }
                ]
            }],
            response_model=ImageDamageAnalysis,
            max_tokens=300,
            temperature=0
        )

        thai_result = ImageDamageAnalysis(
            angle=english_result.angle,
            damage_description="",
            is_damage=english_result.is_damage
        )

        thai_result.damage_description =  await translate_to_thai(english_result.damage_description)

        return ImageDamageAnalyses(
            english_analysis=english_result,
            thai_analysis=thai_result
        )

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify if the server is running.
    """
    return {"status": "ok"}

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

    angle_key_map = {
        CarAngle.front: "f",
        CarAngle.front_left: "fl",
        CarAngle.front_right: "fr",
        CarAngle.left: "l",
        CarAngle.right: "r",
        CarAngle.back: "b",
        CarAngle.back_left: "bl",
        CarAngle.back_right: "br"
    }

    temp_files = {}
    file_contents = {}

    for angle, upload_file in files_map.items():
        temp_filename = os.path.join(TEMP_IMAGE_DIR, f"{uuid.uuid4()}_{upload_file.filename}")
        file_content = await upload_file.read()
        file_contents[angle] = file_content

        with open(temp_filename, "wb") as f:
            f.write(file_content)

        temp_files[angle] = temp_filename

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    tasks = []
    for angle, temp_path in temp_files.items():
        tasks.append(analyze_single_image_english(angle, temp_path, semaphore))

    try:
        all_analyses = await asyncio.gather(*tasks)
    except Exception as e:
        for _, fp in temp_files.items():
            try:
                os.remove(fp)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Damage analysis failed: {str(e)}")

    damage_items_en = []
    damage_items_th = []
    
    angles_in_order = list(files_map.keys())
    damage_detected = False

    for i, angle in enumerate(angles_in_order):
        combined = all_analyses[i]
        eng = combined.english_analysis
        th = combined.thai_analysis

        if eng.is_damage:
            damage_detected = True
            # For English report
            angle_label_en = eng.angle.value.replace("_", " ")
            item_text_en = f"{angle_label_en.title()}: {eng.damage_description}"
            damage_items_en.append(item_text_en)
            
            # For Thai report - using the same format but with Thai description
            angle_label_th = eng.angle.value.replace("_", " ")
            item_text_th = f"{angle_label_th.title()}: {th.damage_description}"
            damage_items_th.append(item_text_th)

    # Create base64 encoded images
    angle_images = {}
    for angle in files_map.keys():
        content = file_contents[angle]
        file_ext = os.path.splitext(files_map[angle].filename)[1].lower()

        if file_ext == ".png":
            mime_type = "image/png"
        elif file_ext == ".gif":
            mime_type = "image/gif"
        elif file_ext == ".webp":
            mime_type = "image/webp"
        else:
            mime_type = "image/jpeg"

        base64_str = base64.b64encode(content).decode("utf-8")
        data_url = f"data:{mime_type};base64,{base64_str}"
        
        angle_key = angle_key_map[angle]
        angle_images[angle_key] = data_url

    if not damage_detected:
        report_en = DamageReportEnglish(
            insured_name=insured_name,
            vehicle_make=vehicle_make,
            vehicle_model=vehicle_model,
            damage_items=[],
            summary="No damage detected.",
            angle_images=angle_images
        )
        
        report_th = DamageReportThai(
            insured_name=insured_name,
            vehicle_make=vehicle_make,
            vehicle_model=vehicle_model,
            damage_items=[],
            summary="ไม่พบความเสียหายใดๆ",
            angle_images=angle_images
        )
    else:
        report_en = DamageReportEnglish(
            insured_name=insured_name,
            vehicle_make=vehicle_make,
            vehicle_model=vehicle_model,
            damage_items=damage_items_en,
            summary="Damage has been detected as listed above. Please contact the insurance provider for further repairs.",
            angle_images=angle_images
        )
        
        report_th = DamageReportThai(
            insured_name=insured_name,
            vehicle_make=vehicle_make,
            vehicle_model=vehicle_model,
            damage_items=damage_items_th,
            summary="พบความเสียหายตามรายการด้านบน โปรดติดต่อบริษัทประกันภัยเพื่อดำเนินการซ่อมแซม",
            angle_images=angle_images
        )

    for _, fp in temp_files.items():
        try:
            os.remove(fp)
        except:
            pass

    return JSONResponse(
        content={
            "english_report": report_en.to_markdown(),
            "thai_report": report_th.to_markdown()
        }
    )