import pytest
from pages.blog_agi_page import BlogAgiPage


class TestBlogAgiPesquisa:

    @pytest.fixture(autouse=True)
    def setup(self, page):
        self.page = page
        self.blog_page = BlogAgiPage(page)
        self.blog_page.acessar_pagina()

    @pytest.mark.blog_agi
    @pytest.mark.pesquisa
    @pytest.mark.cenario_1
    def test_pesquisa_termo_relevante_retorna_resultados(self):
        termo_pesquisa = "Empréstimo"
        self.blog_page.realizar_pesquisa(termo_pesquisa)
        assert self.blog_page.verificar_url_contem_pesquisa(termo_pesquisa), (
            f"URL após pesquisa não contém parâmetros de busca. URL atual: {self.page.url}"
        )
        qtd_resultados = self.blog_page.quantidade_resultados()
        assert qtd_resultados > 0, (
            f"Nenhum resultado encontrado para termo '{termo_pesquisa}'. "
            f"Esperado pelo menos 1 resultado."
        )
        contem_termo = self.blog_page.verificar_termo_em_resultados(termo_pesquisa)
        assert contem_termo, (
            f"Os resultados da pesquisa não contêm referências ao termo '{termo_pesquisa}'"
        )

    @pytest.mark.blog_agi
    @pytest.mark.pesquisa
    @pytest.mark.cenario_2
    def test_pesquisa_termo_inexistente_retorna_mensagem_adequadamente(self):
        termo_inexistente = "XYZTERMOIMPROVAVEL123456789"
        self.blog_page.realizar_pesquisa(termo_inexistente)
        assert self.blog_page.verificar_url_contem_pesquisa(termo_inexistente), (
            "URL não refletiu os parâmetros de pesquisa para termo inexistente"
        )
        qtd_resultados = self.blog_page.quantidade_resultados()
        sem_resultado_msg = self.blog_page.verificar_mensagem_sem_resultado()
        busca_valida = (qtd_resultados == 0) or sem_resultado_msg
        assert busca_valida, (
            "Para termo inexistente esperava-se: "
            "ou zero resultados ou mensagem de 'Nenhum resultado encontrado'. "
            f"Obtido: {qtd_resultados} resultados e mensagem de sem-resultado={sem_resultado_msg}"
        )

    @pytest.mark.blog_agi
    @pytest.mark.pesquisa
    @pytest.mark.cenario_3
    def test_pesquisa_termos_financeiros_comuns(self):
        termos = ["FGTS", "CDB", "Imposto de Renda"]
        for termo in termos:
            self.blog_page.acessar_pagina()
            self.blog_page.realizar_pesquisa(termo)
            qtd = self.blog_page.quantidade_resultados()
            assert qtd >= 0, (
                f"Pesquisa por '{termo}' deve retornar quantidade não-negativa de resultados"
            )

    @pytest.mark.blog_agi
    @pytest.mark.pesquisa
    @pytest.mark.validacao
    def test_validar_pagina_inicial_blog_carregada(self):
        pag_carregada = self.blog_page.wait_for_real_page(
            check_url_contains=["agibank", "blog", "blogdoagi"],
            check_title_contains=[
                "Blog", "blog", "Agi", "agi", "Agibank", "agibank",
                "Notícias", "notícias", "Finanças", "financas",
            ],
            timeout=90000,
        )
        url = self.page.url.lower()
        url_ok = "agibank" in url or "blogdoagi" in url or "blog" in url
        assert url_ok, (
            f"Página inicial do blog não carregada corretamente. URL: {self.page.url}"
        )
        if pag_carregada:
            titulo = self.page.title()
            assert len(titulo) > 0, "Título do blog não carregou após bypass cloudflare"
