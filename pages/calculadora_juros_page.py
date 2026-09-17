import re
from pages.base_page import BasePage


class CalculadoraJurosCompostosPage(BasePage):
    URL = "https://blog.agibank.com.br/como-calcular-juros-compostos/"
    URL_IFRAME_STANDALONE = (
        "https://blog.agibank.com.br/wp-content/uploads/2026/04/"
        "calculadora_juros_compostos_final_v4.html"
    )
    IFRAME_URL_KEYWORDS = ["calculadora_juros_compostos", "v4.html"]

    ABA_DIVIDA = [
        'xpath=//div[@id=\'choiceScreen\']/div/div/span',
        'xpath=//*[@id="choiceScreen"]/div[1]/div[1]/span',
        '#choiceScreen > div.choice-cards > div.choice-card:first-child',
        '#choiceScreen > div.choice-cards > div.choice-card:first-child > div.choice-title',
        '#choiceScreen div.choice-card:not(.investimento)',
        '#choiceScreen span.choice-icon:first-of-type',
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
        '#choiceScreen > div.choice-cards > div.choice-card.investimento',
        '#choiceScreen > div.choice-cards > div.choice-card.investimento > div.choice-title',
        '#choiceScreen div.choice-card.investimento',
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
        '#formDivida #valorEmprestimo',
        '#valorEmprestimo',
        '#formInvestimento #valorInicial',
        '#valorInicial',
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
        'input[placeholder*="Empréstimo"]',
        'input[placeholder*="R$"]',
        'input[aria-label*="Valor Inicial"]',
        'input[aria-label*="valor inicial"]',
    ]

    INPUT_APORTE_MENSAL = [
        '#valorMensal',
        '#formInvestimento #valorMensal',
        'input[name*="aporte"]',
        'input[name*="mensal"]',
        'input[name*="contribuicao"]',
        'input[name*="parcela"]',
        'input[id*="aporte"]',
        'input[id*="mensal"]',
        'input[id*="contribuicao"]',
        'input[id*="parcela"]',
        'input[id*="valorMensal"]',
        'input[placeholder*="Aporte"]',
        'input[placeholder*="aporte"]',
        'input[placeholder*="mensal"]',
        'input[placeholder*="Parcela"]',
        'input[placeholder*="parcela"]',
        'input[aria-label*="Aporte"]',
        'input[aria-label*="aporte"]',
    ]

    INPUT_TAXA_JUROS = [
        '#taxaJurosInvest',
        '#taxaJurosDivida',
        '#formInvestimento #taxaJurosInvest',
        '#formDivida #taxaJurosDivida',
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
        '#tipoTaxaInvest',
        '#tipoTaxaDivida',
        '#formInvestimento #tipoTaxaInvest',
        '#formDivida #tipoTaxaDivida',
        'select[name*="periodo"]',
        'select[name*="periodicidade"]',
        'select[name*="prazo"]',
        'select[id*="periodo"]',
        'select[id*="periodicidade"]',
        'select[id*="prazo"]',
        'select[id*="tipoTaxa"]',
        'select:has(option:has-text("mensal"))',
        'select:has(option:has-text("anual"))',
    ]

    INPUT_PERIODO = [
        '#periodoInvest',
        '#prazoDivida',
        '#formInvestimento #periodoInvest',
        '#formDivida #prazoDivida',
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
        'input[id*="periodoInvest"]',
        'input[id*="prazoDivida"]',
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
        '#tipoPeriodoInvest',
        '#tipoPrazoDivida',
        '#formInvestimento #tipoPeriodoInvest',
        '#formDivida #tipoPrazoDivida',
        'select[name*="tipo_periodo"]',
        'select[name*="unidade"]',
        'select[name*="tipo_prazo"]',
        'select[id*="tipo_periodo"]',
        'select[id*="unidade"]',
        'select[id*="tipo_prazo"]',
        'select[id*="tipoPeriodo"]',
        'select[id*="tipoPrazo"]',
        'select:has(option:has-text("Meses"))',
        'select:has(option:has-text("Anos"))',
    ]

    BOTAO_CALCULAR = [
        "xpath=//button[@onclick='calcularDivida()']",
        "xpath=//button[@onclick='calcularInvestimento()']",
        '#formDivida button',
        '#formInvestimento button',
        'button:has-text("Calcular Agora")',
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
        '#valorTotal',
        '#valorEmprestimoResult',
        '#totalJuros',
        '#valorParcela',
        '#numeroParcelas',
        '#taxaTextoDivida',
        '#resultInvestimento',
        '#resultDivida',
        '#resultInvestimento .result-details',
        '#resultDivida .result-details',
        '#resultInvestimento .result-title',
        '#resultDivida .result-title',
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

    RESULTADO_DIVIDA_VALOR_TOTAL = ['#valorTotal']
    RESULTADO_DIVIDA_VALOR_EMPRESTIMO = ['#valorEmprestimoResult']
    RESULTADO_DIVIDA_TOTAL_JUROS = ['#totalJuros']
    RESULTADO_DIVIDA_VALOR_PARCELA = ['#valorParcela']
    RESULTADO_DIVIDA_NUMERO_PARCELAS = ['#numeroParcelas']
    RESULTADO_DIVIDA_TAXA_TEXTO = ['#taxaTextoDivida']

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
        self._ensure_calculadora_context()

    # ======================================================================
    # SUPORTE A IFRAMES / CONTEXTO DA CALCULADORA
    # (Muitos blogs WordPress embebem calculadoras em <iframe>)
    # ======================================================================
    def _active_page(self):
        """
        Retorna o Page/Frame correto onde a calculadora realmente existe.
        Verifica primeiro o contexto top-level, depois busca em iframes.
        """
        return getattr(self, "_calc_frame", None) or self.page

    def _find_text_in_context(self, ctx, textos):
        if ctx is None:
            return None
        for t in textos:
            try:
                m = ctx.get_by_text(t, exact=False)
                if m.count() > 0:
                    return m.first
            except Exception:
                continue
        return None

    def _ensure_calculadora_context(self, keywords=None):
        """
        Busca o contexto (frame ou pagina top-level) no qual a calculadora
        realmente existe. Como a calculadora MORAVA DENTRO DE UM IFRAME
        (confirmado em debug: src = URL_IFRAME_STANDALONE), procuramos
        PRIMEIRO em page.frames (API nativa Playwright) por URL.

        Fallbacks:
            1) Frames que contenham keywords no texto interno
            2) Top-level page como ultimo recurso
        """
        if keywords is None:
            keywords = ["Dívida", "Divida", "Investimento", "choiceScreen",
                        "Calcule quanto você vai pagar", "Calcule quanto seu dinheiro"]

        page = self.page

        # =====================================================================
        # PASSO 1: Tentar frames por URL (MELHOR MÉTODO — sabemos a URL!)
        # =====================================================================
        try:
            for kw_url in self.IFRAME_URL_KEYWORDS:
                for frame in page.frames:
                    try:
                        furl = getattr(frame, "url", "") or ""
                        if kw_url.lower() in furl.lower():
                            try:
                                frame.wait_for_load_state("domcontentloaded", timeout=8000)
                            except Exception:
                                pass
                            try:
                                frame.wait_for_timeout(1500)
                            except Exception:
                                pass
                            # Validar que contem keyword interna
                            valid = False
                            try:
                                if frame.locator("#choiceScreen").count() > 0:
                                    valid = True
                            except Exception:
                                pass
                            if not valid:
                                for kw in keywords:
                                    try:
                                        if frame.get_by_text(kw, exact=False).count() > 0:
                                            valid = True
                                            break
                                    except Exception:
                                        continue
                            if valid:
                                self._calc_frame = frame
                                self._swap_active_context(frame)
                                return frame
                    except Exception:
                        continue
        except Exception:
            pass

        # =====================================================================
        # PASSO 2: Iterar TODOS os frames (mesmo sem URL match) e testar texto
        # =====================================================================
        try:
            for frame in page.frames:
                if not frame or (frame is page.main_frame and False):
                    continue
                try:
                    for kw in keywords:
                        try:
                            if frame.get_by_text(kw, exact=False).count() > 0:
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
                        if frame.locator("#choiceScreen").count() > 0:
                            self._calc_frame = frame
                            self._swap_active_context(frame)
                            return frame
                    except Exception:
                        pass
                except Exception:
                    continue
        except Exception:
            pass

        # =====================================================================
        # PASSO 3: Ultimo recurso -> Top-level
        # =====================================================================
        self._calc_frame = page
        self._swap_active_context(page)
        return page

    def _swap_active_context(self, ctx):
        """
        Guarda self.page original e substitui por ctx (Frame) para que
        os métodos herdados de BasePage (click_element, fill_input, etc)
        atuem no CONTEXTO CORRETO (iframe) invés de no top-level page.

        self._page_orig = backup da original.
        """
        if not getattr(self, "_page_orig", None):
            self._page_orig = self.page
        self.page = ctx or self._page_orig

    def _restore_top_context(self):
        if getattr(self, "_page_orig", None):
            self.page = self._page_orig

    # ======================================================================
    # HELPERS LOCAIS que usam _active_page() (sem depender de self.page herdado)
    # ======================================================================
    @staticmethod
    def _normalizar_decimal_ptbr(valor, duas_casas=True):
        """
        Converte entradas numericas para formato pt-BR.
        SE duas_casas=True: formata COM VÍRGULA + 2 casas decimais FIXAS (para MÁSCARAS
        de moeda/porcentagem que tratam digitos sem vírgula como CENTAVOS).
        Exemplos:
            10000          -> '10000,00'  (R$ 10.000,00)
            '2.5'          -> '2,50'
            '10000'        -> '10000,00'
            '24' (prazo)   -> '24'        (se duas_casas=False)
            10000 (prazo)  -> '10000'     (se duas_casas=False)
        """
        if isinstance(valor, (int, float)):
            if isinstance(valor, float):
                s = f"{valor:.2f}".replace(".", ",") if duas_casas else f"{valor:.10f}".rstrip("0").rstrip(".").replace(".", ",")
                return s
            if duas_casas:
                return f"{valor},00"
            return str(valor)
        s = str(valor).strip()
        if not s:
            return s
        tem_virgula = "," in s
        tem_ponto = "." in s
        if tem_virgula and not tem_ponto:
            if duas_casas:
                antes, _, depois = s.partition(",")
                depois = (depois + "00")[:2]
                antes = antes.replace(".", "")
                return f"{antes},{depois}"
            return s
        if tem_ponto and not tem_virgula:
            if s.count(".") > 1:
                return s.replace(".", "") + (",00" if duas_casas else "")
            antes, _, depois = s.partition(".")
            if duas_casas:
                depois = (depois + "00")[:2]
                return f"{antes},{depois}"
            return s.replace(".", ",")
        if tem_virgula and tem_ponto:
            s2 = s.replace(".", "#TEMP#").replace(",", ".").replace("#TEMP#", ",")
            return CalculadoraJurosCompostosPage._normalizar_decimal_ptbr(s2, duas_casas=duas_casas)
        if s.isdigit() and duas_casas:
            return f"{s},00"
        return s

    def _preencher_com_mascara_br(self, locator_element, valor, delay_ms=60):
        """
        Preenche input com máscara brasileira (R$, %, etc).
        Máscaras (IMask/Cleave) NÃO FUNCIONAM com fill(). É OBRIGATÓRIO
        limpar com Ctrl+A e digitar caractere por caractere via teclado.
        """
        valor_br = self._normalizar_decimal_ptbr(valor)
        try:
            # Foca e clica 2x para garantir foco
            locator_element.scroll_into_view_if_needed(timeout=5000)
            locator_element.click()
            try:
                locator_element.click(click_count=2, timeout=2000)
            except Exception:
                pass
        except Exception:
            pass
        # Seleciona TUDO e apaga (Ctrl+A, Delete)
        try:
            locator_element.press("Control+A")
        except Exception:
            pass
        try:
            locator_element.press("Delete")
        except Exception:
            pass
        # Garantia adicional: tenta .fill('') para zerar buffer
        try:
            locator_element.fill("")
        except Exception:
            pass
        try:
            locator_element.press("Control+A")
            locator_element.press("Backspace")
        except Exception:
            pass
        # Digita lentamente caractere por caractere (mascara pega cada tecla)
        locator_element.type(valor_br, delay=delay_ms)
        return valor_br

    def _click_text(self, options_text, timeout=30000, exact=False):
        """Clica no PRIMEIRO elemento que contenha algum dos textos listados."""
        ctx = self._active_page()
        last_err = None
        for txt in options_text:
            try:
                loc = ctx.get_by_text(txt, exact=exact)
                # pega o primeiro visivel
                for i in range(loc.count()):
                    try:
                        el = loc.nth(i)
                        el.wait_for(state="visible", timeout=5000)
                        el.scroll_into_view_if_needed(timeout=5000)
                        el.click(timeout=timeout)
                        return True
                    except Exception as err:
                        last_err = err
                        continue
            except Exception as err:
                last_err = err
                continue
        raise last_err or RuntimeError(f"Nenhum elemento encontrado com textos {options_text}")

    def _fill_by_placeholder_label_or_nearby(self, valor, keywords, tipo="input",
                                              mascara=False, delay_ms=60):
        """
        Busca o input mais proximo de alguma keyword (label/placeholder).
        Se mascara=True usa _preencher_com_mascara_br() (Ctrl+A + type char a char).
        """
        ctx = self._active_page()
        valor_str = str(valor)

        def _aplicar_fill(el):
            if mascara:
                self._preencher_com_mascara_br(el, valor_str, delay_ms=delay_ms)
            else:
                try:
                    el.click()
                    try:
                        el.fill(valor_str)
                    except Exception:
                        # fallback mascara mesmo se pedido fill() (pode ser mascara oculta)
                        self._preencher_com_mascara_br(el, valor_str, delay_ms=delay_ms)
                except Exception:
                    self._preencher_com_mascara_br(el, valor_str, delay_ms=delay_ms)
            return True

        # 0) Metodo PRIORITARIO: ids/attrs da lista de seletores externos
        # (aqui placeholder/label abaixo)

        # 1) por placeholder exato ou aproximado
        for kw in keywords:
            try:
                loc = ctx.get_by_placeholder(kw, exact=False)
                if loc.count() > 0:
                    for i in range(loc.count()):
                        try:
                            el = loc.nth(i)
                            el.wait_for(state="visible", timeout=5000)
                            _aplicar_fill(el)
                            return True
                        except Exception:
                            continue
            except Exception:
                pass

        # 2) por label proximo
        for kw in keywords:
            try:
                loc = ctx.get_by_label(kw, exact=False)
                if loc.count() > 0:
                    for i in range(loc.count()):
                        try:
                            el = loc.nth(i)
                            el.wait_for(state="visible", timeout=5000)
                            _aplicar_fill(el)
                            return True
                        except Exception:
                            continue
            except Exception:
                pass

        # 3) busca input name/class aproximado
        for kw in keywords:
            try:
                kw_norm = kw.lower().replace(" ", "_").replace("á", "a").replace("ã", "a").replace("í", "i").replace("ç", "c").replace("õ", "o").replace("ê", "e")
                css = (
                    f'{tipo}[name*="{kw_norm}"],'
                    f'{tipo}[placeholder*="{kw}"],'
                    f'{tipo}[id*="{kw_norm}"],'
                    f'{tipo}[aria-label*="{kw}"]'
                )
                loc = ctx.locator(css)
                if loc.count() > 0:
                    for i in range(loc.count()):
                        try:
                            el = loc.nth(i)
                            el.wait_for(state="visible", timeout=5000)
                            _aplicar_fill(el)
                            return True
                        except Exception:
                            continue
            except Exception:
                pass
        raise RuntimeError(f"Input nao encontrado para keywords={keywords}")

    # ======================================================================
    # AÇÕES DA PÁGINA (SOBRESCRITAS para usar contexto ativo + texto)
    # ======================================================================
    def selecionar_aba_divida(self):
        self._ensure_calculadora_context()
        try:
            self._click_text(["Dívida", "Divida", "Calcule quanto você vai pagar em um empréstimo",
                              "Calcule quanto voce vai pagar em um emprestimo",
                              "Calcule quanto você vai pagar", "Empréstimo", "emprestimo"], timeout=40000)
        except Exception:
            locator = self._find_locator(self.ABA_DIVIDA, fallback_text="Dívida")
            self.click_element(locator)
        self.wait_for_load()

    def selecionar_aba_investimento(self):
        self._ensure_calculadora_context()
        try:
            self._click_text(["Investimento", "Calcule quanto seu dinheiro vai render",
                              "Investir", "Rendimento", "investimento"], timeout=40000)
        except Exception:
            locator = self._find_locator(self.ABA_INVESTIMENTO, fallback_text="Investimento")
            self.click_element(locator)
        self.wait_for_load()

    def preencher_valor_inicial(self, valor):
        self._ensure_calculadora_context()
        ctx = self._active_page()

        # METODO PRINCIPAL: ID DIRETO (MAIS CONFIAVEL - Katalon confirmou!)
        ids_prioridade = ['#valorEmprestimo', '#valorInicial']
        for _id in ids_prioridade:
            try:
                el = ctx.locator(_id)
                if el.count() > 0:
                    try:
                        for i in range(el.count()):
                            try:
                                el_i = el.nth(i)
                                if el_i.is_visible():
                                    self._preencher_com_mascara_br(el_i, valor, delay_ms=70)
                                    return
                            except Exception:
                                continue
                        self._preencher_com_mascara_br(el.first, valor, delay_ms=70)
                        return
                    except Exception:
                        pass
            except Exception:
                continue

        try:
            self._fill_by_placeholder_label_or_nearby(
                valor,
                ["Valor do Empréstimo", "Valor do Emprestimo", "Empréstimo",
                 "Emprestimo", "Valor inicial", "Valor Inicial", "Valor",
                 "Capital", "Principal", "Quanto você quer aplicar",
                 "valor_inicial", "valor inicial", "Quanto você tem",
                 "Montante inicial"],
                mascara=True, delay_ms=70,
            )
        except Exception:
            locator = self._find_locator(self.INPUT_VALOR_INICIAL)
            el = self._apply_locator(locator)
            try:
                self._preencher_com_mascara_br(el.first, valor, delay_ms=70)
            except Exception:
                self.fill_input(locator, str(valor))

    def preencher_aporte_mensal(self, valor):
        self._ensure_calculadora_context()
        ctx = self._active_page()
        try:
            el = ctx.locator('#valorMensal')
            if el.count() > 0:
                for i in range(el.count()):
                    try:
                        if el.nth(i).is_visible():
                            self._preencher_com_mascara_br(el.nth(i), valor, delay_ms=70)
                            return
                    except Exception:
                        continue
                try:
                    self._preencher_com_mascara_br(el.first, valor, delay_ms=70)
                    return
                except Exception:
                    pass
        except Exception:
            pass
        try:
            self._fill_by_placeholder_label_or_nearby(
                valor,
                ["Aporte mensal", "Aporte Mensal", "Aporte", "Mensal",
                 "Depósito mensal", "Contribuição mensal", "Contribuicao mensal",
                 "aporte_mensal", "parcela mensal", "Pagamento mensal"],
                mascara=True, delay_ms=70,
            )
        except Exception:
            locator = self._find_locator(self.INPUT_APORTE_MENSAL)
            el = self._apply_locator(locator)
            try:
                self._preencher_com_mascara_br(el.first, valor, delay_ms=70)
            except Exception:
                self.fill_input(locator, str(valor))

    def preencher_taxa_juros(self, taxa):
        self._ensure_calculadora_context()
        ctx = self._active_page()
        for _id in ['#taxaJurosDivida', '#taxaJurosInvest']:
            try:
                el = ctx.locator(_id)
                if el.count() > 0:
                    for i in range(el.count()):
                        try:
                            if el.nth(i).is_visible():
                                self._preencher_com_mascara_br(el.nth(i), taxa, delay_ms=70)
                                return
                        except Exception:
                            continue
                    try:
                        self._preencher_com_mascara_br(el.first, taxa, delay_ms=70)
                        return
                    except Exception:
                        pass
            except Exception:
                pass
        try:
            self._fill_by_placeholder_label_or_nearby(
                taxa,
                ["Taxa de juros", "Taxa Juros", "Taxa", "Juros",
                 "Taxa anual", "Taxa mensal", "Percentual", "%",
                 "taxa_juros", "taxa de juros", "Selic", "Rentabilidade"],
                mascara=True, delay_ms=70,
            )
        except Exception:
            locator = self._find_locator(self.INPUT_TAXA_JUROS)
            el = self._apply_locator(locator)
            try:
                self._preencher_com_mascara_br(el.first, taxa, delay_ms=70)
            except Exception:
                self.fill_input(locator, str(taxa))

    def preencher_periodo(self, periodo):
        self._ensure_calculadora_context()
        ctx = self._active_page()
        for _id in ['#prazoDivida', '#periodoInvest']:
            try:
                el = ctx.locator(_id)
                if el.count() > 0:
                    for i in range(el.count()):
                        try:
                            if el.nth(i).is_visible():
                                el.nth(i).click()
                                try:
                                    el.nth(i).fill(str(periodo))
                                except Exception:
                                    self._preencher_com_mascara_br(el.nth(i), periodo, delay_ms=50)
                                return
                        except Exception:
                            continue
                    try:
                        el.first.click()
                        el.first.fill(str(periodo))
                        return
                    except Exception:
                        pass
            except Exception:
                pass
        try:
            self._fill_by_placeholder_label_or_nearby(
                periodo,
                ["Período", "Periodo", "Prazo", "Tempo", "Meses", "Anos",
                 "Quantidade de meses", "periodo", "prazo", "tempo",
                 "Quantos meses", "Quantos anos"],
                mascara=False,
            )
        except Exception:
            locator = self._find_locator(self.INPUT_PERIODO)
            self.fill_input(locator, str(periodo))

    def selecionar_periodicidade_taxa(self, periodicidade="mensal"):
        self._ensure_calculadora_context()
        ctx = self._active_page()
        eh_ano = "ano" in periodicidade.lower()
        opcao_texto = "anual" if eh_ano else "mensal"
        try:
            # tenta por texto (toggle/radio)
            options = [
                opcao_texto,
                opcao_texto.capitalize(),
                "Ao mês" if not eh_ano else "Ao ano",
                "a.m." if not eh_ano else "a.a.",
                "am" if not eh_ano else "aa",
                "por mês" if not eh_ano else "por ano",
            ]
            for t in options:
                try:
                    loc = ctx.get_by_text(t, exact=False)
                    if loc.count() > 0:
                        for i in range(loc.count()):
                            try:
                                el = loc.nth(i)
                                if el.is_visible():
                                    el.click()
                                    return
                            except Exception:
                                continue
                except Exception:
                    continue
            # fallback select
            self.select_dropdown(
                self._find_locator(self.SELECT_PERIODICIDADE_TAXA),
                "anual" if eh_ano else "mensal"
            )
        except Exception:
            try:
                if "ano" in periodicidade.lower():
                    self.select_dropdown(self._find_locator(self.SELECT_PERIODICIDADE_TAXA), "anual")
                else:
                    self.select_dropdown(self._find_locator(self.SELECT_PERIODICIDADE_TAXA), "mensal")
            except Exception:
                pass

    def selecionar_unidade_periodo(self, unidade="meses"):
        self._ensure_calculadora_context()
        ctx = self._active_page()
        eh_ano = "ano" in unidade.lower()
        try:
            options = [
                "anos" if eh_ano else "meses",
                "Anos" if eh_ano else "Meses",
                "ano(s)" if eh_ano else "mês(es)",
                "por ano" if eh_ano else "por mês",
                "Ano" if eh_ano else "Mês",
            ]
            for t in options:
                try:
                    loc = ctx.get_by_text(t, exact=False)
                    if loc.count() > 0:
                        for i in range(loc.count()):
                            try:
                                el = loc.nth(i)
                                if el.is_visible():
                                    el.click()
                                    return
                            except Exception:
                                continue
                except Exception:
                    continue
            self.select_dropdown(
                self._find_locator(self.SELECT_PERIODICIDADE_PERIODO),
                "anos" if eh_ano else "meses"
            )
        except Exception:
            try:
                if "ano" in unidade.lower():
                    self.select_dropdown(self._find_locator(self.SELECT_PERIODICIDADE_PERIODO), "anos")
                else:
                    self.select_dropdown(self._find_locator(self.SELECT_PERIODICIDADE_PERIODO), "meses")
            except Exception:
                pass

    def clicar_calcular(self):
        self._ensure_calculadora_context()
        try:
            self._click_text([
                "Calcular", "Calcular agora", "Simular", "Simule agora",
                "Simular agora", "Resultado", "Ver resultado",
                "Calcular simulação", "Calcular simulacao"
            ], timeout=40000)
        except Exception:
            locator = self._find_locator(self.BOTAO_CALCULAR, fallback_text="Calcular")
            self.click_element(locator)
        self.wait_for_load()

    def obter_resultado(self):
        self._ensure_calculadora_context()
        ctx = self._active_page()

        # 1) Busca qualquer elemento com "R$" + digitos visivel primeiro
        try:
            all_currency = ctx.get_by_text(re.compile(r"R\$\s*\d"))
            if all_currency.count() > 0:
                for i in range(all_currency.count()):
                    try:
                        el = all_currency.nth(i)
                        if el.is_visible():
                            txt = el.inner_text().strip()
                            if txt:
                                return txt
                    except Exception:
                        continue
        except Exception:
            pass

        # 2) Fallback sistema antigo
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
        self._ensure_calculadora_context()
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

    # ======================================================================
    # CAMPOS DE RESULTADO ESPECÍFICOS DA DIVIDA (capturados via Katalon)
    # ======================================================================
    def _obter_campo_especifico(self, lista_ids, timeout=15000):
        self._ensure_calculadora_context()
        ctx = self._active_page()
        for loc_id in lista_ids:
            try:
                loc = ctx.locator(loc_id)
                if loc.count() > 0:
                    try:
                        loc.first.wait_for(state="visible", timeout=timeout)
                    except Exception:
                        pass
                    txt = (loc.first.inner_text() or loc.first.input_value() or "").strip()
                    if txt:
                        return txt
            except Exception:
                continue
        # fallback usando BasePage
        raw = self._find_locator(lista_ids)
        try:
            if self.is_element_visible(raw, timeout=timeout):
                return self.get_text(raw)
        except Exception:
            pass
        return ""

    def obter_valor_total(self):
        return self._obter_campo_especifico(self.RESULTADO_DIVIDA_VALOR_TOTAL)

    def obter_valor_emprestimo_resultado(self):
        return self._obter_campo_especifico(self.RESULTADO_DIVIDA_VALOR_EMPRESTIMO)

    def obter_total_juros(self):
        return self._obter_campo_especifico(self.RESULTADO_DIVIDA_TOTAL_JUROS)

    def obter_valor_parcela(self):
        return self._obter_campo_especifico(self.RESULTADO_DIVIDA_VALOR_PARCELA)

    def obter_numero_parcelas(self):
        return self._obter_campo_especifico(self.RESULTADO_DIVIDA_NUMERO_PARCELAS)

    def obter_taxa_texto_divida(self):
        return self._obter_campo_especifico(self.RESULTADO_DIVIDA_TAXA_TEXTO)

    # Helpers de alto nivel: retorna dict completo do resultado divida
    def obter_resulado_divida_completo(self):
        """Retorna dict com todos os campos de resultado da divida"""
        return {
            "valor_total": self.obter_valor_total(),
            "valor_emprestimo": self.obter_valor_emprestimo_resultado(),
            "total_juros": self.obter_total_juros(),
            "valor_parcela": self.obter_valor_parcela(),
            "numero_parcelas": self.obter_numero_parcelas(),
            "taxa_texto": self.obter_taxa_texto_divida(),
        }

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
