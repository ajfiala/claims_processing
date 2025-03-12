import { createElement, cloneElement } from 'react';
import { useLocation, useOutlet } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import Layout from './pages/Layout';

import Home from './pages/Home';
import Upload from './pages/Upload';

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
            title="Upload Front Photo"
            description="Please take 3 steps back and take a photo of the Front bumper"
            orientation="f"
            next="/claim/upload/2"
             />)
    },
    {
        path: "/claim/upload/2",
        element: createElement(() => <Upload
            title="Upload Front Left Photo"
            description="Please take 3 steps back and take a photo of the Front Left bumper"
            orientation="fl"
            next="/claim/upload/3" />)
    },
    {
        path: "/claim/upload/3",
        element: createElement(() => <Upload
            title="Upload Left Photo"
            description="Please take 3 steps back and take a photo of the Left bumper"
            orientation="l"
            next="/claim/upload/4" />)
    },
    {
        path: "/claim/upload/4",
        element: createElement(() => <Upload
            title="Upload Back Left Photo"
            description="Please take 3 steps back and take a photo of the Back Left bumper"
            orientation="bl"
            next="/claim/upload/5" />)
    },
    {
        path: "/claim/upload/5",
        element: createElement(() => <Upload
            title="Upload Back Photo"
            description="Please take 3 steps back and take a photo of the Back bumper"
            orientation="b"
            next="/claim/upload/6" />)
    },
    {
        path: "/claim/upload/6",
        element: createElement(() => <Upload
            title="Upload Back Right Photo"
            description="Please take 3 steps back and take a photo of the Back Right bumper"
            orientation="br"
            next="/claim/upload/7" />)
    },
    {
        path: "/claim/upload/7",
        element: createElement(() => <Upload
            title="Upload Right Photo"
            description="Please take 3 steps back and take a photo of the Right bumper"
            orientation="r"
            next="/claim/upload/8" />)
    },
    {
        path: "/claim/upload/8",
        element: createElement(() => <Upload
            title="Upload Front Right Photo"
            description="Please take 3 steps back and take a photo of the Front Right bumper"
            orientation="fr"
            next="" />)
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