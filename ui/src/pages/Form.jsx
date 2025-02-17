import { AnimatePresence, motion } from "framer-motion";
import { useState, useEffect } from "react";
import Transition from "@/components/Transition";

const animate = {
    initial: { opacity: 0.01 },
    animate: { opacity: 1 },
    exit: { opacity: 0, },
    transition: { type: "spring", stiffness: 100, damping: 20 },
}


const Claim = () => {
    const [thinking, setThinking] = useState(true);
    useEffect(() => {
        const t = setTimeout(() => {
            setThinking(false)
        }, 3000)
        return () => clearTimeout(t)
    }, []);

    return (
        <Transition>
            <AnimatePresence mode="sync">
                {thinking ? <motion.div key="thinking" {...animate} className="absolute w-full">




                    <div className="flex justify-center ">
                        <div>
                            <h1 className="text-3xl text-center ">
                                Hang tight. We're working on it ...
                            </h1>
                        </div>
                    </div>


                    <div className="px-4 flex justify-center w-full mt-12" {...animate}>
                        <img src="/file-load.gif" className="w-[200px]" alt="file load" />
                    </div>





                </motion.div>
                    :
                    <motion.div key="not-thinking" className=" absolute w-full" {...animate}>
                        <div className="w-full flex flex-col items-center ">

                            <h1 className="text-3xl text-center max-w-[400px] w-fit">
                                We've filled out some answers as best as we can. <br />

                            </h1>
                            <p className="text-center mt-8 text-muted-foreground ">
                                Please double check the form to complete the claim process.
                            </p>
                            <p className="text-center mt-32 text-muted-foreground">
                                {`[ Some form to be built ]`}
                            </p>

                        </div>
                    </motion.div>
                }


            </AnimatePresence>

            <div>

            </div>

            {/* <div className="w-full flex justify-center mt-24">
            <button disabled={!value} className="btn" onClick={() => navigate("/claim/form")}>
                Next
            </button>
        </div> */}
        </Transition>

    )
}

export default Claim;