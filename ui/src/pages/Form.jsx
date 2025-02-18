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
import { Checkbox } from "@/components/shadcn/checkbox";

const animate = {
    initial: { opacity: 0.01 },
    animate: { opacity: 1 },
    exit: { opacity: 0, },
    transition: { type: "spring", stiffness: 100, damping: 20 },
}


const Form = () => {
    const answers = useStore(state => state.answers)
    const [generateForm, questions, isThinking] = useStore(useShallow(state => [state.generateForm, state.questions, state.isThinking]));
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
                            <div className="border-b pb-12">



                                <h1 className="text-3xl text-center max-w-[500px] w-fit">
                                    We've filled out some answers as best as we can. <br />

                                </h1>
                                <p className="text-center mt-8 text-muted-foreground ">
                                    Please double check the form to complete the claim process.
                                </p>
                            </div>
                            <div className="flex flex-col gap-y-12 mt-18 pb-24">
                                <AnimatePresence mode="popLayout">
                                    {questions.map((props, idx) => {
                                        const { dependsOn, id, type, label, optional, validate, lovs } = props

                                        const shouldRender = dependsOn ? eval(`${dependsOn}`)(answers) === true : true

                                        return (
                                            shouldRender &&
                                            <motion.div layout="preserve-aspect" key={idx + id} {...animate}>
                                                <p className="text-muted-foreground text-sm pb-4">
                                                    {label}
                                                </p>
                                                <Component {...props} />
                                            </motion.div>
                                        )

                                    })}
                                </AnimatePresence>
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

const Component = ({ dependsOn, id, type, label, optional, validate, lovs, ...props }) => {
    const answers = useStore(state => state.answers)
    const setAnswer = useStore(state => state.setAnswer)
    const setAnswerRaw = useStore(state => state.setAnswerRaw)

    const answer = useMemo(() => answers[id].value, [answers])

    return (
        // dependsOn ? fn : 
        <>
            {type === "select" &&
                <Select onValueChange={(value) => setAnswer(id, value)} value={answer}>
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
                <RadioGroup onValueChange={(value) => setAnswer(id, value)} value={answer}
                    className="flex flex-col space-y-1">


                    {
                        (() =>
                            type === "yes-or-no" ?
                                [{ value: true, label: "Yes" }, { value: false, label: "No" }]
                                : type === "yes-or-no-or-unknown" ?
                                    [{ value: true, label: "Yes" }, { value: false, label: "No" }, { value: "unknown", label: "Unknown" }]
                                    : lovs
                        )().map(({ value, label }, jdx) => (
                            <div key={jdx} className="flex items-center space-x-2">
                                <RadioGroupItem value={value} id={id + value} />
                                <Label htmlFor={id + value}>{label}</Label>
                            </div>
                        ))}


                </RadioGroup>
            }


            {(type === "input" || type === "input-phone" || type === "numeric") &&
                <Input onChange={(e) => setAnswer(id, e.target.value)} value={answer === null ? "" : answer} className="w-[500px] h-[60px]" {...(type === "numeric" && { type: "number" })} />

            }

            {type === "checkbox" &&
                <div className="flex flex-col space-y-4">
                    {lovs.map((lov, jdx) => {
                        const { value, label } = lov
                        return (

                            <div key={jdx} className="flex items-center space-x-2">

                                <Checkbox
                                    key={jdx}
                                    checked={answers[id] instanceof Array && answers[id].some(x => x.value == value)}
                                    onCheckedChange={() => {

                                        let checkedList = answers[id]
                                        console.log("cehcedk List:", checkedList)

                                        if (checkedList.findIndex(item => item.value === value) === -1) {
                                            checkedList.push(lov)
                                        }
                                        else {
                                            checkedList = checkedList.filter(item => item.value !== value);
                                        }
                                        console.log("after: ", checkedList)
                                        setAnswerRaw(id, checkedList)
                                    }}
                                />
                                <Label htmlFor={id + value}>{label}</Label>
                            </div>)

                    })}
                </div>
            }
        </>
    )

}


// function toggleObjectInArray(array, value) {
//     const index = array.findIndex(item => item.value === value);
//     if (index === -1) {
//         // Add if doesn't exist
//         return false;
//     } else {
//         // Remove if exists
//         return array.filter(item => item.value !== value);
//     }
// }


export default Form;