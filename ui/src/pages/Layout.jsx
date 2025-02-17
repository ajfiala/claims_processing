
import Restart from "@/lib/assets/refresh.svg"
import Question from "@/lib/assets/question.svg"
import { useNavigate } from "react-router-dom"


const Layout = ({ children, ...props }) => {
    const navigate=useNavigate()
    
    return (
        <div className="relative w-full h-screen grid grid-rows-[70px_1fr] overflow-x-hidden">
            <div/>
            <nav className="fixed top-0 left-0 h-[70px] w-full border-b flex items-center px-8  bg-primary shadow-2xl dark:bg-background dark:shadow-none z-50">
                <img src="/logo.png" alt="logo" className=" h-[35px] cursor-pointer" onClick={() => navigate("/")} />

                 <img src="/avatar.png" alt="avatar" className="absolute right-[calc(50%-25px)] -bottom-[calc(25px)] rounded-full border w-[50px] h-[50px] pointer-events-none" />
   
                <div className="ml-auto [&>*]:ml-6 text-background dark:text-foreground">
                    <button className="cursor-pointer opacity-80 hover:opacity-100 transition-opacity">
                        <Restart className="h-[24px]"/>
                    </button>
                    <button className="cursor-pointer opacity-80 hover:opacity-100 transition-opacity">
                        <Question className="h-[24px]"/>
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