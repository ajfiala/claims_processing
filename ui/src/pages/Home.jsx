import { Textarea } from "@/components/shadcn/textarea";
import { useState } from "react"
import { useNavigate } from "react-router-dom";
import Transition from "../components/Transition";



const Home = (props) => {
    const [value, setValue] = useState("");
    const navigate = useNavigate()
    return (
        <Transition>
            <div className="flex justify-center ">
                <div>
                    <h1 className="text-3xl text-center ">
                        Hello, I'm Bpom!<br />
                        Please describe what happened.
                    </h1>
                </div>
            </div>
            <div className="px-4 flex justify-center w-full mt-12">
                <Textarea className="w-full sm:w-[600px] shadow-2xl min-h-[200px]" value={value} onChange={e => setValue(e.target.value)}/>
            </div>
            
            <div className="w-full flex justify-center mt-24">
                <button disabled={!value} className="bg-primary disabled:opacity-20 disabled:bg-gray-500 text-white h-[48px] px-16 rounded-md disabled:cursor-not-allowed cursor-pointer hover:opacity-70 disabled:translate-y-1.5 transition ease-[cubic-bezier(.17,.67,.56,.98)] duration-500 dark:shadow-2xl dark:border"
                    onClick={() => navigate("/claim")}>
                    Next
                </button>
            </div>
        </Transition>
    )
}

export default Home