import os
import json
import time
import pytest
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright

# =============================================================================
# NOVO (2026-09-17): SISTEMA DE SCREENSHOTS POR CASO DE TESTE COM OVERLAY
# Cada teste, independente de passar/falhar/pular, TEM UM SCREENSHOT salvo
# em reports/screenshots/NN_NOME_TESTE_STATUS_DATAHORA.png
# Características do overlay (módulo reports.screenshot_utils):
#   • Faixa colorida topo: VERDE=PASS, VERMELHA=FAIL, AMARELA=SKIP, AZUL=XFAIL
#   • Numeração do cenário [01/35] (parse das docstrings das suites de teste)
#   • Descrição do cenário (igual docstring)
#   • Nome completo do teste: tests/x.py::Classe::nome
#   • Data/hora com PRECISÃO DE MILISSEGUNDOS
#   • Rodapé com 6 linhas de ambiente: SO, Python, Playwright, Browser +
#     versão, CPU, RAM, resolução página, hostname, usuário, cwd, HEADLESS?
#   • Hash SHA-256 curto (12 chars) para integridade da screenshot
#   • Placeholder geométrico para testes sem Playwright (unitários auditoria)
# =============================================================================
try:
    from reports.screenshot_utils import (
        salvar_screenshot_teste_automatica,
        obter_info_ambiente,
        obter_numero_e_descricao_para_teste,
        agora_str_milis,
        OverlayCtx,
    )
    SCREENSHOT_OVERLAY_ATIVO = True
except Exception as _err_scr:  # pragma: no cover - nunca quebra execucao
    import sys
    sys.stderr.write(
        f"[WARN] Screenshot overlay DESATIVADO (Pillow/psutil?): {_err_scr}\n"
        f"[WARN]   → Screenshots simples ainda serão tiradas em falhas.\n"
    )
    SCREENSHOT_OVERLAY_ATIVO = False

# Variáveis GLOBAIS (nesta sessão pytest) — usadas pelos hooks:
_NUMERACAO_CACHE_DOCSTRINGS = {}     # path_arquivo → {"nome_func": ("02", "descrição")}
_INFO_AMBIENTE_GLOBAL = None         # 1 coleta no sessionstart
_TOTAL_TESTES_SESSAO = 0            # quantos coletados (para montar "03/35")
_REPORT_HTML_GLOBAL = ""            # caminho report html (footer do overlay)
_SESSION_ID_GLOBAL = ""             # prefixo arquivos datahora
_PW_BROWSER_VERSION = ""            # capturado no fixture browser


# =============================================================================
# SISTEMA DE AUDITORIA DE RELATORIOS (Logs criptografados 2 camadas JSONL + SQLite)
# 5 eventos criticos auditados:
#   RELATORIO_ACESSO | DADOS_MODIFICACAO | RELATORIO_EXPORTACAO |
#   PROCESSAMENTO_ERRO | TENTATIVA_ACESSO_NAO_AUTORIZADO
# =============================================================================
try:
    from reports.auditoria import (
        obter_logger_auditoria, AcaoAuditoria, StatusAuditoria
    )
    AUDITORIA_ATIVA = True
    _audit_logger = obter_logger_auditoria()
except Exception as err:  # pragma: no cover - auditoria nao quebra execucao
    import sys
    sys.stderr.write(f"[WARN] Auditoria de relatorios DESATIVADA: {err}\n")
    AUDITORIA_ATIVA = False
    _audit_logger = None  # type: ignore


def _audit(acao, status, detalhes=None):
    if not AUDITORIA_ATIVA or _audit_logger is None:
        return None
    try:
        return _audit_logger.registrar(acao=acao, status=status, detalhes=detalhes)
    except Exception:  # pragma: no cover - falha auditoria nunca quebra o teste
        return None



STEALTH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--disable-dev-shm-usage",
    "--disable-features=IsolateOrigins,site-per-process",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-web-security",
    "--disable-site-isolation-trials",
    "--disable-features=BlockInsecurePrivateNetworkRequests",
    "--start-maximized",
    "--disable-infobars",
    "--hide-scrollbars",
    "--mute-audio",
    "--ignore-certificate-errors",
    "--ignore-ssl-errors=yes",
    "--allow-running-insecure-content",
]

