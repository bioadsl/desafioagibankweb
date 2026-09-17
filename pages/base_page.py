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
        self._locator_cache = {}

    def _build_locator(self, raw):
        """
        Resolve o seletor de forma robusta:
        - Se começa com 'xpath=' -> xpath explicitamente (Playwright aceita)
        - Se contém ':has-text(' ou é CSS comum -> page.locator(raw)
        - Como fallback final, tenta get_by_text / get_by_label / get_by_role
        """
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
            xpath_str = raw[6:]
            try:
                candidates.append(self.page.locator(f"xpath={xpath_str}"))
            except Exception:
                pass

        if "has-text" in raw.lower():
            try:
                match = raw.lower().find("has-text(")
                if match > 0:
                    text_start = match + len("has-text(")
                    text_end = raw.find(")", text_start)
                    if text_end > text_start:
                        inside = raw[text_start + 1 : text_end - 1].replace('"', "").replace("'", "")
                        candidates.append(self.page.get_by_text(inside, exact=False).first)
            except Exception:
                pass

        self._locator_cache[raw] = candidates
        return candidates

    def _find_locator(self, options, prefer_visible=True, fallback_text=None):
        """
        Percorre options (lista de seletores) e retorna o PRIMEIRO que
        possui count > 0 (visível se prefer_visible=True).

        Suporta automaticamente seletores iniciados com 'xpath='.
        Se fallback_text for fornecido, tenta get_by_text no final.
        """
        last_working = None
        for raw in options:
            candidates = self._build_locator(raw)
            if not candidates:
                continue
            for loc in candidates:
                try:
                    if loc.count() > 0:
                        first = loc.first
                        try:
                            if not prefer_visible or first.is_visible():
                                return raw
                            if last_working is None:
                                last_working = raw
                        except Exception:
                            if last_working is None:
                                last_working = raw
                except Exception:
                    continue

        if fallback_text:
            try:
                gbt = self.page.get_by_text(fallback_text, exact=False)
                if gbt.count() > 0:
                    return f"__text__:{fallback_text}"
            except Exception:
                pass

        if last_working:
            return last_working
        return options[0] if options else None

    def _apply_locator(self, resolved_raw_or_text):
        """Retorna um objeto Locator dado o resultado do _find_locator."""
        if isinstance(resolved_raw_or_text, str) and resolved_raw_or_text.startswith("__text__:"):
            txt = resolved_raw_or_text[len("__text__:"):]
            return self.page.get_by_text(txt, exact=False).first
        return self.page.locator(resolved_raw_or_text).first

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
        el = self._apply_locator(locator)
        el.wait_for(state="visible", timeout=30000)
        try:
            el.click()
        except Exception:
            # fallback: scroll + click force
            try:
                el.scroll_into_view_if_needed(timeout=5000)
                el.click(force=True)
            except Exception:
                # ultimo recurso: click via evaluate (força evento DOM mesmo offscreen)
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

        valor_br = str(value).strip()
        # Tentativa 1: fill nativo (bom para type=number, sem mascara)
        #    (mas inputs com IMask/Cleave truncam -> usam fallback abaixo)
        try:
            el.fill(valor_br)
        except Exception:
            pass
        # Confirmar: valor input_value bate?
        try:
            atual = (el.input_value() or "").strip()
            valor_br_numerico = "".join(ch for ch in valor_br if ch.isdigit() or ch in ",.-")
            atual_numerico = "".join(ch for ch in atual if ch.isdigit() or ch in ",.-")
            # Se numerico bate (ou foi zerado e queremos numero !=0), usar type fallback
            if (valor_br_numerico and valor_br_numerico not in atual_numerico) or (
                valor_br and not atual and valor_br not in "0"
            ):
                raise RuntimeError("fill nao funcionou: fallback mascara")
            # OK: bateu
            return
        except Exception:
            pass

        # FALLBACK para MASCARA (moeda/porcentagem BR): normaliza decimal
        # Converte '.' -> ',' pt-BR, limpa com Ctrl+A + type(char a char delay)
        def _normalize(v):
            """
            Converte numeros para formato BR com 2 casas decimais OBRIGATORIAS
            (a mascara da calculadora interpreta N digitos como CENTAVOS).

            Exemplos:
                10000     -> '10000,00'   (R$10mil = 10000 reais e 00 centavos)
                '2.5'     -> '2,50'       (2,5% a.m.)
                2.5       -> '2,50'
                '2'       -> '2,00'
                24        -> '24'         (inteiro sem decimal -> type number, nesse caso passa fill normal)
                '10000,00' -> '10000,00'  (ja formatado)
                '1.000,50' -> '1000,50'   (mantem, ja BR)
            """
            # 1) Numeros puros:
            if isinstance(v, (int, float)):
                if isinstance(v, float):
                    # float: formata 2 casas
                    return f"{v:.2f}".replace(".", ",")
                # Inteiro: adiciona ,00 a menos que seja prazo/meses (que geralmente pequeno)
                if 0 <= v <= 9999:
                    # Inteiros pequenos podem ser meses/prazo -> mantem. A mascara
                    # de moeda se der errado vai cair no fill_input normal.
                    return f"{v},00"
                return f"{v},00"
            s = str(v).strip()
            if not s:
                return s
            tem_v = "," in s
            tem_p = "." in s

            # Ja pt-BR e ja tem virgula: garantir 2 casas apos virgula
            if tem_v and not tem_p:
                antes, _, depois = s.partition(",")
                depois = (depois + "00")[:2]
                antes = antes.replace(".", "")  # remove separador de milhar
                return f"{antes},{depois}"

            # So ponto e sem virgula: decimal en-US
            if tem_p and not tem_v:
                # >1 pontos = separador de milhar (ex: 1.000.000) = inteiro
                if s.count(".") > 1:
                    return s.replace(".", "") + ",00"
                # 1 ponto = decimal (ex: 1234.56 ou 2.5)
                antes, _, depois = s.partition(".")
                depois = (depois + "00")[:2]
                return f"{antes},{depois}"

            # Misto (, e .) = en-US com separador de milhar (1,234.56 -> pt-BR 1234,56)
            if tem_p and tem_v:
                s2 = s.replace(".", "#TEMP#").replace(",", ".").replace("#TEMP#", ",")
                return _normalize(s2)

            # So digitos (sem separador nenhum)
            if s.isdigit():
                # Inteiro puro: garantir ,00
                return f"{s},00"
            return s

        v_br = _normalize(value)
        try:
            el.press("Control+A")
            el.press("Delete")
        except Exception:
            pass
        try:
            el.press("Control+A")
            el.press("Backspace")
        except Exception:
            pass
        try:
            el.fill("")
        except Exception:
            pass
        # type com delay (garante mascara capturar cada tecla)
        el.type(v_br, delay=60)

    def select_dropdown(self, locator, value):
        self._wait_cloudflare_bypass(max_attempts=4, wait_ms=2000)
        el = self._apply_locator(locator)
        el.wait_for(state="visible", timeout=30000)
        try:
            el.select_option(value)
        except Exception:
            # fallback: tenta por label/value exato ou por texto
            try:
                el.select_option(label=value)
            except Exception:
                try:
                    el.select_option(value=str(value))
                except Exception:
                    # Ultimo recurso: simular clicks
                    try:
                        el.click()
                        opt = el.locator(f"option:has-text('{value}')").first
                        if opt.count() > 0:
                            opt.click()
                    except Exception as err:
                        raise err

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
