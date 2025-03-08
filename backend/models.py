from typing import Optional, List, Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator



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

# Element types for form fields
class ElementType(str, Enum):
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

# Define explicit dependency types
class DependencyType(str, Enum):
    NONE = "none"
    EVENT_TYPE = "event_type"
    EVENT_TYPE_AND_WHO_DRIVING = "event_type_and_who_driving"
    EVENT_TYPE_AND_INJURIES = "event_type_and_injuries"
    
# List of values for selectable options
class LOV(BaseModel):
    value: str
    label: str
    description: Optional[str] = None

# Model for each question in the claims flow
class Question(BaseModel):
    id: str
    type: ElementType
    label: Optional[str] = None
    description: Optional[str] = None
    optional: bool = False
    validate: Optional[str] = None
    lovs: Optional[List[LOV]] = None
    
    # This is the dependency expression needed by the frontend computed from our structured dependency data
    dependsOn: Optional[str] = None
    
    dependency_type: DependencyType = DependencyType.NONE
    depends_on_event_types: List[EventType] = Field(default_factory=list)
    depends_on_who_driving: Optional[str] = None  
    depends_on_injuries: Optional[bool] = None

    def model_post_init(self, __context):
        # Convert dependency_type and related fields to dependsOn string
        self.dependsOn = self._compute_depends_on()
    
    def _compute_depends_on(self) -> Optional[str]:
        """Convert our structured dependency data to the legacy dependsOn string format"""
        if self.dependency_type == DependencyType.NONE:
            return None
            
        elif self.dependency_type == DependencyType.EVENT_TYPE:
            event_types_str = ", ".join([f"'{et.value}'" for et in self.depends_on_event_types])
            return f"ans => [{event_types_str}].includes(ans?.eventType?.value)"
            
        elif self.dependency_type == DependencyType.EVENT_TYPE_AND_WHO_DRIVING:
            return f"ans => ans?.eventType?.value == '{self.depends_on_event_types[0].value}' && ans?.whoWasDriving?.value == '{self.depends_on_who_driving}'"
            
        elif self.dependency_type == DependencyType.EVENT_TYPE_AND_INJURIES:
            injuries_value = "true" if self.depends_on_injuries else "false"
            return f"ans => ans?.eventType?.value == '{self.depends_on_event_types[0].value}' && ans?.wereInjuries?.value == {injuries_value}"
            
        return None

# Request model for loss description
class LossDescription(BaseModel):
    description: str

class ImageLossDescription(LossDescription):
    image: Optional[str] = None  
    
class ImageAnalysisResponse(BaseModel):
    image_description: Optional[str] = None

# Classification response model
class ClassificationResponse(BaseModel):
    event_type: str

# Model for question answers
class QuestionAnswer(BaseModel):
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
    injuredParty: List[Optional[str]] = Field(default_factory=list)
    vehicleDriverFirstName: Optional[str] = None
    vehicleDriverLastName: Optional[str] = None
    vehicleDriverPhoneNumber: Optional[str] = None
    isVehicleDrivable: Optional[bool] = None
    insuredInjured: List[Optional[str]] = Field(default_factory=list)
    whoElseWasInjured: List[Optional[str]] = Field(default_factory=list)

# Define Pydantic model for list of relevant questions
class RelevantQuestionList(BaseModel):
    relevant_questions: List[Question]

##############################
# Prepare the question set
##############################

# Helper function to create a question with clear dependency structure
def create_question(
    id: str,
    type: ElementType,
    label: str,
    description: Optional[str] = None,
    optional: bool = False,
    validate: Optional[str] = None,
    lovs: Optional[List[LOV]] = None,
    dependency_type: DependencyType = DependencyType.NONE,
    depends_on_event_types: List[EventType] = None,
    depends_on_who_driving: Optional[str] = None,
    depends_on_injuries: Optional[bool] = None
) -> Question:
    """Helper function to create a question with clear dependency structure"""
    return Question(
        id=id,
        type=type,
        label=label,
        description=description,
        optional=optional,
        validate=validate,
        lovs=lovs,
        dependency_type=dependency_type,
        depends_on_event_types=depends_on_event_types or [],
        depends_on_who_driving=depends_on_who_driving,
        depends_on_injuries=depends_on_injuries
    )

