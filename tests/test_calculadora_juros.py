import re
import pytest
from pages.calculadora_juros_page import CalculadoraJurosCompostosPage


class TestCalculadoraJurosCompostos:

    @pytest.fixture(autouse=True)
    def setup(self, page):
        self.page = page
        self.calc_page = CalculadoraJurosCompostosPage(page)
        self.calc_page.acessar_pagina()

    def _extrair_valor_numerico(self, texto):
        if not texto:
            return 0.0
        try:
            texto_limpo = texto.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
            numeros = re.findall(r'\d+\.?\d*', texto_limpo)
            if numeros:
                return float(numeros[0])
        except Exception:
            pass
        return 0.0

    @pytest.mark.juros_compostos
    @pytest.mark.cenario_feliz
    @pytest.mark.investimento
    def test_calcular_juros_compostos_investimento_cenario_basico(self):
        self.calc_page.calcular_investimento(
            valor_inicial="1000",
            aporte_mensal="100",
            taxa_juros="1.0",
            periodo="12",
            periodicidade_taxa="mensal",
            unidade_periodo="meses"
        )
        resultado = self.calc_page.obter_resultado()
        assert resultado is not None, "Nenhum resultado retornado para cálculo de investimento"
        assert len(resultado) > 0, "Resultado do investimento está vazio"
        valor = self._extrair_valor_numerico(resultado)
        assert valor > 1000, (
            f"Montante final ({valor}) deve ser maior que valor inicial após investimento com juros"
        )

    @pytest.mark.juros_compostos
    @pytest.mark.cenario_feliz
    @pytest.mark.investimento
    def test_calcular_investimento_longo_prazo(self):
        self.calc_page.calcular_investimento(
            valor_inicial="5000",
            aporte_mensal="500",
            taxa_juros="0.8",
            periodo="24",
            periodicidade_taxa="mensal",
            unidade_periodo="meses"
        )
        resultado = self.calc_page.obter_resultado()
        assert resultado is not None, "Nenhum resultado retornado para investimento de longo prazo"
        assert len(resultado) > 0, "Resultado do investimento de longo prazo está vazio"
        valor = self._extrair_valor_numerico(resultado)
        valor_total_aplicado = 5000 + (500 * 24)
        assert valor >= valor_total_aplicado, (
            f"Montante final ({valor}) deve ser >= valor aplicado ({valor_total_aplicado})"
        )

    @pytest.mark.juros_compostos
    @pytest.mark.cenario_feliz
    @pytest.mark.divida
    @pytest.mark.katalon_golden
    def test_calcular_divida_katalon_golden_cem_doismeio_vintequatro(self):
        """
        Cenário GOLDEN extraído diretamente da gravação Katalon Recorder
        do usuário, com asserts exatos.

        Dados Katalon:
          - Valor do Empréstimo ....... R$ 10.000,00
          - Taxa de juros .............. 2,50% a.m. (mensal)
          - Prazo ...................... 24 meses

        Resultado esperado (asserts Katalon):
          - valorTotal ............... R$ 13.419,08
          - valorEmprestimoResult .... R$ 10.000,00
          - totalJuros ............... R$ 3.419,08
          - valorParcela ............. R$ 559,13
          - numeroParcelas ........... 24x
          - taxaTextoDivida .......... 2,50% a.m.
        """
        self.calc_page.selecionar_aba_divida()
        self.calc_page.preencher_valor_inicial("10000")  # R$ 10.000,00
        self.calc_page.preencher_taxa_juros("2.5")        # 2,5% a.m.
        self.calc_page.selecionar_periodicidade_taxa("mensal")
        self.calc_page.preencher_periodo("24")            # 24 meses
        self.calc_page.selecionar_unidade_periodo("meses")
        self.calc_page.clicar_calcular()

        resultado = self.calc_page.obter_resulado_divida_completo()

        # --- Valores exatos (capturados no Katalon) ---
        assert resultado["valor_total"]         == "R$ 13.419,08", (
            f"Valor total divergente: esperado R$ 13.419,08, recebido '{resultado['valor_total']}'"
        )
        assert resultado["valor_emprestimo"]    == "R$ 10.000,00", (
            f"Valor empréstimo divergente: esperado R$ 10.000,00, recebido '{resultado['valor_emprestimo']}'"
        )
        assert resultado["total_juros"]         == "R$ 3.419,08", (
            f"Total juros divergente: esperado R$ 3.419,08, recebido '{resultado['total_juros']}'"
        )
        assert resultado["valor_parcela"]       == "R$ 559,13", (
            f"Valor parcela divergente: esperado R$ 559,13, recebido '{resultado['valor_parcela']}'"
        )
        assert resultado["numero_parcelas"]     == "24x", (
            f"Núm. parcelas divergente: esperado '24x', recebido '{resultado['numero_parcelas']}'"
        )
        assert resultado["taxa_texto"]          == "2,50% a.m.", (
            f"Taxa formatada divergente: esperado '2,50% a.m.', recebido '{resultado['taxa_texto']}'"
        )

        # --- Sinais vitais (checagens fracas de sanidade) ---
        total_juros_num = self._extrair_valor_numerico(resultado["total_juros"])
        val_emp_num   = self._extrair_valor_numerico(resultado["valor_emprestimo"])
        val_tot_num   = self._extrair_valor_numerico(resultado["valor_total"])
        parcela_num   = self._extrair_valor_numerico(resultado["valor_parcela"])
        parcela_calc  = round(val_tot_num / 24, 2)
        assert total_juros_num > 0, "Juros deve ser positivo em uma dívida"
        assert abs(val_tot_num - (val_emp_num + total_juros_num)) < 0.10, (
            "Valor total deve ser igual a valor empréstimo + juros (tolerância R$ 0,10)"
        )
        assert abs(parcela_num - parcela_calc) < 0.10, (
            f"Parcela informada ({parcela_num}) não bate com valor total / 24 ({parcela_calc})"
        )

    @pytest.mark.juros_compostos
    @pytest.mark.cenario_feliz
    @pytest.mark.divida
    def test_calcular_juros_compostos_divida(self):
        self.calc_page.calcular_divida(
            valor_inicial="2000",
            aporte_mensal="200",
            taxa_juros="5.0",
            periodo="6",
            periodicidade_taxa="mensal",
            unidade_periodo="meses"
        )
        resultado = self.calc_page.obter_resultado()
        assert resultado is not None, "Nenhum resultado retornado para cálculo de dívida"
        assert len(resultado) > 0, "Resultado da dívida está vazio"

    @pytest.mark.juros_compostos
    @pytest.mark.cenario_erro
    @pytest.mark.investimento
    def test_calcular_sem_valor_inicial(self):
        self.calc_page.selecionar_aba_investimento()
        self.calc_page.preencher_aporte_mensal("100")
        self.calc_page.preencher_taxa_juros("1.0")
        self.calc_page.preencher_periodo("12")
        self.calc_page.clicar_calcular()
        resultado = self.calc_page.obter_resultado()
        msg_erro = self.calc_page.obter_mensagem_erro()
        tem_tratamento = (len(msg_erro) > 0) or (len(resultado) == 0)
        assert tem_tratamento, "Sistema deve validar valor inicial obrigatório"

    @pytest.mark.juros_compostos
    @pytest.mark.cenario_erro
    @pytest.mark.investimento
    def test_calcular_sem_taxa_juros(self):
        self.calc_page.selecionar_aba_investimento()
        self.calc_page.preencher_valor_inicial("1000")
        self.calc_page.preencher_aporte_mensal("100")
        self.calc_page.preencher_periodo("12")
        self.calc_page.clicar_calcular()
        resultado = self.calc_page.obter_resultado()
        msg_erro = self.calc_page.obter_mensagem_erro()
        tem_tratamento = (len(msg_erro) > 0) or (len(resultado) == 0)
        assert tem_tratamento, "Sistema deve validar taxa de juros obrigatória"

    @pytest.mark.juros_compostos
    @pytest.mark.cenario_erro
    @pytest.mark.investimento
    def test_calcular_sem_periodo(self):
        self.calc_page.selecionar_aba_investimento()
        self.calc_page.preencher_valor_inicial("1000")
        self.calc_page.preencher_aporte_mensal("100")
        self.calc_page.preencher_taxa_juros("1.0")
        self.calc_page.clicar_calcular()
        resultado = self.calc_page.obter_resultado()
        msg_erro = self.calc_page.obter_mensagem_erro()
        tem_tratamento = (len(msg_erro) > 0) or (len(resultado) == 0)
        assert tem_tratamento, "Sistema deve validar período obrigatório"

    @pytest.mark.juros_compostos
    @pytest.mark.validacao
    def test_validar_abas_existem(self):
        pag_carregada = self.calc_page.wait_for_real_page(
            check_url_contains=["juros", "agibank", "compostos"],
            check_title_contains=[
                "Juros Compostos", "Juros compostos", "juros compostos",
                "Calcular Juros", "Calculadora", "Agibank", "agibank",
            ],
            timeout=90000,
        )
        url_lower = self.page.url.lower()
        url_ok = (
            "agibank" in url_lower
            and ("juros" in url_lower or "compostos" in url_lower)
        )
        assert url_ok, (
            f"Página de juros compostos não carregada corretamente. URL atual: {self.page.url}"
        )
        if pag_carregada:
            titulo = self.page.title().lower()
            tem_titulo_ok = (
                "juros" in titulo
                or "compostos" in titulo
                or "calculadora" in titulo
                or "agibank" in titulo
            )
            assert tem_titulo_ok, (
                f"Título da página não confere após bypass cloudflare: {self.page.title()}"
            )
