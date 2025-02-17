import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';

const INIT = {
    description: ""
}

const useStore = create(immer((set, get) => ({
    ...INIT,
})))

export default useStore;