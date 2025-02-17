import { Button } from "@/components/shadcn/button";
import { Textarea } from "@/components/shadcn/textarea";
import { useState } from "react"
import { useNavigate } from "react-router-dom";
import useStore from "@/lib/store";
import { useShallow } from "zustand/react/shallow";
import Transition from "../components/Transition";



const Describe = (props) => {
    const [description, setDescription] = useStore(useShallow(state => [state.description, state.setDescription]));
    
    const navigate = useNavigate()
    return (
        <Transition>
            <div className="flex justify-center ">
                <div>
                    <h1 className="text-3xl text-center ">
                        Please describe what happened.
                    </h1>
                </div>
            </div>
            <div className="px-4 flex justify-center w-full mt-24">
                <Textarea placeholder="e.g: My car got stolen at Arby's while I went in to get ice cream" className="w-full sm:w-[600px] shadow-2xl min-h-[200px] border-[rgba(236,236,236,0.43)] dark:border"
                 value={description} onChange={e => setDescription(e.target.value)}/>
            </div>
            
            <div className="w-full flex justify-center mt-24">
                <button disabled={!description} className="btn" onClick={() => navigate("/claim/form")}>
                    Next
                </button>
            </div>
        </Transition>
    )
}

export default Describe