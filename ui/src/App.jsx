import { createElement, cloneElement } from 'react';
import { useLocation, useOutlet } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import Layout from './pages/Layout';

import Home from './pages/Home';
import Upload from './pages/Upload';
import Results from './pages/Results';

function App() {
    return (
        <Layout>
            <Outlet />
        </Layout>
    );
}

export const PATHS = [
    {
        path: "/",
        element: createElement(Home)
    },
    {
        path: "/claim/upload/1",
        element: createElement(() => <Upload
            orientation="f"
            next="/claim/upload/2" />)
    },
    {
        path: "/claim/upload/2",
        element: createElement(() => <Upload
            orientation="fl"
            next="/claim/upload/3" />)
    },
    {
        path: "/claim/upload/3",
        element: createElement(() => <Upload
            orientation="l"
            next="/claim/upload/4" />)
    },
    {
        path: "/claim/upload/4",
        element: createElement(() => <Upload
            orientation="bl"
            next="/claim/upload/5" />)
    },
    {
        path: "/claim/upload/5",
        element: createElement(() => <Upload
            orientation="b"
            next="/claim/upload/6" />)
    },
    {
        path: "/claim/upload/6",
        element: createElement(() => <Upload
            orientation="br"
            next="/claim/upload/7" />)
    },
    {
        path: "/claim/upload/7",
        element: createElement(() => <Upload
            orientation="r"
            next="/claim/upload/8" />)
    },
    {
        path: "/claim/upload/8",
        element: createElement(() => <Upload
            orientation="fr"
            next="/results" />)
    },
    {
        path: "/results",
        element: createElement(Results)
    }
];

const Outlet = () => {
    const location = useLocation();
    const element = useOutlet();

    return (
        <AnimatePresence mode="sync" initial={false}>
            {element && cloneElement(element, { key: location.pathname })}
        </AnimatePresence>
    );
};

export default App;