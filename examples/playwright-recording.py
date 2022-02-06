import asyncio

from playwright.async_api import Playwright, async_playwright


async def run(playwright: Playwright) -> None:
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()

    # Open new page
    page = await context.new_page()

    # Go to https://www.google.com/?gws_rd=ssl
    await page.goto("https://www.google.com/?gws_rd=ssl")

    # Click button:has-text("Jag godkänner")
    # async with page.expect_navigation(url="https://www.google.com/?gws_rd=ssl"):
    async with page.expect_navigation():
        await page.click('button:has-text("Jag godkänner")')

    # Click :nth-match(:text("Sök på Google"), 2)
    await page.click(':nth-match(:text("Sök på Google"), 2)')

    # ---------------------
    await context.close()
    await browser.close()


async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)


asyncio.run(main())
