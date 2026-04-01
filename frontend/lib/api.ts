import type { UseCase, Evaluation, BusinessCase } from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail ?? "Request failed");
  }

  return res.json() as Promise<T>;
}

// Use Cases
export const api = {
  useCases: {
    list: () => apiFetch<UseCase[]>("/api/use-cases"),
    get: (id: string) => apiFetch<UseCase>(`/api/use-cases/${id}`),
    create: (data: Partial<UseCase>) =>
      apiFetch<UseCase>("/api/use-cases", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    updateStatus: (id: string, status: UseCase["status"]) =>
      apiFetch<UseCase>(`/api/use-cases/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      }),
  },

  evaluations: {
    list: (useCaseId: string) =>
      apiFetch<Evaluation[]>(`/api/use-cases/${useCaseId}/evaluations`),
    trigger: (useCaseId: string) =>
      apiFetch<{ message: string }>(`/api/use-cases/${useCaseId}/evaluate`, {
        method: "POST",
      }),
  },

  businessCases: {
    get: (useCaseId: string) =>
      apiFetch<BusinessCase>(`/api/use-cases/${useCaseId}/business-case`),
    generate: (useCaseId: string) =>
      apiFetch<{ message: string }>(
        `/api/use-cases/${useCaseId}/generate-business-case`,
        { method: "POST" }
      ),
    approve: (useCaseId: string) =>
      apiFetch<{ message: string }>(
        `/api/use-cases/${useCaseId}/business-case/approve`,
        { method: "POST" }
      ),
    reject: (useCaseId: string, reason: string) =>
      apiFetch<{ message: string }>(
        `/api/use-cases/${useCaseId}/business-case/reject`,
        { method: "POST", body: JSON.stringify({ reason }) }
      ),
  },
};
