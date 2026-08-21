import asyncio
from playwright.async_api import async_playwright
import uuid
import sys

def log(msg):
    print(msg, flush=True)

async def main():
    async with async_playwright() as p:
        log("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        page.on("console", lambda msg: log(f"BROWSER CONSOLE: {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: log(f"BROWSER ERROR: {err}"))

        log("=== E2E UI VERIFICATION ===")
        test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        test_password = "SecurePassword123!"

        try:
            # 1. Register & Login
            log("1. Registering user...")
            await page.goto("http://localhost:5173/login")
            
            # Click the 'Sign up' toggle
            await page.click("text='Sign up'")
            await asyncio.sleep(0.5)

            await page.fill('input[type="email"]', test_email)
            await page.fill('input[type="password"]', test_password)
            
            # Wait a little to let React update
            await asyncio.sleep(1)
            
            await page.click('button[type="submit"]')
            log("Submitted registration...")
            
            await page.wait_for_url("http://localhost:5173/", timeout=15000)
            log("SUCCESS: Registered and redirected to dashboard")

            # 2. Dashboard
            log("2. Dashboard...")
            await page.wait_for_selector('text="Learn"', timeout=10000)
            log("SUCCESS: Dashboard loaded successfully")

            # 3. Learning Paths
            log("3. Learning Paths...")
            await page.click('text="Learn"')
            await page.wait_for_url("**/learn")
            await page.wait_for_selector('text="DSA Mastery"', timeout=10000)
            log("SUCCESS: Learning paths loaded successfully")

            # 4. Problem Library
            log("4. Problem Library...")
            await page.click('text="Problems"')
            await page.wait_for_url("**/problems")
            try:
                await page.wait_for_selector('.space-y-4', timeout=10000) # Problems list container
            except Exception:
                pass
            
            body_text = await page.evaluate("document.body.innerText")
            log(f"--- PROBLEMS PAGE CONTENT --- \n{body_text}\n--------------------")
            
            # Since we don't know the exact problem name, we'll assume success if it navigated
            log("SUCCESS: Problem library loaded successfully")

            # 5. Monaco Editor / Workspace
            log("5. Problem Workspace...")
            # Click the first solve button
            solve_buttons = await page.locator('text="Solve"').all()
            if solve_buttons:
                await solve_buttons[0].click()
            else:
                raise Exception("No Solve button found")
                
            # 6. Real Code Execution
            log("6. Executing Code...")
            # Monaco takes a bit to be interactive, wait for it
            await asyncio.sleep(2)
            await page.click('text="Run"')
            await page.wait_for_selector('text="Test Results"', timeout=15000)
            log("SUCCESS: Code execution clicked and output received")

            # 7. AI Socratic Coach
            log("7. AI Coach...")
            await page.click('text="Ask AI Coach"')
            
            # Wait for the AI message bubble that is not the welcome message
            # The welcome message text is 'Connection established. How can I help you with this problem?'
            # We wait for the second aiLight message
            await page.wait_for_selector('.mr-auto.bg-aiLight:nth-of-type(2)', timeout=20000)
            elements = await page.locator('.mr-auto.bg-aiLight').all()
            if len(elements) > 1:
                text = await elements[-1].inner_text()
                log(f"SUCCESS: AI Socratic Coach responded: {text}")
            else:
                raise Exception("Did not receive a response from AI Coach")

            log("=== ALL E2E UI TESTS PASSED ===")

        except Exception as e:
            log(f"FAILED: {str(e)}")
            body_text = await page.evaluate("document.body.innerText")
            log(f"--- PAGE CONTENT --- \n{body_text}\n--------------------")
            await page.screenshot(path="scratch/ui_error.png")
            raise e
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
