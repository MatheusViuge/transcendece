import { useState } from "react";
import { AboutTab } from "./tabs/AboutTab";
import { ContentTab } from "./tabs/ContentTab";
import { ReviewsTab } from "./tabs/ReviewsTab";
import { basedPathProtected } from "@/pages/Layout/PrivateRoute";
import { useLocation } from "react-router-dom";

export function CourseTabs() {
  const location = useLocation();
  const isProtectedRoute = basedPathProtected.some(path => location.pathname.startsWith(path));

  const [activeTab, setActiveTab] = useState<"about" | "content" | "reviews">(isProtectedRoute ? "content" : "about");

  return (
    <div className="flex flex-col w-full">
      
      {/* Container "Cápsula" Cinza */}
      <div className="inline-flex bg-neutral-100 p-1 rounded-full w-max mb-8">
        
        {/* Botão Sobre */}
        <button
          onClick={() => setActiveTab("about")}
          className={`cursor-pointer px-6 py-1.5 rounded-full text-sm font-medium transition-all ${
            activeTab === "about"
              ? "bg-white text-neutral-900 shadow-sm" // Ativo
              : "text-neutral-500 hover:text-neutral-900" // Inativo
          }`}
        >
          Sobre
        </button>

        {/* Botão Conteúdo */}
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

        {/* Botão Avaliações */}
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

      {/* Renderização do Conteúdo */}
      <div>
        {activeTab === "about" && <AboutTab />}
        {activeTab === "content" && <ContentTab />}
        {activeTab === "reviews" && <ReviewsTab />}
      </div>

    </div>
  );
}