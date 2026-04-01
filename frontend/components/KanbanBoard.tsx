"use client";

import { useEffect, useState } from "react";
import { DragDropContext, Droppable, Draggable, DropResult } from "@hello-pangea/dnd";
import { api } from "@/lib/api";
import type { UseCase, UseCaseStatus } from "@/types";
import Link from "next/link";

const COLUMNS: { id: UseCaseStatus; label: string }[] = [
  { id: "new", label: "New" },
  { id: "evaluating", label: "Evaluating" },
  { id: "scored", label: "Scored" },
  { id: "business_case", label: "Business Case" },
  { id: "review", label: "In Review" },
  { id: "approved", label: "Approved" },
  { id: "archived", label: "Archived" },
];

const URGENCY_BADGE: Record<string, string> = {
  low: "bg-gray-100 text-gray-600",
  medium: "bg-yellow-100 text-yellow-700",
  high: "bg-orange-100 text-orange-700",
  critical: "bg-red-100 text-red-700",
};

export function KanbanBoard() {
  const [items, setItems] = useState<UseCase[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.useCases
      .list()
      .then(setItems)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const onDragEnd = async (result: DropResult) => {
    if (!result.destination) return;
    const newStatus = result.destination.droppableId as UseCaseStatus;
    const id = result.draggableId;
    setItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, status: newStatus } : item))
    );
    try {
      await api.useCases.updateStatus(id, newStatus);
    } catch {
      // revert on failure
      setItems((prev) =>
        prev.map((item) =>
          item.id === id
            ? {
                ...item,
                status: items.find((i) => i.id === id)?.status ?? item.status,
              }
            : item
        )
      );
    }
  };

  if (loading) return <div className="text-gray-500 text-sm">Loading...</div>;

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <div className="flex gap-3 overflow-x-auto pb-4">
        {COLUMNS.map((col) => {
          const colItems = items.filter((i) => i.status === col.id);
          return (
            <div key={col.id} className="flex-shrink-0 w-56">
              <div className="bg-gray-100 rounded-lg p-3">
                <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wide mb-3">
                  {col.label}{" "}
                  <span className="text-gray-400 font-normal">
                    ({colItems.length})
                  </span>
                </h3>
                <Droppable droppableId={col.id}>
                  {(provided) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      className="min-h-20 flex flex-col gap-2"
                    >
                      {colItems.map((item, index) => (
                        <Draggable
                          key={item.id}
                          draggableId={item.id}
                          index={index}
                        >
                          {(provided) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              className="bg-white rounded-md p-3 shadow-sm border border-gray-200 text-sm"
                            >
                              <Link
                                href={`/cases/${item.id}`}
                                className="font-medium text-gray-900 hover:text-blue-600 line-clamp-2 block mb-2"
                              >
                                {item.title}
                              </Link>
                              <div className="flex items-center justify-between">
                                <span
                                  className={`text-xs px-2 py-0.5 rounded-full ${
                                    URGENCY_BADGE[item.urgency]
                                  }`}
                                >
                                  {item.urgency}
                                </span>
                                {item.composite_score !== null && (
                                  <span className="text-xs text-gray-500 font-medium">
                                    {Math.round(item.composite_score)}
                                  </span>
                                )}
                              </div>
                            </div>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
              </div>
            </div>
          );
        })}
      </div>
    </DragDropContext>
  );
}
