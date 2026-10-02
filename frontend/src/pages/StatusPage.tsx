import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../shared/api/client";

interface HealthResponse {
  status: string;
  timestamp: string;
}

function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: () => apiClient.get<HealthResponse>("/health"),
    retry: 2,
  });
}

export function StatusPage() {
  const { data, isLoading, isError, error } = useHealth();

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "system-ui, sans-serif",
        background: "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
        color: "#f1f5f9",
        gap: "1.5rem",
        padding: "2rem",
      }}
    >
      <h1 style={{ fontSize: "2rem", fontWeight: 700, margin: 0 }}>🚨 DisasterAI</h1>

      <div
        style={{
          background: "rgba(255,255,255,0.05)",
          border: "1px solid rgba(255,255,255,0.1)",
          borderRadius: "1rem",
          padding: "2rem 3rem",
          textAlign: "center",
          minWidth: "320px",
        }}
      >
        <p style={{ margin: "0 0 0.5rem", fontSize: "0.9rem", color: "#94a3b8" }}>Backend Status</p>

        {isLoading && (
          <p style={{ color: "#facc15", fontSize: "1.2rem", fontWeight: 600 }}>⏳ Connecting…</p>
        )}

        {isError && (
          <>
            <p style={{ color: "#f87171", fontSize: "1.2rem", fontWeight: 600 }}>❌ Offline</p>
            <p style={{ color: "#94a3b8", fontSize: "0.8rem", marginTop: "0.5rem" }}>
              {error instanceof Error ? error.message : "Backend unreachable"}
            </p>
          </>
        )}

        {data && (
          <>
            <p style={{ color: "#4ade80", fontSize: "1.2rem", fontWeight: 600 }}>
              ✅ {data.status.toUpperCase()}
            </p>
            <p style={{ color: "#94a3b8", fontSize: "0.8rem", marginTop: "0.5rem" }}>
              {new Date(data.timestamp).toLocaleString()}
            </p>
          </>
        )}
      </div>

      <p style={{ color: "#475569", fontSize: "0.8rem" }}>Phase 0 — Scaffolding Complete</p>
    </main>
  );
}
