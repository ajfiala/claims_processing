export const DUMMY_RES = {
    "questions": [
      {
        "dependsOn": null,
        "id": "eventType",
        "type": "select",
        "description": null,
        "label": "Select Event",
        "optional": false,
        "validate": null,
        "lovs": [
          {
            "value": "towing-only",
            "label": "Towing Only",
            "description": "Vehicle requires towing without additional damage."
          },
          {
            "value": "collision",
            "label": "Collision",
            "description": "Involvement in a vehicular accident."
          },
          {
            "value": "injured-as-pedestrian",
            "label": "Injured as Pedestrian/Bicyclist",
            "description": "Policyholder was injured while on foot or cycling."
          },
          {
            "value": "injured-a-pedestrian",
            "label": "Injured a Pedestrian/Bicyclist",
            "description": "Policyholder’s vehicle injured a pedestrian or cyclist."
          },
          {
            "value": "damage-caused-by-weather",
            "label": "Damage Caused by Weather",
            "description": "Vehicle damaged due to weather events such as flooding or hail."
          },
          {
            "value": "damage-caused-by-fire",
            "label": "Damage Caused by Fire",
            "description": "Vehicle damaged due to fire."
          },
          {
            "value": "damage-caused-by-animals",
            "label": "Damage Caused by Animals",
            "description": "Vehicle damaged due to an animal-related incident."
          },
          {
            "value": "vehicle-vandalized",
            "label": "Vehicle Vandalized",
            "description": "Vehicle intentionally damaged by a third party."
          },
          {
            "value": "vehicle-broken-into-or-stolen",
            "label": "Vehicle Broken Into or Stolen",
            "description": "Vehicle was broken into or stolen."
          },
          {
            "value": "other-vehicle-damage",
            "label": "Other Vehicle Damage",
            "description": "Any vehicle damage that does not fit the above categories."
          }
        ]
      },
      {
        "dependsOn": "ans => ['collision', 'injured-a-pedestrian', 'damage-caused-by-weather', 'damage-caused-by-fire', 'damage-caused-by-animals', 'vehicle-vandalized', 'vehicle-broken-into-or-stolen', 'other-vehicle-damage'].includes(ans?.eventType?.value)",
        "id": "whichVehicleInvolved",
        "type": "radio",
        "description": "Relevant for collision, injured-a-pedestrian, damage caused by weather/fire/animals, vandalism, theft, or other damage claims.",
        "label": "Which of your vehicles was involved?",
        "optional": false,
        "validate": null,
        "lovs": [
          {
            "value": "2023-bmw-x1",
            "label": "2023 BMW X1",
            "description": null
          },
          {
            "value": "rental-car",
            "label": "Rental Car",
            "description": null
          },
          {
            "value": "other",
            "label": "Other car not on policy",
            "description": null
          }
        ]
      },
      {
        "dependsOn": "ans => ['collision', 'injured-a-pedestrian', 'damage-caused-by-weather', 'damage-caused-by-fire', 'damage-caused-by-animals', 'vehicle-vandalized', 'vehicle-broken-into-or-stolen'].includes(ans?.eventType?.value)",
        "id": "whoWasDriving",
        "type": "radio",
        "description": "Select the person driving during the event.",
        "label": "Who was driving the vehicle?",
        "optional": false,
        "validate": null,
        "lovs": [
          {
            "value": "driver-1",
            "label": "Billy BadDriver",
            "description": "Main driver on the account; select if the collision is described in first person."
          },
          {
            "value": "other",
            "label": "Other",
            "description": null
          },
          {
            "value": "not-driven-when-damage-occured",
            "label": "Vehicle was not being driven at the time of damage",
            "description": null
          }
        ]
      },
      {
        "dependsOn": "ans => ans?.eventType?.value == 'collision' && ans?.whoWasDriving?.value == 'other'",
        "id": "otherDriverFirstName",
        "type": "input",
        "description": "Provide the first name of the other driver if 'Other' was selected.",
        "label": "Other Driver First Name",
        "optional": true,
        "validate": null,
        "lovs": null
      },
      {
        "dependsOn": "ans => ans?.eventType?.value == 'collision' && ans?.whoWasDriving?.value == 'other'",
        "id": "otherDriverLastName",
        "type": "input",
        "description": "Provide the last name of the other driver if 'Other' was selected.",
        "label": "Other Driver Last Name",
        "optional": true,
        "validate": null,
        "lovs": null
      },
      {
        "dependsOn": "ans => ans?.eventType?.value == 'collision' && ans?.whoWasDriving?.value == 'other'",
        "id": "otherDriverPhoneNumber",
        "type": "input-phone",
        "description": "Provide the phone number of the other driver if applicable.",
        "label": "Other Driver Phone Number",
        "optional": true,
        "validate": "phone => !/^\\d{3}-\\d{3}-\\d{4}$/.test(phone) ? 'Phone format should be xxx-xxx-xxxx' : false",
        "lovs": null
      },
      {
        "dependsOn": "ans => ['collision', 'injured-a-pedestrian', 'damage-caused-by-weather', 'damage-caused-by-fire', 'damage-caused-by-animals', 'vehicle-vandalized', 'vehicle-broken-into-or-stolen'].includes(ans?.eventType?.value)",
        "id": "wasVehicleTowed",
        "type": "yes-or-no",
        "description": "Select whether the vehicle required towing.",
        "label": "Was your vehicle towed?",
        "optional": false,
        "validate": null,
        "lovs": null
      },
      {
        "dependsOn": "ans => ['collision', 'injured-a-pedestrian', 'damage-caused-by-weather', 'damage-caused-by-fire', 'damage-caused-by-animals', 'vehicle-vandalized', 'vehicle-broken-into-or-stolen'].includes(ans?.eventType?.value)",
        "id": "wasVehicleGlassDamaged",
        "type": "yes-or-no",
        "description": "Select whether the vehicle's glass was damaged.",
        "label": "Was any of your vehicle's glass damaged?",
        "optional": false,
        "validate": null,
        "lovs": null
      },
      {
        "dependsOn": "ans => ['collision', 'injured-as-pedestrian', 'injured-a-pedestrian'].includes(ans?.eventType?.value)",
        "id": "wereFatalities",
        "type": "yes-or-no",
        "description": "Indicate if any fatalities occurred during the event.",
        "label": "Fatalities?",
        "optional": false,
        "validate": null,
        "lovs": null
      },
      {
        "dependsOn": "ans => ans?.eventType?.value == 'collision'",
        "id": "wereInjuries",
        "type": "yes-or-no",
        "description": "Indicate if there were injuries (fatalities imply injuries).",
        "label": "Injuries?",
        "optional": false,
        "validate": null,
        "lovs": null
      },
      {
        "dependsOn": "ans => ['collision', 'injured-a-pedestrian'].includes(ans?.eventType?.value)",
        "id": "numOtherVehicles",
        "type": "numeric",
        "description": "Provide the number of additional vehicles involved (as a string integer), or '0' if none.",
        "label": "How many other vehicles were involved?",
        "optional": false,
        "validate": null,
        "lovs": null
      },
      {
        "dependsOn": "ans => ans?.eventType?.value == 'injured-as-pedestrian'",
        "id": "injuredParty",
        "type": "checkbox",
        "description": "Select the injured party that is also insured on the policy.",
        "label": "Insured (Injured Party)",
        "optional": false,
        "validate": null,
        "lovs": [
          {
            "value": "other",
            "label": "Other",
            "description": null
          }
        ]
      },
      {
        "dependsOn": "ans => ans?.eventType?.value == 'injured-as-pedestrian'",
        "id": "vehicleDriverFirstName",
        "type": "input",
        "description": "Provide the first name of the external driver involved.",
        "label": "Vehicle Driver's First Name",
        "optional": true,
        "validate": null,
        "lovs": null
      },
      {
        "dependsOn": "ans => ans?.eventType?.value == 'injured-as-pedestrian'",
        "id": "vehicleDriverLastName",
        "type": "input",
        "description": "Provide the last name of the external driver involved.",
        "label": "Vehicle Driver's Last Name",
        "optional": true,
        "validate": null,
        "lovs": null
      },
      {
        "dependsOn": "ans => ans?.eventType?.value == 'injured-as-pedestrian'",
        "id": "vehicleDriverPhoneNumber",
        "type": "input-phone",
        "description": "Provide the phone number of the external driver involved.",
        "label": "Vehicle Driver's Phone Number",
        "optional": true,
        "validate": "phone => !/^\\d{3}-\\d{3}-\\d{4}$/.test(phone) ? 'Phone format should be xxx-xxx-xxxx' : false",
        "lovs": null
      },
      {
        "dependsOn": "ans => ['injured-a-pedestrian', 'damage-caused-by-weather', 'damage-caused-by-fire', 'damage-caused-by-animals', 'vehicle-vandalized', 'vehicle-broken-into-or-stolen', 'other-vehicle-damage'].includes(ans?.eventType?.value)",
        "id": "isVehicleDrivable",
        "type": "yes-or-no-or-unknown",
        "description": "Select whether the vehicle remains operable after the event.",
        "label": "Is the Vehicle Drivable?",
        "optional": false,
        "validate": null,
        "lovs": null
      }
    ],
    "answers": {
      "eventType": {
        "value": "collision"
      },
      "whichVehicleInvolved": {
        "value": "2023-bmw-x1"
      },
      "whoWasDriving": {
        "value": "driver-1"
      },
      "otherDriverFirstName": {
        "value": null
      },
      "otherDriverLastName": {
        "value": null
      },
      "otherDriverPhoneNumber": {
        "value": null
      },
      "wasVehicleTowed": {
        "value": null
      },
      "wasVehicleGlassDamaged": {
        "value": true
      },
      "wereFatalities": {
        "value": false
      },
      "wereInjuries": {
        "value": true
      },
      "numOtherVehicles": {
        "value": "0"
      },
      "injuredParty": {
        "value": "driver-1"
      },
      "vehicleDriverFirstName": {
        "value": null
      },
      "vehicleDriverLastName": {
        "value": null
      },
      "vehicleDriverPhoneNumber": {
        "value": null
      },
      "isVehicleDrivable": {
        "value": false
      }
    }
  }