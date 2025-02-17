import { AnimatePresence, motion } from "framer-motion";
import React, { useState, useEffect, useMemo, useLayoutEffect } from "react";
import Transition from "@/components/Transition";
import useStore from "@/lib/store";
import { useShallow } from 'zustand/react/shallow';



import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/shadcn/select"

import { Label } from "@/components/shadcn/label"
import { RadioGroup, RadioGroupItem } from "@/components/shadcn/radio-group"
import { Input } from "@/components/shadcn/input";
import { useCallback } from "react";

const animate = {
    initial: { opacity: 0.01 },
    animate: { opacity: 1 },
    exit: { opacity: 0, },
    transition: { type: "spring", stiffness: 100, damping: 20 },
}


const Form = () => {

    const [generateForm, questions, isThinking] = useStore(useShallow(state => [state.generateForm, state.questions, state.isThinking]));
    const answers = useStore(state => state.answers)
    const setAnswer = useStore(state => state.setAnswer)
    useEffect(() => {
        generateForm()
    }, []);

    // const [answers, setAnswers] = useState(_answers)
    // useLayoutEffect(() => {
    //     setTimeout(() => setAnswers(_answers), 500)
    // }, [_answers])

    // const answer = useMemo((id) => answers[id].value, [answers])

    return (
        <Transition>
            <AnimatePresence mode="sync">
                {isThinking ? <motion.div key="thinking" {...animate} className="absolute w-full">




                    <div className="flex justify-center ">
                        <div>
                            <h1 className="text-3xl text-center ">
                                Hang tight. We're working on it ...
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

                            <h1 className="text-3xl text-center max-w-[500px] w-fit">
                                We've filled out some answers as best as we can. <br />

                            </h1>
                            <p className="text-center mt-8 text-muted-foreground ">
                                Please double check the form to complete the claim process.
                            </p>
                            <div className="flex flex-col gap-y-12 mt-12">
                                {questions.map(({ dependsOn, id, type, label, optional, validate, lovs }, idx) => {
                                    // console.log(`${dependsOn}`)
                                    // const fn = eval(`${dependsOn}`); 
                                    // console.log(fn(answers))
                                    console.log("VAL", answers[id].value)
                                    return (
                                        // dependsOn ? fn : 
                                        true && <div key={idx} className="">
                                            <p className="text-muted-foreground text-sm pb-4">
                                                {label}
                                            </p>
                                            {type === "select" &&
                                                <Select onValueChange={(value) => setAnswer(id, value)} value={answers[id].value}>
                                                    <SelectTrigger className="w-[500px] h-[60px]">
                                                        <SelectValue placeholder="Select" />
                                                    </SelectTrigger>
                                                    <SelectContent>
                                                        {lovs.map(({ value, label }, jdx) => (
                                                            <SelectItem key={jdx} value={value}>{label}</SelectItem>
                                                        ))}
                                                    </SelectContent>
                                                </Select>
                                            }

                                            {(type === "radio" || type === "yes-or-no" || type === "yes-or-no-or-unknown") &&
                                                <RadioGroup onValueChange={(value) => setAnswer(id, value)} value={answers[id].value}
                                                    className="flex flex-col space-y-1">


                                                    {
                                                        (() => 
                                                            type === "yes-or-no" ? 
                                                                [{ value: true, label: "Yes" }, { value: false, label: "No" }] 
                                                                : type === "yes-or-no-or-unknown" ?
                                                                [{ value: true, label: "Yes" }, { value: false, label: "No" }, { value: "unknown", label: "Unknown" }] 
                                                                :lovs
                                                        )().map(({ value, label }, jdx) => (
                                                            <div key={jdx} className="flex items-center space-x-2">
                                                                <RadioGroupItem value={value} id={id + value} />
                                                                <Label htmlFor={id + value}>{label}</Label>
                                                            </div>
                                                        ))}


                                                </RadioGroup>
                                            }


                                            {(type === "input" || type === "input-phone" || type === "numeric") &&
                                                <Input onChange={(value) => setAnswer(id, value)} value={answers[id].value === null ? "" :  answers[id].value} className="w-[500px] h-[60px]" {...(type === "numeric" && {type:"number"})} />

                                            }
                                        </div>
                                    )

                                })}
                            </div>

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

export default Form;