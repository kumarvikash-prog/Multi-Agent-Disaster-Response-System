/**
 * Typed fetch wrapper for the DisasterAI API.
 *
 * Rules:
 * - Always uses relative /api/v1 base path (Vite proxy in dev; Render rewrite in prod).
 * - credentials: "same-origin" so HTTP-only cookies are sent automatically.
 * - Adds X-Requested-With: fetch header on all non-GET requests (CSRF protection).
 * - Normalises the backend error envelope into a typed ApiError.
 *
 * Refresh-token single-flight logic is deferred to M1.1.
 */

const BASE = "/api/v1";

export interface ApiError {
  code: string;
  message: string;
  details: Record<string, unknown>;
  request_id: string;
}

export class ApiRequestError extends Error {
  constructor(
    public readonly status: number,
    public readonly error: ApiError,
  ) {
    super(error.message);
    this.name = "ApiRequestError";
  }
}

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

async function request<T>(
  method: HttpMethod,
  path: string,
  body?: unknown,
  extraHeaders?: Record<string, string>,
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...extraHeaders,
  };

  /* CSRF: every non-GET must carry this header (server returns 403 without it) */
  if (method !== "GET") {
    headers["X-Requested-With"] = "fetch";
  }

  const response = await fetch(`${BASE}${path}`, {
    method,
    credentials: "same-origin",
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const json = await response.json().catch(() => ({
      error: {
        code: "UNKNOWN_ERROR",
        message: `HTTP ${response.status}`,
        details: {},
        request_id: response.headers.get("x-request-id") ?? "",
      },
    }));
    throw new ApiRequestError(response.status, (json as { error: ApiError }).error);
  }

  /* 204 No Content — return undefined cast as T */
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const apiClient = {
  get: <T>(path: string) => request<T>("GET", path),
  post: <T>(path: string, body?: unknown) => request<T>("POST", path, body),
  put: <T>(path: string, body?: unknown) => request<T>("PUT", path, body),
  patch: <T>(path: string, body?: unknown) => request<T>("PATCH", path, body),
  delete: <T>(path: string) => request<T>("DELETE", path),
};
