import type { ReactNode } from "react";
import { Outlet } from "react-router-dom";
import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";
import { ToastContainer, Slide } from "react-toastify";

export function Layout({ children }: { children?: ReactNode }) {
    return (
        <div className="flex min-h-screen flex-col overflow-x-clip">
            <Navbar />

            <main className="flex-1 pt-navbar">
                {children ?? <Outlet />}
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
