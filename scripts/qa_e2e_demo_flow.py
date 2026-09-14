"""Playwright End-to-End Verification of Topic Learning Preview & Demo Account Flow."""

import asyncio
import httpx
from playwright.async_api import async_playwright


async def run_e2e_demo_flow():
    # 1. Login via backend API to get fresh JWT token
    print("1. Authenticating demo user via API...")
    res = httpx.post(
        "http://127.0.0.1:8000/api/v1/auth/login",
        json={"email": "demo@kalvium.com", "password": "DemoPassword123!"},
        timeout=10.0
    )
    if res.status_code != 200:
        print("Login API failed:", res.status_code, res.text)
        return

    data = res.json()
    token = data["access_token"]
    print("Obtained token successfully!")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await context.new_page()

        # 2. Inject token into localStorage before page load
        print("2. Opening application with pre-authenticated state...")
        await page.goto("http://localhost:5173/login", wait_until="domcontentloaded")
        await page.evaluate(f"localStorage.setItem('access_token', '{token}')")

        # 3. Navigate to Dashboard
        print("3. Navigating to Dashboard...")
        await page.goto("http://localhost:5173/", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="qa_dashboard_demo.png")
        print("Captured qa_dashboard_demo.png")

        # 4. Navigate to Topic Learning Journey for Arrays
        print("4. Navigating to Topic Learning Journey: /topics/arrays...")
        await page.goto("http://localhost:5173/topics/arrays", wait_until="networkidle")
        await page.wait_for_selector('text=Arrays & Dynamic Arrays', timeout=10000)
        await page.wait_for_timeout(1000)
        await page.screenshot(path="qa_topic_tab_1_learn.png")
        print("Captured qa_topic_tab_1_learn.png (Learn / Video Intuition tab)")

        # 5. Switch to Understand Tab (Notes & Multi-Language Code)
        print("5. Switching to Understand Tab...")
        await page.click('button:has-text("2. Understand")')
        await page.wait_for_selector('text=Reference Implementations', timeout=5000)
        await page.wait_for_timeout(1000)
        await page.screenshot(path="qa_topic_tab_2_understand.png")
        print("Captured qa_topic_tab_2_understand.png (Understand / Notes & Multi-lang Code tab)")

        # 6. Switch to Practice Tab (Adaptive Problems)
        print("6. Switching to Practice Tab...")
        await page.click('button:has-text("3. Practice")')
        await page.wait_for_selector('text=Progressive Practice Curriculum', timeout=5000)
        await page.wait_for_timeout(1000)
        await page.screenshot(path="qa_topic_tab_3_practice.png")
        print("Captured qa_topic_tab_3_practice.png (Practice / Adaptive Problems tab)")

        # 7. Switch to Master Tab (Milestones & Next Step)
        print("7. Switching to Master Tab...")
        await page.click('button:has-text("4. Master")')
        await page.wait_for_selector('text=Topic Mastery Milestone', timeout=5000)
        await page.wait_for_timeout(1000)
        await page.screenshot(path="qa_topic_tab_4_master.png")
        print("Captured qa_topic_tab_4_master.png (Master / Milestone tab)")

        # 8. Click Solve Problem to enter Monaco Workspace
        print("8. Opening Problem Workspace for Two Sum...")
        await page.click('button:has-text("3. Practice")')
        await page.wait_for_selector('button:has-text("Solve Problem")', timeout=5000)
        await page.locator('button:has-text("Solve Problem")').first.click()

        # Wait for Monaco editor
        await page.wait_for_selector('.monaco-editor', timeout=15000)
        await page.wait_for_timeout(2000)
        await page.screenshot(path="qa_problem_workspace.png")
        print("Captured qa_problem_workspace.png (Monaco Editor Problem Workspace)")

        # 9. Navigate to Roadmap page
        print("9. Navigating to Roadmap page: /learn...")
        await page.goto("http://localhost:5173/learn", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="qa_roadmap_page.png")
        print("Captured qa_roadmap_page.png (Roadmap with Start Topic Journey CTA)")

        await browser.close()
        print("ALL E2E UI AND FEATURE FLOWS VERIFIED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(run_e2e_demo_flow())
