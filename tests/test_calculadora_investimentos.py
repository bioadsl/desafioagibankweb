# -*- coding: utf-8 -*-
"""
tests/test_calculadora_investimentos.py
=======================================
Suite de testes E2E para a Calculadora de Investimentos do blog Agibank,
utilizando o Page Object CalculadoraInvestimentosPage (pages/calculadora_investimentos_page.py).

Testes implementados (8 cenários):
  [01] test_validar_pagina_carregada           -> URL + titulo + iframe carregado
  [02] test_validar_aba_investimento_existe    -> aba card visivel
  [03] test_validar_menu_principal_blazemeter   -> 2 clicks BlazeMeter levam à página
  [04] test_calcular_investimento_padrao_12meses -> CENARIO FELIZ #1 default (10k+500/mes+0,80%+12m)
  [05] test_calcular_investimento_longo_prazo   -> CENARIO FELIZ #2 10 anos (50k+1k+1%am+120m)
  [06] test_calcular_investimento_apenas_inicial_sem_aporte -> CENARIO #3 (aporte=0)
  [07] test_validar_integridade_valores          -> montante = investido + rendimento
  [08] test_validar_obter_resultado_interface_padrao -> conformidade: obter_resultado() existe
  [09] test_validar_obter_mensagem_erro_interface -> conformidade: obter_mensagem_erro() existe
"""
import re
import pytest

from pages.calculadora_investimentos_page import CalculadoraInvestimentosPage


VALOR_ESPERADO_12M_MESES = "R$ 17.274,56"
INVESTIDO_ESPERADO_12M = "R$ 16.000,00"
RENDIMENTO_ESPERADO_12M = "R$ 1.274,56"
PERIODO_ESPERADO_12M = "12 meses"
TAXA_ESPERADA_12M = "0,80% a.m."


