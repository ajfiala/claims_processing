import { createElement, cloneElement } from 'react';
import { useLocation, useOutlet } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import Layout from './pages/Layout'

import Type from './pages/Type'
import Describe from './pages/Describe'
import Form from './pages/Form'

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
        element: createElement(Type)
    },
    {
        path: "/claim/describe",
        element: createElement(Describe)
    },
    {
        path: "/claim/form", //TODO ?description="jdjdjndf"
        element: createElement(Form)
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
