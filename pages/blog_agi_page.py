import re
from pages.base_page import BasePage


class BlogAgiPage(BasePage):
    URL = "https://blogdoagi.com.br/"

    BOTAO_LUPA = [
        'button[aria-label*="Pesquisar"]',
        'button[aria-label*="Buscar"]',
        'button[class*="search"]',
        'button[class*="Search"]',
        'a[class*="search"]',
        'a[class*="Search"]',
        'button[class*="lupa"]',
        'div[class*="search"] svg',
        'div[class*="Search"] svg',
        '.header-search',
        '.search-toggle',
        '#searchsubmit',
        'svg[class*="search-icon"]',
    ]

    INPUT_PESQUISA = [
        'input[name="s"]',
        'input.search-field',
        'input[placeholder="Digite sua busca"]',
        'input[placeholder*="Digite sua busca"]',
        'input[name="search"]',
        'input[id="search"]',
        'input[type="search"]',
        'input[placeholder*="Pesquisar"]',
        'input[placeholder*="pesquisar"]',
        'input[placeholder*="Buscar"]',
        'input[placeholder*="buscar"]',
        'input[aria-label*="Pesquisar"]',
        'input[aria-label*="pesquisar"]',
        '.search-field',
        '.search-input',
        '#search-field',
    ]

    BOTAO_SUBMIT_PESQUISA = [
        'button[type="submit"]',
        'input[type="submit"][value*="Pesquisar"]',
        'input[type="submit"][value*="Buscar"]',
        'button:has-text("Pesquisar")',
        'button:has-text("Buscar")',
        '.search-submit',
        '#searchsubmit',
    ]

    RESULTADOS_PESQUISA = [
        'article',
        'div[class*="resultado"]',
        'div[class*="search-result"]',
        'div[class*="search-results"]',
        '.search-results',
        '.search_result',
        '.archive',
        '.posts',
        '.blog-posts',
        'main article',
        '#primary article',
    ]

    TITULO_ARTIGO = [
        'h1',
        'h2',
        '.entry-title',
        '.post-title',
        '.article-title',
        'article h2',
        'article h1',
        'h1[class*="title"]',
        'h2[class*="title"]',
    ]

    MENSAGEM_NENHUM_RESULTADO = [
        'div:has-text("Nenhum resultado")',
        'div:has-text("nenhum resultado")',
        'p:has-text("Nenhum resultado")',
        'p:has-text("nenhum resultado")',
        'h1:has-text("Nada encontrado")',
        'h2:has-text("Nada encontrado")',
        'h3:has-text("Nada encontrado")',
        '.no-results',
        '.not-found',
        '.error-404',
    ]

    def acessar_pagina(self):
        self.navigate(self.URL)
        self.wait_for_load()

    def clicar_lupa(self):
        locator = self._find_locator(self.BOTAO_LUPA, fallback_text="Pesquisar")
        try:
            self.click_element(locator)
        except Exception:
            try:
                botao = self.page.get_by_role("button", name=re.compile(r"(?i)pesquisar|buscar|lupa|search"))
                if botao.count() > 0:
                    botao.first.click()
            except Exception:
                pass

    def preencher_campo_pesquisa(self, texto):
        locator = self._find_locator(self.INPUT_PESQUISA)
        try:
            self.wait_for_element(locator, timeout=15000)
        except Exception:
            pass
        try:
            self.fill_input(locator, texto)
        except Exception:
            try:
                campo = self.page.get_by_role("searchbox", name=re.compile(r"(?i)pesquisar|buscar|search"))
                if campo.count() > 0:
                    campo.first.fill(texto)
                else:
                    self.page.keyboard.type(texto)
            except Exception:
                self.page.keyboard.type(texto)

    def submeter_pesquisa(self):
        locator = self._find_locator(self.BOTAO_SUBMIT_PESQUISA)
        try:
            candidates = self._build_locator(locator)
            achou = False
            for cand in candidates or []:
                if cand.count() > 0 and cand.first.is_visible():
                    cand.first.click()
                    achou = True
                    break
            if not achou:
                self.page.keyboard.press("Enter")
        except Exception:
            self.page.keyboard.press("Enter")
        self.wait_for_load()

    def realizar_pesquisa(self, termo):
        self.clicar_lupa()
        self.page.wait_for_timeout(400)
        self.preencher_campo_pesquisa(termo)
        self.submeter_pesquisa()

    def quantidade_resultados(self):
        raw = self._find_locator(self.RESULTADOS_PESQUISA)
        try:
            el = self._apply_locator(raw)
            if "article" in raw.lower() or "results" in raw.lower() or "posts" in raw.lower():
                return self.page.locator(raw).count()
            return el.count()
        except Exception:
            return 0

    def obter_titulos_resultados(self):
        raw = self._find_locator(self.RESULTADOS_PESQUISA)
        titulos = []
        try:
            artigos = self.page.locator(raw)
            count = artigos.count()
            for i in range(min(count, 10)):
                try:
                    artigo = artigos.nth(i)
                    titulo_raw = self._find_locator(self.TITULO_ARTIGO)
                    titulo_cand = self._build_locator(titulo_raw)
                    texto = ""
                    for tc in titulo_cand or []:
                        try:
                            if artigo.locator(titulo_raw).count() > 0:
                                texto = artigo.locator(titulo_raw).first.inner_text().strip()
                                break
                        except Exception:
                            continue
                    if not texto:
                        texto = artigo.inner_text().strip().splitlines()[0].strip() if artigo.inner_text().strip() else ""
                    if texto:
                        titulos.append(texto)
                except Exception:
                    continue
        except Exception:
            pass
        return titulos

    def verificar_termo_em_resultados(self, termo):
        resultados = self.obter_titulos_resultados()
        termo_lower = termo.lower()
        for titulo in resultados:
            if termo_lower in titulo.lower():
                return True
        try:
            page_text = self.page.inner_text("body").lower()
            return termo_lower in page_text
        except Exception:
            return False

    def verificar_mensagem_sem_resultado(self):
        raw = self._find_locator(self.MENSAGEM_NENHUM_RESULTADO, fallback_text="Nenhum resultado")
        for loc in [raw] + self.MENSAGEM_NENHUM_RESULTADO:
            try:
                candidates = self._build_locator(loc) if not loc.startswith("__text__:") else [self.page.get_by_text(loc[len("__text__:"):], exact=False)]
                for cand in candidates or []:
                    try:
                        cand.first.wait_for(state="visible", timeout=5000)
                        return True
                    except Exception:
                        continue
            except Exception:
                continue
        return False

    def verificar_url_contem_pesquisa(self, termo):
        url = self.page.url
        return termo in url or "s=" in url or "search" in url.lower()
