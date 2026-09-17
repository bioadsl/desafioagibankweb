# -*- coding: utf-8 -*-
"""
screenshot_utils.py — Sistema de screenshots AUTOMÁTICOS por caso de teste
com OVERLAY de identificação (número cenário, status, data/hora ms, ambiente).

Objetivo: Atender o requisito do usuário:
   1. Screenshots tirados NO FINAL de cada caso de teste (PASS / FAIL / SKIP).
   2. Overlay HEADER COLORIDO no topo (verde = PASS, vermelho = FAIL,
      amarelo = SKIP / XFAIL), informando:
         • Numeração do cenário (ex: [03/35]) + descrição do cenário
           (igual docstring das suites de teste: "[03] test_incluindo_sab_dom...")
         • Nome completo do teste (arquivo.py::Classe::teste)
         • Status com ícone e cor
         • Data/Hora com PRECISÃO DE MILISSEGUNDOS
         • Informações do ambiente (SO, Python, Playwright, Browser, CPU, RAM,
           Resolução página) para rastreabilidade LGPD.
   3. Rodapé com hash SHA-256 curto da execução (integridade) e caminho do
      report.html para cruzamento.
   4. Para testes SEM Playwright (ex: unitários auditoria), gera uma imagem
      PLACEHOLDER de 1920x1080 com fundo padrão + overlay (não deixa faltar
      screenshot — 100% dos casos de teste tem sua captura numerada).
"""

