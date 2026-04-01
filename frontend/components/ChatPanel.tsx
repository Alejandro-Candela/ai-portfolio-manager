"use client";

import { CopilotChat } from "@copilotkit/react-ui";

export function ChatPanel() {
  return (
    <div className="h-[600px] border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm">
      <CopilotChat
        instructions="You are an AI Portfolio Manager intake agent. Guide the user to describe their AI use case idea. Extract: problem description, stakeholders, available data, expected outcome, and urgency. Be conversational and friendly."
        labels={{
          title: "Use Case Intake Assistant",
          initial:
            "Hi! Tell me about the AI use case you have in mind. What problem are you trying to solve?",
        }}
      />
    </div>
  );
}
