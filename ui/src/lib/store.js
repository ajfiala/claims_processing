import { create } from 'zustand';
import { getForm } from './api';
import { getFormWithImage } from './api';
import { DUMMY_RES } from './constants';

const INIT = {
    description: "",
    questions: [],
    answers: {},
    isThinking: false,
    isDone: false,
    imageFile: null,
    imageDescription: null
};

const useStore = create((set, get) => ({
    ...INIT,

    setDescription: (description) => set(state => ({ ...state, description })),
    
    setImageFile: (imageFile) => set(state => ({ ...state, imageFile })),

    generateForm: async () => {
        try {
            set(state => ({ ...state, isThinking: true }));
            
            let res;
            
            // If we have an image, use the image API endpoint
            if (get().imageFile) {
                // NOTE: Uncomment if API is offline
                // res = DUMMY_RES
                
                res = await getFormWithImage(get().description, get().imageFile);
            } else {
                // NOTE: Uncomment if API is offline
                // res = DUMMY_RES
                
                res = await getForm(get().description);
            }
            
            // Store the image description if available
            const imageDescription = res.image_description || null;
            
            set(state => ({ 
                ...state, 
                ...res, 
                imageDescription,
                isDone: true 
            }));
        }
        catch (e) {
            console.error("Error generating form:", e);
        }
        finally {
            set(state => ({ ...state, isThinking: false }));
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
        );
    },

    setAnswerRaw: (key, answer) => {
        set((state) => 
        ({ ...state,
            answers: {
                ...state.answers,
                [key]: answer
            }})
        );
    },

    reset: () => {
        set(state => ({ ...state, ...INIT }));
    }
}));

export default useStore;