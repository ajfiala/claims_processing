import { createElement, cloneElement } from 'react';
import { useLocation, useOutlet } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import Layout from './pages/Layout'
import Home from './pages/Home'
import Claim from './pages/Claim'

// TODO: Code split if app grows too big
// const Home = lazy(() => import('./pages/Home'));

function App() {
    return (
        <Layout>
            <Outlet />
        </Layout>
    )
}

export const PATHS = [
    {
        path: "/",
        element: createElement(Home)
    },
    {
        path: "/claim", //TODO ?description="jdjdjndf"
        element: createElement(Claim)
    }
]

const Outlet = () => {
    const location = useLocation();
    const element = useOutlet();

    return (
        <AnimatePresence mode="sync" initial={false}>
            {element && cloneElement(element, { key: location.pathname })}
        </AnimatePresence>
    );
};


export default App
