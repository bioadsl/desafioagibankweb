import os
import pytest
from playwright.sync_api import sync_playwright


STEALTH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--disable-dev-shm-usage",
    "--disable-features=IsolateOrigins,site-per-process",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-web-security",
    "--disable-site-isolation-trials",
    "--disable-features=BlockInsecurePrivateNetworkRequests",
    "--start-maximized",
    "--disable-infobars",
    "--hide-scrollbars",
    "--mute-audio",
    "--ignore-certificate-errors",
    "--ignore-ssl-errors=yes",
    "--allow-running-insecure-content",
]

CHROME_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="function")
def browser(playwright_instance):
    headless = os.getenv("HEADLESS", "true").lower() == "true"
    browser = playwright_instance.chromium.launch(
        headless=headless,
        slow_mo=int(os.getenv("SLOW_MO", "0")),
        channel="chrome" if os.getenv("USE_SYSTEM_CHROME", "false").lower() == "true" else None,
        args=STEALTH_ARGS,
    )
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser):
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        locale="pt-BR",
        timezone_id="America/Sao_Paulo",
        user_agent=CHROME_UA,
        accept_downloads=True,
        ignore_https_errors=True,
        permissions=["geolocation", "notifications"],
        extra_http_headers={
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
        },
    )

    context.tracing.start(screenshots=True, snapshots=True, sources=True)

    def handle_cloudflare(page):
        for _ in range(6):
            try:
                title = page.title()
                if (
                    "Checking your browser" in title
                    or "Just a moment" in title
                    or "Verifying you are human" in title
                    or title.strip().lower() == "attention required"
                ):
                    page.wait_for_timeout(5000)
                else:
                    break
            except Exception:
                page.wait_for_timeout(5000)

    context.on("page", handle_cloudflare)

    yield context
    context.tracing.stop(path="reports/trace.zip")
    context.close()


@pytest.fixture(scope="function")
def page(context):
    page = context.new_page()
    page.set_default_timeout(60000)
    page.set_default_navigation_timeout(60000)

    try:
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5].map(i => (
                    {0: i, name: `Chrome PDF Plugin ${i}`, filename: `internal-pdf-viewer-${i}`, length: 1}
                )),
            });
            Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en-US', 'en']});
            Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
            window.chrome = { runtime: {} };
        """)
    except Exception:
        pass

    yield page
    page.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        if "page" in item.fixturenames:
            page = item.funcargs["page"]
            os.makedirs("reports/screenshots", exist_ok=True)
            screenshot_path = f"reports/screenshots/{item.name}.png"
            try:
                page.screenshot(path=screenshot_path, full_page=True)
            except Exception:
                pass
