from typing import Optional, List, Union
from enum import Enum
from pydantic import BaseModel, field_validator

class QuestionAnswer(BaseModel):
    # We'll store a single string or "null"
    # or for booleans 'true'/'false'
    # We keep it as a string to avoid constant JSON parse issues
    answer: Union[str, None]

    @field_validator("answer")
    def ensure_double_quotes(cls, v):
        # Ensure the answer is always a string with double quotes
        if isinstance(v, str):
            return v
        elif v is None:
            return "null"
        elif isinstance(v, bool):
            return "true" if v else "false"
        else:
            return v

# Standardized event types for auto claims
class EventType(str, Enum):
    TOWING_ONLY = "towing-only"
    COLLISION = "collision"
    INJURED_AS_PEDESTRIAN = "injured-as-pedestrian"
    INJURED_A_PEDESTRIAN = "injured-a-pedestrian"
    DAMAGE_BY_WEATHER = "damage-caused-by-weather"
    DAMAGE_BY_FIRE = "damage-caused-by-fire"
    DAMAGE_BY_ANIMALS = "damage-caused-by-animals"
    VEHICLE_VANDALIZED = "vehicle-vandalized"
    VEHICLE_BROKEN_INTO_OR_STOLEN = "vehicle-broken-into-or-stolen"
    OTHER_VEHICLE_DAMAGE = "other-vehicle-damage"

# Request model for loss description
class LossDescription(BaseModel):
    description: str

class ClassificationResponse(BaseModel):
    event_type: str

# Element types for form fields
class ELEMENT(str, Enum):
    SELECT = "select"
    MULTI_SELECT = "multiselect"
    RADIO = "radio"
    INPUT = "input"
    INPUT_PHONE = "input-phone"
    YES_OR_NO = "yes-or-no"
    YES_OR_NO_OR_UNKNOWN = "yes-or-no-or-unknown"
    NUMERIC = "numeric"
    CHECKBOX = "checkbox"
    INFOBOX = "infobox"

# List of values for selectable options
class LOV(BaseModel):
    value: str
    label: str
    description: Optional[str] = None

# Model for each question in the claims flow
class Question(BaseModel):
    dependsOn: Optional[str] = None
    id: str
    type: ELEMENT
    description: Optional[str] = None
    label: Optional[str] = None
    optional: bool = False
    validate: Optional[str] = None
    lovs: Optional[List[LOV]] = None

# Aggregated answers for an auto claim
class AutoAnswers(BaseModel):
    eventType: Optional[str] = None
    whichVehicleInvolved: Optional[str] = None
    whoWasDriving: Optional[str] = None
    otherDriverFirstName: Optional[str] = None
    otherDriverLastName: Optional[str] = None
    otherDriverPhoneNumber: Optional[str] = None
    wasVehicleTowed: Optional[bool] = None
    wasVehicleGlassDamaged: Optional[bool] = None
    wereFatalities: Optional[bool] = None
    wereInjuries: Optional[bool] = None
    numOtherVehicles: Optional[str] = None
    injuredParty: List[Optional[str]] = None 
    vehicleDriverFirstName: Optional[str] = None
    vehicleDriverLastName: Optional[str] = None
    vehicleDriverPhoneNumber: Optional[str] = None
    isVehicleDrivable: Optional[bool] = None

##############################
# Prepare the question set
##############################