CHROME_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="function")
def browser(playwright_instance):
    global _PW_BROWSER_VERSION
    headless = os.getenv("HEADLESS", "true").lower() == "true"
    browser = playwright_instance.chromium.launch(
        headless=headless,
        slow_mo=int(os.getenv("SLOW_MO", "0")),
        channel="chrome" if os.getenv("USE_SYSTEM_CHROME", "false").lower() == "true" else None,
        args=STEALTH_ARGS,
    )
    try:
        _PW_BROWSER_VERSION = str(getattr(browser, "version", "") or "")
    except Exception:
        _PW_BROWSER_VERSION = ""
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser):
    headless = os.getenv("HEADLESS", "true").lower() == "true"
    # Quando solicitado maximizado (HEADED), passar viewport=None para
    # respeitar --start-maximized. No headless, viewport tem que ser fixo.
    viewport_cfg = None if (not headless) else {"width": 1920, "height": 1080}

    context = browser.new_context(
        viewport=viewport_cfg,
        no_viewport=(not headless),  # Chrome nativo maximizado
        locale="pt-BR",
        timezone_id="America/Sao_Paulo",
        user_agent=CHROME_UA,
        accept_downloads=True,
        ignore_https_errors=True,
        permissions=["geolocation", "notifications"],
        extra_http_headers={
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
        },
    )

    context.tracing.start(screenshots=True, snapshots=True, sources=True)

    def handle_cloudflare(page):
        for _ in range(6):
            try:
                title = page.title()
                if (
                    "Checking your browser" in title
                    or "Just a moment" in title
                    or "Verifying you are human" in title
                    or title.strip().lower() == "attention required"
                ):
                    page.wait_for_timeout(5000)
                else:
                    break
            except Exception:
                page.wait_for_timeout(5000)

    context.on("page", handle_cloudflare)

    yield context
    context.tracing.stop(path="reports/trace.zip")
    context.close()


