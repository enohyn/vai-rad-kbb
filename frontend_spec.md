# Frontend Specification & API Handoff

> This document is the contract between the Django backend (`vai-rad-kbb`) and the future React/Next.js + TypeScript frontend (`vai-rad-kbf`). Feed this file to the frontend task. It is the single source of truth for endpoints, auth flow, request/response shapes, and suggested component structure.

## 1. Environment

- **Frontend stack:** Next.js (App Router) + React + TypeScript + Tailwind CSS.
- **State management:** Zustand (recommended) or `useContext` for auth + selected date.
- **HTTP client:** `axios` or native `fetch` wrapper; base URL from `NEXT_PUBLIC_API_URL`.
- **Backend base URL (dev):** `http://localhost:8000`
- **CORS:** backend allows `http://localhost:3000`.

## 2. Authentication Flow (JWT)

1. `POST /api/auth/register/` → `{ access, refresh, user }` (201) — or use this once to create the demo account.
2. `POST /api/auth/login/` with `{ email, password }` → `{ access, refresh }` (200).
3. Store `access` (memory / Zustand) and `refresh` (localStorage / httpOnly cookie).
4. Send `Authorization: Bearer <access>` on every protected request.
5. On 401, call `POST /api/auth/refresh/` with `{ refresh }` → new `{ access }`.
6. `POST /api/auth/logout/` with `{ refresh }` → blacklists the refresh token.
7. `GET /api/auth/me/` → current user profile (use on app load to validate session).

| Endpoint | Method | Auth | Body / Params | Success |
|---|---|---|---|---|
| `/api/auth/register/` | POST | – | `{ email, name, password, password2 }` | 201 `{ access, refresh, user }` |
| `/api/auth/login/` | POST | – | `{ email, password }` | 200 `{ access, refresh }` |
| `/api/auth/refresh/` | POST | – | `{ refresh }` | 200 `{ access }` |
| `/api/auth/logout/` | POST | Bearer | `{ refresh }` | 205 |
| `/api/auth/me/` | GET | Bearer | – | 200 `{ id, email, name }` |

**User type:**
```ts
interface User { id: number; email: string; name: string; }
interface TokenPair { access: string; refresh: string; }
```

## 3. Tasks (Kanban Board) — `/tasks`

### Data model
```ts
type TaskStatus = "todo" | "in_progress" | "done";
type TaskPriority = "low" | "medium" | "high";

interface Tag { id: number; name: string; color: string; }

interface Task {
  id: number;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  due_date: string;          // "YYYY-MM-DD"
  order: number;
  tags: Tag[];
}

interface TaskWrite {
  title: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date: string;          // "YYYY-MM-DD"
  order?: number;
  tag_ids?: number[];
}
```

### Endpoints
| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `/api/tags/` | GET, POST | Bearer | List/create tags |
| `/api/tags/{id}/` | GET, PUT, PATCH, DELETE | Bearer | CRUD a tag |
| `/api/tasks/?date=YYYY-MM-DD` | GET, POST | Bearer | List tasks for a date (filter) / create |
| `/api/tasks/{id}/` | GET, PUT, PATCH, DELETE | Bearer | CRUD a task |
| `/api/tasks/reorder/` | PATCH | Bearer | Bulk update status + order after drag |

**`PATCH /api/tasks/reorder/`** body:
```json
{ "items": [ { "id": 1, "status": "done", "order": 0 }, { "id": 2, "status": "in_progress", "order": 1 } ] }
```
Response: `200 { updated: <count> }`.

### Suggested components
- `<DateSelector/>` — shared reusable date picker (emits `YYYY-MM-DD`).
- `<Board date={...}/>` — fetches `/api/tasks/?date=` and renders 3 `<Column/>`s.
- `<Column status=... tasks=.../>` — drop target; uses `@dnd-kit/core` or `react-beautiful-dnd`.
- `<TaskCard task=.../>` — draggable; shows title, priority badge, due date, tags.
- `<TaskModal mode="create"|"edit"/>` — add/edit form.
- `useDateStore` (Zustand) — single source of truth for selected date.
- `useTaskStore` — caches tasks per date, invalidates on mutate.

### Edge cases
- No tasks for a date → empty column states.
- Creating a task with a different `due_date` than the selected date → it won't appear (filter by `due_date`).
- Optimistic drag: update local order, fire `reorder`, rollback on failure.

## 4. Annotations — `/annotate`

### Data model
```ts
interface AnnoImage {
  id: number;
  file: string;              // URL
  original_filename: string;
  uploaded_at: string;       // ISO8601
  annotations: Annotation[];
}

interface Annotation {
  id: number;
  image: number;             // image id
  label: string;
  points: number[][];        // normalized [[x,y],...], values 0..1
  color: string;             // hex e.g. "#ff0000"
}
```

### Endpoints
| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `/api/images/` | GET, POST(multipart) | Bearer | List images / upload (`file` field) |
| `/api/images/{id}/` | GET, DELETE | Bearer | Retrieve (with nested annotations) / delete |
| `/api/images/{image_id}/annotations/` | GET, POST | Bearer | List/create polygon on an image |
| `/api/images/{image_id}/annotations/{id}/` | GET, PATCH, DELETE | Bearer | Update/delete a specific polygon |

### Polygon coordinate convention
- `points` are **normalized 0–1** relative to image dimensions.
- To render: `x_px = points[i][0] * imageWidth`, `y_px = points[i][1] * imageHeight`.
- To save: divide pointer coordinates by rendered image width/height.
- Minimum 3 points per polygon (backend rejects fewer with 400).

### Suggested components / libraries
- `react-konva` (Canvas) or `fabric.js` for polygon drawing.
- `<Annotator/>` — loads current image, draws polygons, handles undo/remove.
- `<ImageCarousel/>` or scroll list — switch between uploaded images.
- Persist on `mouseup` (after closing polygon) via `POST /api/images/{id}/annotations/`.
- Remove a shape → `DELETE /api/images/{id}/annotations/{anno_id}/`.

## 5. Error contract
All errors use DRF's default shape:
```json
{ "field_name": ["message."], "non_field_errors": ["message."] }
```
HTTP status codes: `400` validation, `401` unauthenticated, `403` forbidden, `404` not found (also used for cross-user object access — no leakage), `405` method not allowed.

## 6. Demo credentials (after seed)
```
Email:    demo@example.com
Password: Demo@12345
```
Created via `python manage.py seed_demo_user`. Override with env `DEMO_EMAIL` / `DEMO_PASSWORD`.

## 7. Pages to build
| Route | Page | Primary backend |
|---|---|---|
| `/login` | Login | `/api/auth/login` |
| `/tasks` | Kanban board | `/api/tasks`, `/api/tasks/reorder/`, `/api/tags` |
| `/annotate` | Annotation tool | `/api/images`, `/api/images/{id}/annotations/` |

## 8. Deployment
- Frontend → Vercel (Next.js native). Set `NEXT_PUBLIC_API_URL` to the PythonAnywhere backend URL.
- Backend → PythonAnywhere (see backend README).