from pages.base_page import BasePage


class CalculadoraDiasUteisPage(BasePage):
    URL = "https://blog.agibank.com.br/calculadora-dias-uteis/"

    INPUT_DATA_INICIAL = [
        'input[name*="data_inicial"]',
        'input[name*="data-inicial"]',
        'input[id*="data_inicial"]',
        'input[id*="data-inicial"]',
        'input[type="date"]:nth-child(1)',
        'input[placeholder*="Data Inicial"]',
        'input[placeholder*="data inicial"]',
        'input[data-date*="inicial"]',
        'input[aria-label*="Data Inicial"]',
    ]

    INPUT_DATA_FINAL = [
        'input[name*="data_final"]',
        'input[name*="data-final"]',
        'input[id*="data_final"]',
        'input[id*="data-final"]',
        'input[type="date"]:nth-child(2)',
        'input[placeholder*="Data Final"]',
        'input[placeholder*="data final"]',
        'input[data-date*="final"]',
        'input[aria-label*="Data Final"]',
    ]

    CHECKBOX_SABADO = [
        'input[name*="sabado"]',
        'input[name*="sab"]',
        'input[id*="sabado"]',
        'input[id*="sab"]',
        'input[type="checkbox"]:nth-child(1)',
        'label:has-text("Sábado") input',
        'label:has-text("Sabado") input',
    ]

    CHECKBOX_DOMINGO = [
        'input[name*="domingo"]',
        'input[name*="dom"]',
        'input[id*="domingo"]',
        'input[id*="dom"]',
        'input[type="checkbox"]:nth-child(2)',
        'label:has-text("Domingo") input',
    ]

    CHECKBOX_FERIADOS = [
        'input[name*="feriado"]',
        'input[name*="feriados"]',
        'input[id*="feriado"]',
        'input[id*="feriados"]',
        'label:has-text("Feriado") input',
        'label:has-text("feriado") input',
    ]

    BOTAO_CALCULAR = [
        'button:has-text("Calcular")',
        'button:has-text("Calcular Agora")',
        'input[type="submit"][value*="Calcular"]',
        'button[name*="calcular"]',
        'button[id*="calcular"]',
        'a:has-text("Calcular")',
        '.btn:has-text("Calcular")',
        '.button:has-text("Calcular")',
        '.wp-block-button__link:has-text("Calcular")',
    ]

    RESULTADO = [
        'div[class*="resultado"]',
        'div[class*="result"]',
        'div[id*="resultado"]',
        'div[id*="result"]',
        'span[class*="resultado"]',
        'span[id*="resultado"]',
        'p[class*="resultado"]',
        'strong:has-text("úteis")',
        'strong:has-text("dias")',
        '.dias-uteis-resultado',
        '.dias_uteis_resultado',
    ]

    MENSAGEM_ERRO = [
        'div[class*="erro"]',
        'div[class*="error"]',
        'span[class*="erro"]',
        'span[class*="error"]',
        'label[class*="erro"]',
        '.message-error',
        '.mensagem-erro',
    ]

    def marcar_checkbox(self, opcoes, marcar):
        raw = self._find_locator(opcoes)
        checkbox = self._apply_locator(raw)
        checkbox.wait_for(state="visible")
        if marcar and not checkbox.is_checked():
            checkbox.check()
        elif not marcar and checkbox.is_checked():
            checkbox.uncheck()

    def acessar_pagina(self):
        self.navigate(self.URL)
        self.wait_for_load()

    def preencher_data_inicial(self, data):
        locator = self._find_locator(self.INPUT_DATA_INICIAL)
        self.fill_input(locator, data)

    def preencher_data_final(self, data):
        locator = self._find_locator(self.INPUT_DATA_FINAL)
        self.fill_input(locator, data)

    def marcar_sabado(self, marcar=True):
        self.marcar_checkbox(self.CHECKBOX_SABADO, marcar)

    def marcar_domingo(self, marcar=True):
        self.marcar_checkbox(self.CHECKBOX_DOMINGO, marcar)

    def marcar_feriados(self, marcar=True):
        self.marcar_checkbox(self.CHECKBOX_FERIADOS, marcar)

    def clicar_calcular(self):
        locator = self._find_locator(self.BOTAO_CALCULAR, fallback_text="Calcular")
        self.click_element(locator)
        self.wait_for_load()

    def obter_resultado(self):
        raw = self._find_locator(self.RESULTADO, fallback_text="dias úteis")
        if self.is_element_visible(raw, timeout=15000):
            return self.get_text(raw)
        for loc in self.RESULTADO:
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

    def calcular_dias_uteis(self, data_inicial, data_final, sabado=False, domingo=False, feriados=True):
        self.preencher_data_inicial(data_inicial)
        self.preencher_data_final(data_final)
        self.marcar_sabado(sabado)
        self.marcar_domingo(domingo)
        self.marcar_feriados(feriados)
        self.clicar_calcular()
