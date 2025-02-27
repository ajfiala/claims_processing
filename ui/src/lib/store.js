import { create } from 'zustand';
import { getForm } from './api';
import { DUMMY_RES } from './constants';

const INIT = {
    description: "",
    questions: [],
    answers: {},
    isThinking: false,
    isDone: false
}

const useStore = create((set, get) => ({
    ...INIT,

    setDescription: (description) => set(state => ({ ...state, description })),


    generateForm: async () => {

        try {
            set(state => ({ ...state, isThinking: true }))

            // NOTE: Uncomment if API is offline
            // const res = DUMMY_RES

            const res = await getForm(get().description)


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
    },

    reset: () => {
        set(state => ({ ...state, ...INIT }))
    }
}))

export default useStore;