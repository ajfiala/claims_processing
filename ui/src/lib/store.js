import { create } from 'zustand';
import { getForm } from './api';
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
    isDone: false,
    scope: {
        carId: null
    },
}

const useStore = create((set, get) => ({
    ...INIT,

    setPhoto: (key, value) => set(state => ({ ...state, photos: {...state.photos, [key]: value}  })),

    setScope: (key, value) => set(state => ({ ...INIT, scope: {...INIT.scope, [key]: value}  })),

    reset: () => {
        set(state => ({ ...state, ...INIT }))
    }
}))

export default useStore;