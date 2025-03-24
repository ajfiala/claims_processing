from pydantic import BaseModel, Field
from typing import Optional, Dict
from enum import Enum
from datetime import datetime
from typing import List
from datetime import datetime
from uuid import uuid4

class CarAngle(str, Enum):
    front = "front"
    front_left = "front_left"
    front_right = "front_right"
    left = "left"
    right = "right"
    back = "back"
    back_left = "back_left"
    back_right = "back_right"

class TranslationResponse(BaseModel):
    """แบบจำลองสำหรับรับคำอธิบายความเสียหายของรถยนต์ที่แปลเป็นภาษาไทย"""
    damage_description: str = Field(
        description="คำอธิบายความเสียหายของรถยนต์คำแปลภาษาไทย."
    )

class CarAngleCheckRequest(BaseModel):
    angle: CarAngle = Field(...)

class CarAngleCheckResponse(BaseModel):
    reasoning: str
    valid: bool

class ImageDamageAnalysis(BaseModel):
    angle: CarAngle
    damage_description: str
    is_damage: bool

class ImageDamageAnalyses(BaseModel):
    english_analysis: ImageDamageAnalysis 
    thai_analysis: ImageDamageAnalysis

class DamageReportEnglish(BaseModel):
    insured_name: str
    vehicle_make: str
    vehicle_model: str
    damage_items: List[str]
    summary: str
    angle_images: Optional[Dict[str, str]] = None

    def to_markdown(self) -> str:
        current_date = datetime.now().strftime("%B %d, %Y")
        report_id = str(uuid4())[:8].upper()
        lines = [
            "# Vehicle Damage Assessment Report",
            f"*Generated on {current_date}*",
            "",
            "-----",
            "",
            "## Claim Information",
            "",
            f"**Report ID:** {report_id}",
            f"**Insured Name:** {self.insured_name}",
            f"**Vehicle:** {self.vehicle_make} {self.vehicle_model}",
            "",
            "-----",
            "",
            "## Damage Assessment",
            "",
        ]
  
        angle_to_key = {
            "front": "f",
            "front left": "fl",
            "front_left": "fl",
            "front right": "fr",
            "front_right": "fr",
            "left": "l",
            "right": "r",
            "back": "b",
            "back left": "bl",
            "back_left": "bl",
            "back right": "br",
            "back_right": "br"
        }

        if self.damage_items:
            for idx, item in enumerate(self.damage_items):
                colon_pos = item.find(':')
                if colon_pos > 0:
                    angle_name = item[:colon_pos].strip()
                    description = item[colon_pos+1:].strip()
                    lines.append(f"**{angle_name}:** {description}")
                    angle_key = angle_to_key.get(angle_name.lower(), None)
                    if angle_key and self.angle_images and angle_key in self.angle_images:
                        lines.append("")
                        lines.append(f"![{angle_name} damage]({self.angle_images[angle_key]})")
                else:
                    lines.append(f"**{item}**")
                if idx < len(self.damage_items) - 1:
                    lines.append("")
        else:
            lines.append("**No damage detected on vehicle inspection.**")
        lines.append("")
        lines.append("-----")
        lines.append("")
        lines.append("## Summary")
        lines.append("")
        lines.append(f"**{self.summary}**")
        lines.append("")
        lines.append("-----")
        lines.append("")
        lines.append("## Next Steps")
        lines.append("")
        if self.damage_items:
            steps = [
                "Review the damage assessment report",
                "Contact your insurance provider",
                "Schedule a repair appointment",
                "Submit any additional documentation requested"
            ]
            for idx, step in enumerate(steps):
                lines.append(f"{idx + 1}. {step}")
                if idx < len(steps) - 1:
                    lines.append("")
        else:
            lines.append("1. Keep this report for your records")
            lines.append("")
            lines.append("2. No further action required at this time")
        lines.append("")
        lines.append("-----")
        lines.append("")
        lines.append("*For assistance, contact Bangkok Insurance at 02-123-4567 or support@bangkokinsurance.com*")
        return "\n".join(lines)

