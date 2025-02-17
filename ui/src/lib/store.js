import { create } from 'zustand';
import { getForm } from './api';
import { DUMMY_RES } from './constants';

const INIT = {
    description: "",
    questions: [],
    answers: {},
    // answers: {
    //     "eventType": {
    //       "value": "collision"
    //     },
    //     "whichVehicleInvolved": {
    //       "value": "2023-bmw-x1"
    //     },
    //     "whoWasDriving": {
    //       "value": "driver-1"
    //     },
    //     "otherDriverFirstName": {
    //       "value": null
    //     },
    //     "otherDriverLastName": {
    //       "value": null
    //     },
    //     "otherDriverPhoneNumber": {
    //       "value": null
    //     },
    //     "wasVehicleTowed": {
    //       "value": null
    //     },
    //     "wasVehicleGlassDamaged": {
    //       "value": true
    //     },
    //     "wereFatalities": {
    //       "value": false
    //     },
    //     "wereInjuries": {
    //       "value": true
    //     },
    //     "numOtherVehicles": {
    //       "value": "0"
    //     },
    //     "injuredParty": {
    //       "value": "driver-1"
    //     },
    //     "vehicleDriverFirstName": {
    //       "value": null
    //     },
    //     "vehicleDriverLastName": {
    //       "value": null
    //     },
    //     "vehicleDriverPhoneNumber": {
    //       "value": null
    //     },
    //     "isVehicleDrivable": {
    //       "value": false
    //     }
    //   },
    isThinking: false,
    isDone: false
}

const useStore = create((set, get) => ({
    ...INIT,

    setDescription: (description) => set(state => ({ ...state, description })),


    generateForm: async () => {

        try {
            set(state => ({ ...state, isThinking: true }))

            const res = DUMMY_RES

            // const res = await getForm(get().description)

            // console.log(res)


            set(state => ({ ...state, ...res, isDone: true }))
        }
        catch (e) {




        }
        finally {
            set(state => ({ ...state, isThinking: false }))
        }







    },

    setAnswer: (key, answer) => {
        set((state) => 
        ({ ...state,
            answers: {
                ...state.answers,
                [key]: {
                    ...state.answers[key],
                    value: answer
                }
            }})
        ) 
    },

    setAnswerRaw: (key, answer) => {
        set((state) => 
        ({ ...state,
            answers: {
                ...state.answers,
                [key]: answer
            }})
        ) 
    }
}))

export default useStore;