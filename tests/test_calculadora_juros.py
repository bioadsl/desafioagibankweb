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
