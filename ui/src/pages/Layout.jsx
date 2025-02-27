import Logo from "@/lib/assets/logo.svg"
import Avatar from "@/lib/assets/avatar.svg"
import Restart from "@/lib/assets/refresh.svg"
import Question from "@/lib/assets/question.svg"
import { useNavigate } from "react-router-dom"
import useStore from "@/lib/store";


const Layout = ({ children, ...props }) => {
    const navigate = useNavigate();
    const reset = useStore(state => state.reset)

    return (
        <div className="relative w-full h-screen grid grid-rows-[70px_1fr] overflow-x-hidden">
            <div />
            <nav className="fixed top-0 left-0 h-[70px] w-full border-b flex items-center px-8 bg-background z-50">
                <Logo className="h-[35px] cursor-pointer" onClick={() => navigate("/")} />

                <div className="absolute right-[calc(50%-25px)] -bottom-[25px] w-[50px] h-[50px] flex items-center justify-center rounded-full border p-3 bg-background pointer-events-none">
                    <Avatar className="h-[85%]" />
                </div>

                <div className="ml-auto [&>*]:ml-6">
                    <button className="cursor-pointer opacity-80 hover:opacity-100 transition-opacity" onClick={() => {reset(); navigate("/")}}>
                        <Restart className="h-[24px]" />
                    </button>
                    <button className="cursor-pointer opacity-80 hover:opacity-100 transition-opacity">
                        <Question className="h-[24px]" />
                    </button>

                </div>
            </nav>
            <main className="relative w-full h-full">
                {children}
            </main>
        </div>
    )

}

export default Layout