import { useShallow } from "zustand/react/shallow";
import useStore from "@/lib/store";
import { motion, AnimatePresence } from "framer-motion";
import Transition from "@/components/Transition";
import { useMemo } from "react";
import SuccessIcon from "@/lib/assets/success.svg"
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";




const animate = {
    initial: { opacity: 0.01 },
    animate: { opacity: 1 },
    exit: { opacity: 0, },
    transition: { type: "spring", stiffness: 100, damping: 20 },
}



const Results = () => {

    const [results, analyze, isThinking] = useStore(useShallow((state) => [state.results, state.analyze, state.isThinking]))

    const isSuccess = useMemo(() => !!results, [results])

    const navigate = useNavigate()

    useEffect(() => {
        analyze()
    }, [])

    return (
        <Transition>
            <AnimatePresence mode="sync">
                {isThinking ?
                    <motion.div key="thinking" {...animate} className="absolute w-full">

                        <div className="flex justify-center ">
                            <div>
                                <h1 className="text-3xl text-center ">
                                    Validating form ...
                                </h1>
                            </div>
                        </div>


                        <div className="px-4 flex justify-center w-full mt-12" {...animate}>
                            <img src="/file-load.gif" className="w-[175px]" alt="file load" />
                        </div>
                    </motion.div>
                    :
                    <motion.div key="not-thinking" className=" absolute w-full pb-12" {...animate}>



                        <div className="flex justify-center ">
                            <div>
                                <h1 className="text-3xl text-center ">
                                    {isSuccess ? "Your Form is Valid" : "We Found the Following Issues"}
                                </h1>
                                <p className="text-muted-foreground mt-2 text-center">
                                    {isSuccess ? "Your form matches up with the rules you specified." : "Please check the issues and upload another form or tweak your rules."}
                                </p>
                            </div>
                        </div>
                        <div className="flex justify-center mt-24">
                            <div className=" flex flex-col items-center">




                                {!isSuccess ?
                                    <>

                                        Oops something went wrong
                                    </>
                                    :

                                    <>
                                    
                                    <SuccessIcon className="text-[limegreen] w-full max-w-[200px] mb-24 mt-4" />
                                    <div>

                                    
                                    {
                                        JSON.stringify(results)
                                    }
                                    </div>
                                    </>



                                }

                                <button className="btn btn-secondary mt-4 w-12 mx-auto"
                                    onClick={() => { setFile(null); navigate("/" + scope.id + "/upload") }}>
                                    Upload another
                                </button>



                            </div>

                        </div>




                    </motion.div>
                }


            </AnimatePresence>

        </Transition >
    )
}

export default Results;
