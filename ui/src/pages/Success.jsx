import { AnimatePresence, motion } from "framer-motion";
import React, { useState, useEffect } from "react";
import Transition from "@/components/Transition";

import SuccessIcon from "@/lib/assets/success.svg"
import { useNavigate } from "react-router-dom";
import useStore from "@/lib/store";



const animate = {
    initial: { opacity: 0.01 },
    animate: { opacity: 1 },
    exit: { opacity: 0, },
    transition: { type: "spring", stiffness: 100, damping: 20 },
}


const SuccessPage = () => {
    const reset = useStore(state => state.reset)

    // Spoof loader
    const [isThinking, setIsThinking] = useState(true)
    useEffect(() => {
        const t = setTimeout(() => setIsThinking(false), 3000)
        return () => clearTimeout(t)
    }, [])

    const navigate = useNavigate();
    



    return (
        <Transition>
            <AnimatePresence mode="sync">
                {isThinking ? <motion.div key="thinking" {...animate} className="absolute w-full">




                    <div className="flex justify-center ">
                        <div>
                            <h1 className="text-3xl text-center ">
                                Submitting your claim ...
                            </h1>
                        </div>
                    </div>


                    <div className="px-4 flex justify-center w-full mt-12" {...animate}>
                        <img src="/file-load.gif" className="w-[175px]" alt="file load" />
                    </div>





                </motion.div>
                    :
                    <motion.div key="not-thinking" className=" absolute w-full" {...animate}>
                        <div className="w-full flex flex-col items-center ">
                            <div className=" pb-0">

                                <h1 className="text-3xl text-center max-w-[500px] w-fit">
                                    Your claim was submitted successfully <br />

                                </h1>
                                <p className="text-center mt-2 text-muted-foreground ">
                                    Check your email inbox for the latest notifications on your claim.
                                </p>
                            </div>
                            <SuccessIcon className="text-[limegreen] w-full max-w-[200px] mb-24 mt-24" />

                            <motion.div layout="preserve-aspect" className="w-full flex justify-center mt-4">
                                <button className="btn text-foreground bg-background border" onClick={() => {reset(); navigate("/")}}>
                                    Submit Another Claim
                                </button>
                            </motion.div>

                        </div>
                    </motion.div>
                }



            </AnimatePresence>




        </Transition>

    )
}

export default SuccessPage