import { useState } from "react"
import { useNavigate } from "react-router-dom";
import Transition from "../components/Transition";



const Home = (props) => {
    const [selected, setSelected] = useState();
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
            
            <div className="w-full flex justify-center mt-24">
                <button disabled={!selected} className="bg-accent disabled:opacity-20 disabled:bg-gray-500 text-white h-[48px] px-16 rounded-md disabled:cursor-not-allowed cursor-pointer hover:opacity-70 disabled:translate-y-1.5 transition ease-[cubic-bezier(.17,.67,.56,.98)] duration-500"
                    onClick={() => navigate("/claim")}>
                    Next
                </button>
            </div>
        </Transition>
    )
}

export default Home