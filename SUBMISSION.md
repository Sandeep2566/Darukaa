# Darukaa.Earth submission checklist

Replace the placeholders below after deploying.

- **GitHub repository:** `https://github.com/<your-account>/darukaa-earth`
- **Live web application:** `https://<your-vercel-project>.vercel.app`
- **API documentation:** `https://<your-render-api>.onrender.com/docs`

## Reviewer setup notes

1. Open the live web application and choose **Register**.
2. Enter an email address and a password of at least eight characters.
3. The application creates a private Atlas Earth project and seeds illustrative restoration sites for the new account.
4. Use **New site** to persist an additional site. Configure `VITE_MAPBOX_TOKEN` to draw and retain a GeoJSON polygon before saving.

## Architecture summary

The Vite/React client authenticates against the FastAPI service using a JWT, then accesses account-owned projects and sites. FastAPI stores data in PostgreSQL; Render enables the PostGIS extension during startup. The dashboard derives its metrics and Chart.js series from API-backed site data. GitHub Actions runs frontend lint/test/build and backend lint/test before deployment.

## Required secrets

| Platform | Name | Value |
| --- | --- | --- |
| Render | `JWT_SECRET` | Generated secret (the Blueprint can generate it) |
| Render | `FRONTEND_ORIGINS` | Your Vercel URL, e.g. `https://darukaa-earth.vercel.app` |
| Vercel | `VITE_API_URL` | Your Render API URL |
| Vercel | `VITE_MAPBOX_TOKEN` | Restricted Mapbox public `pk...` token |
