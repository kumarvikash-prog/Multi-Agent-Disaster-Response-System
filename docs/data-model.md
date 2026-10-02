# Data Model — DisasterAI

## Conventions

- UUID primary keys (`gen_random_uuid()`).
- `created_at` / `updated_at` as `TIMESTAMP WITH TIME ZONE` defaulting to `NOW()`.
- Enums stored as `VARCHAR` with `CHECK` constraints (easier to evolve than native Postgres enums).
- All names in `snake_case`.

## Tables

### users
| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| name | varchar(100) | not null |
| email | varchar(254) | not null; unique index on `lower(email)` |
| password_hash | text | not null |
| role | varchar(20) | `CITIZEN` \| `AUTHORITY`; default CITIZEN |
| is_active | boolean | default true |
| created_at, updated_at | timestamptz | |

### refresh_tokens
| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| user_id | uuid FK users | indexed |
| token_hash | char(64) | SHA-256 of the opaque token; unique |
| expires_at | timestamptz | now + 7 days |
| revoked_at | timestamptz null | set on logout |
| created_at | timestamptz | |

### incidents
| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| code | varchar(16) unique | `INC-` + zero-padded sequence |
| status | varchar(24) | SUBMITTED / ANALYZING / PENDING_REVIEW / DISPATCHED / RESOLVED / REJECTED |
| hazard_types | text[] | HazardType values; may be empty before analysis |
| latitude, longitude | double precision | CHECK ranges |
| location_text | varchar(300) null | landmark / free text |
| people_count | integer null | null = unknown; CHECK ≥ 0 and ≤ 100000 |
| summary | varchar(500) null | AI summary |
| urgency | varchar(10) null | LOW / MEDIUM / HIGH / CRITICAL |
| risk_flags | text[] | from analysis, editable |
| required_resources | jsonb | `{ambulance, fire_truck, rescue_team, medical_team}` |
| priority_score | smallint null | 0–100 |
| priority_level | varchar(10) null | computed |
| priority_override_level | varchar(10) null | authority override |
| priority_override_reason | varchar(300) null | |
| needs_manual_review | boolean | true when analysis failed |
| analysis_attempts | smallint | default 0 |
| destination_hospital_id | uuid FK null | set on approval |
| reject_reason | varchar(300) null | |
| resolution_note | varchar(500) null | |
| reviewed_by | uuid FK users null | authority |
| dispatched_at, resolved_at, rejected_at | timestamptz null | |
| version | integer | optimistic lock; +1 on every change |
| created_at, updated_at | timestamptz | |

Indexes: `(status, priority_score DESC, created_at)`, `(created_at)`.

### reports
| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| incident_id | uuid FK incidents | indexed |
| user_id | uuid FK users | indexed with `created_at` |
| description | text | 10–2000 chars after trim |
| people_count | integer null | as typed by citizen |
| latitude, longitude | double precision | |
| location_text | varchar(300) null | |
| idempotency_key | uuid | unique `(user_id, idempotency_key)` |
| created_at | timestamptz | |

### ai_analyses
| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| incident_id | uuid FK | indexed |
| status | varchar(10) | SUCCESS \| FAILED |
| provider, model | varchar(50) | |
| prompt_version | varchar(20) | e.g. `analysis_v1` |
| input_snapshot | jsonb | text length, people_count, suspicious_input flag (not full text) |
| output | jsonb null | validated AnalysisOutput |
| error_code | varchar(40) null | TIMEOUT / RATE_LIMITED / INVALID_OUTPUT / CIRCUIT_OPEN |
| latency_ms | integer null | |
| created_at | timestamptz | |

### recommendations
| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| incident_id | uuid FK | indexed |
| status | varchar(12) | ACTIVE \| SUPERSEDED \| APPROVED |
| plan | jsonb | units, hospital, shortfall, warnings |
| requested | jsonb | required counts used |
| rationale | text | template-generated in Phase 1 |
| source | varchar(10) | AI \| MANUAL_EDIT |
| created_at | timestamptz | |

Partial unique index: **one ACTIVE recommendation per incident**.

### resources
| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| type | varchar(20) | AMBULANCE / FIRE_TRUCK / RESCUE_TEAM / MEDICAL_TEAM |
| call_sign | varchar(30) unique | e.g. `AMB-01` |
| home_base_name | varchar(100) | |
| home_latitude, home_longitude | double precision | |
| status | varchar(12) | AVAILABLE \| ASSIGNED |
| created_at, updated_at | timestamptz | |

Index: `(type, status)`.

### hospitals
| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| name | varchar(120) unique | |
| latitude, longitude | double precision | |
| total_beds, available_beds | integer | CHECK `0 ≤ available ≤ total` |
| icu_total, icu_available | integer | CHECK `0 ≤ icu_available ≤ icu_total` |
| updated_at | timestamptz | |
| updated_by | uuid FK users null | |

### assignments
| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| incident_id | uuid FK | indexed |
| resource_id | uuid FK | |
| status | varchar(10) | ACTIVE \| RELEASED |
| assigned_by | uuid FK users | |
| assigned_at | timestamptz | |
| released_at | timestamptz null | |

**Partial unique index on `(resource_id) WHERE status = 'ACTIVE'`** — prevents double-booking even if application code has a bug.

### audit_logs (append-only)
| Column | Type | Notes |
|---|---|---|
| id | bigserial PK | |
| occurred_at | timestamptz | default now() |
| actor_type | varchar(10) | USER \| AI \| SYSTEM |
| actor_id | uuid null | |
| action | varchar(40) | see audit actions below |
| entity_type | varchar(30) | |
| entity_id | uuid | |
| incident_id | uuid null | indexed; drives the timeline |
| details | jsonb | before/after, counts, reason (no secrets, no full report text) |

A database trigger raises an exception on `UPDATE` or `DELETE` of this table.

## Audit actions

`USER_REGISTERED`, `REPORT_SUBMITTED`, `ANALYSIS_STARTED`, `ANALYSIS_COMPLETED`, `ANALYSIS_FAILED`, `PRIORITY_COMPUTED`, `RECOMMENDATION_CREATED`, `INCIDENT_EDITED`, `PRIORITY_OVERRIDDEN`, `INCIDENT_APPROVED`, `UNITS_ASSIGNED`, `INCIDENT_REJECTED`, `INCIDENT_RESOLVED`, `UNITS_RELEASED`, `HOSPITAL_UPDATED`, `SWEEP_REQUEUED`.
