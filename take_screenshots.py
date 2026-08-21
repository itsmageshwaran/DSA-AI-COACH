import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1440, 'height': 900})
        
        await page.goto('http://localhost:5173/learn')
        await asyncio.sleep(2)
        
        if 'login' in page.url:
            await page.fill('input[type="email"]', 'testuser@example.com')
            await page.fill('input[type="password"]', 'password123')
            await page.click('button[type="submit"]')
            await asyncio.sleep(2)
            await page.goto('http://localhost:5173/learn')
            await asyncio.sleep(2)
            
        await page.screenshot(path='C:/Users/Mageshwaran/.gemini/antigravity/brain/357ededd-8205-4e02-8ac5-2988d34fd2a0/scratch/screenshots/02_learn_new.png')
        
        await page.goto('http://localhost:5173/problems')
        await asyncio.sleep(2)
        await page.screenshot(path='C:/Users/Mageshwaran/.gemini/antigravity/brain/357ededd-8205-4e02-8ac5-2988d34fd2a0/scratch/screenshots/03_problems_new.png')
        
        await page.goto('http://localhost:5173/')
        await asyncio.sleep(2)
        await page.screenshot(path='C:/Users/Mageshwaran/.gemini/antigravity/brain/357ededd-8205-4e02-8ac5-2988d34fd2a0/scratch/screenshots/01_dashboard_new.png')
        
        await browser.close()

asyncio.run(main())
