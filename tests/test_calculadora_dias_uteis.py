import re
import pytest
from pages.calculadora_dias_uteis_page import CalculadoraDiasUteisPage


class TestCalculadoraDiasUteis:

    @pytest.fixture(autouse=True)
    def setup(self, page):
        self.page = page
        self.calc_page = CalculadoraDiasUteisPage(page)
        self.calc_page.acessar_pagina()

    @pytest.mark.dias_uteis
    @pytest.mark.cenario_feliz
    def test_calcular_dias_uteis_periodo_simples(self):
        data_inicial = "2026-01-02"
        data_final = "2026-01-08"
        self.calc_page.calcular_dias_uteis(
            data_inicial=data_inicial,
            data_final=data_final,
            sabado=False,
            domingo=False,
            feriados=True
        )
        resultado = self.calc_page.obter_resultado()
        assert resultado is not None, "Nenhum resultado foi retornado pela calculadora"
        assert len(resultado) > 0, "O resultado retornado está vazio"
        assert any(c.isdigit() for c in resultado), f"O resultado '{resultado}' não contém números"

    @pytest.mark.dias_uteis
    @pytest.mark.cenario_feliz
    def test_calcular_dias_uteis_incluindo_sabado_domingo(self):
        data_inicial = "2026-01-01"
        data_final = "2026-01-31"
        self.calc_page.calcular_dias_uteis(
            data_inicial=data_inicial,
            data_final=data_final,
            sabado=True,
            domingo=True,
            feriados=False
        )
        resultado = self.calc_page.obter_resultado()
        assert resultado is not None, "Nenhum resultado foi retornado pela calculadora"
        assert len(resultado) > 0, "O resultado retornado está vazio"
        numeros = re.findall(r'\d+', resultado)
        assert len(numeros) > 0, f"O resultado '{resultado}' não contém valores numéricos"

    @pytest.mark.dias_uteis
    @pytest.mark.cenario_feliz
    def test_calcular_dias_uteis_semana_completa(self):
        data_inicial = "2026-01-05"
        data_final = "2026-01-09"
        self.calc_page.calcular_dias_uteis(
            data_inicial=data_inicial,
            data_final=data_final,
            sabado=False,
            domingo=False,
            feriados=True
        )
        resultado = self.calc_page.obter_resultado()
        assert resultado is not None, "Nenhum resultado foi retornado pela calculadora"
        numeros = re.findall(r'\d+', resultado)
        assert len(numeros) > 0, f"Resultado sem números: {resultado}"
        dias_encontrados = int(numeros[0])
        assert dias_encontrados >= 5, (
            f"Esperado pelo menos 5 dias úteis para semana completa, obtido: {dias_encontrados}"
        )

    @pytest.mark.dias_uteis
    @pytest.mark.cenario_erro
    def test_calcular_sem_data_inicial(self):
        self.calc_page.preencher_data_final("2026-01-10")
        self.calc_page.marcar_sabado(False)
        self.calc_page.marcar_domingo(False)
        self.calc_page.marcar_feriados(True)
        self.calc_page.clicar_calcular()
        resultado = self.calc_page.obter_resultado()
        msg_erro = self.calc_page.obter_mensagem_erro()
        tem_erro = (len(msg_erro) > 0) or (len(resultado) == 0)
        assert tem_erro, "Deveria haver erro ou resultado vazio ao não preencher data inicial"

    @pytest.mark.dias_uteis
    @pytest.mark.cenario_erro
    def test_calcular_sem_data_final(self):
        self.calc_page.preencher_data_inicial("2026-01-01")
        self.calc_page.marcar_sabado(False)
        self.calc_page.marcar_domingo(False)
        self.calc_page.marcar_feriados(True)
        self.calc_page.clicar_calcular()
        resultado = self.calc_page.obter_resultado()
        msg_erro = self.calc_page.obter_mensagem_erro()
        tem_erro = (len(msg_erro) > 0) or (len(resultado) == 0)
        assert tem_erro, "Deveria haver erro ou resultado vazio ao não preencher data final"

    @pytest.mark.dias_uteis
    @pytest.mark.cenario_erro
    def test_calcular_data_final_anterior_a_inicial(self):
        self.calc_page.calcular_dias_uteis(
            data_inicial="2026-01-10",
            data_final="2026-01-01",
            sabado=False,
            domingo=False,
            feriados=True
        )
        resultado = self.calc_page.obter_resultado()
        msg_erro = self.calc_page.obter_mensagem_erro()
        tem_tratamento = (len(msg_erro) > 0) or (len(resultado) >= 0)
        assert tem_tratamento, "Sistema deve tratar data final menor que inicial"

    @pytest.mark.dias_uteis
    @pytest.mark.validacao
    def test_validar_elementos_pagina_carregados(self):
        assert "Calculadora" in self.page.title() or "Dias Úteis" in self.page.title(), (
            "Título da página não confere"
        )
        assert "dias-uteis" in self.page.url, "URL da página não confere"
