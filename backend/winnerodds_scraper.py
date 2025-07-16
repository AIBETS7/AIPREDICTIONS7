import asyncio
from playwright.async_api import async_playwright
import os

PAGES = [
    ("football", "https://winnerodds.com/football"),
    ("tennis", "https://winnerodds.com/tennis"),
    ("football_history", "https://winnerodds.com/football-history"),
    ("tennis_history", "https://winnerodds.com/tennis-history"),
]

async def download_dynamic_pages():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for name, url in PAGES:
            page = await browser.new_page()
            await page.goto(url)
            await page.wait_for_timeout(5000)
            html = await page.content()
            out_path = os.path.join(os.path.dirname(__file__), 'data', f'winnerodds_{name}_dynamic.html')
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"Guardado: {out_path}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(download_dynamic_pages()) 