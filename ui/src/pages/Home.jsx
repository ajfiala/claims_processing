import CarCareIcon from "@/lib/assets/car-care.svg"
import { Checkbox } from "@/components/shadcn/checkbox";
import { useState } from "react"
import { useNavigate } from "react-router-dom";
import Transition from "../components/Transition";
import useStore from "@/lib/store";

const Home = (props) => {
    const scope = useStore(state => state.scope)
    const setScope = useStore(state => state.setScope)

    const selected = scope?.policyId ?? null

    const navigate = useNavigate();

    return (
        <Transition>
            <div className="flex justify-center ">
                <div>
                    <h1 className="text-3xl text-center ">
                        Hello, I'm Mr. Rocket!<br />
                        Select a policy to report a claim.
                    </h1>
                </div>
            </div>
            <div className="w-full flex flex-col sm:flex-row justify-center mt-24 gap-12 px-2">
                {
                    [
                        { id: "honda-fit", label: "Honda Fit", Icon: CarCareIcon },
                        { id: "lexus-s30", label: "Lexus ES30", Icon: CarCareIcon },
                        { id: "mazda-cx30", label: "Mazda CX-30", Icon: CarCareIcon },
                    ].map(({ id, label, Icon }, idx) => (
                        <div data-selected={selected === id} key={idx} className="card"
                            onClick={() => selected === id ? setScope("policyId", null) : setScope("policyId", id)}
                        >
                            <div className="relative w-[40%] mt-[12%] flex justify-center">
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
            <div className="w-full flex justify-center py-24">
                <button disabled={!selected} className="btn"
                    onClick={() => navigate("/claim/upload/1")}>
                    Next
                </button>
            </div>
        </Transition>
    )
}

export default Home