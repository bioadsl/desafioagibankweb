import os
import json
import time
import pytest
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright

try:
    from reports.screenshot_utils import (
        salvar_screenshot_teste_automatica as save_test_shot,
        obter_info_ambiente as get_env_info,
        obter_numero_e_descricao_para_teste as parse_scenario_meta,
        agora_str_milis as now_ms,
        OverlayCtx,
    )
    SCREENSHOT_OVERLAY_ATIVO = True
except Exception as _e:  # pragma: no cover
    import sys
    sys.stderr.write(f"[WARN] Screenshot overlay desligado (deps? {_e})\n")
    SCREENSHOT_OVERLAY_ATIVO = False

_doc_cache = {}
_env = None
_total = 0
_report_path = ""
_session_prefix = ""
_pw_ver = ""

try:
    from reports.auditoria import (
        obter_logger_auditoria as get_audit_logger,
        AcaoAuditoria, StatusAuditoria
    )
    AUDITORIA_ATIVA = True
    _audit_logger = get_audit_logger()
except Exception as _e:  # pragma: no cover
    import sys
    sys.stderr.write(f"[WARN] Auditoria desligada: {_e}\n")
    AUDITORIA_ATIVA = False
    _audit_logger = None  # type: ignore


def _audit(acao, status, detalhes=None):
    if not AUDITORIA_ATIVA or _audit_logger is None:
        return None
    try:
        return _audit_logger.registrar(acao=acao, status=status, detalhes=detalhes)
    except Exception:  # pragma: no cover
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
    global _pw_ver
    headless = os.getenv("HEADLESS", "true").lower() == "true"
    browser = playwright_instance.chromium.launch(
        headless=headless,
        slow_mo=int(os.getenv("SLOW_MO", "0")),
        channel="chrome" if os.getenv("USE_SYSTEM_CHROME", "false").lower() == "true" else None,
        args=STEALTH_ARGS,
    )
    try:
        _pw_ver = str(getattr(browser, "version", "") or "")
    except Exception:
        _pw_ver = ""
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser):
    headless = os.getenv("HEADLESS", "true").lower() == "true"
    viewport_cfg = None if (not headless) else {"width": 1920, "height": 1080}

    context = browser.new_context(
        viewport=viewport_cfg,
        no_viewport=(not headless),
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

    cf_titles = ("Checking your browser", "Just a moment",
                  "Verifying you are human", "attention required")

    def handle_cloudflare(page):
        for _ in range(6):
            try:
                title = (page.title() or "").strip().lower()
                if any(flag in title for flag in cf_titles):
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

    if SCREENSHOT_OVERLAY_ATIVO and rep.when == "call":
        _overlay_screenshot(item, rep)

    # fallback: screenshot crú extra em caso de falha
    if rep.when == "call" and rep.failed and "page" in item.fixturenames:
        page = item.funcargs["page"]
        os.makedirs("reports/screenshots", exist_ok=True)
        shot = f"reports/screenshots/RAW_FALHA_{item.name}.png"
        try:
            page.screenshot(path=shot, full_page=True)
            extras = getattr(rep, "extras", None)
            if extras is not None:
                import pytest_html  # noqa
                rep.extras.append(pytest_html.extras.image(shot))
        except Exception:
            pass


def _overlay_screenshot(item, rep):
    global _doc_cache, _env, _total, _report_path, _session_prefix, _pw_ver

    try:
        os.makedirs("reports/screenshots", exist_ok=True)
        page = item.funcargs["page"] if "page" in item.fixturenames else None
    except Exception:
        page = None

    try:
        if _env is None:
            _env = get_env_info(page=page, browser_name="Chromium",
                               browser_version=_pw_ver,
                               headless_override=os.getenv("HEADLESS", "true"),
                               slow_mo_override=os.getenv("SLOW_MO", "0"))
        else:
            _env = get_env_info(page=page,
                               browser_name=getattr(_env, "browser_nome", None) or "Chromium",
                               browser_version=_pw_ver or getattr(_env, "browser_versao", ""),
                               headless_override=getattr(_env, "modo_headless", "true"),
                               slow_mo_override=getattr(_env, "slow_mo_ms", "0"))
    except Exception:
        pass
    amb = _env or get_env_info(page=page)

    num, desc = parse_scenario_meta(item, _doc_cache)
    total_cenarios = _total or None

    # map status (mesmo pattern usado no audit_map abaixo — evita if/elif chain)
    raw = (rep.outcome or "").lower()
    xfail = bool(getattr(rep, "wasxfail", False))
    status_rules = {
        (True, "passed"):  "XPASS",
        (True, "skipped"): "XFAIL",
        (True, "failed"):  "XFAIL",
        (False, "passed"): "PASS",
        (False, "failed"): "FAIL",
        (False, "skipped"):"SKIP",
        (False, "error"):  "ERROR",
    }
    status_out = status_rules.get((xfail, raw), raw.upper())

    # Nao usar [ ] no nome: file URL interpreta glob character class
    ts = datetime.now().strftime("%Y%m%d_%H%M%S%f")[:-3]
    prefixo_num = f"({int(num):02d})_" if num else "(NA)_"
    slug = "".join(c if c.isalnum() or c in "-_" else "_" for c in (item.name or ""))[:70].rstrip("_")
    out_png = f"reports/screenshots/{_session_prefix}{prefixo_num}{slug}_{status_out}_{ts}.png"

    ctx = OverlayCtx(
        status=status_out,
        numero_cenario=num,
        total_cenarios=int(total_cenarios) if total_cenarios else None,
        descricao_cenario=desc,
        nome_completo_teste=str(getattr(item, "nodeid", "") or item.name or ""),
        data_hora_str=now_ms(),
        ambiente=amb,
        report_path=_report_path,
    )
    save_test_shot(page=page, output_png=out_png, ctx=ctx, full_page=True)

    # Anexo imagem — 3 camadas de fallback
    try:
        extras = getattr(rep, "extras", None)
        if extras is not None and os.path.isfile(out_png):
            import pytest_html  # type: ignore
            import base64

            with open(out_png, "rb") as fh:
                data_uri = (f"data:image/png;name={os.path.basename(out_png)};base64,"
                            + base64.b64encode(fh.read()).decode("ascii"))
            basename = os.path.basename(out_png)
            abs_url = "file:///" + os.path.abspath(out_png).replace("\\", "/")

            for src in (data_uri, f"./screenshots/{basename}", abs_url):
                try:
                    rep.extras.append(pytest_html.extras.image(src))
                except Exception:
                    pass
    except Exception:
        pass
    except Exception as _e:
        try:
            import sys
            sys.stderr.write(f"[WARN] overlay screenshot fail ({item.name}): {_e.__class__.__name__}\n")
        except Exception:
            pass


def pytest_sessionstart(session):
    global _env, _session_prefix, _total, _report_path

    try:
        if _env is None:
            _env = get_env_info(page=None, browser_name="Chromium", browser_version="",
                               headless_override=os.getenv("HEADLESS", "true"),
                               slow_mo_override=os.getenv("SLOW_MO", "0"))
    except Exception:
        pass
    try:
        _session_prefix = datetime.now().strftime("%Y%m%d_%H%M_")
    except Exception:
        _session_prefix = ""
    try:
        _total = (
            len(session.items)
            if (hasattr(session, "items") and session.items)
            else int((getattr(session.config, "workerinput", None) or {}).get("testscount", 0))
        )
    except Exception:
        _total = 0
    try:
        opt_html = getattr(session.config, "option", None)
        _report_path = str(getattr(opt_html, "htmlpath", "") or "")
    except Exception:
        _report_path = ""

    if not AUDITORIA_ATIVA:
        return
    detalhes = {
        "session_id": (str(getattr(session.config, "workerinput", {}) or "") or session.name or "main"),
        "rootdir": str(getattr(session.config, "rootdir", "")),
        "inifile": str(getattr(session.config, "inifile", "")),
        "plugins": sorted([k for k in getattr(session.config.pluginmanager, "_name2plugin", {}).keys()]),
        "arg_options": (session.config.known_args_namespace.__dict__
                        if hasattr(session.config, "known_args_namespace") else {}),
        "env": {
            "HEADLESS": os.getenv("HEADLESS"),
            "SLOW_MO": os.getenv("SLOW_MO"),
            "CI": os.getenv("CI"),
            "GITHUB_ACTIONS": os.getenv("GITHUB_ACTIONS"),
        },
        "timestamp_inicio_sessao": datetime.utcnow().isoformat() + "Z",
        "total_testes_coletados": _total,
        "report_html_path": _report_path,
        "session_prefixo_arquivos": _session_prefix,
        "screenshot_overlay_ativo": SCREENSHOT_OVERLAY_ATIVO,
    }
    _audit(AcaoAuditoria.RELATORIO_GERACAO_INICIO, StatusAuditoria.SUCESSO, detalhes=detalhes)



def pytest_runtest_logreport(report):
    if not AUDITORIA_ATIVA:
        return
    if report.when not in ("call", "setup"):
        return

    status_map = {
        "passed": StatusAuditoria.SUCESSO,
        "failed": StatusAuditoria.FALHA,
        "error":  StatusAuditoria.FALHA,
        "skipped": StatusAuditoria.SUCESSO,
    }
    status_audit = status_map.get(report.outcome, StatusAuditoria.FALHA)

    markers_golden = []
    try:
        if report.keywords:
            kw = ("katalon_golden", "portfolio", "blazemeter", "conformidade")
            markers_golden = [m for m in kw if m in report.keywords]
    except Exception:
        pass

    detalhes = {
        "test_nodeid": report.nodeid,
        "fase": report.when,
        "outcome_pytest": report.outcome,
        "duracao_segundos": round(report.duration, 4),
        "markers": markers_golden,
        "possui_screenshot_falha": report.outcome == "failed",
        "linha_fail": (str(getattr(report, "longrepr", ""))[:500]
                     if report.outcome in ("failed", "error") else ""),
    }
    # Teste GOLDEN que passa marca modificacao massa benchmark
    acao = (AcaoAuditoria.DADOS_MODIFICACAO
            if (markers_golden and report.outcome == "passed")
            else AcaoAuditoria.TESTE_EXECUCAO)
    _audit(acao, status_audit, detalhes=detalhes)


def pytest_exception_interact(node, call, report):
    if not AUDITORIA_ATIVA:
        return
    detalhes = {
        "nodeid": str(getattr(node, "nodeid", "")),
        "tipo_excecao": type(call.excinfo.value).__name__ if call.excinfo else "",
        "mensagem": (str(call.excinfo.value))[:1000] if call.excinfo else "",
        "traceback": (str(report.longrepr))[:2000] if getattr(report, "longrepr", None) else "",
    }
    _audit(AcaoAuditoria.PROCESSAMENTO_ERRO, StatusAuditoria.FALHA, detalhes=detalhes)


def pytest_unconfigure(config):
    if not AUDITORIA_ATIVA:
        return
    arquivos_gerados: list = []
    try:
        reports_dir = Path("reports")
        if reports_dir.exists():
            htmls = sorted(reports_dir.glob("*.html"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
            zips = sorted(reports_dir.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)[:2]
            for f in (*htmls, *zips):
                arquivos_gerados.append({
                    "arquivo": f.name,
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
    _audit(AcaoAuditoria.RELATORIO_GERACAO_FIM, StatusAuditoria.SUCESSO, detalhes=detalhes_fim)
    _audit(AcaoAuditoria.RELATORIO_EXPORTACAO, StatusAuditoria.SUCESSO, detalhes=detalhes_fim)


_CSS_CUSTOM = r"""
.results-table td { vertical-align: top !important; }
.results-table td img, .col-links img, .extra img, div.extras img, tbody img {
    max-width: 100% !important; max-height: 420px !important;
    width: auto !important; height: auto !important; object-fit: contain !important;
    border: 1px solid #cfd8e3 !important; border-radius: 6px !important;
    margin: 6px 4px !important; padding: 3px !important; background: #fff !important;
    box-shadow: 0 1px 4px rgba(0,0,0,.08) !important; cursor: zoom-in;
    transition: transform .2s, box-shadow .2s ease-in-out;
}
.results-table td img:hover, .col-links img:hover, .extra img:hover {
    transform: scale(1.015); box-shadow: 0 3px 10px rgba(0,48,100,.25) !important;
    border-color: #003064 !important;
}
.extras, .extra, div.extra { display:block !important; max-width:100% !important;
    overflow-x:hidden !important; page-break-inside:avoid !important; }
.col-links { min-width:130px; max-width:260px; word-break: break-word; }
.col-links a img { max-height:64px !important; max-width:120px !important; }
"""


def pytest_html_results_summary(prefix, summary, postfix):
    try:
        import pytest_html  # type: ignore
        prefix.append(pytest_html.extras.html(
            f"\n<style type='text/css' media='all'>{_CSS_CUSTOM}\n</style>\n"
        ))
    except Exception:
        pass


