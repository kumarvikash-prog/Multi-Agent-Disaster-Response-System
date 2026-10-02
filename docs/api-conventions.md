# API Conventions

## Base path

All endpoints are prefixed `/api/v1`.

## Encoding and casing

- Request/response bodies: **JSON**.
- Field names: **`snake_case`**.
- Enum values: **`UPPER_SNAKE_CASE`** strings.
- Timestamps: **ISO-8601 UTC** with trailing `Z` — e.g. `"2026-10-02T12:00:00Z"`.
- IDs: **UUID** strings — e.g. `"9f2c3d4e-1234-5678-abcd-ef0123456789"`.
- Incident codes: human-readable `INC-000001` format.

## Standard error envelope

Every non-2xx response uses this envelope:

```json
{
  "error": {
    "code": "UNITS_UNAVAILABLE",
    "message": "Some units were just assigned elsewhere.",
    "details": { "unit_ids": ["..."] },
    "request_id": "9f2c..."
  }
}
```

`request_id` matches the `X-Request-ID` response header. Use it when reporting bugs.

## HTTP status codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Created |
| 204 | No content (e.g. logout) |
| 400 | Malformed request |
| 401 | Not authenticated |
| 403 | Wrong role **or** missing CSRF header |
| 404 | Not found (also used to hide other citizens' data) |
| 409 | State conflict (duplicate, stale version, invalid transition) |
| 413 | Request body too large (> 100 KB) |
| 422 | Validation error (Pydantic) |
| 429 | Rate limited — includes `Retry-After` header |
| 500 | Unexpected server error |
| 503 | Dependency unavailable (e.g. database down) |

## CSRF protection

Every **non-GET** request must include:

```
X-Requested-With: fetch
```

Missing → `403 CSRF_HEADER_MISSING`.

This is enforced server-side. Frontend clients must always include this header.

## Pagination

Query params: `limit` (default 20, max 100) and `offset` (default 0).

Response shape:

```json
{
  "items": [...],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

## Idempotency

`POST /reports` requires an `Idempotency-Key: <uuid>` header. Generate a new UUID when the form opens. Submitting the same key from the same user returns the original result without creating a duplicate.

## Optimistic concurrency

Incident write operations accept `expected_version` (integer). Mismatch → `409 STALE_VERSION`.

## Versioning

Within `/v1`: only additive changes (new optional fields, new endpoints). Breaking changes require `/v2`.

## Security headers

Every API response includes:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: no-referrer
X-Request-ID: <uuid>
```
