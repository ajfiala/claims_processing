import { useMemo, useEffect } from "react";
import Restart from "@/lib/assets/refresh.svg"
import BackIcon from "@/lib/assets/chevron-left.svg"
import { useNavigate } from "react-router-dom"
import useStore from "@/lib/store";

import { useTranslation } from 'react-i18next';
import { motion } from "framer-motion";

const Layout = ({ children, ...props }) => {
    const navigate = useNavigate();
    const reset = useStore(state => state.reset);
    const scope = useStore(state => state.scope);

    // navigate home if you're fooling around on a page you shouldn't or we'll send Ton' to fix you up good
    useEffect(() => {
        if (!scope?.policyId) {
            navigate("/")
        }
    }, [navigate])


    return (
        <div className="relative w-full h-screen grid grid-rows-[70px_1fr] overflow-x-hidden">
            <div />
            <nav className="fixed top-0 left-0 h-[70px] w-full border-b flex items-center px-4 sm:px-8  bg-primary shadow-2xl dark:bg-background dark:shadow-none z-50">
                <img src="/logo.png" alt="logo" className="hidden sm:block h-[35px] cursor-pointer" onClick={() => navigate("/")} />

                <img src="/avatar.png" alt="avatar" className="absolute right-[calc(50%-25px)] -bottom-[calc(25px)] rounded-full border w-[50px] h-[50px] pointer-events-none" />

                <div className="sm:ml-auto text-background dark:text-foreground flex gap-x-2 sm:gap-x-4 w-full sm:w-fit">
                    <button className="cursor-pointer opacity-80 hover:opacity-100 transition-opacity" onClick={() => { reset(); navigate("/") }}>
                        <Restart className="h-[24px]" />
                    </button>
                    <div className="ml-auto sm:ml-0 flex gap-x-2">
                        <LanguageSelect />
                    </div>
                </div>
            </nav>
            <div className="hidden xs:block fixed top-0 left-0 w-full h-full pointer-events-none z-10">
                <button disabled={location.pathname === "/"} className="widget xs:p-4 sm:p-12 mt-[80px] pointer-events-auto disabled:opacity-0" onClick={() => navigate(-1)}>
                    <BackIcon />
                </button>
            </div>
            <main className="relative w-full h-full">
                {children}
            </main>
        </div>
    )

}

const LanguageSelect = () => {
    const { i18n } = useTranslation()
    const on = useMemo(() => i18n.language === "th")

    return (
        <button className="relative bg-muted dark:bg-muted-foreground w-[78px] h-[36px] rounded-full" onClick={() => i18n.language === "en" ? i18n.changeLanguage('th') : i18n.changeLanguage('en')}>
            <motion.div animate={{ x: on ? 0 : 34 }} className="absolute left-0 top-0 w-full h-full p-[2px]">
                <div className="w-[40px] h-full bg-primary dark:bg-background rounded-full" />
            </motion.div>
            <div className="absolute w-full h-full flex flex-row px-[13px] items-center justify-center top-0 ">
                <p data-selected={!on} className="text-[12px] data-[selected=true]:text-[black] transition-colors font-bold">
                    TH
                </p>
                <p data-selected={!!on} className="ml-auto text-[12px] data-[selected=true]:text-[black] transition-colors font-bold">
                    EN
                </p>
            </div>
        </button>
    )

}

export default Layout