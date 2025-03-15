import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App, {PATHS} from './App.jsx'
import Providers from './lib/providers'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import './i18n';


const router = createBrowserRouter([
    {
        path: "/",
        element: <App />,
        children: PATHS
    },
]);

createRoot(document.getElementById('root')).render(

        <Providers>
            <RouterProvider router={router}/>
        </Providers>

)
