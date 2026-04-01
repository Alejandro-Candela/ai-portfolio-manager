import { Suspense } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";

export default function PipelinePage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Pipeline</h1>
      <Suspense fallback={<div className="text-gray-500">Loading pipeline...</div>}>
        <KanbanBoard />
      </Suspense>
    </div>
  );
}
