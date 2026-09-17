# -*- coding: utf-8 -*-
"""
reports/auditoria/auditoria_consultar.py
========================================

CLI (Interface Linha de Comando) para CONSULTAR o sistema de auditoria.

Uso:
  python reports\\auditoria\\auditoria_consultar.py --ultimos-dias 7
  python reports\\auditoria\\auditoria_consultar.py --acao PROCESSAMENTO_ERRO --limit 50
  python reports\\auditoria\\auditoria_consultar.py --usuario "fabri" --limit 20
  python reports\\auditoria\\auditoria_consultar.py --validar-cadeia
  python reports\\auditoria\\auditoria_consultar.py --resumo --ultimos-dias 30

Flags (todas opcionais):
  --ultimos-dias N      | filtra registros dos ultimos N dias (default 7)
  --acao ACAO_ENUM      | filtra por acao: RELATORIO_ACESSO / DADOS_MODIFICACAO /
                        |                RELATORIO_EXPORTACAO / PROCESSAMENTO_ERRO /
                        |                TENTATIVA_ACESSO_NAO_AUTORIZADO
  --status SUCESSO|FALHA
  --usuario TEXTO       | busca (em memoria, descriptografado) por user_id_raw
  --limit N             | max registros p/ exibir
  --resumo              | mostra estatisticas compactas (sucessos / falhas por ação)
  --top-erros           | lista top 10 ações com mais erros últimos 30 dias
  --validar-cadeia      | executa validacao INTEGRIDADE cadeia de custódia hash
  --json                | output em JSON (em vez de tabela bonita)
  --verbose             | mostra user_id e ip DESCRIPTOGRAFADOS (requer chave Fernet OK)
"""
import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

_PROJ = Path(__file__).resolve().parents[2]
if str(_PROJ) not in sys.path:
    sys.path.insert(0, str(_PROJ))

from reports.auditoria import (  # noqa: E402
    obter_logger_auditoria, AcaoAuditoria, StatusAuditoria,
)


def _print_tabela(linhas: list, headers: list) -> None:
    if not linhas:
        print("(sem registros no período / filtro selecionado)")
        return
    widths = [len(h) for h in headers]
    for linha in linhas:
        for i, c in enumerate(linha):
            widths[i] = max(widths[i], len(str(c)))
    sep = "+-" + "-+-".join(["-" * w for w in widths]) + "-+"
    print(sep)
    print("| " + " | ".join(f"{h:<{widths[i]}}" for i, h in enumerate(headers)) + " |")
    print(sep)
    for l in linhas:
        print("| " + " | ".join(f"{str(c):<{widths[i]}}" for i, c in enumerate(l)) + " |")
    print(sep)
    print(f"> Total de registros exibidos: {len(linhas)}")


def main():
    parser = argparse.ArgumentParser(description="Auditoria de relatórios desafioagibank")
    parser.add_argument("--ultimos-dias", type=int, default=7)
    parser.add_argument("--acao", type=str, default=None)
    parser.add_argument("--status", type=str, default=None)
    parser.add_argument("--usuario", type=str, default=None)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--resumo", action="store_true")
    parser.add_argument("--top-erros", action="store_true")
    parser.add_argument("--validar-cadeia", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logger = obter_logger_auditoria()
    dao = logger.obter_dao()

    # Validar cadeia primeiro (se --validar-cadeia)
    if args.validar_cadeia:
        ok, qtd, msg = dao.validar_cadeia_custodia()
        print(f"> VALIDADE CADEIA CUSTÓDIA: {'✅ íntegra' if ok else '❌ QUEBRADA'} "
              f"(registros analisados: {qtd})")
        print(f"  Detalhe: {msg}")
        if not ok:
            return 1
        print()

    # Resumo
    if args.resumo:
        res = dao.estatisticas_resumo(ultimos_dias=args.ultimos_dias)
        print(f"=== Estatísticas últimos {res['periodo_dias']} dias ===")
        print(f"  Total de eventos auditados: {res['total_eventos']}")
        print(f"  SUCESSOS: {res['sucessos']}  |  FALHAS: {res['falhas']}")
        print()
        print("Eventos POR AÇÃO (mais comuns primeiro):")
        for a in res["eventos_por_acao"]:
            print(f"   - {a['acao']:<38s} {a['qtd']:>6d} eventos")
        return 0

    if args.top_erros:
        tops = dao.top_erros(ultimos_dias=args.ultimos_dias, limit=args.limit)
        _print_tabela(
            [[t["acao"], t["qtd"], t.get("ultimo_erro", "")] for t in tops],
            ["ACAO", "QTD_ERROS", "ULTIMO_ERRO"]
        )
        return 0

    # Busca por usuario (em memoria, descriptogr.)
    if args.usuario:
        regs = dao.por_usuario_raw(args.usuario, limit=args.limit)
    elif args.acao:
        try:
            acao_enum = AcaoAuditoria(args.acao.upper())
        except Exception:
            print(f"ERRO: --acao invalida. Valores aceitos: {[e.value for e in AcaoAuditoria]}")
            return 2
        regs = dao.por_acao(acao_enum, limit=args.limit)
    elif args.status:
        try:
            st_enum = StatusAuditoria(args.status.upper())
        except Exception:
            print("ERRO: --status invalido. Use SUCESSO ou FALHA.")
            return 2
        regs = dao.por_status(st_enum, limit=args.limit)
    else:
        fim = datetime.now(tz=timezone.utc)
        inicio = fim - timedelta(days=args.ultimos_dias)
        regs = dao.por_periodo(inicio=inicio, fim=fim, limit=args.limit)

    if args.json:
        print(json.dumps(regs, ensure_ascii=False, indent=2, default=str))
        return 0

    headers = ["#", "TIMESTAMP", "ACAO", "STATUS", "EVENT_ID", "USER", "IP"]
    linhas = []
    for i, ev in enumerate(regs, 1):
        u = (
            logger.descriptografar_user(str(ev.get("user_id_enc") or ""))
            if args.verbose else (str(ev.get("user_id_enc") or "")[:24] + "...")
        )
        ip = (
            logger.descriptografar_ip(str(ev.get("ip_origem_enc") or ""))
            if args.verbose else (str(ev.get("ip_origem_enc") or "")[:18] + "...")
        )
        linhas.append([
            i,
            str(ev.get("timestamp_ms") or "")[:24],
            str(ev.get("acao") or "")[:34],
            str(ev.get("status") or ""),
            str(ev.get("event_id") or "")[:14],
            str(u or "")[:26],
            str(ip or "")[:18],
        ])
    _print_tabela(linhas, headers)
    if not args.verbose:
        print("")
        print("Dica: use --verbose p/ exibir user_id e IP DESCRIPTOGRAFADOS (não só hash/cifra).")
        print("Dica 2: use --json para exportar para Excel.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
