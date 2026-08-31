import { create } from "zustand";

interface Store {
    /** The nav bar should show after the user is verified
     * to have already logged in and signed in to their
     * account
     */
    shouldShow:boolean,
    setValues: (values: Partial<Store>) => void
}

export const useMobileNavBarStore = create<Store>((set) => ({
    shouldShow: false,
    setValues:(values)=>set(values)
}));