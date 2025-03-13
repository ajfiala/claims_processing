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

class DamageReport(BaseModel):
    insured_name: str
    vehicle_make: str
    vehicle_model: str
    damage_items: List[str]
    summary_thai: str
    summary_english: str
    # Optional field to store base64 image data for each angle (if available)
    angle_images: Optional[Dict[str, str]] = None

    def to_markdown(self) -> str:
        """Generate a professionally formatted markdown report of vehicle damage with images"""
        
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
        
        # Map for converting angles to image keys
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
                    
                    # Add image placeholder to be processed by frontend
                    angle_key = angle_name.lower().replace(' ', '_')
                    if angle_key in angle_to_key:
                        lines.append("")
                        lines.append(f"![{angle_name} damage](image_placeholder_for_{angle_key})")
                else:
                    lines.append(f"**{item}**")
                
                # Add spacing between items except after the last one
                if idx < len(self.damage_items) - 1:
                    lines.append("")
        else:
            lines.append("**No damage detected on vehicle inspection.**")
        
        lines.append("")
        lines.append("-----")
        lines.append("")
        
        # Add Thai summary
        lines.append("## สรุปรายงาน")
        lines.append("")
        lines.append(f"{self.summary_thai}")
        lines.append("")
        
        # Add English summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"**{self.summary_english}**")
        lines.append("")
        lines.append("-----")
        lines.append("")
        lines.append("## Next Steps")
        lines.append("")
        
        if self.damage_items:
            steps = [
                "Review the damage assessment report",
                "Contact your insurance provider at the number below",
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