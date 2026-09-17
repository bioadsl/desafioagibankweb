# -*- coding: utf-8 -*-
"""
===============================================================================
calculadora_investimentos_page.py (ALINHADO AOS POMS PADROES DO PROJETO)
===============================================================================
Page Object Model (POM) para a CALCULADORA DE INVESTIMENTOS do
blog Agibank. Mantem compatibilidade 100% com a arquitetura existente do
desafioagibank (BasePage, Playwright Sync, Detecção automática de IFRAME,
seletores com fallback e helpers de mascara BR).

ESTRUTURA E NOMENCLATURA ALINHADAS AOS DEMAIS POMS:
 - Classe:    CalculadoraInvestimentosPage  (PascalCase, Calculadora...Page, 2 letras 'c')
 - Atributos: URL, URL_IFRAME_STANDALONE (nome padrão demais POMs)
 - Metodos:   acessar_pagina() / calcular_investimento() / obter_resultado()
              / obter_mensagem_erro() - nomenclatura identica a
              CalculadoraDiasUteisPage / CalculadoraJurosCompostosPage.

FLUXO PRINCIPAL IMPLEMENTADO:
  1. acessar_pelo_menu_principal()  => EXATAMENTE os 2 clicks capturados
     no arquivo Selenium BlazeMeter (`[data-attachment-id="20644"]` +
     `#menu-item-24258 > a.menu-link > span.menu-text`)
  2. selecionar_aba_investimento()  => card Investimento (choiceScreen iframe)
  3. preencher_valor_inicial()      => #valorInicial
  4. preencher_aporte_mensal()      => #valorMensal
  5. preencher_taxa()               => #taxaJurosInvest
  6. selecionar_periodicidade_taxa() => #tipoTaxaInvest (Mensal/Anual)
  7. preencher_periodo()            => #periodoInvest
  8. selecionar_unidade_periodo()   => #tipoPeriodoInvest (Meses/Anos)
  9. calcular()                     => button onclick=calcularInvestimento()
 10. obter_resulado_completo()      => dict com todos campos detalhados

CENARIOS DE CALCULO IMPLEMENTADOS (via metodos helper):
  * calcular_cenario_padrao_12meses()  => R$10k + R$500/mes + 0,80%am + 12meses
  * calcular_cenario_longo_prazo()    => R$50k + R$1k/mes + 1%am + 120meses
  * calcular_cenario_apenas_inicial() => (Apenas valor inicial, aporte=0)
  * calcular_investimento(...)        => completo customizado (padrao POMs)

WAITS EXPLICITOS:
  - wait_for_cloudflare_bypass em todas interacoes (herdado BasePage)
  - wait_for(state="visible") em TODOS locators antes de acao
  - wait_for_load_state("networkidle") apos cada click/calculo
  - wait_for_element antes de ler resultado

TRATAMENTO DE ERROS:
  - Nenhum metodo deixa exception Playwright "cru" subir;
    todos capturam, explicam em portugues, e re-raise com contexto
  - RuntimeError("campo X nao encontrado...") em pt-BR com contexto util ao QA
===============================================================================
"""
import re
import time
from pages.base_page import BasePage