class DamageReportThai(BaseModel):
    insured_name: str
    vehicle_make: str
    vehicle_model: str
    damage_items: List[str]
    summary: str
    angle_images: Optional[Dict[str, str]] = None  
    
    def to_markdown(self) -> str:
        current_date = datetime.now().strftime("%d %B %Y")
        report_id = str(uuid4())[:8].upper()
        
        lines = [
            "# รายงานการประเมินความเสียหายของรถยนต์",
            f"*สร้างเมื่อ {current_date}*",
            "",
            "-----",
            "",
            "## ข้อมูลการเคลม",
            "",
            f"**รหัสรายงาน:** {report_id}",
            f"**ชื่อผู้เอาประกัน:** {self.insured_name}",
            f"**รถยนต์:** {self.vehicle_make} {self.vehicle_model}",
            "",
            "-----",
            "",
            "## การประเมินความเสียหาย",
            "",
        ]

        angle_to_key = {
            "front": "f",
            "front left": "fl",
            "front_left": "fl",
            "front right": "fr",
            "front_right": "fr",
            "left": "l",
            "right": "r",
            "back": "b",
            "back left": "bl",
            "back_left": "bl",
            "back right": "br",
            "back_right": "br"
        }
        
        thai_angle_names = {
            "front": "ด้านหน้า",
            "front left": "ด้านหน้าซ้าย",
            "front_right": "ด้านหน้าขวา",
            "front right": "ด้านหน้าขวา",
            "left": "ด้านซ้าย",
            "right": "ด้านขวา",
            "back": "ด้านหลัง",
            "back left": "ด้านหลังซ้าย",
            "back_right": "ด้านหลังขวา",
            "back right": "ด้านหลังขวา"
        }
        
        if self.damage_items:
            for idx, item in enumerate(self.damage_items):
                colon_pos = item.find(':')
                if colon_pos > 0:
                    angle_name = item[:colon_pos].strip()
                    description = item[colon_pos+1:].strip()

                    english_angle = angle_name.lower()
                    # Attempt to find a Thai label
                    display_name = thai_angle_names.get(english_angle, angle_name)
                    
                    lines.append(f"**{display_name}:** {description}")

                    angle_key = angle_to_key.get(english_angle, None)
                    if angle_key and self.angle_images and angle_key in self.angle_images:
                        lines.append("")
                        lines.append(f"![ความเสียหาย{display_name}]({self.angle_images[angle_key]})")
                else:
                    lines.append(f"**{item}**")
                
                if idx < len(self.damage_items) - 1:
                    lines.append("")
        else:
            lines.append("**ไม่พบความเสียหายจากการตรวจสอบรถยนต์**")
        
        lines.append("")
        lines.append("-----")
        lines.append("")
        lines.append("## สรุป")
        lines.append("")
        lines.append(f"**{self.summary}**")
        lines.append("")
        lines.append("-----")
        lines.append("")
        lines.append("## ขั้นตอนต่อไป")
        lines.append("")
        
        if self.damage_items:
            steps = [
                "ตรวจสอบรายงานการประเมินความเสียหาย",
                "ติดต่อบริษัทประกันภัยของคุณ",
                "นัดหมายการซ่อมแซม",
                "ส่งเอกสารเพิ่มเติมตามที่ร้องขอ"
            ]
            for idx, step in enumerate(steps):
                lines.append(f"{idx + 1}. {step}")
                if idx < len(steps) - 1:
                    lines.append("")
        else:
            lines.append("1. เก็บรายงานนี้ไว้เป็นหลักฐาน")
            lines.append("")
            lines.append("2. ไม่จำเป็นต้องดำเนินการใดๆ เพิ่มเติมในขณะนี้")
        
        lines.append("")
        lines.append("-----")
        lines.append("")
        lines.append("*สำหรับความช่วยเหลือ โปรดติดต่อ บริษัท กรุงเทพประกันภัย จำกัด ที่ 02-123-4567 หรือ support@bangkokinsurance.com*")
        
        return "\n".join(lines)
