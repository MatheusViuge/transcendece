import { useState } from "react";
import { useLocation } from "react-router-dom";
import { isProtectedPath } from "@/pages/Layout/protectedRoutes";
import { AboutTab } from "./tabs/AboutTab";
import { ContentTab } from "./tabs/ContentTab";
import { ReviewsTab } from "./tabs/ReviewsTab";

export function CourseTabs() {
  const location = useLocation();
  const isProtectedRoute = isProtectedPath(location.pathname);
  const [activeTab, setActiveTab] = useState<"about" | "content" | "reviews">(
    isProtectedRoute ? "content" : "about",
  );

  return (
    <div className="flex flex-col w-full">
      <div className="inline-flex bg-neutral-100 p-1 rounded-full w-max mb-8">
        <button
          onClick={() => setActiveTab("about")}
          className={`cursor-pointer px-6 py-1.5 rounded-full text-sm font-medium transition-all ${
            activeTab === "about"
              ? "bg-white text-neutral-900 shadow-sm"
              : "text-neutral-500 hover:text-neutral-900"
          }`}
        >
          Sobre
        </button>

        <button
          onClick={() => setActiveTab("content")}
          className={`cursor-pointer px-6 py-1.5 rounded-full text-sm font-medium transition-all ${
            activeTab === "content"
              ? "bg-white text-neutral-900 shadow-sm"
              : "text-neutral-500 hover:text-neutral-900"
          }`}
        >
          Conteúdo
        </button>

        <button
          onClick={() => setActiveTab("reviews")}
          className={`cursor-pointer px-6 py-1.5 rounded-full text-sm font-medium transition-all ${
            activeTab === "reviews"
              ? "bg-white text-neutral-900 shadow-sm"
              : "text-neutral-500 hover:text-neutral-900"
          }`}
        >
          Avaliações
        </button>
      </div>

      <div>
        {activeTab === "about" && <AboutTab />}
        {activeTab === "content" && <ContentTab />}
        {activeTab === "reviews" && <ReviewsTab />}
      </div>
    </div>
  );
}
