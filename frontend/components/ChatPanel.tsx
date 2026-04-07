"use client";

import { useState } from "react";
import { CopilotChat } from "@copilotkit/react-ui";
import { useCopilotAction } from "@copilotkit/react-core";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

function ChatPanelInner() {
  const [isSaving, setIsSaving] = useState(false);
  const router = useRouter();

  useCopilotAction({
    name: "save_use_case",
    description: "Save the completed use case intake to the database once all fields are collected.",
    parameters: [
      { name: "title", type: "string", description: "Short descriptive title, max 8 words" },
      { name: "problem_statement", type: "string", description: "One clear sentence describing the problem" },
      { name: "stakeholders", type: "string[]", description: "List of stakeholder roles or groups" },
      { name: "available_data", type: "string", description: "Brief description of available data" },
      { name: "expected_outcome", type: "string", description: "One clear sentence describing success" },
      { name: "urgency", type: "string", description: "One of: low, medium, high, critical" },
    ],
    handler: async ({ title, problem_statement, stakeholders, available_data, expected_outcome, urgency }) => {
      try {
        setIsSaving(true);
        await api.useCases.create({
          title,
          description: "",
          problem_statement,
          stakeholders: Array.isArray(stakeholders) ? stakeholders : [stakeholders],
          available_data,
          expected_outcome,
          urgency: urgency as "low" | "medium" | "high" | "critical",
        });
        router.push("/pipeline");
        return "Use case saved successfully.";
      } catch (error) {
        const msg = error instanceof Error ? error.message : "Unknown error";
        return `Failed to save use case: ${msg}`;
      } finally {
        setIsSaving(false);
      }
    },
  });

  return (
    <div className="relative flex flex-col h-[600px] border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm [&_.copilotKitChat]:flex [&_.copilotKitChat]:flex-col [&_.copilotKitChat]:h-full [&_.copilotKitMessages]:flex-1 [&_.copilotKitMessages]:overflow-y-auto [&_.copilotKitInputContainer]:shrink-0">
      <CopilotChat
        labels={{
          title: "Use Case Intake",
          initial: "Hi! What AI use case do you have in mind?",
        }}
        imageUploadsEnabled={true}
        onCopy={(message) => {
          navigator.clipboard.writeText(message).catch(console.error);
        }}
      />
      {isSaving && (
        <div className="absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center rounded-xl z-50">
          <div className="bg-white border border-gray-200 px-6 py-4 rounded-lg text-sm font-medium text-gray-700 shadow-sm">
            Saving use case...
          </div>
        </div>
      )}
    </div>
  );
}

export function ChatPanel() {
  return <ChatPanelInner />;
}
