import { Suspense } from "react";
import { BusinessCaseViewer } from "@/components/BusinessCaseViewer";

interface Props {
  params: Promise<{ id: string }>;
}

export default async function CasePage({ params }: Props) {
  const { id } = await params;

  return (
    <Suspense fallback={<div className="text-gray-500">Loading case...</div>}>
      <BusinessCaseViewer id={id} />
    </Suspense>
  );
}
