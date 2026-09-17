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

    def _find_locator(self, options):
        for locator in options:
            try:
                if self.page.locator(locator).count() > 0:
                    return locator
            except Exception:
                continue
        return options[0]

    def acessar_pagina(self):
        self.navigate(self.URL)
        self.wait_for_load()

    def clicar_lupa(self):
        locator = self._find_locator(self.BOTAO_LUPA)
        self.click_element(locator)

    def preencher_campo_pesquisa(self, texto):
        locator = self._find_locator(self.INPUT_PESQUISA)
        self.wait_for_element(locator, timeout=15000)
        self.fill_input(locator, texto)

    def submeter_pesquisa(self):
        locator = self._find_locator(self.BOTAO_SUBMIT_PESQUISA)
        try:
            if self.page.locator(locator).count() > 0:
                self.click_element(locator)
            else:
                self.page.keyboard.press("Enter")
        except Exception:
            self.page.keyboard.press("Enter")
        self.wait_for_load()

    def realizar_pesquisa(self, termo):
        self.clicar_lupa()
        self.preencher_campo_pesquisa(termo)
        self.submeter_pesquisa()

    def quantidade_resultados(self):
        locator = self._find_locator(self.RESULTADOS_PESQUISA)
        try:
            count = self.page.locator(locator).count()
            return count
        except Exception:
            return 0

    def obter_titulos_resultados(self):
        locator = self._find_locator(self.RESULTADOS_PESQUISA)
        titulos = []
        try:
            count = self.page.locator(locator).count()
            for i in range(min(count, 10)):
                try:
                    artigo = self.page.locator(locator).nth(i)
                    titulo_locator = self._find_locator(self.TITULO_ARTIGO)
                    if artigo.locator(titulo_locator).count() > 0:
                        texto = artigo.locator(titulo_locator).first.inner_text().strip()
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
        page_text = self.page.inner_text("body").lower()
        return termo_lower in page_text

    def verificar_mensagem_sem_resultado(self):
        locator = self._find_locator(self.MENSAGEM_NENHUM_RESULTADO)
        for loc in self.MENSAGEM_NENHUM_RESULTADO:
            try:
                self.page.locator(loc).first.wait_for(state="visible", timeout=5000)
                return True
            except Exception:
                continue
        return False

    def verificar_url_contem_pesquisa(self, termo):
        url = self.page.url
        return termo in url or "s=" in url or "search" in url.lower()