@pytest.fixture(scope="function")
def page(context):
    page = context.new_page()
    page.set_default_timeout(60000)
    page.set_default_navigation_timeout(60000)

    try:
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5].map(i => (
                    {0: i, name: `Chrome PDF Plugin ${i}`, filename: `internal-pdf-viewer-${i}`, length: 1}
                )),
            });
            Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en-US', 'en']});
            Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
            window.chrome = { runtime: {} };
        """)
    except Exception:
        pass

    yield page
    page.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    # ---------------------------------------------------------------------
    # Sistema novo: SCREENSHOT COM OVERLAY para CADA CASO DE TESTE
    #   • Aciona SOMENTE em when="call" (fim do teste).
    #   • Mesmo se for SKIP/PASS/FAIL/ERROR → uma screenshot numerada.
    # ---------------------------------------------------------------------
    if SCREENSHOT_OVERLAY_ATIVO and rep.when == "call":
        _gerar_screenshot_overlay_por_teste(item, rep)

    # ---------------------------------------------------------------------
    # Sistema ANTIGO (fallback) — tira screenshot SEM overlay se:
    #   (a) o novo sistema está desligado OU
    #   (b) o teste FALHOU e queremos um extra crú extra.
    # ---------------------------------------------------------------------
    if rep.when == "call" and rep.failed:
        if "page" in item.fixturenames:
            page = item.funcargs["page"]
            os.makedirs("reports/screenshots", exist_ok=True)
            screenshot_path = f"reports/screenshots/RAW_FALHA_{item.name}.png"
            try:
                page.screenshot(path=screenshot_path, full_page=True)
                # Tenta anexar ao pytest-html também
                try:
                    html = getattr(item, "config", None) and hasattr(item.config, "_metadata")
                    extras = getattr(rep, "extras", None)
                    if extras is not None:
                        import pytest_html  # noqa
                        rep.extras.append(pytest_html.extras.image(screenshot_path))
                except Exception:
                    pass
            except Exception:
                pass


def _gerar_screenshot_overlay_por_teste(item, rep):
    """
    Função auxiliar que executa todo o pipeline:
      1. Coleta status do teste (PASS / FAIL / SKIP).
      2. Localiza a fixture 'page' (Playwright) se existir, senão placeholder.
      3. Busca (no cache do conftest) NUMERAÇÃO e DESCRIÇÃO da docstring suite.
      4. Monta OverlayCtx e chama salvar_screenshot_teste_automatica.
      5. Anexa ao pytest-html como IMAGEM extra (visível ao lado do teste).
    """
    global _NUMERACAO_CACHE_DOCSTRINGS
    global _INFO_AMBIENTE_GLOBAL
    global _TOTAL_TESTES_SESSAO
    global _REPORT_HTML_GLOBAL
    global _SESSION_ID_GLOBAL
    global _PW_BROWSER_VERSION

    try:
        os.makedirs("reports/screenshots", exist_ok=True)
        page = None
        if "page" in item.fixturenames:
            try:
                page = item.funcargs["page"]
            except Exception:
                page = None
        # Info ambiente: 1 vez por sessão + atualiza versão do browser + page
        try:
            if _INFO_AMBIENTE_GLOBAL is None:
                _INFO_AMBIENTE_GLOBAL = obter_info_ambiente(
                    page=page,
                    browser_name="Chromium",
                    browser_version=_PW_BROWSER_VERSION,
                    headless_override=os.getenv("HEADLESS", "true"),
                    slow_mo_override=os.getenv("SLOW_MO", "0"),
                )
            else:
                # Atualiza browser_version e resolução com o page atual
                atualizado = obter_info_ambiente(
                    page=page,
                    browser_name=_INFO_AMBIENTE_GLOBAL.browser_nome or "Chromium",
                    browser_version=_PW_BROWSER_VERSION or _INFO_AMBIENTE_GLOBAL.browser_versao,
                    headless_override=_INFO_AMBIENTE_GLOBAL.modo_headless,
                    slow_mo_override=_INFO_AMBIENTE_GLOBAL.slow_mo_ms,
                )
                _INFO_AMBIENTE_GLOBAL = atualizado
        except Exception:
            pass
        amb = _INFO_AMBIENTE_GLOBAL
        if amb is None:
            amb = obter_info_ambiente(page=page)

        num, desc = obter_numero_e_descricao_para_teste(
            item, _NUMERACAO_CACHE_DOCSTRINGS
        )
        total_cenarios = _TOTAL_TESTES_SESSAO or None

        # --- Status normalizado: PASS / FAIL / SKIP / XFAIL / XPASS / ERROR ---
        status_raw = (rep.outcome or "").lower()
        foi_xfail = bool(getattr(rep, "wasxfail", False))
        if foi_xfail and status_raw == "passed":
            status_out = "XPASS"
        elif foi_xfail and status_raw in ("skipped", "failed"):
            status_out = "XFAIL"
        elif status_raw in ("passed",):
            status_out = "PASS"
        elif status_raw in ("failed",):
            status_out = "FAIL"
        elif status_raw in ("skipped",):
            status_out = "SKIP"
        elif status_raw in ("error",):
            status_out = "ERROR"
        else:
            status_out = status_raw.upper()

        # --- Monta nome arquivo: reports/screenshots/[NN]_NomeStatus_.png
        # OBS 2026-09-17: NAO usar colchetes [] NO NOME DO ARQUIVO. Navegadores
        # (Chrome, Edge, Firefox) interpretam [..] em "file:// URLs" como
        # "character class GLOB" e nao abrem o arquivo. Trocar [01] por (01).
        data_arq = datetime.now().strftime("%Y%m%d_%H%M%S%f")[:-3]
        if num:
            # [01] vira "(01)" → sem colchetes, 100% seguro para file URLs
            prefixo_num = f"({int(num):02d})_"
        else:
            prefixo_num = "(NA)_"  # NA = Nao Aplicavel / sem numeracao
        nome_curto = "".join(c if c.isalnum() or c in "-_" else "_" for c in (item.name or ""))
        nome_curto = nome_curto[:70].rstrip("_")
        out_png = (
            "reports/screenshots/"
            f"{_SESSION_ID_GLOBAL}{prefixo_num}{nome_curto}_{status_out}_{data_arq}.png"
        )

        ctx = OverlayCtx(
            status=status_out,
            numero_cenario=num,
            total_cenarios=int(total_cenarios) if total_cenarios else None,
            descricao_cenario=desc,
            nome_completo_teste=str(getattr(item, "nodeid", "") or item.name or ""),
            data_hora_str=agora_str_milis(),
            ambiente=amb,
            report_path=_REPORT_HTML_GLOBAL,
        )
        salvar_screenshot_teste_automatica(page=page, output_png=out_png, ctx=ctx, full_page=True)

        # Anexa a imagem no pytest-html (visível no report.html)
        # ---------------------------------------------------------------------
        # ESTRATEGIA ROBUSTA 3 CAMADAS (evita nao exibir de jeito nenhum):
        #   [1] PRINCIPAL: DATA-URI BASE64 → imagem 100% embutida no HTML
        #       Nao importa caminho relativo, navegador, colchetes, nada.
        #   [2] FALLBACK 1: caminho RELATIVO "./screenshots/arquivo.png"
        #       Correto da perspectiva do report.html salvo em /reports.
        #   [3] FALLBACK 2: caminho ABSOLUTO file:/// + URL ENCODE (%20 espaço etc)
        # ---------------------------------------------------------------------
        try:
            extras = getattr(rep, "extras", None)
            if extras is not None and os.path.isfile(out_png):
                import pytest_html  # type: ignore
                import base64
                from urllib.parse import quote as urlencode  # noqa

                # --- Helper: arquivo -> string base64
                def _png_to_datauri(path_png: str) -> str:
                    with open(path_png, "rb") as fh:
                        dados = fh.read()
                    b64 = base64.b64encode(dados).decode("ascii")
                    return f"data:image/png;name={os.path.basename(path_png)};base64,{b64}"

                basename = os.path.basename(out_png)
                abs_path = os.path.abspath(out_png)

                # CAMADA 1 (mais importante): DATA URI BASE64
                try:
                    data_uri = _png_to_datauri(out_png)
                    rep.extras.append(pytest_html.extras.image(data_uri))
                except Exception:
                    pass

                # CAMADA 2: relativo "./screenshots/FILENAME" (relativo ao report/)
                try:
                    caminho_relativo_certo = f"./screenshots/{basename}"
                    rep.extras.append(pytest_html.extras.image(caminho_relativo_certo))
                except Exception:
                    pass

                # CAMADA 3: caminho absoluto file:/// com URL ENCODE
                try:
                    abs_url = "file:///" + abs_path.replace("\\", "/")
                    rep.extras.append(pytest_html.extras.image(abs_url))
                except Exception:
                    pass
        except Exception:
            pass
    except Exception as _err_gen:
        # Falha no screenshot NUNCA pode quebrar o teste.
        try:
            import sys
            sys.stderr.write(
                f"[WARN] Falha ao gerar screenshot overlay "
                f"({item.name}): {_err_gen.__class__.__name__}\n"
            )
        except Exception:
            pass


# =============================================================================
# HOOKS DE AUDITORIA DE RELATORIOS (integracao pytest -> sistema auditoria)
# =============================================================================
def pytest_sessionstart(session):
    """
    Auditoria: marca INÍCIO de geração de relatório e coleta de metadados
    da sessão (ambiente, python, SO, headless? slow_mo?).

    SCREENSHOT OVERLAY: também inicializa as variáveis globais:
      • _TOTAL_TESTES_SESSAO     — quantos testes a sessão coletou (para montar "01/35")
      • _REPORT_HTML_GLOBAL      — caminho do report.html (aparece no footer do overlay)
      • _SESSION_ID_GLOBAL       — prefixo YYYYMMDD_HHMM_ de todos os arquivos PNG numerados
    """
    global _TOTAL_TESTES_SESSAO
    global _REPORT_HTML_GLOBAL
    global _SESSION_ID_GLOBAL
    global _INFO_AMBIENTE_GLOBAL

    # Inicializa info ambiente o mais cedo possível (page ainda não existe)
    try:
        if _INFO_AMBIENTE_GLOBAL is None:
            _INFO_AMBIENTE_GLOBAL = obter_info_ambiente(
                page=None,
                browser_name="Chromium",
                browser_version="",
                headless_override=os.getenv("HEADLESS", "true"),
                slow_mo_override=os.getenv("SLOW_MO", "0"),
            )
    except Exception:
        pass

    try:
        from datetime import datetime as _dt_now
        _SESSION_ID_GLOBAL = _dt_now.now().strftime("%Y%m%d_%H%M_")
    except Exception:
        _SESSION_ID_GLOBAL = ""

    # Quantos testes a sessão coletou?
    _TOTAL_TESTES_SESSAO = 0
    try:
        if hasattr(session, "items") and session.items:
            _TOTAL_TESTES_SESSAO = len(session.items)
        elif hasattr(session.config, "workerinput"):
            # xdist workers
            _TOTAL_TESTES_SESSAO = int(
                (session.config.workerinput or {}).get("testscount", 0)
            )
    except Exception:
        _TOTAL_TESTES_SESSAO = 0

    # Caminho report HTML (rodapé overlay — facilita cruzamento)
    _REPORT_HTML_GLOBAL = ""
    try:
        opt_html = getattr(session.config, "option", None)
        if opt_html is not None:
            _REPORT_HTML_GLOBAL = str(getattr(opt_html, "htmlpath", "") or "")
    except Exception:
        _REPORT_HTML_GLOBAL = ""

    if not AUDITORIA_ATIVA:
        return
    detalhes = {
        "session_id": str(getattr(session.config, "workerinput", {}) or "") or session.name or "main",
        "rootdir": str(getattr(session.config, "rootdir", "")),
        "inifile": str(getattr(session.config, "inifile", "")),
        "plugins": sorted([k for k in getattr(session.config.pluginmanager, "_name2plugin", {}).keys()]),
        "arg_options": session.config.known_args_namespace.__dict__ if hasattr(session.config, "known_args_namespace") else {},
        "env": {
            "HEADLESS": os.getenv("HEADLESS"),
            "SLOW_MO": os.getenv("SLOW_MO"),
            "CI": os.getenv("CI"),
            "GITHUB_ACTIONS": os.getenv("GITHUB_ACTIONS"),
        },
        "timestamp_inicio_sessao": datetime.utcnow().isoformat() + "Z",
        "total_testes_coletados": _TOTAL_TESTES_SESSAO,
        "report_html_path": _REPORT_HTML_GLOBAL,
        "session_prefixo_arquivos": _SESSION_ID_GLOBAL,
        "screenshot_overlay_ativo": SCREENSHOT_OVERLAY_ATIVO,
    }
    _audit(AcaoAuditoria.RELATORIO_GERACAO_INICIO, StatusAuditoria.SUCESSO, detalhes=detalhes)


def pytest_runtest_logreport(report):
    """
    Auditoria: registra CADA teste individual (pass/fail/skip/error).
    Quando temos um teste GOLDEN (Katalon / portfolio) e ele PASSA também
    marca DADOS_MODIFICACAO (atualizacao massa benchmark).
    """
    if not AUDITORIA_ATIVA:
        return
    if report.when != "call" and report.when != "setup":
        return
    status_map = {
        "passed": StatusAuditoria.SUCESSO,
        "failed": StatusAuditoria.FALHA,
        "error": StatusAuditoria.FALHA,
        "skipped": StatusAuditoria.SUCESSO,
    }
    status_audit = status_map.get(report.outcome, StatusAuditoria.FALHA)
    eh_setup = report.when == "setup"
    markers_golden = [m for m in dir(report) if False]
    markers_golden = []
    try:
        if report.keywords:
            for kw in ["katalon_golden", "portfolio", "blazemeter", "conformidade"]:
                if kw in report.keywords:
                    markers_golden.append(kw)
    except Exception:
        pass
    detalhes = {
        "test_nodeid": report.nodeid,
        "fase": report.when,
        "outcome_pytest": report.outcome,
        "duracao_segundos": round(report.duration, 4),
        "markers": markers_golden,
        "possui_screenshot_falha": bool(report.outcome == "failed"),
        "linha_fail": str(getattr(report, "longrepr", ""))[:500] if report.outcome in ("failed", "error") else "",
    }
    acao = AcaoAuditoria.TESTE_EXECUCAO
    if markers_golden and report.outcome == "passed":
        # A passagem de um teste GOLDEN atualiza baseline (Massa de benchmark)
        acao = AcaoAuditoria.DADOS_MODIFICACAO
    _audit(acao, status_audit, detalhes=detalhes)


def pytest_exception_interact(node, call, report):
    """
    Auditoria: captura TODAS exceptions levantadas (tratadas e interativas)
    como evento PROCESSAMENTO_ERRO para facilitar troubleshooting posterior.
    """
    if not AUDITORIA_ATIVA:
        return
    detalhes = {
        "nodeid": str(getattr(node, "nodeid", "")),
        "tipo_excecao": type(call.excinfo.value).__name__ if call.excinfo else "",
        "mensagem": str(call.excinfo.value)[:1000] if call.excinfo else "",
        "traceback": str(report.longrepr)[:2000] if getattr(report, "longrepr", None) else "",
    }
    _audit(AcaoAuditoria.PROCESSAMENTO_ERRO, StatusAuditoria.FALHA, detalhes=detalhes)


def pytest_unconfigure(config):
    """
    Auditoria: marca FIM de sessão + evento RELATORIO_EXPORTACAO
    (exportação do report.html pytest-html final + zip trace).
    """
    if not AUDITORIA_ATIVA:
        return
    arquivos_gerados: list = []
    try:
        reports_dir = Path("reports")
        if reports_dir.exists():
            for f in sorted(reports_dir.glob("*.html"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]:
                arquivos_gerados.append({
                    "arquivo": str(f.name),
                    "tamanho_bytes": f.stat().st_size,
                    "modificado_em": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                })
            for f in sorted(reports_dir.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)[:2]:
                arquivos_gerados.append({
                    "arquivo": str(f.name),
                    "tamanho_bytes": f.stat().st_size,
                    "modificado_em": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                })
    except Exception:
        pass
    detalhes_fim = {
        "reports_gerados": arquivos_gerados,
        "cmdline_args": " ".join(config.invocation_params.args or []),
        "report_html_path": str(getattr(config.option, "htmlpath", "") or ""),
    }
    # 2 eventos: marca FIM de geração (GERACAO_FIM) + EXPORTACAO (arquivos prontos p/ download)
    _audit(AcaoAuditoria.RELATORIO_GERACAO_FIM, StatusAuditoria.SUCESSO, detalhes=detalhes_fim)
    _audit(AcaoAuditoria.RELATORIO_EXPORTACAO, StatusAuditoria.SUCESSO, detalhes=detalhes_fim)


# =============================================================================
# CORRECAO CSS CUSTOMIZADO — imagens cabem no espaco reservado
# Resolve: espaco 150x150 do report vs imagem 1920x5000. Agora responsivo.
# =============================================================================
_CSS_CUSTOMIZADO_SCREENSHOTS = r"""
/* -----------------------------------------------------------------
   CSS Customizado — Sistema de Relatorios OS com Screenshots
   Garante que as imagens nao estourem a largura maxima do card e
   tenham aparencia profissional (borda, sombra, raio arredondado).
   ----------------------------------------------------------------- */
