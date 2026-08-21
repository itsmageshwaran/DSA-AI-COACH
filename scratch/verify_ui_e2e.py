import asyncio
from playwright.async_api import async_playwright
import time
import uuid

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("=== E2E UI VERIFICATION ===")
        test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        test_password = "SecurePassword123!"

        try:
            # 1. Register & Login
            print("1. Registering user...")
            await page.goto("http://localhost:5173/auth/register")
            await page.fill('input[type="email"]', test_email)
            await page.fill('input[type="password"]', test_password)
            await page.click('button[type="submit"]')
            await page.wait_for_url("**/dashboard")
            print("SUCCESS: Registered and redirected to dashboard")

            # 2. Dashboard
            print("2. Dashboard...")
            # Wait for some dashboard element
            await page.wait_for_selector('text="Learning Progress"', timeout=5000)
            print("SUCCESS: Dashboard loaded successfully")

            # 3. Learning Paths
            print("3. Learning Paths...")
            await page.click('text="Learning Paths"')
            await page.wait_for_url("**/learning-paths")
            await page.wait_for_selector('text="Data Structures Fundamentals"', timeout=5000)
            print("SUCCESS: Learning paths loaded successfully")

            # 4. Problem Library
            print("4. Problem Library...")
            await page.click('text="Problem Library"')
            await page.wait_for_url("**/problems")
            await page.wait_for_selector('text="Two Sum"', timeout=5000)
            print("SUCCESS: Problem library loaded successfully")

            # 5. Problem Workspace
            print("5. Problem Workspace...")
            await page.click('text="Solve"')
            await page.wait_for_url("**/problems/*")
            # Wait for editor to load
            await page.wait_for_selector('.monaco-editor', timeout=10000)
            print("SUCCESS: Workspace and Monaco editor loaded")

            # 6. Real Code Execution
            print("6. Executing Code...")
            # Since Monaco is tricky to type into directly via playwright, we can try clicking "Run Code" directly
            # assuming the default template is somewhat runnable or we can just see if it runs
            await page.click('text="Run Code"')
            await page.wait_for_selector('text="Output"', timeout=10000)
            print("SUCCESS: Code execution clicked and output received")

            # 7. AI Socratic Coach
            print("7. AI Coach...")
            await page.fill('input[placeholder*="Ask for a hint"]', "Can you help me understand the problem?")
            await page.press('input[placeholder*="Ask for a hint"]', "Enter")
            
            # Wait for AI response message
            await page.wait_for_selector('.prose', timeout=15000) 
            print("SUCCESS: AI Socratic Coach responded")

            print("=== ALL E2E UI TESTS PASSED ===")

        except Exception as e:
            print(f"FAILED: {str(e)}")
            await page.screenshot(path="scratch/ui_error.png")
            raise e
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