# We only define one set of questions for an Auto policy
QUESTIONS = [
    create_question(
        id="eventType",
        type=ElementType.SELECT,
        label="Select Event",
        lovs=[
            LOV(value=EventType.TOWING_ONLY.value, label="Towing Only", description="Vehicle requires towing without additional damage."),
            LOV(value=EventType.COLLISION.value, label="Collision", description="Involvement in a vehicular accident."),
            LOV(value=EventType.INJURED_AS_PEDESTRIAN.value, label="Injured as Pedestrian/Bicyclist", description="Policyholder was injured while on foot or cycling."),
            LOV(value=EventType.INJURED_A_PEDESTRIAN.value, label="Injured a Pedestrian/Bicyclist", description="Policyholder's vehicle injured a pedestrian or cyclist."),
            LOV(value=EventType.DAMAGE_BY_WEATHER.value, label="Damage Caused by Weather", description="Vehicle damaged due to weather events such as flooding or hail."),
            LOV(value=EventType.DAMAGE_BY_FIRE.value, label="Damage Caused by Fire", description="Vehicle damaged due to fire."),
            LOV(value=EventType.DAMAGE_BY_ANIMALS.value, label="Damage Caused by Animals", description="Vehicle damaged due to an animal-related incident."),
            LOV(value=EventType.VEHICLE_VANDALIZED.value, label="Vehicle Vandalized", description="Vehicle intentionally damaged by a third party."),
            LOV(value=EventType.VEHICLE_BROKEN_INTO_OR_STOLEN.value, label="Vehicle Broken Into or Stolen", description="Vehicle was broken into or stolen."),
            LOV(value=EventType.OTHER_VEHICLE_DAMAGE.value, label="Other Vehicle Damage", description="Any vehicle damage that does not fit the above categories."),
        ],
    ),
    create_question(
        id="whichVehicleInvolved",
        type=ElementType.RADIO,
        label="Which of your vehicles was involved?",
        description="Relevant for collision, injured-a-pedestrian, damage caused by weather/fire/animals, vandalism, theft, or other damage claims.",
        dependency_type=DependencyType.EVENT_TYPE,
        depends_on_event_types=[
            EventType.COLLISION,
            EventType.INJURED_A_PEDESTRIAN,
            EventType.DAMAGE_BY_WEATHER,
            EventType.DAMAGE_BY_FIRE,
            EventType.DAMAGE_BY_ANIMALS,
            EventType.VEHICLE_VANDALIZED,
            EventType.VEHICLE_BROKEN_INTO_OR_STOLEN,
            EventType.OTHER_VEHICLE_DAMAGE
        ],
        lovs=[
            LOV(value="2023-bmw-x1", label="2023 BMW X1"),
            LOV(value="rental-car", label="Rental Car"),
            LOV(value="other", label="Other car not on policy"),
        ],
    ),
    create_question(
        id="whoWasDriving",
        type=ElementType.RADIO,
        label="Who was driving the vehicle?",
        description="Select the person driving during the event.",
        dependency_type=DependencyType.EVENT_TYPE,
        depends_on_event_types=[
            EventType.COLLISION,
            EventType.INJURED_A_PEDESTRIAN,
            EventType.DAMAGE_BY_WEATHER,
            EventType.DAMAGE_BY_FIRE,
            EventType.DAMAGE_BY_ANIMALS,
            EventType.VEHICLE_VANDALIZED,
            EventType.VEHICLE_BROKEN_INTO_OR_STOLEN
        ],
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
    create_question(
        id="otherDriverFirstName",
        type=ElementType.INPUT,
        label="Other Driver First Name",
        description="Provide the first name of the other driver if 'Other' was selected.",
        optional=True,
        dependency_type=DependencyType.EVENT_TYPE_AND_WHO_DRIVING,
        depends_on_event_types=[EventType.COLLISION],
        depends_on_who_driving="other"
    ),
    create_question(
        id="otherDriverLastName",
        type=ElementType.INPUT,
        label="Other Driver Last Name",
        description="Provide the last name of the other driver if 'Other' was selected.",
        optional=True,
        dependency_type=DependencyType.EVENT_TYPE_AND_WHO_DRIVING,
        depends_on_event_types=[EventType.COLLISION],
        depends_on_who_driving="other"
    ),
    create_question(
        id="otherDriverPhoneNumber",
        type=ElementType.INPUT_PHONE,
        label="Other Driver Phone Number",
        description="Provide the phone number of the other driver if applicable.",
        optional=True,
        validate="phone => !/^\\d{3}-\\d{3}-\\d{4}$/.test(phone) ? 'Phone format should be xxx-xxx-xxxx' : false",
        dependency_type=DependencyType.EVENT_TYPE_AND_WHO_DRIVING,
        depends_on_event_types=[EventType.COLLISION],
        depends_on_who_driving="other"
    ),
    create_question(
        id="wasVehicleTowed",
        type=ElementType.YES_OR_NO,
        label="Was your vehicle towed?",
        description="Select whether the vehicle required towing.",
        dependency_type=DependencyType.EVENT_TYPE,
        depends_on_event_types=[
            EventType.COLLISION,
            EventType.INJURED_A_PEDESTRIAN,
            EventType.DAMAGE_BY_WEATHER,
            EventType.DAMAGE_BY_FIRE,
            EventType.DAMAGE_BY_ANIMALS,
            EventType.VEHICLE_VANDALIZED,
            EventType.VEHICLE_BROKEN_INTO_OR_STOLEN
        ],
    ),
    create_question(
        id="wasVehicleGlassDamaged",
        type=ElementType.YES_OR_NO,
        label="Was any of your vehicle's glass damaged?",
        description="Select whether the vehicle's glass was damaged.",
        dependency_type=DependencyType.EVENT_TYPE,
        depends_on_event_types=[
            EventType.COLLISION,
            EventType.INJURED_A_PEDESTRIAN,
            EventType.DAMAGE_BY_WEATHER,
            EventType.DAMAGE_BY_FIRE,
            EventType.DAMAGE_BY_ANIMALS,
            EventType.VEHICLE_VANDALIZED,
            EventType.VEHICLE_BROKEN_INTO_OR_STOLEN
        ],
    ),
    create_question(
        id="wereFatalities",
        type=ElementType.YES_OR_NO,
        label="Fatalities?",
        description="Indicate if any fatalities occurred during the event.",
        dependency_type=DependencyType.EVENT_TYPE,
        depends_on_event_types=[
            EventType.COLLISION,
            EventType.INJURED_AS_PEDESTRIAN,
            EventType.INJURED_A_PEDESTRIAN
        ],
    ),
    create_question(
        id="wereInjuries",
        type=ElementType.YES_OR_NO,
        label="Injuries?",
        description="Indicate if there were injuries (fatalities imply injuries).",
        dependency_type=DependencyType.EVENT_TYPE,
        depends_on_event_types=[EventType.COLLISION],
    ),
    create_question(
        id="insuredInjured",
        type=ElementType.CHECKBOX,
        label="Who On The Policy Was Injured?",
        description="Only relevant for collision claims where there was an injury. Select which insured party was injured as a result of the collision",
        dependency_type=DependencyType.EVENT_TYPE_AND_INJURIES,
        depends_on_event_types=[EventType.COLLISION],
        depends_on_injuries=True,
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
    create_question(
        id="whoElseWasInjured",
        type=ElementType.CHECKBOX,
        label="Was Anyone Else Injured?",
        description="Only relevant for collision claims where there was an injury. Select one of the options pertaining on additional parties who were injured as a result of the collision",
        optional=True,
        dependency_type=DependencyType.EVENT_TYPE_AND_INJURIES,
        depends_on_event_types=[EventType.COLLISION],
        depends_on_injuries=True,
        lovs=[
            LOV(value="one-or-more-passengers-in-my-vehicle", label="One Or More Passengers In My Vehicle"),
            LOV(value="driver-of-another-vehicle", label="Driver Of Another Vehicle"),
            LOV(value="one-or-more-passengers-in-another-vehicle", label="One Or More Passengers In Another Vehicle"),
            LOV(value="one-or-more-pedestrians", label="One Or More Pedestrians"),
        ]
    ),
    create_question(
        id="numOtherVehicles",
        type=ElementType.NUMERIC,
        label="How many other vehicles were involved?",
        description="Provide the number of additional vehicles involved (as a string integer), or '0' if none.",
        dependency_type=DependencyType.EVENT_TYPE,
        depends_on_event_types=[
            EventType.COLLISION,
            EventType.INJURED_A_PEDESTRIAN
        ],
    ),
    create_question(
        id="injuredParty",
        type=ElementType.CHECKBOX,
        label="Insured (Injured Party)",
        description="Select the injured party that is also insured on the policy.",
        dependency_type=DependencyType.EVENT_TYPE,
        depends_on_event_types=[EventType.INJURED_AS_PEDESTRIAN],
        lovs=[
            LOV(
                value="driver-1",
                label="Billy BadDriver",
                description="Main driver on the account; select if the collision is described in first person."
            ),
            LOV(value="other", label="Other")
        ],
    ),
    create_question(
        id="vehicleDriverFirstName",
        type=ElementType.INPUT,
        label="Vehicle Driver's First Name",
        description="Provide the first name of the external driver involved.",
        optional=True,
        dependency_type=DependencyType.EVENT_TYPE,
        depends_on_event_types=[EventType.INJURED_AS_PEDESTRIAN],
    ),
    create_question(
        id="vehicleDriverLastName",
        type=ElementType.INPUT,
        label="Vehicle Driver's Last Name",
        description="Provide the last name of the external driver involved.",
        optional=True,
        dependency_type=DependencyType.EVENT_TYPE,
        depends_on_event_types=[EventType.INJURED_AS_PEDESTRIAN],
    ),
    create_question(
        id="vehicleDriverPhoneNumber",
        type=ElementType.INPUT_PHONE,
        label="Vehicle Driver's Phone Number",
        description="Provide the phone number of the external driver involved.",
        optional=True,
        validate="phone => !/^\\d{3}-\\d{3}-\\d{4}$/.test(phone) ? 'Phone format should be xxx-xxx-xxxx' : false",
        dependency_type=DependencyType.EVENT_TYPE,
        depends_on_event_types=[EventType.INJURED_AS_PEDESTRIAN],
    ),
    create_question(
        id="isVehicleDrivable",
        type=ElementType.YES_OR_NO_OR_UNKNOWN,
        label="Is the Vehicle Drivable?",
        description="Select whether the vehicle remains operable after the event.",
        dependency_type=DependencyType.EVENT_TYPE,
        depends_on_event_types=[
            EventType.INJURED_A_PEDESTRIAN,
            EventType.DAMAGE_BY_WEATHER,
            EventType.DAMAGE_BY_FIRE,
            EventType.DAMAGE_BY_ANIMALS,
            EventType.VEHICLE_VANDALIZED,
            EventType.VEHICLE_BROKEN_INTO_OR_STOLEN,
            EventType.OTHER_VEHICLE_DAMAGE
        ],
    ),
]

# Helper functions to find relevant questions by event type
def get_relevant_questions(event_type: EventType) -> List[Question]:
    """Get questions that are relevant for a given event type"""
    return [
        q for q in QUESTIONS 
        if q.dependency_type == DependencyType.NONE or
           (q.dependency_type == DependencyType.EVENT_TYPE and 
            event_type in q.depends_on_event_types) or
           (q.dependency_type in [DependencyType.EVENT_TYPE_AND_WHO_DRIVING, DependencyType.EVENT_TYPE_AND_INJURIES] and
            event_type in q.depends_on_event_types)
    ]

def get_question_by_id(question_id: str) -> Optional[Question]:
    """Get a question by its ID"""
    for q in QUESTIONS:
        if q.id == question_id:
            return q
    return None