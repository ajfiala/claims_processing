import { create } from 'zustand';
import { analyzeImages } from './api';
import { DUMMY_RES } from './constants';

const INIT = {
    photos: {
        f: null,
        fl: null,
        l: null,
        bl: null,
        b: null,
        br: null,
        r: null,
        fr: null
    },
    isThinking: false,
    scope: {
        policyId: null,
        namedInsured: "John Doe",
        make: "Honda",
        model: "Fit"
    },
    results: null,
}

const useStore = create((set, get) => ({
    ...INIT,

    setPhoto: (key, value) => set(state => ({ ...state, photos: {...state.photos, [key]: value}  })),

    setScope: (key, value) => set(state => ({ ...INIT, scope: {...INIT.scope, [key]: value}  })),

    analyze: async () => {
        const {f, fl, l, bl, b, br, r, fr} = get().photos
        const {namedInsured, make, model} = get().scope
        try{
            set(state => ({...state, isThinking: true}))
            const res = await analyzeImages(namedInsured, make, model, f, fl, l, bl, b, br, r, fr);
            console.log(res)
            set(state => ({...state, results: res}))
        }
        catch(e){
            console.error(e)
        }
        finally{
            set(state => ({...state, isThinking: false}))
        }
    },

    reset: () => {
        set(state => ({ ...state, ...INIT }))
    }
}))

export default useStore;