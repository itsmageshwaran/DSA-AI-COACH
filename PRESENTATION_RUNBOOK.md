# Presentation Runbook — DSA AI Coach

**Target Event:** Tomorrow's Live Presentation  
**Demo Account:** `demo@kalvium.com` / `DemoPassword123!`  
**Primary URLs:**  
- Web Application: `http://localhost:5173`  
- Backend API Docs: `http://127.0.0.1:8000/docs`  
- System Health Check: `http://127.0.0.1:8000/health`  

---

## 1. Pre-Presentation Sanity Checklist (5 Minutes Before)

1. **Verify Backend is Running:**
   ```bash
   curl http://127.0.0.1:8000/health
   # Expected: {"status":"ok","version":"0.1.0","database":"connected","redis":"connected"}
   ```
2. **Verify Frontend Dev Server is Running:**
   - Open browser to `http://localhost:5173/login`.
3. **Verify Demo User Exists in Database:**
   ```bash
   python scripts/seed_demo_user.py
   # Expected output: "Presentation demo account setup complete and verified!"
   ```

---

## 2. Step-by-Step Presentation Script

### Act 1: The Student Entrypoint & Login (1 minute)
- **Action:** Open `http://localhost:5173/login`.
- **Narration:** *"Welcome to the DSA AI Coach. Let's log in as our demo candidate who is preparing for Backend Engineering roles."*
- **Credentials:**
  - Email: `demo@kalvium.com`
  - Password: `DemoPassword123!`
- **Key Highlight:** Notice smooth, instant authentication without loops or redirects.

### Act 2: Personalized Dashboard & Roadmap (2 minutes)
- **Action:** Land on `http://localhost:5173/`.
- **Narration:** *"The dashboard provides immediate clarity. The candidate sees their specialization: Backend Engineering, current focus topic, daily streak, and their next best action."*
- **Action:** Click on **"My Roadmap"** (`/learn`).
- **Narration:** *"Here is the structured learning path. Every phase connects foundational concepts to production-grade problem solving. Notice the new 'Start Topic Journey' CTA on our current focus topic: Arrays."*

### Act 3: The 4-Phase Topic Learning Experience (4 minutes)
- **Action:** Click **"Start Topic Journey"** on Phase 1: Arrays (navigating to `/topics/arrays`).
- **Phase 1 — Learn:**
  - *"Before writing a single line of code, students need visual intuition. We provide curated video explanations, production relevance, and asymptotic complexity bounds."*
- **Phase 2 — Understand:**
  - Click tab **"2. Understand"**.
  - *"Students review architectural notes on memory allocation and two-pointer trade-offs. Notice the instant language switcher: Python, JavaScript, C++, Java, and Go with one-click copy."*
- **Phase 3 — Practice:**
  - Click tab **"3. Practice"**.
  - *"The curriculum is adaptively sequenced from foundational Easy challenges like Two Sum to Medium and Hard challenges. Every problem has an explicit rationale explaining why the student is solving it."*
- **Phase 4 — Master:**
  - Click tab **"4. Master"**.
  - *"Mastery is tracked dynamically from verified database submissions. Once problems are solved, certification milestones unlock."*

### Act 4: Live Code Execution in the Problem Workspace (3 minutes)
- **Action:** In the Practice tab, click **"Solve Problem"** on **Two Sum**.
- **Narration:** *"The student lands in a full-fidelity IDE powered by Monaco editor with problem instructions, test runner, and real-time execution."*
- **Action:** Click **"Run Code"** or **"Submit"**.
- **Narration:** *"Code is securely executed against automated test fixtures with instant feedback."*

---

## 3. Emergency Backup Plan
If any network or port conflict arises during setup:
```powershell
# Free ports 8000 and 5173:
Get-NetTCPConnection -LocalPort 8000,5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }

# Restart Backend:
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Restart Frontend:
npm --prefix frontend run dev
```
The database is configured locally with 0 cloud dependencies, ensuring 100% offline immunity during your presentation.
