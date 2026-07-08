import { Outlet } from "react-router-dom";
import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";
import { ToastContainer, Slide } from "react-toastify";

export function Layout() {
    return (
        <div className="grid grid-rows-[1fr_auto] h-screen">
            <Navbar />

            <main className="pt-navbar">
                <Outlet />
            </main>

            <Footer />

            <ToastContainer
                position="top-right"
                autoClose={5000}
                hideProgressBar={true}
                newestOnTop={false}
                closeOnClick
                rtl={false}
                pauseOnFocusLoss={false}
                draggable
                pauseOnHover
                theme="light"
                transition={Slide}
            />
        </div>
    );
}

