# MileLedger contributor commands

Run commands from the indicated directory. Tests use deterministic routes and do not require network access or an OpenRouteService key.

## Backend (`backend/`)

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
python -m ruff format --check .
python -m ruff check .
python manage.py test
```

Use `python -m ruff format .` only when intentionally formatting backend files. For a production-settings audit, set the production environment variables and run `python manage.py check --deploy`.

## Frontend (`frontend/`)

```bash
pnpm install --frozen-lockfile
pnpm dev
pnpm lint
pnpm typecheck
pnpm test
pnpm build
pnpm exec playwright install chromium
pnpm e2e
```

Windows no-admin fallback: run `npx --yes pnpm@10 install --frozen-lockfile`, then use `npm run dev`, `npm run lint`, `npm run typecheck`, `npm test`, `npm run build`, or `npm run e2e`. Do not run `corepack enable` when Node is installed under protected `C:\Program Files`.

Local services are expected at `http://127.0.0.1:8000` and `http://127.0.0.1:5173`. The Vite server proxies `/api` to Django.

## Guardrails

- Keep the HOS scheduler pure, deterministic, integer-minute based, and independent of Django views.
- Tests must use checked-in route fixtures; never call live routing services.
- Never expose `OPENROUTESERVICE_API_KEY` to the frontend.
- Preserve the structured API error shape: `code`, `message`, `field_errors`, `retryable`.
- Every daily log must total exactly 1,440 minutes.
