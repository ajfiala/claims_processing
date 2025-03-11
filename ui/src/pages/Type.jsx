import HomeCareIcon from "@/lib/assets/home-care.svg"
import CarCareIcon from "@/lib/assets/car-care.svg"
import { Checkbox } from "@/components/shadcn/checkbox";
import { useState } from "react"
import { useNavigate } from "react-router-dom";
import Transition from "../components/Transition";

const Type = (props) => {
    const [selected, setSelected] = useState();
    const navigate = useNavigate()
    return (
        <Transition>
            <div className="flex justify-center ">
                <div>
                    <h1 className="text-3xl text-center ">
                        Hello, Bpom!<br />
                        Please select your claim type.
                    </h1>
                </div>
            </div>
            <div className="w-full flex justify-center mt-24 gap-x-12">
                {
                    [
                        { id: "auto", label: "Home Claim", Icon: HomeCareIcon },
                        { id: "home", label: "Auto Claim", Icon: CarCareIcon },
                    ].map(({ id, label, Icon }, idx) => (
                        <div data-selected={selected === id} key={idx} className="card"
                            onClick={() => selected === id ? setSelected(null) : setSelected(id)}
                        >
                            <div className="relative w-[40%] mt-[12%]">
                                <Icon data-selected={selected === id} className="data-[selected=true]:text-primary text-transparent transition-colors"/>
                            </div>
                            <h2 className="font-bold mt-4">
                                {label}
                            </h2>

                            <Checkbox className="mt-4 pointer-events-none" checked={selected === id} />

                        </div>
                    ))
                }
            </div>
            <div className="w-full flex justify-center mt-24">
                <button disabled={!selected} className="btn"
                    onClick={() => navigate("/claim/describe")}>
                    Next
                </button>
            </div>
        </Transition>
    )
}

export default Type