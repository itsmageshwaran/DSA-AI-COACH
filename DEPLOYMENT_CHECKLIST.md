# Deployment Checklist — DSA AI Coach

**Version:** 1.0.0-RELEASE  
**Environment:** Production & Demo  

---

## 1. Environment & Configuration
- [x] `.env` configured with verified `DATABASE_URL`.
- [x] CORS middleware in `src/core/middleware/cors.py` allows frontend origin (`http://localhost:5173`).
- [x] Vite reverse proxy configured in `frontend/vite.config.ts` for `/api` and `/ws`.
- [x] Top-level `/health` endpoint exposed on port 8000.
- [x] Top-level `/metrics` endpoint exposed for Prometheus observability.

---

## 2. Database & Data Integrity
- [x] All database tables initialized (Users, Profiles, Paths, Courses, Modules, Lessons, Exercises, Concepts, Submissions).
- [x] Curated DSA problems (25 challenges) seeded with starter codes and test cases.
- [x] Presentation demo candidate (`demo@kalvium.com` / `DemoPassword123!`) seeded with active roadmap.
- [x] Database connection pool configured with `pool_pre_ping=True` and `pool_recycle=300`.

---

## 3. Frontend Build & Quality Gates
- [x] TypeScript compilation: `npm --prefix frontend run build` passes with **0 errors**.
- [x] Bundle optimization: Gzip bundle size under 115 kB.
- [x] Monaco Editor integration verified for live Python code execution.
- [x] Light & Dark theme tokens unified across all pages.
- [x] WCAG color contrast verified across all badges and code blocks.

---

## 4. Backend Automated Test Suite
- [x] Pytest suite: `python -m pytest -v` passes **82/82 tests (100%)**.
- [x] Auth flow tests (login, registration, password policy) passing.
- [x] Code execution and AST security filters passing.
- [x] AI Gateway guardrails and prompt injection protections passing.
- [x] Knowledge RAG vector search passing.

---

## 5. Verification Commands
```bash
# Backend Test Suite
python -m pytest -v

# Frontend Production Build
npm --prefix frontend run build

# Presentation Seeder
python scripts/seed_demo_user.py

# End-to-End Playwright Demo Flow
python scripts/qa_e2e_demo_flow.py
```
