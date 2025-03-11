from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, List

class CarAngle(str, Enum):
    front = "front"
    front_left = "front_left"
    front_right = "front_right"
    left = "left"
    right = "right"
    back = "back"
    back_left = "back_left"
    back_right = "back_right"

class CarAngleCheckRequest(BaseModel):
    angle: CarAngle = Field(...)

class CarAngleCheckResponse(BaseModel):
    reasoning: str
    valid: bool

class ImageDamageAnalysis(BaseModel):
    angle: CarAngle
    damage_description: str     
    is_damage: bool

class DamageReport(BaseModel):
    insured_name: str
    vehicle_make: str
    vehicle_model: str

    damage_items: List[str]

    summary_thai: str
    summary_english: str
