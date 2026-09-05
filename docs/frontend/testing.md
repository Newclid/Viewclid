# Frontend testing

The frontend uses [Vitest](https://vitest.dev) with a `jsdom` environment.
Tests live under `frontend/tests/`, split into two projects: `unit` and
`integration`.

```text
tests/
├── unit/
│   ├── api/          BackendClient, JobPoller, API types
│   ├── construction/ Construction catalogue entries
│   ├── render/       Renderer
│   ├── theorem/      TheoremStore, validation, predicates
│   └── ui/           Toolbar, proof panel, notifications, …
└── integration/
    └── submissionLifecycle.test.ts  # end-to-end job submit -> poll -> result
```

Unit tests cover individual modules in isolation; integration tests exercise
the full job lifecycle with a mocked HTTP layer.

## Running tests

```bash
npm test               # watch mode, all tests
npm run test:run       # single run, all tests
npm run test:unit      # unit tests only
npm run test:integration  # integration tests only
npm run test:coverage  # coverage report -> frontend/coverage/
```

## Writing tests

Add new test files under `tests/unit/` or `tests/integration/`, following
the existing directory structure. `jsdom` is available in both projects, so
DOM manipulation works out of the box.

The [geometry layer](modules/scene-and-geometry.md) has no DOM dependency and
is straightforward to unit-test with plain assertions. For modules that touch
the DOM, use the helpers in `src/ui/dom.ts` to create elements and assert on
their state.
