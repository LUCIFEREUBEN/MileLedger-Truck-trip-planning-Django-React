# Deployment

This repository is ready for a Vercel frontend and a Render Docker web service backed by PostgreSQL. No hosted deployment is claimed until both public URLs are verified.

## 1. Backend on Render

1. Push the repository to GitHub and create a Render Blueprint from `render.yaml`.
2. Create an OpenRouteService key with directions/geocoding access.
3. In the `mileledger-api` service, set:
   - `OPENROUTESERVICE_API_KEY` to the server-only key.
   - `DJANGO_ALLOWED_HOSTS` to the Render host, without a scheme.
   - `CORS_ALLOWED_ORIGINS` to the final Vercel HTTPS origin.
   - `CSRF_TRUSTED_ORIGINS` to the same HTTPS origin.
4. Keep `DJANGO_DEBUG=false` and `DEMO_MODE=false` for real routing. Set `DEMO_MODE=true` only if the public review should also support the two labelled fixtures.
5. Deploy. Render builds `backend/Dockerfile`; the container runs `python manage.py migrate` before Gunicorn starts, and Render checks `/api/health/`.
6. Verify `https://<render-host>/api/health/` returns `{"status":"ok"}` and `route_mode:"live"`.

The blueprint generates `DJANGO_SECRET_KEY` and connects `DATABASE_URL` to the managed PostgreSQL database. Do not put the routing key in Vercel.

The checked-in blueprint uses Render’s free instance types for assessment review. As of August 2026, free Postgres expires after 30 days and has no backups; choose a paid database before storing durable production data.

## 2. Frontend on Vercel

1. Import the same repository in Vercel.
2. Set Root Directory to `frontend`.
3. Framework Preset: Vite. Build command: `pnpm build`. Output directory: `dist`.
4. Set `VITE_API_BASE_URL=https://<render-host>` with no trailing slash.
5. Deploy, then update the Render CORS and CSRF values to the final Vercel origin if it changed.
6. Verify a fresh plan, a persisted `?trip=<uuid>` refresh, print preview, and the 390px mobile tabs.

## 3. Release checks

Before promoting a release:

```bash
cd backend
python manage.py migrate --check
python manage.py check --deploy
python manage.py test

cd ../frontend
pnpm lint
pnpm typecheck
pnpm test
pnpm build
pnpm e2e
```

For `check --deploy`, use the same production variables as the hosted service. Confirm `DJANGO_DEBUG=false`, HTTPS-only origins, a long generated secret, a PostgreSQL URL, and the exact public backend host.

## 4. Rollback and operations

- Roll back the frontend to the previous Vercel deployment.
- Roll back the backend image in Render; do not reverse a database migration without reviewing its reversibility.
- Use `/api/health/` for uptime monitoring.
- Rotate an exposed OpenRouteService key in the provider console and update Render; frontend redeployment is unnecessary.
- Review provider usage and API throttle logs if route plans begin returning structured `route_provider_unavailable` errors.
