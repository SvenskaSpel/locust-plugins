import asyncio

from playwright.async_api import Playwright, async_playwright


async def run(playwright: Playwright) -> None:
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()

    # Open new page
    page = await context.new_page()

    # Go to https://example.com/
    await page.goto("https://example.com/")

    # Click text=More information...
    await page.click("text=More information...")
    # assert page.url == "https://www.iana.org/domains/reserved"

    # ---------------------
    await context.close()
    await browser.close()


async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)


asyncio.run(main())