.results-table td {
    vertical-align: top !important;
}
/* Cada imagem no relatório (tanto link da coluna Links, quanto as extras abaixo): */
.results-table td img,
.col-links img,
#results-table img,
.extra img,
div.extras img,
.col-result img,
tbody.results img {
    max-width: 100% !important;
    max-height: 420px !important;
    width: auto !important;
    height: auto !important;
    object-fit: contain !important;
    border: 1px solid #cfd8e3 !important;
    border-radius: 6px !important;
    margin: 6px 4px !important;
    padding: 3px !important;
    background: #ffffff !important;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08) !important;
    cursor: zoom-in;
    transition: transform .2s ease-in-out, box-shadow .2s ease-in-out;
}
.results-table td img:hover,
.col-links img:hover,
#results-table img:hover,
.extra img:hover {
    transform: scale(1.015);
    box-shadow: 0 3px 10px rgba(0, 48, 100, 0.25) !important;
    border-color: #003064 !important; /* azul Agibank */
}
/* Bloco "Image 1 / 2": ajustar layout para nao ter rolagem horizontal */
.extras,
.extra,
div.extra {
    display: block !important;
    max-width: 100% !important;
    overflow-x: hidden !important;
    page-break-inside: avoid !important;
}
/* Espaco reservado da coluna Links (primeiro icone pequeno + texto link): */
.col-links {
    min-width: 130px;
    max-width: 260px;
    word-break: break-word;
}
.col-links a img {
    max-height: 64px !important;
    max-width: 120px !important;
}
"""


def pytest_html_results_summary(prefix, summary, postfix):
    """
    Hook do pytest-html v4.x.x — adicionado 2026-09-17.
    Injeta o CSS customizado ACIMA da tabela de resultados (no summary section).
    O CSS garante que as imagens dos screenshots sejam exibidas no espaco
    reservado (max 420px altura, max 100% largura, borda profissional azul).
    """
    try:
        import pytest_html  # type: ignore
        bloco_style = (
            f"\n<style type='text/css' media='all'>\n"
            f"/* CSS AUTOMATICO — Screenshots OS custom — nao remover */\n"
            f"{_CSS_CUSTOMIZADO_SCREENSHOTS}\n"
            f"</style>\n"
        )
        prefix.append(pytest_html.extras.html(bloco_style))
    except Exception:
        # Nao quebrar relatorio se CSS nao carregar
        pass

