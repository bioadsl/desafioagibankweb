class BasePage:
    CLOUDFLARE_TITLES = [
        "Checking your browser",
        "Just a moment",
        "Verifying you are human",
        "Attention required",
        "Just a moment...",
    ]

    def __init__(self, page):
        self.page = page

    def _is_cloudflare_pending(self):
        try:
            title = self.page.title().lower().strip()
            for cf in self.CLOUDFLARE_TITLES:
                if cf.lower() in title:
                    return True
            return False
        except Exception:
            return False

    def _wait_cloudflare_bypass(self, max_attempts=10, wait_ms=4000):
        for _ in range(max_attempts):
            if not self._is_cloudflare_pending():
                try:
                    body = self.page.inner_text("body", timeout=1000).lower()
                    if "checking your browser" in body or "just a moment" in body:
                        self.page.wait_for_timeout(wait_ms)
                        continue
                except Exception:
                    pass
                return True
            self.page.wait_for_timeout(wait_ms)
        return not self._is_cloudflare_pending()

    def navigate(self, url, wait_cloudflare=True):
        self.page.goto(url, wait_until="domcontentloaded")
        if wait_cloudflare:
            try:
                self._wait_cloudflare_bypass()
            except Exception:
                pass
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            pass

    def click_element(self, locator):
        self._wait_cloudflare_bypass(max_attempts=4, wait_ms=2000)
        self.page.locator(locator).wait_for(state="visible", timeout=30000)
        self.page.locator(locator).click()

    def fill_input(self, locator, value):
        self._wait_cloudflare_bypass(max_attempts=4, wait_ms=2000)
        self.page.locator(locator).wait_for(state="visible", timeout=30000)
        self.page.locator(locator).fill(value)

    def select_dropdown(self, locator, value):
        self._wait_cloudflare_bypass(max_attempts=4, wait_ms=2000)
        self.page.locator(locator).wait_for(state="visible", timeout=30000)
        self.page.locator(locator).select_option(value)

    def get_text(self, locator):
        self.page.locator(locator).wait_for(state="visible", timeout=30000)
        return self.page.locator(locator).inner_text().strip()

    def is_element_visible(self, locator, timeout=10000):
        try:
            self.page.locator(locator).wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def wait_for_element(self, locator, timeout=30000):
        self.page.locator(locator).wait_for(state="visible", timeout=timeout)

    def wait_for_load(self):
        try:
            self.page.wait_for_load_state("networkidle", timeout=45000)
        except Exception:
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            except Exception:
                pass
        self._wait_cloudflare_bypass(max_attempts=5, wait_ms=2000)

    def wait_for_real_page(self, check_url_contains=None, check_title_contains=None, timeout=60000):
        import time
        start = time.time()
        while (time.time() - start) < timeout / 1000:
            if self._is_cloudflare_pending():
                self.page.wait_for_timeout(1000)
                continue
            title_ok = True
            url_ok = True
            if check_title_contains:
                try:
                    title_ok = any(t.lower() in self.page.title().lower() for t in check_title_contains) if isinstance(check_title_contains, list) else check_title_contains.lower() in self.page.title().lower()
                except Exception:
                    title_ok = False
            if check_url_contains:
                try:
                    u = self.page.url.lower()
                    url_ok = any(c.lower() in u for c in check_url_contains) if isinstance(check_url_contains, list) else check_url_contains.lower() in u
                except Exception:
                    url_ok = False
            if title_ok and url_ok:
                return True
            self.page.wait_for_timeout(1000)
        return False