# We only define one set of questions for an Auto policy
QUESTIONS = [
    Question(
        dependsOn=None,
        id="eventType",
        type=ELEMENT.SELECT,
        label="Select Event",
        lovs=[
            LOV(value=EventType.TOWING_ONLY.value, label="Towing Only", description="Vehicle requires towing without additional damage."),
            LOV(value=EventType.COLLISION.value, label="Collision", description="Involvement in a vehicular accident."),
            LOV(value=EventType.INJURED_AS_PEDESTRIAN.value, label="Injured as Pedestrian/Bicyclist", description="Policyholder was injured while on foot or cycling."),
            LOV(value=EventType.INJURED_A_PEDESTRIAN.value, label="Injured a Pedestrian/Bicyclist", description="Policyholder’s vehicle injured a pedestrian or cyclist."),
            LOV(value=EventType.DAMAGE_BY_WEATHER.value, label="Damage Caused by Weather", description="Vehicle damaged due to weather events such as flooding or hail."),
            LOV(value=EventType.DAMAGE_BY_FIRE.value, label="Damage Caused by Fire", description="Vehicle damaged due to fire."),
            LOV(value=EventType.DAMAGE_BY_ANIMALS.value, label="Damage Caused by Animals", description="Vehicle damaged due to an animal-related incident."),
            LOV(value=EventType.VEHICLE_VANDALIZED.value, label="Vehicle Vandalized", description="Vehicle intentionally damaged by a third party."),
            LOV(value=EventType.VEHICLE_BROKEN_INTO_OR_STOLEN.value, label="Vehicle Broken Into or Stolen", description="Vehicle was broken into or stolen."),
            LOV(value=EventType.OTHER_VEHICLE_DAMAGE.value, label="Other Vehicle Damage", description="Any vehicle damage that does not fit the above categories."),
        ],
    ),
    Question(
        dependsOn="ans => ['collision', 'injured-a-pedestrian', 'damage-caused-by-weather', 'damage-caused-by-fire', 'damage-caused-by-animals', 'vehicle-vandalized', 'vehicle-broken-into-or-stolen', 'other-vehicle-damage'].includes(ans?.eventType?.value)",
        id="whichVehicleInvolved",
        type=ELEMENT.RADIO,
        label="Which of your vehicles was involved?",
        description="Relevant for collision, injured-a-pedestrian, damage caused by weather/fire/animals, vandalism, theft, or other damage claims.",
        lovs=[
            LOV(value="2023-bmw-x1", label="2023 BMW X1"),
            LOV(value="rental-car", label="Rental Car"),
            LOV(value="other", label="Other car not on policy"),
        ],
    ),
    Question(
        dependsOn="ans => ['collision', 'injured-a-pedestrian', 'damage-caused-by-weather', 'damage-caused-by-fire', 'damage-caused-by-animals', 'vehicle-vandalized', 'vehicle-broken-into-or-stolen'].includes(ans?.eventType?.value)",
        id="whoWasDriving",
        type=ELEMENT.RADIO,
        label="Who was driving the vehicle?",
        description="Select the person driving during the event.",
        lovs=[
            LOV(
                value="driver-1",
                label="Billy BadDriver",
                description="Main driver on the account; select if the collision is described in first person."
            ),
            LOV(value="other", label="Other"),
            LOV(value="not-driven-when-damage-occured", label="Vehicle was not being driven at the time of damage"),
        ],
    ),
    Question(
        dependsOn="ans => ans?.eventType?.value == 'collision' && ans?.whoWasDriving?.value == 'other'",
        id="otherDriverFirstName",
        type=ELEMENT.INPUT,
        label="Other Driver First Name",
        optional=True,
        description="Provide the first name of the other driver if 'Other' was selected."
    ),
    Question(
        dependsOn="ans => ans?.eventType?.value == 'collision' && ans?.whoWasDriving?.value == 'other'",
        id="otherDriverLastName",
        type=ELEMENT.INPUT,
        label="Other Driver Last Name",
        optional=True,
        description="Provide the last name of the other driver if 'Other' was selected."
    ),
    Question(
        dependsOn="ans => ans?.eventType?.value == 'collision' && ans?.whoWasDriving?.value == 'other'",
        id="otherDriverPhoneNumber",
        type=ELEMENT.INPUT_PHONE,
        label="Other Driver Phone Number",
        optional=True,
        validate="phone => !/^\\d{3}-\\d{3}-\\d{4}$/.test(phone) ? 'Phone format should be xxx-xxx-xxxx' : false",
        description="Provide the phone number of the other driver if applicable."
    ),
    Question(
        dependsOn="ans => ['collision', 'injured-a-pedestrian', 'damage-caused-by-weather', 'damage-caused-by-fire', 'damage-caused-by-animals', 'vehicle-vandalized', 'vehicle-broken-into-or-stolen'].includes(ans?.eventType?.value)",
        id="wasVehicleTowed",
        type=ELEMENT.YES_OR_NO,
        label="Was your vehicle towed?",
        description="Select whether the vehicle required towing."
    ),
    Question(
        dependsOn="ans => ['collision', 'injured-a-pedestrian', 'damage-caused-by-weather', 'damage-caused-by-fire', 'damage-caused-by-animals', 'vehicle-vandalized', 'vehicle-broken-into-or-stolen'].includes(ans?.eventType?.value)",
        id="wasVehicleGlassDamaged",
        type=ELEMENT.YES_OR_NO,
        label="Was any of your vehicle's glass damaged?",
        description="Select whether the vehicle's glass was damaged."
    ),
    Question(
        dependsOn="ans => ['collision', 'injured-as-pedestrian', 'injured-a-pedestrian'].includes(ans?.eventType?.value)",
        id="wereFatalities",
        type=ELEMENT.YES_OR_NO,
        label="Fatalities?",
        description="Indicate if any fatalities occurred during the event."
    ),
    Question(
        dependsOn="ans => ans?.eventType?.value == 'collision'",
        id="wereInjuries",
        type=ELEMENT.YES_OR_NO,
        label="Injuries?",
        description="Indicate if there were injuries (fatalities imply injuries)."
    ),
    Question(
        dependsOn="ans => ['collision', 'injured-a-pedestrian'].includes(ans?.eventType?.value)",
        id="numOtherVehicles",
        type=ELEMENT.NUMERIC,
        label="How many other vehicles were involved?",
        description="Provide the number of additional vehicles involved (as a string integer), or '0' if none."
    ),
    Question(
        dependsOn="ans => ans?.eventType?.value == 'injured-as-pedestrian'",
        id="injuredParty",
        type=ELEMENT.CHECKBOX,
        label="Insured (Injured Party)",
        description="Select the injured party that is also insured on the policy.",
        lovs=[
            LOV(
                value="driver-1",
                label="Billy BadDriver",
                description="Main driver on the account; select if the collision is described in first person."
            ),
            LOV(value="other", label="Other")]
    ),
    Question(
        dependsOn="ans => ans?.eventType?.value == 'injured-as-pedestrian'",
        id="vehicleDriverFirstName",
        type=ELEMENT.INPUT,
        label="Vehicle Driver's First Name",
        optional=True,
        description="Provide the first name of the external driver involved."
    ),
    Question(
        dependsOn="ans => ans?.eventType?.value == 'injured-as-pedestrian'",
        id="vehicleDriverLastName",
        type=ELEMENT.INPUT,
        label="Vehicle Driver's Last Name",
        optional=True,
        description="Provide the last name of the external driver involved."
    ),
    Question(
        dependsOn="ans => ans?.eventType?.value == 'injured-as-pedestrian'",
        id="vehicleDriverPhoneNumber",
        type=ELEMENT.INPUT_PHONE,
        label="Vehicle Driver's Phone Number",
        optional=True,
        validate="phone => !/^\\d{3}-\\d{3}-\\d{4}$/.test(phone) ? 'Phone format should be xxx-xxx-xxxx' : false",
        description="Provide the phone number of the external driver involved."
    ),
    Question(
        dependsOn="ans => ['injured-a-pedestrian', 'damage-caused-by-weather', 'damage-caused-by-fire', 'damage-caused-by-animals', 'vehicle-vandalized', 'vehicle-broken-into-or-stolen', 'other-vehicle-damage'].includes(ans?.eventType?.value)",
        id="isVehicleDrivable",
        type=ELEMENT.YES_OR_NO_OR_UNKNOWN,
        label="Is the Vehicle Drivable?",
        description="Select whether the vehicle remains operable after the event."
    ),
]
