# 砺学多题库刷题平台 MVP

FastAPI + React/Vite implementation for the 砺学 quiz MVP. It supports employee import/login, question-bank import, practice feedback, wrong-question state, points, rankings, lightweight exams, AI explanation fallback, dashboard, and CSV exports.

## Local Development

```powershell
cd server
python -m pytest tests -q

cd ../web
npm install
npm run build
```

Backend dev server:

```powershell
cd server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend dev server:

```powershell
cd web
npm run dev
```

## CSV Fixtures

The first production fixture is `question/questions.csv`. The importer previews invalid rows instead of crashing. In the current file, row 169 is missing the answer fields, so 168 rows are importable and one row is reported as an error.

## Deployment

1. Buy a lightweight cloud server with 2 vCPU, 4 GB RAM, and Ubuntu LTS.
2. Point a domain name to the server.
3. Install Docker and Docker Compose.
4. Copy `.env.example` to `.env` and replace secrets.
5. Run `docker compose up -d --build`.
6. Configure HTTPS with Nginx or a cloud certificate manager.
7. Open `/admin/login`, import employees, create a question bank, and import `question/questions.csv`.
