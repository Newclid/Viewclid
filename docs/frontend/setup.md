# Frontend setup

## Prerequisites

- **Node.js 20+ or 22+** (the Docker image uses Node 22).
- The backend running locally on port `8000` — optional for pure UI work,
  required to submit proofs.

## Install

From `frontend/`:

```bash
npm ci
```

Use `npm install` only when intentionally changing dependencies.

## Dev server

```bash
npm run dev
```

Vite starts at `http://localhost:5173` and opens the browser automatically.
API requests to `/api` are proxied to `http://localhost:8000`, so the
backend is transparent to frontend code.

## Type checking

```bash
npm run typecheck
```

Runs `tsc -b --noEmit`, without emitting files. Run this before committing.

## Production build

```bash
npm run build
```

Output goes to `frontend/dist/`, which the frontend's Docker image serves via
nginx.
