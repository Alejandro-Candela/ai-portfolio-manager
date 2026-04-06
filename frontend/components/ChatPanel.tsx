"use client";

import { CopilotChat } from "@copilotkit/react-ui";

export function ChatPanel() {
  return (
    <div className="flex flex-col h-[600px] border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm [&_.copilotKitChat]:flex [&_.copilotKitChat]:flex-col [&_.copilotKitChat]:h-full [&_.copilotKitMessages]:flex-1 [&_.copilotKitMessages]:overflow-y-auto [&_.copilotKitInputContainer]:shrink-0">
      <CopilotChat
        labels={{
          title: "Use Case Intake",
          initial: "Hi! What AI use case do you have in mind?",
        }}
      />
    </div>
  );
}
