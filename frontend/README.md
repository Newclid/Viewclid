# Viewclid Frontend

Browser-based interface for constructing geometry problems, defining goals, submitting solver jobs to the backend, managing custom theorems, and displaying the resulting proof.

The frontend is intentionally framework-light: no UI framework, just TypeScript and direct DOM manipulation. Rendering is split between SVG (interactive construction) and Canvas (proof-step highlighting).

## Tech stack

| | |
|---|---|
| Language | TypeScript |
| Build tool | [Vite](https://vitejs.dev/) |
| UI | Vanilla DOM/SVG/Canvas — no framework |
| Testing | [Vitest](https://vitest.dev/) (unit/integration) + [Playwright](https://playwright.dev/) (e2e) |

## Features

* Interactive geometry workspace with pan and zoom
* Construction toolbar — points, lines, circles, triangles, angle bisectors, intersections, and more
* Visual problem definition, or direct JGEX input for advanced users
* Goal definition and custom theorem authoring, persisted locally in the browser
* Asynchronous job submission with status polling
* Step-by-step proof display with canvas highlighting

## Requirements

Node.js 20+ or 22+ (the Docker image uses Node 22).

```bash
cd frontend
npm ci
```

## Running locally

```bash
npm run dev
```

Runs at `http://localhost:5173`. Requires a backend reachable at `/api` — run it separately (see [`backend/README.md`](../backend/README.md)) or use Docker Compose for the full stack.

## Building

```bash
npm run typecheck
npm run build       # → dist/
npm run preview     # preview the production build locally
```

## Running with Docker

See the [root README](../README.md#getting-started) for the full Docker Compose stack. To run just the frontend against an already-running backend:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build web
```

The image builds the app with Node, then serves the static output through nginx, which proxies `/api/` to the backend service.

## Architecture

```text
src/
├── geometry/     pure coordinate math, no DOM
├── scene/        in-memory object store + undo
├── input/        click, pan/zoom, keyboard → tool dispatch
├── render/       SVG scene + Canvas proof overlay
├── tools/        construction tools (points, lines, circles, …)
├── ui/           toolbar, panels, dialogs, app store
├── api/          backend client and shared API types
└── main.ts       wiring: creates scene/viewport/renderer/UI, owns the job lifecycle
```

Data flows one way: input → scene mutation → render. The job lifecycle is: draw or enter a problem → define a goal → optionally add custom theorems → submit → poll status → fetch result → display proof.

Branded `WorldPoint`/`ScreenPoint` types keep canvas and screen-pixel coordinates from being mixed up at compile time.

## Testing

```text
tests/
├── unit/          isolated subsystem tests
├── integration/   multiple real modules together, no real backend/engine
└── e2e/           Playwright, against a running frontend (+ backend)
```

```bash
npm run test              # default suite
npm run test:unit:run     # unit tests, once
npm run test:integration:run
npm run test:coverage     # → coverage/
```

End-to-end tests need a running frontend (`npm run dev`), then:

```bash
npx playwright install chromium   # first time only
npm run test:e2e
```

For the frontend-backend e2e suite, start the full Docker Compose stack first, then:

```bash
FRONTEND_BASE_URL=http://127.0.0.1:8080 npm run test:e2e:frontend-backend
```

## Third-party licenses

Dependency license report: [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md). Regenerate after a dependency change:

```bash
npx license-checker-rseidelsohn --markdown --out THIRD_PARTY_LICENSES.md --excludePrivatePackages
```

---

See the [root README](../README.md) for the full project overview and the backend counterpart.
