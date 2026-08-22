import { BrowserRouter } from "react-router-dom";

import { ConnectivityBanner } from "@/pwa";
import { AppRoutes } from "@/routes/AppRoutes";

export default function App() {
    return (
        <>
            <ConnectivityBanner />
            <BrowserRouter>
                <AppRoutes />
            </BrowserRouter>
        </>
    );
}
