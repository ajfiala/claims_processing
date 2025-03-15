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

class CarAngleCheckRequest(BaseModel):
    angle: CarAngle = Field(...)

class CarAngleCheckResponse(BaseModel):
    reasoning: str
    valid: bool

class ImageDamageAnalysis(BaseModel):
    angle: CarAngle
    damage_description: str     
    is_damage: bool

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
            "front_left": "fl",
            "front_right": "fr",
            "left": "l",
            "right": "r",
            "back": "b",
            "back_left": "bl",
            "back_right": "br"
        }
        if self.damage_items:
            for idx, item in enumerate(self.damage_items):
                colon_pos = item.find(':')
                if colon_pos > 0:
                    angle_name = item[:colon_pos].strip()
                    description = item[colon_pos+1:].strip()
                    lines.append(f"**{angle_name}:** {description}")
                    angle_key = angle_name.lower().replace(' ', '_')
                    if angle_key in angle_to_key:
                        lines.append("")
                        lines.append(f"![{angle_name} damage](image_placeholder_for_{angle_key})")
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
            f"*จัดทำเมื่อวันที่ {current_date}*",
            "",
            "-----",
            "",
            "## ข้อมูลเคลม",
            "",
            f"**เลขที่รายงาน:** {report_id}",
            f"**ชื่อผู้เอาประกันภัย:** {self.insured_name}",
            f"**ยี่ห้อรถยนต์:** {self.vehicle_make} {self.vehicle_model}",
            "",
            "-----",
            "",
            "## การประเมินความเสียหาย",
            "",
        ]
        angle_to_key = {
            "front": "f",
            "front_left": "fl",
            "front_right": "fr",
            "left": "l",
            "right": "r",
            "back": "b",
            "back_left": "bl",
            "back_right": "br"
        }
        if self.damage_items:
            for idx, item in enumerate(self.damage_items):
                colon_pos = item.find(':')
                if colon_pos > 0:
                    angle_name = item[:colon_pos].strip()
                    description = item[colon_pos+1:].strip()
                    lines.append(f"**{angle_name}:** {description}")
                    angle_key = angle_name.lower().replace(' ', '_')
                    if angle_key in angle_to_key:
                        lines.append("")
                        lines.append(f"![{angle_name}](image_placeholder_for_{angle_key})")
                else:
                    lines.append(f"**{item}**")
                if idx < len(self.damage_items) - 1:
                    lines.append("")
        else:
            lines.append("**ไม่พบความเสียหายระหว่างการตรวจสอบ**")
        lines.append("")
        lines.append("-----")
        lines.append("")
        lines.append("## สรุปรายงาน")
        lines.append("")
        lines.append(f"{self.summary}")
        lines.append("")
        lines.append("-----")
        lines.append("")
        lines.append("## ขั้นตอนต่อไป")
        lines.append("")
        if self.damage_items:
            steps = [
                "ตรวจสอบรายงานการประเมินความเสียหาย",
                "ติดต่อบริษัทประกันภัยของคุณ",
                "นัดหมายซ่อมรถยนต์",
                "ส่งเอกสารเพิ่มเติมหากมีการร้องขอ"
            ]
            for idx, step in enumerate(steps):
                lines.append(f"{idx + 1}. {step}")
                if idx < len(steps) - 1:
                    lines.append("")
        else:
            lines.append("1. เก็บรายงานนี้ไว้เพื่อเป็นหลักฐาน")
            lines.append("")
            lines.append("2. ไม่ต้องดำเนินการใด ๆ เพิ่มเติม")
        lines.append("")
        lines.append("-----")
        lines.append("")
        lines.append("*หากต้องการความช่วยเหลือ กรุณาติดต่อ Bangkok Insurance ที่ 02-123-4567 หรือ support@bangkokinsurance.com*")
        return "\n".join(lines)