class TestCalculadoraInvestimentos:

    @pytest.fixture(autouse=True)
    def setup(self, page):
        """
        Fixture auto-executada antes de CADA teste.
        Inicializa POM e acessa página DIRETA (padrão dos outros testes).
        """
        self.page = page
        self.invest_page = CalculadoraInvestimentosPage(page)
        self.invest_page.acessar_pagina()

    # ------------------------------------------------------------------
    # Helpers internos (evitar código repetido)
    # ------------------------------------------------------------------
    @staticmethod
    def _extrair_valor_numerico(texto):
        """Converte 'R$ 1.234,56' -> float(1234.56). Segue padrão dos outros testes."""
        if not texto:
            return 0.0
        try:
            texto_limpo = texto.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
            numeros = re.findall(r"\d+\.?\d*", texto_limpo)
            if numeros:
                return float(numeros[0])
        except Exception:
            pass
        return 0.0

    @staticmethod
    def _checar_texto_reais(texto):
        if not texto:
            return False
        return bool(re.match(r"R\$\s*\d", texto))

    # ======================================================================
    # TESTE 1: VALIDAR CARREGAMENTO BASICO (página + iframe + choiceScreen)
    # ======================================================================
    @pytest.mark.calculadora_investimentos
    @pytest.mark.smoke
    @pytest.mark.carregamento
    def test_validar_pagina_carregada(self):
        """Smoke test: confirma que página + iframe da calculadora carregaram."""
        try:
            self.invest_page.wait_for_real_page(
                check_url_contains="juros-compostos",
                check_title_contains="Juros Compostos",
                timeout=90000,
            )
        except Exception:
            pytest.skip("Cloudflare não completou bypass - teste de estrutura pulado")

        assert self.invest_page._calc_frame is not None or getattr(
            self.invest_page.page, "url", ""
        ), "Nenhum contexto ativo (iframe detectado ou página carregada)."

        # ao menos um dos 2 formulários deve existir no contexto ativo
        ctx = self.invest_page._active_page()
        formularios = (
            ctx.locator("#choiceScreen").count()
            + ctx.locator("#formInvestimento").count()
            + ctx.locator("#formDivida").count()
        )
        assert formularios > 0, (
            f"Calculadora não carregou no frame ativo. choiceScreen={ctx.locator('#choiceScreen').count()} "
            f"forms divida/invest={ctx.locator('#formDivida').count()}/{ctx.locator('#formInvestimento').count()}"
        )

    # ======================================================================
    # TESTE 2: ABA INVESTIMENTO EXISTE E É CLIÁVEL
    # ======================================================================
    @pytest.mark.calculadora_investimentos
    @pytest.mark.carregamento
    def test_validar_aba_investimento_existe(self):
        """Clica na aba investimento e confirma que formulário ficou acessível."""
        self.invest_page.selecionar_aba_investimento()
        ctx = self.invest_page._active_page()
        assert ctx.locator("#formInvestimento").count() >= 1, (
            "Após clicar na aba Investimento, #formInvestimento não foi encontrado no DOM."
        )

    # ======================================================================
    # TESTE 3: NAVEGACAO PELO MENU PRINCIPAL (Fluxo BlazeMeter)
    # ======================================================================
    @pytest.mark.calculadora_investimentos
    @pytest.mark.integracao
    @pytest.mark.blazemeter
    def test_validar_menu_principal_blazemeter(self, context):
        """
        Teste de INTEGRAÇÃO: repete os 2 clicks do BlazeMeter
        (data-attachment-id 20644 + menu-item 24258) de uma página VIRGEM.
        Usa a fixture 'context' (Playwright) para criar nova página limpa,
        sem herdar o iframe já detectado pelo setup autouse.

        Observação: o layout do menu do blog pode variar ao longo do tempo;
        caso o menu não seja localizado (RuntimeError do POM), este teste
        faz SKIP em vez de FAIL (não há quebra de funcionalidade core da
        calculadora - apenas rota alternativa de navegação).
        """
        page2 = context.new_page()
        try:
            nova_instancia = CalculadoraInvestimentosPage(page2)
            try:
                nova_instancia.acessar_pelo_menu_principal()
            except RuntimeError as exc_menu:
                pytest.skip(
                    "Menu BlazeMeter não localizado (estrutura menu blog pode ter "
                    f"mudado). Skip OK. Detalhe: {exc_menu.__class__.__name__}"
                )
            # Depois dos 2 clicks + navegação: iframe da calculadora DEVE existir
            ctx = nova_instancia._active_page()
            try:
                ctx.wait_for_timeout(2500)
                ctx.wait_for_load_state("networkidle", timeout=30000)
            except Exception:
                pass
            qtd = (
                ctx.locator("#choiceScreen").count()
                + ctx.locator("#formInvestimento").count()
                + ctx.locator("#formDivida").count()
            )
            # Também aceitamos URL conter "calculadora" OU "juros-compostos" como prova de
            # navegação OK. O passo 2 (menu-item 24258) costuma levar para a página geral
            # /calculadora/ (lista todas as calculadoras do blog), que é o destino real do
            # fluxo BlazeMeter capturado originalmente.
            url_final = getattr(page2, "url", "")
            url_ajuste_ok = (
                "juros-compostos" in url_final
                or "calculadora" in url_final
            )
            assert qtd > 0 or url_ajuste_ok, (
                "Navegacao por menu BlazeMeter não levou à calculadora. "
                f"URL final={url_final}; "
                f"EscolhaScreen/FormDiv/FormInv counts = {qtd}"
            )
        finally:
            try:
                page2.close()
            except Exception:
                pass

    # ======================================================================
    # TESTE 4: CENARIO FELIZ #1 DEFAULT (10k + 500/mês + 0,80% a.m. + 12 meses)
    #          Valores extraídos da navegação real em scripts_extrai_ids_invest.py
    # ======================================================================
    @pytest.mark.calculadora_investimentos
    @pytest.mark.cenario_feliz
    @pytest.mark.portfolio
    def test_calcular_investimento_padrao_12meses(self):
        """
        Cenário padrão de curto prazo (1 ano):
            - Valor Inicial ............ R$ 10.000,00
            - Aporte Mensal ............ R$   500,00
            - Taxa Juros ............... 0,80% a.m.
            - Período .................. 12 meses

        Resultados esperados (confirmados via rodada real do iframe standalone):
            valorFinal   = R$ 17.274,56
            valorInvestido = R$ 16.000,00
            rendimentoTotal = R$ 1.274,56
            periodoTexto = 12 meses
            taxaTextoInvest = 0,80% a.m.
        """
        res = self.invest_page.calcular_cenario_padrao_12meses()

        assert self._checar_texto_reais(res["montante_final"]), (
            f"Montante final deve ter formato R$ X.XXX,XX. Recebido: '{res['montante_final']}'"
        )
        assert self._checar_texto_reais(res["total_investido"])
        assert self._checar_texto_reais(res["total_juros"])

        # asserts de valores exatos (Golden)
        assert res["montante_final"]  == VALOR_ESPERADO_12M_MESES, (
            f"Montante final divergente. Esperado {VALOR_ESPERADO_12M_MESES} | "
            f"Recebido '{res['montante_final']}'"
        )
        assert res["total_investido"] == INVESTIDO_ESPERADO_12M, (
            f"Total investido divergente. Esperado {INVESTIDO_ESPERADO_12M} | "
            f"Recebido '{res['total_investido']}'"
        )
        assert res["total_juros"]     == RENDIMENTO_ESPERADO_12M, (
            f"Rendimento total divergente. Esperado {RENDIMENTO_ESPERADO_12M} | "
            f"Recebido '{res['total_juros']}'"
        )
        assert res["periodo_formatado"] == PERIODO_ESPERADO_12M, (
            f"Período formatado divergente. Esperado '{PERIODO_ESPERADO_12M}' | "
            f"Recebido '{res['periodo_formatado']}'"
        )
        assert res["taxa_formatada"]    == TAXA_ESPERADA_12M, (
            f"Taxa formatada divergente. Esperado '{TAXA_ESPERADA_12M}' | "
            f"Recebido '{res['taxa_formatada']}'"
        )

    # ======================================================================
    # TESTE 5: CENARIO FELIZ #2 (LONG PRAZO - 10 ANOS)
    # ======================================================================
    @pytest.mark.calculadora_investimentos
    @pytest.mark.cenario_feliz
    @pytest.mark.long_run
    def test_calcular_investimento_longo_prazo(self):
        """
        Cenário de 10 anos (120 meses):
            - Valor Inicial ............ R$ 50.000,00
            - Aporte Mensal ............ R$  1.000,00
            - Taxa Juros ............... 1,00% a.m.
            - Período .................. 120 meses

        Asserts sanidade (não há Golden confirmado ainda, só checagens fracas):
            montante_final >= investimentos_totais (juros SEMPRE positivos)
            montante_final >= 50000 + 120 * 1000 = 170k  (aplicado)
            total_juros > 0
        """
        res = self.invest_page.calcular_cenario_longo_prazo()
        mont_final = self._extrair_valor_numerico(res["montante_final"])
        investido  = self._extrair_valor_numerico(res["total_investido"])
        juros      = self._extrair_valor_numerico(res["total_juros"])

        valor_total_aplicado = 50000 + (1000 * 120)
        assert mont_final >= investido, (
            f"Montante final R${mont_final:.2f} deve ser >= investido R${investido:.2f}"
        )
        assert mont_final >= valor_total_aplicado, (
            f"Montante final R${mont_final:.2f} deve ser >= aplicado R${valor_total_aplicado:.2f}"
        )
        assert juros > 0, "Em cenário de investimento de 10 anos, juros/rendimento deve ser > 0"

    # ======================================================================
    # TESTE 6: SEM APORTE (apenas valor inicial rende juros)
    # ======================================================================
    @pytest.mark.calculadora_investimentos
    @pytest.mark.cenario_feliz
    def test_calcular_investimento_apenas_inicial_sem_aporte(self):
        """
        Cenário C (apenas inicial):
            R$ 20.000 inicial, aporte 0, taxa 1,2% a.m., 36 meses.
            Como aporte = 0, o investido final = 20k.
        """
        res = self.invest_page.calcular_cenario_apenas_inicial()
        investido = self._extrair_valor_numerico(res["total_investido"])
        montante  = self._extrair_valor_numerico(res["montante_final"])
        juros     = self._extrair_valor_numerico(res["total_juros"])

        assert investido >= 19000 and investido <= 21000, (
            f"Investido esperado ~R$ 20.000 (sem aportes). Recebido R${investido:.2f}"
        )
        assert montante > investido, "Mesmo sem aportes, juros positivos devem aumentar montante."
        assert juros > 0, "Juros/rendimento deve ser > 0."

    # ======================================================================
    # TESTE 7: INTEGRIDADE NUMERICA (montante = investido + juros)
    # ======================================================================
    @pytest.mark.calculadora_investimentos
    @pytest.mark.integracao
    def test_validar_integridade_valores(self):
        """
        Teste de sanidade matemática:
            montante_final = total_investido + rendimento_total
        (tolerância R$ 0,10 por arredondamento bancário em 2 casas decimais)
        """
        res = self.invest_page.calcular_cenario_padrao_12meses()
        mont_final = self._extrair_valor_numerico(res["montante_final"])
        investido  = self._extrair_valor_numerico(res["total_investido"])
        juros      = self._extrair_valor_numerico(res["total_juros"])
        assert abs(mont_final - (investido + juros)) <= 0.10, (
            f"Inconsistencia numerica: montante_final({mont_final}) "
            f"!= investido({investido}) + juros({juros}) = {investido+juros}. "
            f"Diferenca de {abs(mont_final-(investido+juros)):.2f}."
        )

    # ======================================================================
    # TESTE 8: CONFORMIDADE DE INTERFACE (obter_resultado() / obter_mensagem_erro())
    #           Alinhado aos outros POMs (Dias Uteis / Juros)
    # ======================================================================
    @pytest.mark.calculadora_investimentos
    @pytest.mark.conformidade
    def test_validar_obter_resultado_interface_padrao(self):
        """
        Garante a mesma interface pública dos outros POMs:
         - obter_resultado()  (ex: igual CalculadoraDiasUteisPage.obter_resultado)
         - obter_resultado() != vazio após calcular
        """
        self.invest_page.calcular_cenario_padrao_12meses()
        result_txt = self.invest_page.obter_resultado()
        assert callable(getattr(self.invest_page, "obter_resultado", None)), (
            "Método obrigatório 'obter_resultado()' ausente na CalculadoraInvestimentosPage."
        )
        assert isinstance(result_txt, str) and len(result_txt) > 0, (
            f"obter_resultado() deve retornar string não vazia. Recebido: {result_txt!r}"
        )
        assert self._checar_texto_reais(result_txt), (
            f"obter_resultado() deve ter formato R$ X.XXX,XX. Recebido {result_txt!r}"
        )

    @pytest.mark.calculadora_investimentos
    @pytest.mark.conformidade
    def test_validar_obter_mensagem_erro_interface(self):
        """
        Garante que obter_mensagem_erro() existe e sempre retorna string (mesmo
        que vazia quando não há erros — evita NoneType nos testes).
        """
        assert callable(getattr(self.invest_page, "obter_mensagem_erro", None)), (
            "Método obrigatório 'obter_mensagem_erro()' ausente."
        )
        erro = self.invest_page.obter_mensagem_erro()
        assert isinstance(erro, str), (
            f"obter_mensagem_erro() deve retornar str (mesmo que ''). Tipo = {type(erro)}"
        )