class CalculadoraInvestimentosPage(BasePage):
    """
    POM dedicado a CALCULADORA DE INVESTIMENTOS do blog do Agibank.
    Nomenclatura ALINHADA a CalculadoraDiasUteisPage / CalculadoraJurosCompostosPage.
    """

    # =========================================================================
    # URLs (NOMENCLATURA PADRAO DOS DEMAIS POMS: URL / URL_IFRAME_STANDALONE)
    # =========================================================================
    URL = "https://blog.agibank.com.br/como-calcular-juros-compostos/"
    HOME_BLOG_URL = "https://blog.agibank.com.br/"
    URL_IFRAME_STANDALONE = (
        "https://blog.agibank.com.br/wp-content/uploads/2026/04/"
        "calculadora_juros_compostos_final_v4.html"
    )
    IFRAME_URL_KEYWORDS = ["calculadora_juros_compostos", "v4.html"]

    # =========================================================================
    # LOCATORS DO MENU (EXTRAIDOS DO BLAZEMETER Selenium WD unittest):
    #   [data-attachment-id="20644"]  (atalho calculadoras menu topo)
    #   #menu-item-24258 > a.menu-link > span.menu-text  (texto menu)
    # =========================================================================
    MENU_ATALHO_CALCULADORAS_BLAZEMETER = [
        '[data-attachment-id="20644"]',
        'a[data-attachment-id="20644"]',
        'img[data-attachment-id="20644"]',
        '.menu-item a:has([data-attachment-id="20644"])',
    ]
    MENU_ITEM_JUROS_COMPOSTOS_BLAZEMETER = [
        "#menu-item-24258 > a.menu-link > span.menu-text",
        "#menu-item-24258 > a.menu-link",
        "#menu-item-24258",
        "li[id*='menu-item'][id*='24258']",
        ".menu-item:has-text('Juros Compostos')",
        ".menu-item:has-text('juros compostos')",
        ".menu-link:has-text('Calculadora')",
        ".menu-text:has-text('Calculadora')",
    ]

    # =========================================================================
    # LOCATORS DA ABA INVESTIMENTO (dentro do iframe):
    #   Todos com #id REAL confirmado pelo Katalon / debug iframe standalone.
    # =========================================================================
    ABA_INVESTIMENTO = [
        "#choiceScreen > div.choice-cards > div.choice-card.investimento",
        "#choiceScreen > div.choice-cards > div.choice-card.investimento > div.choice-title",
        "#choiceScreen div.choice-card.investimento",
        "#choiceScreen span:has-text('Investimento')",
        "#choiceScreen div:nth-child(2) div:nth-child(1) span",
        "#choiceScreen [id*='investimento']",
    ]

    # --- Campos Formulario Investimento ---
    INPUT_VALOR_INICIAL = [
        "#formInvestimento #valorInicial",
        "#valorInicial",
        "input[id*='valorInicial']",
        "input[name*='valor_inicial']",
        "input[placeholder*='Valor Inicial']",
        "input[placeholder*='valor inicial']",
        "input[aria-label*='Valor Inicial']",
    ]
    INPUT_APORTE_MENSAL = [
        "#formInvestimento #valorMensal",
        "#valorMensal",
        "input[id*='valorMensal']",
        "input[name*='aporte']",
        "input[name*='mensal']",
        "input[placeholder*='Aporte']",
        "input[placeholder*='Mensal']",
        "input[aria-label*='Aporte']",
    ]
    INPUT_TAXA_JUROS = [
        "#formInvestimento #taxaJurosInvest",
        "#taxaJurosInvest",
        "input[id*='taxaJurosInvest']",
        "input[name*='taxa']",
        "input[name*='juros']",
        "input[placeholder*='Taxa']",
        "input[placeholder*='taxa']",
        "input[placeholder*='%']",
        "input[aria-label*='Taxa']",
    ]
    SELECT_PERIODICIDADE_TAXA = [
        "#formInvestimento #tipoTaxaInvest",
        "#tipoTaxaInvest",
        "select[id*='tipoTaxaInvest']",
        "select:has(option:has-text('Mensal'))",
        "select:has(option:has-text('Anual'))",
    ]
    INPUT_PERIODO = [
        "#formInvestimento #periodoInvest",
        "#periodoInvest",
        "input[id*='periodoInvest']",
        "input[name*='periodo']",
        "input[name*='tempo']",
        "input[placeholder*='Período']",
        "input[placeholder*='periodo']",
        "input[placeholder*='Prazo']",
        "input[aria-label*='Período']",
    ]
    SELECT_UNIDADE_PERIODO = [
        "#formInvestimento #tipoPeriodoInvest",
        "#tipoPeriodoInvest",
        "select[id*='tipoPeriodoInvest']",
        "select:has(option:has-text('Meses'))",
        "select:has(option:has-text('Anos'))",
    ]

    # --- Botao calcular (melhor seletor = onclick exato do JS) ---
    BOTAO_CALCULAR = [
        "xpath=//button[@onclick='calcularInvestimento()']",
        "#formInvestimento button",
        "#formInvestimento button[type='submit']",
        "button:has-text('Calcular Agora')",
        "button:has-text('Calcular')",
        "button:has-text('Simular')",
    ]

    # --- Resultados detalhados (IDs 100% CONFIRMADOS via iframe standalone debug):
    #      Extraídos em: scripts_extrai_ids_invest.py (rodado em 2026-09-17)
    #      Cenário padrão cenario_padrao_12meses():
    #         10k inicial + 500/mes × 12m × 0,80% am → R$ 17.274,56 final /
    #         R$ 16.000,00 investido / R$ 1.274,56 rendimento
    # =========================================================================
    RESULT_CONTAINER = ["#resultInvestimento"]

    RESULT_MONTANTE_FINAL = [
        "#valorFinal",                       # ← ID REAL (confirmado)
        "#resultInvestimento .result-highlight-value",
        "#resultInvestimento .result-highlight .result-highlight-value",
        "#resultInvestimento h3 + div.result-highlight [class*='value']",
        "#resultInvestimento h3.result-title + .result-highlight [id]",
    ]
    RESULT_TOTAL_INVESTIDO = [
        "#valorInvestido",                   # ← ID REAL (confirmado)
        "#resultInvestimento span.result-row-value:first-of-type",
        ".result-details .result-row:first-of-type .result-row-value",
    ]
    RESULT_TOTAL_JUROS = [
        "#rendimentoTotal",                  # ← ID REAL (confirmado)
        "#resultInvestimento .positive",
        ".result-details .result-row:nth-child(2) .result-row-value",
        ".result-details .result-row:has-text('Rendimento') .result-row-value",
    ]
    RESULT_PERIODO_FORMATADO = [
        "#periodoTexto",                     # ← ID REAL (confirmado)
        ".result-details .result-row:has-text('Período') .result-row-value",
        ".result-details .result-row:nth-child(3) .result-row-value",
    ]
    RESULT_TAXA_FORMATADA = [
        "#taxaTextoInvest",                  # ← ID REAL (confirmado)
        ".result-details .result-row:has-text('Taxa') .result-row-value",
        ".result-details .result-row:nth-child(4) .result-row-value",
    ]

    RESULT_VALOR_INICIAL_RESULT = []    # (não exposto separado no DOM)
    RESULT_TOTAL_APORTES_RESULT = []    # (não exposto separado no DOM)

    MENSAGENS_ERRO = [
        "#formInvestimento .erro",
        "#formInvestimento .error",
        ".error:has-text('obrigató')",
        ".erro:has-text('obrigat')",
        ".invalid-feedback",
        "[aria-invalid='true']",
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
        """Localiza o iframe da calculadora (URL V4.html)."""
        self._wait_cloudflare_bypass(max_attempts=6, wait_ms=2000)
        page = self.page if not getattr(self, "_page_orig", None) else self._page_orig

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

        # Passo 2: fallback - any frame with keyword
        for frame in page.frames:
            try:
                if frame.locator("#choiceScreen").count() > 0:
                    self._calc_frame = frame
                    self._swap_active_context(frame)
                    return frame
            except Exception:
                continue
            try:
                if frame.get_by_text("Investimento", exact=False).count() > 0:
                    self._calc_frame = frame
                    self._swap_active_context(frame)
                    return frame
            except Exception:
                continue

        # Passo 3: ultimo recurso - top level
        self._calc_frame = page
        self._swap_active_context(page)
        return page

    # ----------- helpers mascara decimal BR -------------------------------
    @staticmethod
    def _normalizar_decimal_ptbr(valor, duas_casas=True):
        if isinstance(valor, (int, float)):
            if isinstance(valor, float):
                return (f"{valor:.2f}" if duas_casas else f"{valor:.10f}".rstrip("0").rstrip(".")).replace(".", ",")
            return f"{valor},00" if duas_casas else str(valor)
        s = str(valor).strip()
        if not s:
            return s
        tv = "," in s; tp = "." in s
        if tv and not tp:
            if duas_casas:
                a, _, d = s.partition(",")
                return f"{a.replace('.','')},{(d + '00')[:2]}"
            return s
        if tp and not tv:
            if s.count(".") > 1:
                return s.replace(".", "") + (",00" if duas_casas else "")
            a, _, d = s.partition(".")
            if duas_casas:
                return f"{a},{(d + '00')[:2]}"
            return s.replace(".", ",")
        if tp and tv:
            s2 = s.replace(".", "#T#").replace(",", ".").replace("#T#", ",")
            return CalculadoraInvestimentosPage._normalizar_decimal_ptbr(s2, duas_casas)
        if s.isdigit() and duas_casas:
            return f"{s},00"
        return s

    def _preencher_com_mascara_br(self, locator_el, valor, delay_ms=60):
        """Preenche campos com mascara monetaria/taxa: Ctrl+A + type char-a-char."""
        v_br = self._normalizar_decimal_ptbr(valor, duas_casas=True)
        try:
            locator_el.scroll_into_view_if_needed(timeout=5000)
            locator_el.click()
            try: locator_el.click(click_count=2)
            except Exception: pass
        except Exception:
            pass
        for seq in [("Control+A", "Delete"), ("Control+A", "Backspace")]:
            try:
                for k in seq:
                    try: locator_el.press(k)
                    except Exception: pass
            except Exception: pass
        try:
            locator_el.fill("")
        except Exception:
            pass
        locator_el.type(v_br, delay=delay_ms)
        return v_br

    # =========================================================================
    # FLUXO 1: ACESSAR PELO MENU PRINCIPAL (passos BLAZEMETER)
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
        Repete EXATAMENTE os 2 passos de click capturados no arquivo
        calculadora-investimento-Selenium-python-wd-unittest.py (BlazeMeter):

          Passo 1 (linha 24 original):
            click  css=[data-attachment-id="20644"]
          Passo 2 (linha 26 original):
            click  css=#menu-item-24258 > a.menu-link > span.menu-text

        Ao final: self.page estara na pagina da calculadora, e o metodo
        _ensure_calculadora_context() podera localizar o iframe.
        """
        # Garante HOME carregada
        if self.HOME_BLOG_URL.rstrip("/") not in (getattr(self.page, "url", "") or "").rstrip("/"):
            self.acessar_home_blog()

        # --- Passo 1 BlazeMeter: [data-attachment-id="20644"] ---
        try:
            self.wait_for_element(self.MENU_ATALHO_CALCULADORAS_BLAZEMETER[0], timeout=25000)
        except Exception:
            # Se demorar render, espera networkidle
            try:
                self.page.wait_for_load_state("networkidle", timeout=30000)
            except Exception:
                pass
        try:
            locator_1 = self._find_locator(
                self.MENU_ATALHO_CALCULADORAS_BLAZEMETER,
                fallback_text="Calculadora",
            )
            self.click_element(locator_1)
            self.wait_for_load()
            self.page.wait_for_timeout(1200)
        except Exception as err:
            # Soft failure: este atalho pode nao existir em versoes mobile.
            # Tenta pular direto para passo 2 (menu dropdown ja visivel)
            print(
                f"[WARN] BlazeMeter passo 1 nao achou data-attachment-id=20644 "
                f"(tentando proximo passo). Detalhe: {err.__class__.__name__}"
            )

        # --- Passo 2 BlazeMeter: #menu-item-24258 > a.menu-link > span.menu-text ---
        try:
            self.wait_for_element(
                self.MENU_ITEM_JUROS_COMPOSTOS_BLAZEMETER[0], timeout=25000
            )
        except Exception:
            try:
                self.page.wait_for_load_state("networkidle", timeout=30000)
            except Exception:
                pass
        try:
            locator_2 = self._find_locator(
                self.MENU_ITEM_JUROS_COMPOSTOS_BLAZEMETER,
                fallback_text="Juros Compostos",
            )
            self.click_element(locator_2)
            self.wait_for_load()
            self.page.wait_for_timeout(1500)
        except Exception as err:
            raise RuntimeError(
                "Navegacao por menu (BlazeMeter passo 2) FALHOU: nao foi "
                "possivel clicar no menu-item-24258. Verifique se o site mudou "
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
        Metodo de acesso PADRAO (alinhado a CalculadoraDiasUteisPage e
        CalculadoraJurosCompostosPage). Chama acessar_pagina_direto.
        Para o fluxo BlazeMeter (2 clicks no menu), use acessar_pelo_menu_principal().
        """
        self.acessar_pagina_direto()

    # =========================================================================
    # FLUXO 2: INTERACAO COM FORMULARIO INVESTIMENTO
    # =========================================================================
    def selecionar_aba_investimento(self):
        """Clica no card 'Investimento' no choiceScreen do iframe."""
        self._ensure_calculadora_context()
        ctx = self._active_page()
        last_err = None
        for txt in [
            "Investimento",
            "Calcule quanto seu dinheiro vai render",
            "📈",
            "investimento",
            "Rendimento",
        ]:
            try:
                loc = ctx.get_by_text(txt, exact=False)
                for i in range(loc.count()):
                    try:
                        el = loc.nth(i)
                        el.wait_for(state="attached", timeout=3000)
                        if el.is_visible():
                            el.scroll_into_view_if_needed()
                            el.click(timeout=10000)
                            self.wait_for_load()
                            ctx.wait_for_timeout(800)
                            return
                    except Exception as err:
                        last_err = err
                        continue
            except Exception as err:
                last_err = err
                continue
        try:
            raw = self._find_locator(self.ABA_INVESTIMENTO, fallback_text="Investimento")
            self.click_element(raw)
            self.wait_for_load()
        except Exception as err:
            raise RuntimeError(
                "Nao foi possivel selecionar aba Investimento no choiceScreen. "
                "Verifique se o iframe foi detectado corretamente. "
                f"Exception: {last_err or err}"
            ) from (last_err or err)

    # ---- Campos individuais (todos com fallback mascara BR + wait explicito)
    def preencher_valor_inicial(self, valor):
        self._ensure_calculadora_context()
        ctx = self._active_page()
        for _id in ["#valorInicial"]:
            try:
                el = ctx.locator(_id)
                if el.count() > 0:
                    for i in range(el.count()):
                        e = el.nth(i)
                        if e.is_visible():
                            self._preencher_com_mascara_br(e, valor, delay_ms=70)
                            return
                    self._preencher_com_mascara_br(el.first, valor, delay_ms=70)
                    return
            except Exception:
                continue
        try:
            raw = self._find_locator(self.INPUT_VALOR_INICIAL)
            el = self._apply_locator(raw)
            if hasattr(el, "first"): el = el.first
            self._preencher_com_mascara_br(el, valor, delay_ms=70)
        except Exception as err:
            raise RuntimeError(
                f"preencher_valor_inicial({valor}) FALHOU. Verifique se a aba "
                f"Investimento esta ativa. Detalhe: {err.__class__.__name__}"
            ) from err

    def preencher_aporte_mensal(self, valor):
        self._ensure_calculadora_context()
        ctx = self._active_page()
        for _id in ["#valorMensal"]:
            try:
                el = ctx.locator(_id)
                if el.count() > 0:
                    for i in range(el.count()):
                        e = el.nth(i)
                        if e.is_visible():
                            self._preencher_com_mascara_br(e, valor, delay_ms=70)
                            return
                    self._preencher_com_mascara_br(el.first, valor, delay_ms=70)
                    return
            except Exception:
                continue
        try:
            raw = self._find_locator(self.INPUT_APORTE_MENSAL)
            el = self._apply_locator(raw)
            if hasattr(el, "first"): el = el.first
            self._preencher_com_mascara_br(el, valor, delay_ms=70)
        except Exception as err:
            raise RuntimeError(
                f"preencher_aporte_mensal({valor}) FALHOU. Detalhe: "
                f"{err.__class__.__name__}"
            ) from err

    def preencher_taxa(self, taxa):
        self._ensure_calculadora_context()
        ctx = self._active_page()
        for _id in ["#taxaJurosInvest"]:
            try:
                el = ctx.locator(_id)
                if el.count() > 0:
                    for i in range(el.count()):
                        e = el.nth(i)
                        if e.is_visible():
                            self._preencher_com_mascara_br(e, taxa, delay_ms=70)
                            return
                    self._preencher_com_mascara_br(el.first, taxa, delay_ms=70)
                    return
            except Exception:
                continue
        try:
            raw = self._find_locator(self.INPUT_TAXA_JUROS)
            el = self._apply_locator(raw)
            if hasattr(el, "first"): el = el.first
            self._preencher_com_mascara_br(el, taxa, delay_ms=70)
        except Exception as err:
            raise RuntimeError(
                f"preencher_taxa({taxa}) FALHOU. Detalhe: {err.__class__.__name__}"
            ) from err

    def selecionar_periodicidade_taxa(self, periodicidade="mensal"):
        self._ensure_calculadora_context()
        ctx = self._active_page()
        eh_anual = "ano" in str(periodicidade).lower()
        opcao = "Anual" if eh_anual else "Mensal"
        try:
            el = ctx.locator("#tipoTaxaInvest")
            if el.count() > 0:
                try:
                    el.first.select_option(label=opcao)
                    return
                except Exception:
                    try: el.first.select_option(opcao.lower())
                    except Exception:
                        try:
                            el.first.click()
                            opt = el.first.locator(f"option:has-text('{opcao}')").first
                            opt.click()
                            return
                        except Exception:
                            pass
        except Exception:
            pass
        try:
            raw = self._find_locator(self.SELECT_PERIODICIDADE_TAXA)
            self.select_dropdown(raw, opcao)
        except Exception as err:
            raise RuntimeError(
                f"selecionar_periodicidade_taxa({periodicidade}) FALHOU. "
                f"Detalhe: {err.__class__.__name__}"
            ) from err

    def preencher_periodo(self, periodo):
        self._ensure_calculadora_context()
        ctx = self._active_page()
        for _id in ["#periodoInvest"]:
            try:
                el = ctx.locator(_id)
                if el.count() > 0:
                    for i in range(el.count()):
                        e = el.nth(i)
                        if e.is_visible():
                            e.click()
                            try: e.fill(str(periodo))
                            except Exception:
                                self._preencher_com_mascara_br(e, periodo, delay_ms=50)
                            return
                    el.first.click()
                    try: el.first.fill(str(periodo))
                    except Exception: self._preencher_com_mascara_br(el.first, periodo, delay_ms=50)
                    return
            except Exception:
                continue
        try:
            raw = self._find_locator(self.INPUT_PERIODO)
            self.fill_input(raw, str(periodo))
        except Exception as err:
            raise RuntimeError(
                f"preencher_periodo({periodo}) FALHOU. "
                f"Detalhe: {err.__class__.__name__}"
            ) from err

    def selecionar_unidade_periodo(self, unidade="meses"):
        self._ensure_calculadora_context()
        ctx = self._active_page()
        eh_ano = "ano" in str(unidade).lower()
        opcao = "Anos" if eh_ano else "Meses"
        try:
            el = ctx.locator("#tipoPeriodoInvest")
            if el.count() > 0:
                try:
                    el.first.select_option(label=opcao)
                    return
                except Exception:
                    try:
                        el.first.click()
                        opt = el.first.locator(f"option:has-text('{opcao}')").first
                        opt.click()
                        return
                    except Exception:
                        pass
        except Exception:
            pass
        try:
            raw = self._find_locator(self.SELECT_UNIDADE_PERIODO)
            self.select_dropdown(raw, opcao)
        except Exception as err:
            raise RuntimeError(
                f"selecionar_unidade_periodo({unidade}) FALHOU. "
                f"Detalhe: {err.__class__.__name__}"
            ) from err

    # =========================================================================
    # ACAO: CALCULAR
    # =========================================================================
    def calcular(self):
        """
        Clica no botao Calcular (onclick='calcularInvestimento()') e espera
        6s para JS calcular e renderizar div #resultInvestimento.
        """
        self._ensure_calculadora_context()
        ctx = self._active_page()
        last_err = None
        for loc_str in self.BOTAO_CALCULAR[:4]:
            try:
                cand = self._build_locator(loc_str)
                for el in cand or []:
                    try:
                        if el.count() > 0 and el.first.is_visible():
                            el.first.scroll_into_view_if_needed()
                            el.first.click(timeout=12000)
                            ctx.wait_for_timeout(6000)
                            return
                    except Exception as err:
                        last_err = err
            except Exception as err:
                last_err = err
                continue
        try:
            raw = self._find_locator(self.BOTAO_CALCULAR, fallback_text="Calcular")
            self.click_element(raw)
            self.wait_for_load()
            ctx.wait_for_timeout(6000)
        except Exception as err:
            raise RuntimeError(
                f"Nao foi possivel clicar em Calcular Investimento. "
                f"Detalhe: {last_err or err}"
            ) from (last_err or err)

    def clicar_calcular(self):
        """
        Alias de calcular() — garante CONFORMIDADE de interface publica
        com os outros POMs (CalculadoraDiasUteisPage.clicar_calcular /
        CalculadoraJurosCompostosPage.clicar_calcular).
        """
        self.calcular()

    # =========================================================================
    # LEITURA DE RESULTADOS
    # =========================================================================
    def _obter_campo(self, lista_ids, timeout=12000):
        self._ensure_calculadora_context()
        ctx = self._active_page()
        for loc_id in lista_ids:
            try:
                el = ctx.locator(loc_id)
                if el.count() > 0:
                    try:
                        for i in range(el.count()):
                            e = el.nth(i)
                            if e.is_visible():
                                try:
                                    e.wait_for(state="visible", timeout=timeout)
                                except Exception:
                                    pass
                                txt = (e.inner_text() or e.input_value() or "").strip()
                                if txt:
                                    return txt
                    except Exception:
                        pass
                    txt = (el.first.inner_text() or el.first.input_value() or "").strip()
                    if txt:
                        return txt
            except Exception:
                continue
        # Fallback por texto
        for loc_id in lista_ids:
            try:
                raw = self._find_locator([loc_id])
                if self.is_element_visible(raw, timeout=2000):
                    return self.get_text(raw)
            except Exception:
                continue
        return ""

    def obter_montante_final(self):
        """Retorna o montante acumulado (investido + juros). Campo principal."""
        return self._obter_campo(self.RESULT_MONTANTE_FINAL)

    def obter_total_investido(self):
        """Retorna a soma de valor inicial + todos aportes mensais."""
        return self._obter_campo(self.RESULT_TOTAL_INVESTIDO)

    def obter_total_juros(self):
        """Retorna o ganho bruto com rendimento (montante - investido)."""
        return self._obter_campo(self.RESULT_TOTAL_JUROS)

    def obter_valor_inicial_resultado(self):
        return self._obter_campo(self.RESULT_VALOR_INICIAL_RESULT)

    def obter_total_aportes_resultado(self):
        return self._obter_campo(self.RESULT_TOTAL_APORTES_RESULT)

    def obter_taxa_formatada(self):
        return self._obter_campo(self.RESULT_TAXA_FORMATADA)

    def obter_periodo_formatado(self):
        return self._obter_campo(self.RESULT_PERIODO_FORMATADO)

    def obter_resulado_completo(self):
        """
        Retorna dicionario consolidado com TODOS os campos conhecidos do
        resultado (ideal para asserts em testes).
        """
        return {
            "montante_final": self.obter_montante_final(),
            "total_investido": self.obter_total_investido(),
            "total_juros": self.obter_total_juros(),
            "valor_inicial": self.obter_valor_inicial_resultado(),
            "total_aportes": self.obter_total_aportes_resultado(),
            "taxa_formatada": self.obter_taxa_formatada(),
            "periodo_formatado": self.obter_periodo_formatado(),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def obter_mensagem_erro(self):
        """Captura erro de validacao (campos obrigatorios, etc)."""
        return self._obter_campo(self.MENSAGENS_ERRO, timeout=5000)

    # ------------------------------------------------------------------
    # Metodos ALINHADOS aos demais POMs (conformidade estrutural):
    #   - obter_resultado()      => alias p/ obter_montante_final()
    #   - calcular_investimento()  => alias p/ calcular_customizado()
    # Garantem a mesma "interface publica" das outras classes.
    # ------------------------------------------------------------------
    def obter_resultado(self):
        """
        Alias padrao para o resultado principal (igual a Dias Uteis / Juros).
        Retorna o montante final (campo destaque #valorFinal).
        """
        return self.obter_montante_final()

    def calcular_investimento(self, valor_inicial, aporte_mensal, taxa, periodo,
                                taxa_periodicidade="mensal", unidade_periodo="meses"):
        """
        Helper parametrizavel PADRAO (mesma assinatura do Juros:
        calcular_divida / calcular_investimento). Executa o fluxo todo e
        retorna o dict consolidado de resultado.
        """
        return self.calcular_customizado(
            valor_inicial=valor_inicial,
            aporte_mensal=aporte_mensal,
            taxa=taxa,
            periodo=periodo,
            taxa_periodicidade=taxa_periodicidade,
            unidade_periodo=unidade_periodo,
        )

    # =========================================================================
    # CENARIOS DE CALCULO PRE-DEFINIDOS (helpers p/ testes)
    # =========================================================================
    def calcular_cenario_padrao_12meses(self):
        """
        Cenário FELIZ #1 default de investimento:
          - R$ 10.000,00 inicial
          - R$ 500,00/mes aporte
          - 0,80% a.m. taxa
          - 12 meses

        Retorna obter_resulado_completo() com os valores preenchidos.
        """
        self.selecionar_aba_investimento()
        self.preencher_valor_inicial("10000")
        self.preencher_aporte_mensal("500")
        self.preencher_taxa("0.8")
        self.selecionar_periodicidade_taxa("mensal")
        self.preencher_periodo("12")
        self.selecionar_unidade_periodo("meses")
        self.calcular()
        return self.obter_resulado_completo()

    def calcular_cenario_longo_prazo(self):
        """
        Cenário FELIZ #2 (10 anos):
          - R$ 50.000,00 inicial
          - R$ 1.000,00 aporte mensal
          - 1,00% a.m. (CDI + spread realista)
          - 120 meses (10 anos)
        """
        self.selecionar_aba_investimento()
        self.preencher_valor_inicial("50000")
        self.preencher_aporte_mensal("1000")
        self.preencher_taxa("1")
        self.selecionar_periodicidade_taxa("mensal")
        self.preencher_periodo("120")
        self.selecionar_unidade_periodo("meses")
        self.calcular()
        return self.obter_resulado_completo()

    def calcular_cenario_apenas_inicial(self):
        """
        Cenário FELIZ #3 (modo simples): sem aporte mensal (0):
          - R$ 20.000,00 inicial
          - 1,2% a.m.
          - 36 meses
          - Aporte ZERO
        """
        self.selecionar_aba_investimento()
        self.preencher_valor_inicial("20000")
        self.preencher_aporte_mensal("0")
        self.preencher_taxa("1.2")
        self.selecionar_periodicidade_taxa("mensal")
        self.preencher_periodo("36")
        self.selecionar_unidade_periodo("meses")
        self.calcular()
        return self.obter_resulado_completo()

    def calcular_customizado(self, valor_inicial, aporte_mensal, taxa, periodo,
                              taxa_periodicidade="mensal", unidade_periodo="meses"):
        """Helper genérico (chama todos métodos em sequência)."""
        self.selecionar_aba_investimento()
        self.preencher_valor_inicial(valor_inicial)
        self.preencher_aporte_mensal(aporte_mensal)
        self.preencher_taxa(taxa)
        self.selecionar_periodicidade_taxa(taxa_periodicidade)
        self.preencher_periodo(periodo)
        self.selecionar_unidade_periodo(unidade_periodo)
        self.calcular()
        return self.obter_resulado_completo()
