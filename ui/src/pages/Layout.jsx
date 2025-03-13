
import Restart from "@/lib/assets/refresh.svg"
import Question from "@/lib/assets/question.svg"
import BackIcon from "@/lib/assets/chevron-left.svg"
import { useNavigate } from "react-router-dom"
import useStore from "@/lib/store";
import { Switch } from "@/components/shadcn/switch";
import { Label } from "@/components/shadcn/label";

import { useTranslation } from 'react-i18next';

const Layout = ({ children, ...props }) => {
    const navigate = useNavigate();
    const reset = useStore(state => state.reset)
    const { t, i18n } = useTranslation()


    return (
        <div className="relative w-full h-screen grid grid-rows-[70px_1fr] overflow-x-hidden">
            <div />
            <nav className="fixed top-0 left-0 h-[70px] w-full border-b flex items-center px-8  bg-primary shadow-2xl dark:bg-background dark:shadow-none z-50">
                <img src="/logo.png" alt="logo" className="hidden sm:block h-[35px] cursor-pointer" onClick={() => navigate("/")} />

                <img src="/avatar.png" alt="avatar" className="absolute right-[calc(50%-25px)] -bottom-[calc(25px)] rounded-full border w-[50px] h-[50px] pointer-events-none" />

                <div className="ml-auto [&>*]:ml-6 text-background dark:text-foreground flex flex-ol">
                    <button className="cursor-pointer opacity-80 hover:opacity-100 transition-opacity" onClick={() => { reset(); navigate("/") }}>
                        <Restart className="h-[24px]" />
                    </button>
                    <div className="flex items-center space-x-2 w-[60px]">
                        <Switch id="airplane-mode"
                            checked={i18n.language === "th"}
                            onCheckedChange={() => i18n.language === "en" ? i18n.changeLanguage('th') : i18n.changeLanguage('en')}
   />
                        <Label htmlFor="airplane-mode" className="uppercase">{i18n.language}</Label>
                    </div>
                    <button className="cursor-pointer opacity-80 hover:opacity-100 transition-opacity">
                        <Question className="h-[24px]" />
                    </button>

                </div>
            </nav>
            <div className="hidden sm:fixed w-full h-full pointer-events-none z-10">
                <button disabled={location.pathname === "/"} className="widget p-12 mt-[80px] pointer-events-auto disabled:opacity-0" onClick={() => navigate(-1)}>
                    <BackIcon />
                </button>
            </div>
            <main className="relative w-full h-full">
                {children}
            </main>
        </div>
    )

}

export default Layout