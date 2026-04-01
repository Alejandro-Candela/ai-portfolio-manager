import { ChatPanel } from "@/components/ChatPanel";

export default function IntakePage() {
  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">
        Submit a Use Case
      </h1>
      <p className="text-gray-600 mb-6 text-sm">
        Describe your AI idea conversationally. Our agent will guide you through
        the details we need to evaluate it.
      </p>
      <ChatPanel />
    </div>
  );
}
