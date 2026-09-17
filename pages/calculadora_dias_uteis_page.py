import re
from pages.base_page import BasePage


class CalculadoraDiasUteisPage(BasePage):
    URL = "https://blog.agibank.com.br/calculadora-dias-uteis/"
    HOME_BLOG_URL = "https://blog.agibank.com.br/"

    URL_IFRAME_STANDALONE = (
        "https://blog.agibank.com.br/wp-content/uploads/2026/04/"
        "calculadora_dias_uteis_final_v4.html"
    )
    IFRAME_URL_KEYWORDS = [
        "calculadora_dias_uteis",
        "calculadora-dias-uteis",
        "dias_uteis",
        "dias-uteis",
        "v4.html",
        "diasuteis",
    ]

    MENU_ITEM_DIAS_UTEIS_BLAZEMETER = [
        "#menu-item-24257 > a.menu-link > span.menu-text",
        "#menu-item-24257 a.menu-link",
        "#menu-item-24257 span.menu-text",
        "li#menu-item-24257 a",
        "li[id*='24257'] a",
        "a:has-text('Dias Úteis')",
        "a:has-text('Dias Uteis')",
        "a:has-text('Calculadora de Dias')",
        "span.menu-text:has-text('Dias Úteis')",
        "span.menu-text:has-text('Dias Uteis')",
        ".menu-link:has-text('Dias Úteis')",
    ]

    MENU_BLOG_ABRIR_DROPDOWN_FERRAMENTAS = [
        "a.menu-link:has-text('Ferramentas')",
        "span.menu-text:has-text('Ferramentas')",
        "li.menu-item-has-children > a",
        "#menu-item-24253 > a",
        "a:has-text('Ferramentas')",
    ]

    INPUT_DATA_INICIAL = [
        "#dataInicial",
        "#data_inicial",
        "#formDiasUteis #dataInicial",
        "input[name*='data_inicial']",
        "input[name*='data-inicial']",
        "input[name*='dataInicial']",
        "input[id*='data_inicial']",
        "input[id*='data-inicial']",
        "input[id*='dataInicial']",
        "input[type='date']:nth-child(1)",
        "input[placeholder*='Data Inicial']",
        "input[placeholder*='data inicial']",
        "input[placeholder*='dd/mm/aaaa']",
        "input[placeholder*='DD/MM/AAAA']",
        "input[data-date*='inicial']",
        "input[aria-label*='Data Inicial']",
        "input[aria-label*='data inicial']",
        "label:has-text('Data Inicial') + input",
        "label:has-text('data inicial') + input",
    ]

    INPUT_DATA_FINAL = [
        "#dataFinal",
        "#data_final",
        "#formDiasUteis #dataFinal",
        "input[name*='data_final']",
        "input[name*='data-final']",
        "input[name*='dataFinal']",
        "input[id*='data_final']",
        "input[id*='data-final']",
        "input[id*='dataFinal']",
        "input[type='date']:nth-child(2)",
        "input[placeholder*='Data Final']",
        "input[placeholder*='data final']",
        "input[data-date*='final']",
        "input[aria-label*='Data Final']",
        "input[aria-label*='data final']",
        "label:has-text('Data Final') + input",
        "label:has-text('data final') + input",
    ]

    CHECKBOX_SABADO = [
        "#incluirSabado",
        "#sabado",
        "input[name*='sabado']",
        "input[name*='sab']",
        "input[id*='sabado']",
        "input[id*='sab']",
        "input[type='checkbox']:nth-of-type(1)",
        "label:has-text('Sábado') input",
        "label:has-text('Sabado') input",
        "label:has-text('sábado') input",
        "label:has-text('sabado') input",
        "input[type='checkbox'] + label:has-text('Sábado') ~ input",
    ]

    CHECKBOX_DOMINGO = [
        "#incluirDomingo",
        "#domingo",
        "input[name*='domingo']",
        "input[name*='dom']",
        "input[id*='domingo']",
        "input[id*='dom']",
        "input[type='checkbox']:nth-of-type(2)",
        "label:has-text('Domingo') input",
        "label:has-text('domingo') input",
        "input[type='checkbox'] + label:has-text('Domingo') ~ input",
    ]

    CHECKBOX_FERIADOS = [
        "#considerarFeriados",
        "#feriados",
        "input[name*='feriado']",
        "input[name*='feriados']",
        "input[id*='feriado']",
        "input[id*='feriados']",
        "input[type='checkbox']:nth-of-type(3)",
        "label:has-text('Feriado') input",
        "label:has-text('feriado') input",
        "label:has-text('Feriados') input",
        "label:has-text('Considerar Feriados') input",
    ]

    BOTAO_CALCULAR = [
        "#calcular",
        "#btnCalcular",
        "#calcularDiasUteis",
        "button:has-text('Calcular')",
        "button:has-text('Calcular Agora')",
        "button:has-text('Calcular Dias')",
        "input[type='submit'][value*='Calcular']",
        "button[name*='calcular']",
        "button[id*='calcular']",
        "a:has-text('Calcular')",
        ".btn:has-text('Calcular')",
        ".button:has-text('Calcular')",
        ".wp-block-button__link:has-text('Calcular')",
        "form input[type='submit']",
        "form button[type='submit']",
    ]

    RESULTADO = [
        "#resultado",
        "#resultadoDiasUteis",
        "#diasUteis",
        "#totalDias",
        "#qtdeDiasUteis",
        "div[class*='resultado']",
        "div[class*='result']",
        "div[id*='resultado']",
        "div[id*='result']",
        "span[class*='resultado']",
        "span[id*='resultado']",
        "p[class*='resultado']",
        "strong:has-text('úteis')",
        "strong:has-text('dias')",
        "b:has-text('úteis')",
        ".dias-uteis-resultado",
        ".dias_uteis_resultado",
        ".resultado-dias-uteis",
        ".resultado-dias",
    ]

    MENSAGEM_ERRO = [
        "#mensagemErro",
        "#msgErro",
        "div[class*='erro']",
        "div[class*='error']",
        "span[class*='erro']",
        "span[class*='error']",
        "label[class*='erro']",
        ".message-error",
        ".mensagem-erro",
        ".text-danger",
        ".erro",
        "[role='alert']",
        "[aria-invalid='true'] ~ *",
    ]

    # =========================================================================
    # Helpers: inicializacao / contexto iframe
    # =========================================================================
    def __init__(self, page):
        super().__init__(page)
        self._calc_frame = None
        self._page_orig = None

    # ------------- compatibilidade iframe (mesma logica juros_page) --------
    def _active_page(self):
        """Retorna Frame correto (iframe calculadora) ou page top-level."""
        return getattr(self, "_calc_frame", None) or self.page

    def _swap_active_context(self, ctx):
        """Troca self.page para o Frame do iframe, para que os metodos
        herdados de BasePage atuem no contexto CALCULADORA (nao blog)."""
        if not getattr(self, "_page_orig", None):
            self._page_orig = self.page
        self.page = ctx or self._page_orig

    def _restore_top_context(self):
        if getattr(self, "_page_orig", None):
            self.page = self._page_orig

    def _ensure_calculadora_context(self):
        """Localiza o iframe da calculadora (URL v4.html), usando exatamente
        o mesmo fluxo da CalculadoraInvestimentosPage.

        Ordem busca:
          1) page.frames por IFRAME_URL_KEYWORDS (melhor metodo)
          2) frames com #dataInicial / #dataFinal / #calcular (inputs conhecidos)
          3) frames com texto 'dias úteis' / 'Data Inicial' / 'Calcular'
          4) fallback: top-level page
        """
        self._wait_cloudflare_bypass(max_attempts=6, wait_ms=2000)
        page = self.page if not getattr(self, "_page_orig", None) else self._page_orig

        keywords_conteudo = [
            "Dias Úteis",
            "Dias Uteis",
            "dias úteis",
            "dias uteis",
            "Data Inicial",
            "Data Final",
            "Calcular Dias",
            "úteis:",
        ]

        # Passo 1: melhor metodo - filtrar page.frames por URL conhecida
        for kw in self.IFRAME_URL_KEYWORDS:
            for frame in page.frames:
                try:
                    furl = getattr(frame, "url", "") or ""
                    if kw.lower() in furl.lower():
                        try:
                            frame.wait_for_load_state("domcontentloaded", timeout=8000)
                        except Exception:
                            pass
                        try:
                            frame.wait_for_timeout(1200)
                        except Exception:
                            pass
                        self._calc_frame = frame
                        self._swap_active_context(frame)
                        return frame
                except Exception:
                    continue

        # Passo 2: fallback - any frame with known ids / fields
        for frame in page.frames:
            try:
                if (
                    frame.locator("#dataInicial").count() > 0
                    or frame.locator("#dataFinal").count() > 0
                    or frame.locator("#calcular").count() > 0
                    or frame.locator("#resultadoDiasUteis").count() > 0
                    or frame.locator("#resultado").count() > 0
                ):
                    try:
                        frame.wait_for_timeout(1000)
                    except Exception:
                        pass
                    self._calc_frame = frame
                    self._swap_active_context(frame)
                    return frame
            except Exception:
                continue
            try:
                for kw in keywords_conteudo:
                    try:
                        if frame.get_by_text(kw, exact=False).count() > 0:
                            try:
                                frame.wait_for_timeout(800)
                            except Exception:
                                pass
                            self._calc_frame = frame
                            self._swap_active_context(frame)
                            return frame
                    except Exception:
                        continue
            except Exception:
                continue

        # Passo 3: ultimo recurso - top level
        self._calc_frame = page
        self._swap_active_context(page)
        return page

    # =========================================================================
    # FLUXO 1: ACESSAR PELO MENU PRINCIPAL (passos BLAZEMETER - arquivo
    # calculadora_DIAS_UTEIS-Selenium-python-wd-unittest.py)
    # =========================================================================
    def acessar_home_blog(self):
        """Navega para a HOME do blog.agibank.com.br (ponto de partida do
        fluxo capturado no BlazeMeter)."""
        self.navigate(self.HOME_BLOG_URL)
        self.wait_for_load()
        self._wait_cloudflare_bypass(max_attempts=8, wait_ms=2500)
        self.page.wait_for_timeout(1500)

    def acessar_pelo_menu_principal(self):
        """
        Repete EXATAMENTE os passos capturados no arquivo Selenium:

          Passo 1 (linha 22 original):
            driver.get("https://blog.agibank.com.br/")   (home)
          Passo 2 (linha 24 original):
            click  css=#menu-item-24257 > a.menu-link > span.menu-text

        Ao final: self.page estara na pagina da calculadora dias uteis,
        e _ensure_calculadora_context() podera localizar o iframe.
        """
        if self.HOME_BLOG_URL.rstrip("/") not in (getattr(self.page, "url", "") or "").rstrip("/"):
            self.acessar_home_blog()

        # --- Passo BlazeMeter: menu-item-24257 ---
        try:
            self.wait_for_element(self.MENU_ITEM_DIAS_UTEIS_BLAZEMETER[0], timeout=25000)
        except Exception:
            try:
                self.page.wait_for_load_state("networkidle", timeout=30000)
            except Exception:
                pass

        # Soft: primeiro tenta abrir dropdown Ferramentas, se houver
        try:
            drp = self._find_locator(
                self.MENU_BLOG_ABRIR_DROPDOWN_FERRAMENTAS,
                fallback_text="Ferramentas",
            )
            try:
                drp_el = self._build_locator(drp)
                if drp_el and drp_el.first.is_visible():
                    drp_el.first.click()
                    self.page.wait_for_timeout(600)
            except Exception:
                pass
        except Exception:
            pass

        try:
            locator_menu = self._find_locator(
                self.MENU_ITEM_DIAS_UTEIS_BLAZEMETER,
                fallback_text="Dias Úteis",
            )
            self.click_element(locator_menu)
            self.wait_for_load()
            self.page.wait_for_timeout(1500)
        except Exception as err:
            raise RuntimeError(
                "Navegacao por menu (BlazeMeter dias uteis) FALHOU: nao foi "
                "possivel clicar no menu-item-24257. Verifique se o site mudou "
                "a estrutura do menu. Exception original: "
                f"{err.__class__.__name__}: {err}"
            ) from err

        # Final: prepara contexto iframe
        self._ensure_calculadora_context()

    # ------------------------------------------------------------------
    # Fluxo alternativo (usado se menu falhar / testes rapidos):
    # acessar URL calculadora direto
    # ------------------------------------------------------------------
    def acessar_pagina_direto(self):
        """Acesso direto (pula menu). Bom para testes de regressao rapidos."""
        self.navigate(self.URL)
        self.wait_for_load()
        self._ensure_calculadora_context()

    def acessar_pagina(self):
        """
        Metodo de acesso PADRAO. Chama acessar_pagina_direto.
        Para o fluxo BlazeMeter (click no menu 24257), use acessar_pelo_menu_principal().
        """
        self.acessar_pagina_direto()

    # =========================================================================
    # Helpers de data: YYYY-MM-DD <-> DD/MM/YYYY (formato nativo BR)
    # =========================================================================
    @staticmethod
    def _converter_para_ddmmyyyy(data_iso):
        """Converte datas '2026-01-05' ou '05/01/2026' -> '05/01/2026'."""
        if not data_iso:
            return ""
        s = str(data_iso).strip()
        if "/" in s and s.count("/") == 2:
            a, b, c = s.split("/")
            if len(c) == 4:
                return s
        if "-" in s and s.count("-") == 2:
            y, m, d = s.split("-")
            if len(y) == 4:
                return f"{d.zfill(2)}/{m.zfill(2)}/{y}"
        return s

    def _preencher_campo_data(self, opcoes_locator, data_iso):
        """Preenche data com 3 estrategias:
           1) Locator nativo type=date (preenche YYYY-MM-DD direto)
           2) Fallback tipo texto: converte p/ DD/MM/AAAA + Ctrl+A + type char-a-char
        """
        self._ensure_calculadora_context()
        ctx = self._active_page()

        data_br = self._converter_para_ddmmyyyy(data_iso)

        locator_key = self._find_locator(opcoes_locator)
        for raw in [locator_key] + opcoes_locator:
            try:
                el_s = raw if hasattr(raw, "fill") else None
                if not el_s:
                    cands = self._build_locator(raw)
                    if not cands:
                        continue
                    el_s = cands.first
                if not el_s or el_s.count() == 0:
                    continue
                if not el_s.is_visible():
                    continue

                try:
                    el_s.scroll_into_view_if_needed(timeout=5000)
                except Exception:
                    pass

                # Tentativa 1: nativa ISO (se input for type=date)
                for tentativa_valor in [data_iso, data_br]:
                    if not tentativa_valor:
                        continue
                    try:
                        try:
                            el_s.click()
                        except Exception:
                            pass
                        for seq in [("Control+A", "Delete"), ("Control+A", "Backspace")]:
                            try:
                                for k in seq:
                                    try:
                                        el_s.press(k)
                                    except Exception:
                                        pass
                            except Exception:
                                pass
                        try:
                            el_s.fill("")
                        except Exception:
                            pass
                        el_s.fill(tentativa_valor)
                        return True
                    except Exception:
                        try:
                            for seq in [("Control+A", "Delete")]:
                                for k in seq:
                                    try:
                                        el_s.press(k)
                                    except Exception:
                                        pass
                            el_s.type(tentativa_valor, delay=70)
                            return True
                        except Exception:
                            continue
            except Exception:
                continue
        return False

    # =========================================================================
    # FLUXO 2: INTERACAO COM FORMULARIO DIAS UTEIS
    # =========================================================================
    def marcar_checkbox(self, opcoes, marcar):
        self._ensure_calculadora_context()
        ctx = self._active_page()

        for raw in opcoes:
            try:
                els = ctx.locator(raw)
                n = els.count()
                for i in range(n):
                    el = els.nth(i)
                    try:
                        el.wait_for(state="visible", timeout=3000)
                    except Exception:
                        continue
                    if not el.is_visible():
                        continue
                    if marcar and not el.is_checked():
                        try:
                            el.check()
                            return
                        except Exception:
                            try:
                                el.click()
                                return
                            except Exception:
                                continue
                    elif not marcar and el.is_checked():
                        try:
                            el.uncheck()
                            return
                        except Exception:
                            try:
                                el.click()
                                return
                            except Exception:
                                continue
            except Exception:
                continue

        # Fallback label-based: click on label text
        try:
            all_labels = ctx.locator("label")
            cnt = all_labels.count()
            target_words = None
            if opcoes is self.CHECKBOX_SABADO:
                target_words = ["Sábado", "Sabado", "sábado", "sabado"]
            elif opcoes is self.CHECKBOX_DOMINGO:
                target_words = ["Domingo", "domingo"]
            elif opcoes is self.CHECKBOX_FERIADOS:
                target_words = ["Feriado", "feriado", "Feriados", "feriados"]

            if target_words:
                for w in target_words:
                    for i in range(cnt):
                        try:
                            lab = all_labels.nth(i)
                            txt = (lab.inner_text() or "").strip()
                            if w.lower() in txt.lower():
                                lab.click()
                                return
                        except Exception:
                            continue
        except Exception:
            pass

    def preencher_data_inicial(self, data):
        self._preencher_campo_data(self.INPUT_DATA_INICIAL, data)

    def preencher_data_final(self, data):
        self._preencher_campo_data(self.INPUT_DATA_FINAL, data)

    def marcar_sabado(self, marcar=True):
        self.marcar_checkbox(self.CHECKBOX_SABADO, marcar)

    def marcar_domingo(self, marcar=True):
        self.marcar_checkbox(self.CHECKBOX_DOMINGO, marcar)

    def marcar_feriados(self, marcar=True):
        self.marcar_checkbox(self.CHECKBOX_FERIADOS, marcar)

    def clicar_calcular(self):
        self._ensure_calculadora_context()
        ctx = self._active_page()

        last_err = None
        for txt in ["Calcular", "Calcular Agora", "Calcular Dias Úteis", "Calcular Dias Uteis"]:
            try:
                btns = ctx.get_by_role("button", name=re.compile(txt, re.I))
                for i in range(btns.count()):
                    try:
                        b = btns.nth(i)
                        if b.is_visible():
                            b.click()
                            self.wait_for_load()
                            try:
                                ctx.wait_for_timeout(1500)
                            except Exception:
                                pass
                            return
                    except Exception as err:
                        last_err = err
                        continue
            except Exception as err:
                last_err = err

        try:
            locator = self._find_locator(self.BOTAO_CALCULAR, fallback_text="Calcular")
            self.click_element(locator)
            self.wait_for_load()
            try:
                ctx.wait_for_timeout(1500)
            except Exception:
                pass
        except Exception as err:
            if last_err is None:
                raise

    def obter_resultado(self):
        self._ensure_calculadora_context()
        ctx = self._active_page()

        # Tentativa 1: por textos chave
        for texto_chave in [
            "dias úteis",
            "dias uteis",
            "Dias Úteis:",
            "Dias Uteis:",
            "úteis:",
            "uteis:",
        ]:
            try:
                els = ctx.get_by_text(re.compile(texto_chave, re.I))
                for i in range(els.count()):
                    try:
                        el = els.nth(i)
                        txt = (el.inner_text() or "").strip()
                        if txt and any(c.isdigit() for c in txt):
                            return txt
                    except Exception:
                        continue
            except Exception:
                continue

        # Tentativa 2: por locators de resultado + fallback
        raw = self._find_locator(self.RESULTADO, fallback_text="dias úteis")
        try:
            if self.is_element_visible(raw, timeout=10000):
                t = self.get_text(raw)
                if t:
                    return t.strip()
        except Exception:
            pass

        for loc in self.RESULTADO:
            try:
                candidates = self._build_locator(loc)
                for cand in candidates or []:
                    try:
                        if cand.count() > 0:
                            for i in range(cand.count()):
                                c = cand.nth(i)
                                try:
                                    if c.is_visible():
                                        t = c.inner_text().strip()
                                        if t:
                                            return t
                                except Exception:
                                    try:
                                        t = c.text_content().strip()
                                        if t:
                                            return t
                                    except Exception:
                                        continue
                    except Exception:
                        continue
            except Exception:
                continue

        # Tentativa 3: fallback - encontra qualquer numero + "dias" proximo
        try:
            tudo = ctx.inner_text("body", timeout=5000) or ""
            m = re.search(r"(\d+)\s*(?:dias\s*úteis|dias\s*uteis|dias)", tudo, re.I)
            if m:
                return m.group(0)
        except Exception:
            pass
        return ""

    def obter_mensagem_erro(self):
        self._ensure_calculadora_context()
        ctx = self._active_page()
        try:
            raw = self._find_locator(self.MENSAGEM_ERRO, fallback_text="obrigat")
            if self.is_element_visible(raw, timeout=8000):
                return self.get_text(raw) or ""
        except Exception:
            pass

        for loc in self.MENSAGEM_ERRO:
            try:
                el = ctx.locator(loc)
                for i in range(el.count()):
                    cand = el.nth(i)
                    try:
                        if cand.is_visible():
                            t = cand.inner_text().strip()
                            if t:
                                return t
                    except Exception:
                        continue
            except Exception:
                continue
        return ""

    def calcular_dias_uteis(self, data_inicial, data_final, sabado=False, domingo=False, feriados=True):
        self.preencher_data_inicial(data_inicial)
        self.preencher_data_final(data_final)
        self.marcar_sabado(sabado)
        self.marcar_domingo(domingo)
        self.marcar_feriados(feriados)
        self.clicar_calcular()
