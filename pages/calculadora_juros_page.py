from pages.base_page import BasePage


class CalculadoraJurosCompostosPage(BasePage):
    URL = "https://blog.agibank.com.br/como-calcular-juros-compostos/"

    ABA_DIVIDA = [
        'xpath=//*[@id="choiceScreen"]/div[1]/div[1]/span',
        '#choiceScreen div:first-child div:first-child span',
        '#choiceScreen span:has-text("Dívida")',
        '#choiceScreen span:has-text("Divida")',
        '[id="choiceScreen"] [id*="divida"]',
        'button:has-text("Dívida")',
        'a:has-text("Dívida")',
        'div[role="tab"]:has-text("Dívida")',
        'li:has-text("Dívida")',
        '[data-tab*="divida"]',
        '[aria-label*="Dívida"]',
        '.tab:has-text("Dívida")',
        '.nav-link:has-text("Dívida")',
        'span:has-text("Dívida")',
        'span:has-text("Divida")',
    ]

    ABA_INVESTIMENTO = [
        'xpath=//*[@id="choiceScreen"]/div[2]/div[1]/span',
        'xpath=//*[@id="choiceScreen"]/div[1]/div[2]/span',
        '#choiceScreen span:has-text("Investimento")',
        '#choiceScreen div:nth-child(2) div:nth-child(1) span',
        '[id="choiceScreen"] [id*="investimento"]',
        'button:has-text("Investimento")',
        'a:has-text("Investimento")',
        'div[role="tab"]:has-text("Investimento")',
        'li:has-text("Investimento")',
        '[data-tab*="investimento"]',
        '[aria-label*="Investimento"]',
        '.tab:has-text("Investimento")',
        '.nav-link:has-text("Investimento")',
        'span:has-text("Investimento")',
    ]

    INPUT_VALOR_INICIAL = [
        'input[name*="valor_inicial"]',
        'input[name*="valor-inicial"]',
        'input[name*="capital"]',
        'input[name*="montante"]',
        'input[name*="principal"]',
        'input[id*="valor_inicial"]',
        'input[id*="valor-inicial"]',
        'input[id*="capital"]',
        'input[id*="montante"]',
        'input[id*="principal"]',
        'input[placeholder*="Valor Inicial"]',
        'input[placeholder*="valor inicial"]',
        'input[placeholder*="R$"]',
        'input[aria-label*="Valor Inicial"]',
        'input[aria-label*="valor inicial"]',
    ]

    INPUT_APORTE_MENSAL = [
        'input[name*="aporte"]',
        'input[name*="mensal"]',
        'input[name*="contribuicao"]',
        'input[name*="parcela"]',
        'input[id*="aporte"]',
        'input[id*="mensal"]',
        'input[id*="contribuicao"]',
        'input[id*="parcela"]',
        'input[placeholder*="Aporte"]',
        'input[placeholder*="aporte"]',
        'input[placeholder*="mensal"]',
        'input[placeholder*="Parcela"]',
        'input[placeholder*="parcela"]',
        'input[aria-label*="Aporte"]',
        'input[aria-label*="aporte"]',
    ]

    INPUT_TAXA_JUROS = [
        'input[name*="taxa"]',
        'input[name*="juros"]',
        'input[name*="percentual"]',
        'input[name*="selic"]',
        'input[id*="taxa"]',
        'input[id*="juros"]',
        'input[id*="percentual"]',
        'input[placeholder*="Taxa"]',
        'input[placeholder*="taxa"]',
        'input[placeholder*="Juros"]',
        'input[placeholder*="juros"]',
        'input[placeholder*="%"]',
        'input[aria-label*="Taxa"]',
        'input[aria-label*="taxa"]',
    ]

    SELECT_PERIODICIDADE_TAXA = [
        'select[name*="periodo"]',
        'select[name*="periodicidade"]',
        'select[name*="prazo"]',
        'select[id*="periodo"]',
        'select[id*="periodicidade"]',
        'select[id*="prazo"]',
        'select:has(option:has-text("mensal"))',
        'select:has(option:has-text("anual"))',
    ]

    INPUT_PERIODO = [
        'input[name*="prazo"]',
        'input[name*="periodo"]',
        'input[name*="tempo"]',
        'input[name*="meses"]',
        'input[name*="anos"]',
        'input[id*="prazo"]',
        'input[id*="periodo"]',
        'input[id*="tempo"]',
        'input[id*="meses"]',
        'input[id*="anos"]',
        'input[placeholder*="Prazo"]',
        'input[placeholder*="prazo"]',
        'input[placeholder*="Período"]',
        'input[placeholder*="período"]',
        'input[placeholder*="Periodo"]',
        'input[placeholder*="periodo"]',
        'input[placeholder*="Mês"]',
        'input[placeholder*="mês"]',
        'input[placeholder*="Ano"]',
        'input[placeholder*="ano"]',
        'input[aria-label*="Prazo"]',
        'input[aria-label*="prazo"]',
        'input[aria-label*="Período"]',
        'input[aria-label*="período"]',
    ]

    SELECT_PERIODICIDADE_PERIODO = [
        'select[name*="tipo_periodo"]',
        'select[name*="unidade"]',
        'select[name*="tipo_prazo"]',
        'select[id*="tipo_periodo"]',
        'select[id*="unidade"]',
        'select[id*="tipo_prazo"]',
        'select:has(option:has-text("Meses"))',
        'select:has(option:has-text("Anos"))',
    ]

    BOTAO_CALCULAR = [
        'button:has-text("Calcular")',
        'button:has-text("Simular")',
        'input[type="submit"][value*="Calcular"]',
        'input[type="submit"][value*="Simular"]',
        'button[name*="calcular"]',
        'button[name*="simular"]',
        'button[id*="calcular"]',
        'button[id*="simular"]',
        'a:has-text("Calcular")',
        'a:has-text("Simular")',
        '.btn:has-text("Calcular")',
        '.btn:has-text("Simular")',
        '.button:has-text("Calcular")',
        '.button:has-text("Simular")',
        '.wp-block-button__link:has-text("Calcular")',
        '.wp-block-button__link:has-text("Simular")',
    ]

    RESULTADO_MONTANTE = [
        'div[class*="resultado"]',
        'div[class*="result"]',
        'div[class*="montante"]',
        'div[class*="total"]',
        'div[class*="final"]',
        'div[id*="resultado"]',
        'div[id*="result"]',
        'div[id*="montante"]',
        'div[id*="total"]',
        'div[id*="final"]',
        'span[class*="resultado"]',
        'span[class*="result"]',
        'span[class*="montante"]',
        'span[class*="total"]',
        'span[id*="resultado"]',
        'span[id*="result"]',
        'span[id*="montante"]',
        'span[id*="total"]',
        'strong:has-text("R$")',
        'b:has-text("R$")',
        '.juros-resultado',
        '.juros_resultado',
        '.valor-total',
        '.valor_total',
    ]

    MENSAGEM_ERRO = [
        'div[class*="erro"]',
        'div[class*="error"]',
        'span[class*="erro"]',
        'span[class*="error"]',
        'label[class*="erro"]',
        '.message-error',
        '.mensagem-erro',
        '.text-danger',
        '.text-danger',
    ]

    def acessar_pagina(self):
        self.navigate(self.URL)
        self.wait_for_load()

    def selecionar_aba_divida(self):
        locator = self._find_locator(self.ABA_DIVIDA, fallback_text="Dívida")
        self.click_element(locator)
        self.wait_for_load()

    def selecionar_aba_investimento(self):
        locator = self._find_locator(self.ABA_INVESTIMENTO, fallback_text="Investimento")
        self.click_element(locator)
        self.wait_for_load()

    def preencher_valor_inicial(self, valor):
        locator = self._find_locator(self.INPUT_VALOR_INICIAL)
        self.fill_input(locator, str(valor))

    def preencher_aporte_mensal(self, valor):
        locator = self._find_locator(self.INPUT_APORTE_MENSAL)
        self.fill_input(locator, str(valor))

    def preencher_taxa_juros(self, taxa):
        locator = self._find_locator(self.INPUT_TAXA_JUROS)
        self.fill_input(locator, str(taxa))

    def selecionar_periodicidade_taxa(self, periodicidade="mensal"):
        locator = self._find_locator(self.SELECT_PERIODICIDADE_TAXA)
        try:
            self.select_dropdown(locator, periodicidade)
        except Exception:
            try:
                if "ano" in periodicidade.lower():
                    self.select_dropdown(locator, "anual")
                else:
                    self.select_dropdown(locator, "mensal")
            except Exception:
                pass

    def preencher_periodo(self, periodo):
        locator = self._find_locator(self.INPUT_PERIODO)
        self.fill_input(locator, str(periodo))

    def selecionar_unidade_periodo(self, unidade="meses"):
        locator = self._find_locator(self.SELECT_PERIODICIDADE_PERIODO)
        try:
            self.select_dropdown(locator, unidade)
        except Exception:
            try:
                if "ano" in unidade.lower():
                    self.select_dropdown(locator, "anos")
                else:
                    self.select_dropdown(locator, "meses")
            except Exception:
                pass

    def clicar_calcular(self):
        locator = self._find_locator(self.BOTAO_CALCULAR, fallback_text="Calcular")
        self.click_element(locator)
        self.wait_for_load()

    def obter_resultado(self):
        raw = self._find_locator(self.RESULTADO_MONTANTE, fallback_text="R$")
        if self.is_element_visible(raw, timeout=15000):
            return self.get_text(raw)
        for loc in self.RESULTADO_MONTANTE:
            try:
                candidates = self._build_locator(loc)
                for cand in candidates or []:
                    if cand.count() > 0 and cand.first.is_visible():
                        return cand.first.inner_text().strip()
            except Exception:
                continue
        return ""

    def obter_mensagem_erro(self):
        raw = self._find_locator(self.MENSAGEM_ERRO, fallback_text="obrigat")
        if self.is_element_visible(raw, timeout=10000):
            return self.get_text(raw)
        for loc in self.MENSAGEM_ERRO:
            try:
                candidates = self._build_locator(loc)
                for cand in candidates or []:
                    if cand.count() > 0 and cand.first.is_visible():
                        return cand.first.inner_text().strip()
            except Exception:
                continue
        return ""

    def calcular_investimento(self, valor_inicial, aporte_mensal, taxa_juros, periodo,
                               periodicidade_taxa="mensal", unidade_periodo="meses"):
        self.selecionar_aba_investimento()
        self.preencher_valor_inicial(valor_inicial)
        self.preencher_aporte_mensal(aporte_mensal)
        self.preencher_taxa_juros(taxa_juros)
        self.selecionar_periodicidade_taxa(periodicidade_taxa)
        self.preencher_periodo(periodo)
        self.selecionar_unidade_periodo(unidade_periodo)
        self.clicar_calcular()

    def calcular_divida(self, valor_inicial, aporte_mensal, taxa_juros, periodo,
                        periodicidade_taxa="mensal", unidade_periodo="meses"):
        self.selecionar_aba_divida()
        self.preencher_valor_inicial(valor_inicial)
        self.preencher_aporte_mensal(aporte_mensal)
        self.preencher_taxa_juros(taxa_juros)
        self.selecionar_periodicidade_taxa(periodicidade_taxa)
        self.preencher_periodo(periodo)
        self.selecionar_unidade_periodo(unidade_periodo)
        self.clicar_calcular()
