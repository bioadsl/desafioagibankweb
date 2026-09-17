def _br_number(v):
    if isinstance(v, (int, float)):
        if isinstance(v, float):
            return f"{v:.2f}".replace(".", ",")
        return f"{v},00"
    s = str(v).strip()
    if not s:
        return s
    tem_v = "," in s
    tem_p = "." in s

    if tem_v and not tem_p:
        antes, _, depois = s.partition(",")
        return f"{antes.replace('.', '')},{(depois + '00')[:2]}"
    if tem_p and not tem_v:
        if s.count(".") > 1:
            return s.replace(".", "") + ",00"
        antes, _, depois = s.partition(".")
        return f"{antes},{(depois + '00')[:2]}"
    if tem_p and tem_v:
        # pt-BR 1.000,50: separador milhar . e decimal ,
        if s.rfind(",") > s.rfind("."):
            cleaned = s.replace(".", "")
            antes, _, depois = cleaned.partition(",")
            return f"{antes},{(depois + '00')[:2]}"
        # en-US 1,234.56: separador milhar , e decimal .
        cleaned = s.replace(",", "")
        antes, _, depois = cleaned.partition(".")
        return f"{antes},{(depois + '00')[:2]}"
    return f"{s},00" if s.isdigit() else s


class BasePage:
    CLOUDFLARE_TITLES = (
        "checking your browser", "just a moment",
        "verifying you are human", "attention required",
        "just a moment...",
    )

    def __init__(self, page):
        self.page = page
        self._locator_cache = {}

    def _build_locator(self, raw):
        if raw in self._locator_cache:
            return self._locator_cache[raw]
        if not raw:
            return None

        candidates = []
        try:
            candidates.append(self.page.locator(raw))
        except Exception:
            pass
        if raw.lower().startswith("xpath="):
            try:
                candidates.append(self.page.locator(f"xpath={raw[6:]}"))
            except Exception:
                pass
        if "has-text(" in raw.lower():
            try:
                i = raw.lower().find("has-text(") + 9
                j = raw.find(")", i)
                if j > i:
                    txt = raw[i + 1:j - 1].replace('"', "").replace("'", "")
                    candidates.append(self.page.get_by_text(txt, exact=False).first)
            except Exception:
                pass
        self._locator_cache[raw] = candidates
        return candidates

    def _find_locator(self, options, prefer_visible=True, fallback_text=None):
        last = None
        for raw in options:
            for loc in self._build_locator(raw) or []:
                try:
                    if loc.count() > 0:
                        first = loc.first
                        if (not prefer_visible) or first.is_visible():
                            return raw
                        if last is None:
                            last = raw
                except Exception:
                    continue
        if fallback_text:
            try:
                if self.page.get_by_text(fallback_text, exact=False).count() > 0:
                    return f"__text__:{fallback_text}"
            except Exception:
                pass
        return last or (options[0] if options else None)

    def _apply_locator(self, resolved_raw_or_text):
        if isinstance(resolved_raw_or_text, str) and resolved_raw_or_text.startswith("__text__:"):
            return self.page.get_by_text(resolved_raw_or_text[9:], exact=False).first
        return self.page.locator(resolved_raw_or_text).first

    def _is_cloudflare_pending(self):
        try:
            t = (self.page.title() or "").lower().strip()
            return any(cf in t for cf in self.CLOUDFLARE_TITLES)
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
        el = self._apply_locator(locator)
        el.wait_for(state="visible", timeout=30000)
        try:
            el.click()
        except Exception:
            try:
                el.scroll_into_view_if_needed(timeout=5000)
                el.click(force=True)
            except Exception:
                el.evaluate("e => e.click()")

    def fill_input(self, locator, value):
        self._wait_cloudflare_bypass(max_attempts=4, wait_ms=2000)
        el = self._apply_locator(locator)
        el.wait_for(state="visible", timeout=30000)
        try:
            el.click()
        except Exception:
            try:
                el.scroll_into_view_if_needed(timeout=5000)
                el.click(force=True)
            except Exception:
                pass

        v_br = str(value).strip()
        try:
            el.fill(v_br)
        except Exception:
            pass
        try:
            atual = (el.input_value() or "").strip()
            vn = "".join(ch for ch in v_br if ch.isdigit() or ch in ",.-")
            an = "".join(ch for ch in atual if ch.isdigit() or ch in ",.-")
            if (vn and vn not in an) or (v_br and not atual and v_br not in "0"):
                raise RuntimeError("fallback mascara")
            return
        except Exception:
            pass

        v_br = _br_number(value)
        clear_tries = [
            lambda: (el.press("Control+A"), el.press("Delete")),
            lambda: (el.press("Control+A"), el.press("Backspace")),
            lambda: el.fill(""),
        ]
        for fn in clear_tries:
            try:
                fn()
            except Exception:
                continue
        el.type(v_br, delay=60)

    def select_dropdown(self, locator, value):
        self._wait_cloudflare_bypass(max_attempts=4, wait_ms=2000)
        el = self._apply_locator(locator)
        el.wait_for(state="visible", timeout=30000)

        strategies = [
            lambda: el.select_option(value),
            lambda: el.select_option(label=value),
            lambda: el.select_option(value=str(value)),
            lambda: _simulate_dropdown_click(el, value),
        ]
        last_err = None
        for strat in strategies:
            try:
                strat()
                return
            except Exception as e:
                last_err = e
        raise last_err if last_err else RuntimeError("select falhou")

    def get_text(self, locator):
        el = self._apply_locator(locator)
        el.wait_for(state="visible", timeout=30000)
        return el.inner_text().strip()

    def is_element_visible(self, locator, timeout=10000):
        try:
            el = self._apply_locator(locator)
            el.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def wait_for_element(self, locator, timeout=30000):
        el = self._apply_locator(locator)
        el.wait_for(state="visible", timeout=timeout)

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
            try:
                t = (self.page.title() or "").lower()
                title_ok = (
                    True if not check_title_contains else
                    any(x.lower() in t for x in check_title_contains) if isinstance(check_title_contains, list)
                    else check_title_contains.lower() in t
                )
            except Exception:
                title_ok = False
            try:
                u = self.page.url.lower()
                url_ok = (
                    True if not check_url_contains else
                    any(x.lower() in u for x in check_url_contains) if isinstance(check_url_contains, list)
                    else check_url_contains.lower() in u
                )
            except Exception:
                url_ok = False
            if title_ok and url_ok:
                return True
            self.page.wait_for_timeout(1000)
        return False


def _simulate_dropdown_click(el, value):
    el.click()
    opt = el.locator(f"option:has-text('{value}')").first
    if opt.count() > 0:
        opt.click()
