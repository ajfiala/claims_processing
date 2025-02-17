import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App, {PATHS} from './App.jsx'
import Providers from './lib/providers'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'

const router = createBrowserRouter([
    {
        path: "/",
        element: <App />,
        children: PATHS
    },
]);

createRoot(document.getElementById('root')).render(
    <StrictMode>
        <Providers>
            <RouterProvider router={router}/>
        </Providers>
    </StrictMode>,
)