import datetime as _dt
import hashlib
import os
import platform
import sys
import textwrap
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Pillow para desenhar overlay (com fallback se não tiver instalado —
# apenas imprime warn + não desenha texto, sem quebrar execução de teste).
try:
    from PIL import Image, ImageDraw, ImageFont  # type: ignore
    PILLOW_OK = True
except Exception as _e_pillow:
    PILLOW_OK = False
    _PILLOW_ERR = str(_e_pillow)


# ---------------------------------------------------------------------------
# Helpers de ambiente / SO
# ---------------------------------------------------------------------------
def _tam_fonte(n: int) -> int:
    """Garante tamanho mínimo de fonte — evita texto ilegível em FHD."""
    return max(14, min(n, 64))


def _font(size: int, bold: bool = False) -> Any:
    """Fonte segura: tenta Consolas, Arial, DejaVu Sans Mono, fallback default."""
    if not PILLOW_OK:
        return None
    size = _tam_fonte(size)
    candidates_bold = [
        "C:/Windows/Fonts/consolab.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
    ]
    candidates_normal = [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    lista = candidates_bold if bold else candidates_normal
    for path in lista:
        try:
            if os.path.isfile(path):
                return ImageFont.truetype(path, size=size)
        except Exception:
            continue
    try:
        return ImageFont.load_default()
    except Exception:
        return None


@dataclass
class AmbienteTesteInfo:
    """Informações de ambiente para exibir no overlay."""
    so_nome: str
    so_versao: str
    so_arquitetura: str
    python_versao: str
    python_implementacao: str
    playwright_versao: str
    pytest_versao: str
    browser_nome: str
    browser_versao: str
    cpu_nome: str
    cpu_cores_fisicos: int
    cpu_cores_logicos: int
    memoria_total_gb: float
    hostname: str
    usuario: str
    pagina_resolucao: str
    modo_headless: str
    slow_mo_ms: str
    cwd: str

    def resumo_curto(self) -> List[str]:
        """Lista de ~6 linhas compactas para caber no rodapé da screenshot."""
        return [
            f"SO: {self.so_nome} {self.so_versao} ({self.so_arquitetura})",
            f"Python {self.python_versao} ({self.python_implementacao}) | "
            f"Playwright {self.playwright_versao} | Pytest {self.pytest_versao}",
            f"Browser: {self.browser_nome} {self.browser_versao} | "
            f"Headless: {self.modo_headless} | slow_mo: {self.slow_mo_ms}ms",
            f"CPU: {self.cpu_nome} | RAM: {self.memoria_total_gb:.1f} GB | "
            f"Resolução: {self.pagina_resolucao}",
            f"Host: {self.hostname} | Usuário: {self.usuario}",
            f"Dir: {self.cwd}",
        ]


def obter_info_ambiente(
    page: Any = None,
    browser_name: str = "",
    browser_version: str = "",
    headless_override: Optional[str] = None,
    slow_mo_override: Optional[str] = None,
) -> AmbienteTesteInfo:
    """Coleta todas as infos de ambiente de forma defensiva (nunca crasha)."""

    # SO / máquina
    so_nome = platform.system() or "Unknown"
    so_versao = (platform.release() or "") + " " + (platform.version() or "")
    so_arquitetura = platform.machine() or ""

    # Python / deps
    py_ver = platform.python_version()
    py_impl = platform.python_implementation()
    try:
        import pytest as _pt
        pytest_v = _pt.__version__
    except Exception:
        pytest_v = "desconhecido"
    try:
        import playwright as _pw
        pw_v = _pw.__version__
    except Exception:
        try:
            from playwright.sync_api import sync_playwright  # noqa
            pw_v = "1.x (instalado)"
        except Exception:
            pw_v = "desconhecido"

    # CPU / memória (psutil, com fallback)
    cpu_nome = "desconhecido"
    cpu_fis = 0
    cpu_log = 0
    ram_gb = 0.0
    try:
        import psutil  # type: ignore
        cpu_log = psutil.cpu_count(logical=True) or 0
        cpu_fis = psutil.cpu_count(logical=False) or 0
        mem = psutil.virtual_memory()
        ram_gb = (mem.total or 0) / (1024 ** 3)
        try:
            if so_nome == "Windows":
                try:
                    import winreg  # type: ignore
                    with winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE,
                        r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
                    ) as k:
                        cpu_nome, _ = winreg.QueryValueEx(k, "ProcessorNameString")
                        cpu_nome = str(cpu_nome).strip()
                except Exception:
                    pass
            if cpu_nome == "desconhecido":
                cpu_nome = platform.processor() or "desconhecido"
        except Exception:
            cpu_nome = platform.processor() or "desconhecido"
    except Exception:
        cpu_nome = platform.processor() or "desconhecido"

    hostname = "desconhecido"
    usuario = "desconhecido"
    try:
        hostname = platform.node() or "desconhecido"
    except Exception:
        pass
    try:
        usuario = os.environ.get("USERNAME") or os.environ.get("USER") or "desconhecido"
    except Exception:
        pass

    # Browser / página (se tiver)
    bn = browser_name or (getattr(page, "browser", None) and getattr(page.browser, "browser_type", None) and page.browser.browser_type.name) or "desconhecido"
    bv = browser_version or ""
    resolucao = "desconhecida"
    if page is not None:
        try:
            if not bv:
                try:
                    bv = page.evaluate(
                        "() => navigator.userAgent.match(/Chrome\\/(\\S+)/)?.[1] || "
                        "navigator.userAgent.match(/Edg\\/(\\S+)/)?.[1] || ''"
                    ) or ""
                except Exception:
                    bv = ""
            try:
                sz = page.viewport_size
                if sz:
                    resolucao = f"{sz.get('width',0)}x{sz.get('height',0)}"
            except Exception:
                try:
                    resolucao = page.evaluate(
                        "() => `${window.innerWidth}x${window.innerHeight}`"
                    )
                except Exception:
                    resolucao = "desconhecida"
        except Exception:
            pass

    modo_hl = headless_override
    if modo_hl is None:
        modo_hl = os.environ.get("HEADLESS", "true")
    sm = slow_mo_override
    if sm is None:
        sm = os.environ.get("SLOW_MO", "0")
    try:
        cwd = os.getcwd()
    except Exception:
        cwd = ""
    return AmbienteTesteInfo(
        so_nome=so_nome,
        so_versao=so_versao,
        so_arquitetura=so_arquitetura,
        python_versao=py_ver,
        python_implementacao=py_impl,
        playwright_versao=pw_v,
        pytest_versao=pytest_v,
        browser_nome=str(bn),
        browser_versao=str(bv),
        cpu_nome=cpu_nome[:80],
        cpu_cores_fisicos=int(cpu_fis),
        cpu_cores_logicos=int(cpu_log),
        memoria_total_gb=float(ram_gb),
        hostname=hostname[:40],
        usuario=usuario[:40],
        pagina_resolucao=resolucao,
        modo_headless=str(modo_hl),
        slow_mo_ms=str(sm),
        cwd=cwd[:140],
    )


# ---------------------------------------------------------------------------
# Helpers de numeração / descrição dos cenários
# ---------------------------------------------------------------------------
def extrair_numeracao_descricao_docstring(arquivo_fonte_path: str) -> Dict[str, Tuple[Optional[str], Optional[str]]]:
    """
    Faz o parse da docstring de cada arquivo de testes (ex:
    tests/test_calculadora_dias_uteis.py), que tem formato padrão:

        Cobertura total: 8 testes
        --------------------------------
         [01] test_validar_pagina_carregada    -> Smoke test: pagina carrega
         [02] test_calcular_xxx                -> CENARIO FELIZ #1
         ...

    Retorna:
       dict:   "test_validar_pagina_carregada"  ->  ("01", "Smoke test: pagina carrega")
    """
    mapa: Dict[str, Tuple[Optional[str], Optional[str]]] = {}
    try:
        if not arquivo_fonte_path or not os.path.isfile(arquivo_fonte_path):
            return mapa
        with open(arquivo_fonte_path, "r", encoding="utf-8", errors="replace") as fh:
            conteudo = fh.read()
    except Exception:
        return mapa

    # 1ª tentativa: extrair docstring do início do arquivo (entre """)
    inicio_doc = conteudo.find('"""')
    if inicio_doc >= 0:
        fim_doc = conteudo.find('"""', inicio_doc + 3)
        if fim_doc > inicio_doc:
            doc = conteudo[inicio_doc + 3: fim_doc]
            for linha in doc.splitlines():
                # Match:   " [01] nome_do_teste   -> descrição"
                try:
                    l = linha.rstrip()
                    m = __import__("re").match(
                        r"\s*\[(\d{2,3})\]\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:[-=:>]{1,3}\s*(.+))?",
                        l,
                    )
                    if m:
                        num = m.group(1)
                        nome = m.group(2)
                        desc = (m.group(3) or "").strip() or None
                        mapa[nome] = (num, desc)
                        continue
                    m2 = __import__("re").match(
                        r"\s*\[(\d{2,3})\]\s*([A-Za-z_][A-Za-z0-9_]*)",
                        l,
                    )
                    if m2:
                        mapa[m2.group(2)] = (m2.group(1), None)
                except Exception:
                    continue
    return mapa


def obter_numero_e_descricao_para_teste(
    item, mapa_cache: Dict[str, Dict[str, Tuple[Optional[str], Optional[str]]]]
) -> Tuple[Optional[str], Optional[str]]:
    """Retorna (numero, descricao) de um item de teste do pytest."""
    try:
        caminho = str(item.path or "") if getattr(item, "path", None) else (item.fspath or "")
        caminho = str(caminho)
    except Exception:
        return None, None
    if not caminho:
        return None, None

    # cache por arquivo (evita ler disco várias vezes)
    if caminho not in mapa_cache:
        mapa_cache[caminho] = extrair_numeracao_descricao_docstring(caminho)
    doc_map = mapa_cache[caminho]

    # Tenta primeiro: nome function exato
    nome_func = (
        getattr(item, "name", None)
        or (item.originalname if hasattr(item, "originalname") else None)
        or (getattr(item.function, "__name__", "") if hasattr(item, "function") else "")
    )
    if nome_func and nome_func in doc_map:
        return doc_map[nome_func]

    # Segunda tentativa: contains
    for k, v in doc_map.items():
        if nome_func and k in nome_func:
            return v
    return None, None


# ---------------------------------------------------------------------------
# Formatação data-hora com milissegundos + hash curto integridade
# ---------------------------------------------------------------------------
def agora_str_milis() -> str:
    """ex: 2026-09-17 15:45:30.741 BR"""
    tz = _dt.timezone(_dt.timedelta(hours=-3), "BR")
    agora = _dt.datetime.now(tz)
    return agora.strftime("%Y-%m-%d %H:%M:%S.") + f"{agora.microsecond // 1000:03d} BR"


def hash_curto_arquivo(png_path: str) -> str:
    """SHA-256 curto (12 chars). Usado para integridade da screenshot."""
    try:
        h = hashlib.sha256()
        with open(png_path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()[:12].upper()
    except Exception:
        return "INTEG."


# ---------------------------------------------------------------------------
# Cores de status (PASS verde / FAIL vermelho / SKIP amarelo / XFAIL azul)
# ---------------------------------------------------------------------------
STATUS_CORES = {
    "PASS":       ((34, 139,  34), (255, 255, 255), "✅ SUCESSO — PASS"),
    "PASSED":     ((34, 139,  34), (255, 255, 255), "✅ SUCESSO — PASS"),
    "FAIL":       ((178, 34,  34), (255, 255, 255), "❌ FALHA — FAIL"),
    "FAILED":     ((178, 34,  34), (255, 255, 255), "❌ FALHA — FAIL"),
    "SKIP":       ((230, 180,  0), (20,  20,  20), "⚠️  PULADO — SKIP"),
    "SKIPPED":    ((230, 180,  0), (20,  20,  20), "⚠️  PULADO — SKIP"),
    "XFAIL":      ((38,  84, 196), (255, 255, 255), "🔷 ESPERADO FALHAR — XFAIL"),
    "XPASS":      ((196,  0, 196), (255, 255, 255), "🔶 PASSOU INESPERADAMENTE — XPASS"),
    "ERROR":      ((150,  0,   0), (255, 255, 255), "🛑 ERRO — EXCEPTION"),
}
STATUS_DEFAULT = ((90, 90, 90), (255, 255, 255), "• DESCONHECIDO")

COR_HEADER_BG   = (0, 48, 100, 245)    # Header azul AGIBANK corporativo (#003064)
COR_RODAPE_BG   = (0, 68, 136, 245)    # Rodapé azul AGIBANK mais claro (#004488)
COR_TEXTO       = (248, 248, 248)
COR_LINHA_HR    = (255, 138, 60, 200)  # Linha separadora: laranja AGIBANK (#ff8a3c)
COR_NUMERO_DOURADO = (255, 152, 60)    # Dourado quente (combina azul agibank) para [01/35]
COR_AGIBANK_LARANJA = (255, 138, 60)   # Laranja oficial da marca
COR_AGIBANK_AZUL    = (0, 48, 100)     # Azul oficial da marca


def _cor_status(status: str):
    return STATUS_CORES.get((status or "").upper(), STATUS_DEFAULT)


def _desenhar_logo_agibank_estilizado(draw, x_canto_direito, y_top, largura_total_logo: int = 320):
    """
    Desenha LOGO estilizado da AGIBANK no canto superior direito, sem PNG externo.
    Formato: 2 retângulos arredondados lado a lado:
      • Bloco ESQUERDO (largura 45%):  Fundo LARANJA, Texto "AGI" branco bold.
      • Bloco DIREITO  (largura 55%):  Fundo AZUL escuro agibank, Texto "BANK" laranja bold.
    Símbolo divisória "|" vertical branca entre os 2 blocos.
    """
    try:
        from PIL import ImageDraw as _ID
    except Exception:
        return
    # Dimensões
    h = int(largura_total_logo * 0.62)
    w = int(largura_total_logo)
    x_left = int(x_canto_direito - w)
    y_bot = int(y_top + h)
    raio = max(6, int(h // 5))

    # Função helper bloco arredondado
    def _retangulo_arredondado(xy, fill, outline=None, radius=raio, width=2):
        try:
            draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)
        except Exception:
            # Versões Pillow antigas não tem rounded_rectangle → fallback retângulo normal
            draw.rectangle(xy, fill=fill, outline=outline)

    # ---- Bloco ESQUERDO: fundo LARANJA, texto AGI branco ----
    x_div = x_left + int(w * 0.44)
    _retangulo_arredondado(
        [x_left, y_top, x_div, y_bot],
        fill=COR_AGIBANK_LARANJA + (255,),
        outline=(255, 255, 255, 230),
        radius=raio,
    )
    # Fonte AGI: ~70% da altura do bloco
    try:
        f_agi = _font(int(h * 0.58), bold=True)
        cx_agi = (x_left + x_div) // 2
        cy_agi = (y_top + y_bot) // 2
        draw.text((cx_agi, cy_agi), "AGI", font=f_agi, fill=(255, 255, 255), anchor="mm")
    except Exception:
        pass

    # ---- Bloco DIREITO: fundo AZUL AGIBANK, texto BANK laranja ----
    _retangulo_arredondado(
        [x_div, y_top, x_canto_direito, y_bot],
        fill=COR_AGIBANK_AZUL + (255,),
        outline=(255, 255, 255, 230),
        radius=raio,
    )
    try:
        f_bank = _font(int(h * 0.58), bold=True)
        cx_bank = (x_div + x_canto_direito) // 2
        cy_bank = (y_top + y_bot) // 2
        draw.text((cx_bank, cy_bank), "BANK", font=f_bank, fill=COR_AGIBANK_LARANJA, anchor="mm")
    except Exception:
        pass

    # Barra vertical divisória branca entre os blocos
    try:
        lw = max(2, h // 28)
        draw.line(
            [(x_div, y_top + int(h * 0.18)), (x_div, y_bot - int(h * 0.18))],
            fill=(255, 255, 255, 240), width=lw,
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Placeholder (para testes sem Playwright — ainda assim, 1 screenshot por teste)
# ---------------------------------------------------------------------------
def _placeholder_img(size: Tuple[int, int] = (1920, 1080)) -> "Image.Image":
    """Gera uma imagem padrão fundo geométrico, sem conteúdo web real."""
    W, H = size
    img = Image.new("RGBA", (W, H), (18, 24, 42, 255))
    if not PILLOW_OK:
        return img
    d = ImageDraw.Draw(img, "RGBA")
    # Padrão diagonal sutil
    for step in range(-H, W + H, 60):
        d.line([(step, 0), (step + H, H)], fill=(40, 52, 80, 255), width=3)
    # Logo do desafio Agibank (texto)
    f_big = _font(110, bold=True)
    f_med = _font(54, bold=True)
    f_small = _font(30)
    cx = W // 2
    try:
        d.text((cx, H // 2 - 130), "Desafio", font=f_big, fill=(120, 150, 220), anchor="mm")
        d.text((cx, H // 2 - 10), "QA Agibank", font=f_med, fill=(220, 200, 130), anchor="mm")
        d.text((cx, H // 2 + 90), "Screenshot de caso de teste (sem página web)",
               font=f_small, fill=(220, 220, 220), anchor="mm")
        d.text((cx, H // 2 + 140), "(teste unitário / auditoria / sem fixture 'page')",
               font=f_small, fill=(170, 170, 170), anchor="mm")
    except Exception:
        pass
    return img


# ---------------------------------------------------------------------------
# DESENHAR OVERLAY (o coração da implementação)
# ---------------------------------------------------------------------------
@dataclass
class OverlayCtx:
    """Todas as infos para desenhar header + rodapé coloridos."""
    status: str                               # PASS / FAIL / SKIP / ERROR
    numero_cenario: Optional[str]             # ex: "03"
    total_cenarios: Optional[int]             # ex: 8
    descricao_cenario: Optional[str]          # ex: "CENARIO FELIZ #1"
    nome_completo_teste: str                  # tests/x.py::Classe::nome
    data_hora_str: str                        # já formatada com ms
    ambiente: AmbienteTesteInfo
    report_path: str                          # caminho report.html
    integridade_prefixo: str = ""             # preenchido depois de salvar o PNG


def desenhar_overlay_no_png(
    png_entrada: str,
    png_saida: str,
    ctx: OverlayCtx,
) -> bool:
    """Abre o screenshot original, desenha HEADER + RODAPÉ, salva em png_saida.
    Retorna True se desenhou overlay com sucesso; False se não tiver PIL.
    Se png_entrada for None/'' desenha placeholder (teste unitário).
    """
    if not PILLOW_OK:
        return False

    # 1) Carregar base (screenshot real ou placeholder)
    try:
        if png_entrada and os.path.isfile(png_entrada):
            base = Image.open(png_entrada).convert("RGBA")
        else:
            base = _placeholder_img()
    except Exception:
        try:
            base = _placeholder_img()
        except Exception:
            return False

    W, H = base.size
    # Garantir tamanho mínimo
    W = max(W, 1280)
    H = max(H, 720)
    if base.size != (W, H):
        base = base.resize((W, H), Image.LANCZOS)

    draw = ImageDraw.Draw(base, "RGBA")
    # -----------------------------------------------------------------------
    # FAIXA SUPERIOR: STATUS colorida
    # -----------------------------------------------------------------------
    cor_status_bg, cor_status_fg, status_texto = _cor_status(ctx.status)
    # FAIXA COLORIDA 50px de altura no topo
    h_status = max(44, W // 55)
    draw.rectangle([(0, 0), (W, h_status)], fill=cor_status_bg + (255,))

    # Texto status (lado ESQUERDO)
    f_status = _font(h_status - 12, bold=True)
    try:
        draw.text((W // 2, h_status // 2), status_texto,
                  font=f_status, fill=cor_status_fg, anchor="mm")
    except Exception:
        pass

    # Data/hora no canto DIREITO da faixa de status
    f_dt = _font(h_status - 24, bold=False)
    try:
        draw.text((W - 20, h_status // 2), f"⏱  {ctx.data_hora_str}",
                  font=f_dt, fill=cor_status_fg, anchor="rm")
    except Exception:
        pass

    # ID integra (canto ESQUERDO)
    try:
        draw.text((20, h_status // 2), f"🔗 {ctx.integridade_prefixo}",
                  font=f_dt, fill=cor_status_fg, anchor="lm")
    except Exception:
        pass

    # -----------------------------------------------------------------------
    # HEADER PRINCIPAL: numeração + nome teste + descrição + LOGO AGIBANK
    # -----------------------------------------------------------------------
    h_header = max(160, W // 19)
    y0 = h_status
    y1 = h_status + h_header
    draw.rectangle([(0, y0), (W, y1)], fill=COR_HEADER_BG)
    # linha separadora superior do header
    draw.line([(0, y0), (W, y0)], fill=COR_LINHA_HR, width=3)
    draw.line([(0, y1), (W, y1)], fill=COR_LINHA_HR, width=3)

    # --- LOGO AGIBANK (canto SUPERIOR DIREITO do header, 320px largura) ---
    logo_largura = min(360, max(240, W // 6))
    _desenhar_logo_agibank_estilizado(
        draw, x_canto_direito=W - 30, y_top=y0 + int((h_header - logo_largura * 0.62) / 2),
        largura_total_logo=logo_largura,
    )
    # Posição X máxima para o texto do nome do teste (não sobrepor o logo)
    texto_teste_max_x = W - (logo_largura + 60)

    # --- LADO ESQUERDO HEADER: Numeração [03 / 08] + descrição
    if ctx.numero_cenario and ctx.total_cenarios:
        num_txt = f"[{int(ctx.numero_cenario):02d}/{int(ctx.total_cenarios):02d}]"
    elif ctx.numero_cenario:
        num_txt = f"[{int(ctx.numero_cenario):02d}]"
    else:
        num_txt = "[--]"
    f_num = _font(W // 40, bold=True)
    try:
        draw.text((30, y0 + 24), num_txt, font=f_num, fill=COR_NUMERO_DOURADO)
    except Exception:
        pass
    # Descrição (abaixo da numeração)
    f_desc = _font(W // 72)
    try:
        desc = (ctx.descricao_cenario or "(sem descrição no docstring da suite)").strip()
        desc = textwrap.shorten(desc, width=88, placeholder="...")
        draw.text((30, y0 + 24 + (W // 40) + 22), desc, font=f_desc, fill=COR_TEXTO)
    except Exception:
        pass

    # --- LADO DIREITO HEADER (ABAIXO do LOGO): Nome completo do teste
    f_nome_teste = _font(W // 78, bold=True)
    try:
        nome = ctx.nome_completo_teste
        if len(nome) > 62:
            sep = nome.rfind("::")
            if sep > 0:
                linha1 = nome[:sep]
                linha2 = nome[sep:]
            else:
                linha1 = nome[: len(nome) // 2]
                linha2 = nome[len(nome) // 2:]
            draw.text((texto_teste_max_x, y0 + 26), linha1,
                      font=f_nome_teste, fill=(232, 241, 255), anchor="rt")
            f_nome_teste2 = _font(W // 82, bold=True)
            draw.text((texto_teste_max_x, y0 + 26 + (W // 78) + 12), linha2,
                      font=f_nome_teste2, fill=(210, 228, 255), anchor="rt")
        else:
            draw.text((texto_teste_max_x, y0 + 56), nome,
                      font=f_nome_teste, fill=(232, 241, 255), anchor="rt")
    except Exception:
        pass

    # -----------------------------------------------------------------------
    # RODAPÉ: 6 linhas de resumo ambiente + hash integridade + report path
    # -----------------------------------------------------------------------
    h_footer = max(170, W // 20)
    y0f = H - h_footer
    y1f = H
    draw.rectangle([(0, y0f), (W, y1f)], fill=COR_RODAPE_BG)
    draw.line([(0, y0f), (W, y0f)], fill=COR_LINHA_HR, width=2)

    f_footer = _font(max(13, W // 170))
    linhas = ctx.ambiente.resumo_curto()
    # última linha = integridade + report
    try:
        report = (ctx.report_path or "") or "(sem report)"
        report = textwrap.shorten(
            f"📄 Report: {report}  |  🔒 Integridade: {ctx.integridade_prefixo}",
            width=130, placeholder="...",
        )
    except Exception:
        report = ""

    all_lines_footer = linhas + ([report] if report else [])
    y = y0f + 14
    for ln in all_lines_footer:
        try:
            draw.text((20, y), f"  {ln}", font=f_footer, fill=(235, 225, 200))
            y += (f_footer.size if hasattr(f_footer, "size") else 18) + 4
        except Exception:
            break

    # Salvar
    Path(png_saida).parent.mkdir(parents=True, exist_ok=True)
    try:
        # Convert RGB final (sem alpha) para reduzir tamanho
        base.convert("RGB").save(png_saida, format="PNG", optimize=True)
    except Exception:
        try:
            base.save(png_saida, format="PNG")
        except Exception:
            return False
    return True


# ---------------------------------------------------------------------------
# Salvar screenshot bruta do Playwright (com fallback placeholder) + overlay
# ---------------------------------------------------------------------------
def salvar_screenshot_teste_automatica(
    page: Any,
    output_png: str,
    ctx: OverlayCtx,
    full_page: bool = True,
) -> str:
    """
    Tenta tirar screenshot da page; se não tiver page ou erro, usa placeholder.
    Sempre desenha overlay. Retorna caminho do PNG final.
    """
    Path(output_png).parent.mkdir(parents=True, exist_ok=True)
    raw_tmp = str(Path(output_png).with_suffix(".RAW.png"))

    # (1) screenshot raw (se possível)
    ok_raw = False
    if page is not None:
        try:
            page.screenshot(path=raw_tmp, full_page=full_page, timeout=20000)
            if os.path.isfile(raw_tmp) and os.path.getsize(raw_tmp) > 0:
                ok_raw = True
        except Exception:
            ok_raw = False
    if not ok_raw:
        try:
            ph = _placeholder_img()
            Path(raw_tmp).parent.mkdir(parents=True, exist_ok=True)
            ph.save(raw_tmp, format="PNG")
            ok_raw = True
        except Exception:
            ok_raw = False

    entrada = raw_tmp if ok_raw else ""
    # Desenhar overlay (1ª passagem — integridade virá depois se necessário)
    desenhar_overlay_no_png(entrada, output_png, ctx)
    # Atualiza integridade (hash do arquivo gravado)
    integridade = hash_curto_arquivo(output_png)
    ctx.integridade_prefixo = integridade
    # Reescreve o overlay com o hash correto já no lugar
    desenhar_overlay_no_png(entrada, output_png, ctx)
    # Remove temporário
    try:
        if os.path.isfile(raw_tmp) and os.path.abspath(raw_tmp) != os.path.abspath(output_png):
            os.remove(raw_tmp)
    except Exception:
        pass
    return output_png
