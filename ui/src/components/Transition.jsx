import { motion } from "framer-motion"
import { cn } from "../lib/utils"

const animate = {
    initial: { opacity: 0.01, x: 100 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -100 },
    transition: { type: "spring", stiffness: 120, damping: 20 },
}

const Transition = ({ children, className, ...props }) => {
    return (
        <>
            <motion.section {...animate} className={cn("absolute w-full h-full pt-16 min-h-[calc(100svh-70px)] px-2", className)} {...props}>
                {children}
            </motion.section>
        </>
    )
}

export default Transition;