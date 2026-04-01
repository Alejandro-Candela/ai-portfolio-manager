import { Suspense } from "react";
import { PortfolioMatrix } from "@/components/PortfolioMatrix";

export default function PortfolioPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">
        Portfolio Matrix
      </h1>
      <p className="text-gray-600 mb-8 text-sm">
        X axis = Business Value · Y axis = Feasibility · Bubble size = Estimated
        Cost · Color = Risk Level
      </p>
      <Suspense fallback={<div className="text-gray-500">Loading portfolio...</div>}>
        <PortfolioMatrix />
      </Suspense>
    </div>
  );
}
