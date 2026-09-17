# -*- coding: utf-8 -*-
"""
reports/auditoria/auditoria_retencao_lgpd.py
============================================

Gerencia a POLÍTICA DE RETENÇÃO dos logs de auditoria (padrão LGPD: 90 dias).

Como rodar:
  python reports\\auditoria\\auditoria_retencao_lgpd.py --dry-run  # simula (DEFAULT)
  python reports\\auditoria\\auditoria_retencao_lgpd.py --dias 90
  python reports\\auditoria\\auditoria_retencao_lgpd.py --aplicar --dias 180

Flag dry-run (padrão) NÃO apaga nada, só informa quantos eventos seriam apagados.
"""
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

_PROJ = Path(__file__).resolve().parents[2]
if str(_PROJ) not in sys.path:
    sys.path.insert(0, str(_PROJ))

from reports.auditoria import obter_logger_auditoria  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Gerencia retenção de logs auditoria (padrão LGPD 90 dias)."
    )
    parser.add_argument("--dias", type=int, default=90,
                        help="Quantos dias logs ficam retidos antes de purgar. Default 90.")
    parser.add_argument("--aplicar", action="store_true",
                        help="SEM ESTA FLAG, RODA EM MODO SIMULAÇÃO (não apaga).")
    args = parser.parse_args()

    logger = obter_logger_auditoria()
    dao = logger.obter_dao()
    dry = not args.aplicar

    agora = datetime.now(tz=timezone.utc).isoformat()
    print(f"=== Auditoria Retenção (LGPD) ===")
    print(f"  Executado em     : {agora}")
    print(f"  Período retenção : {args.dias} dias")
    print(f"  Modo             : {'SIMULAÇÃO (dry-run)' if dry else 'APLICAR PURGE (excluir eventos antigos)'}")
    print(f"  Total eventos ANTES: {logger.total_eventos()}")
    print()
    del_sql, del_jsonl = dao.aplicar_retencao_lgpd(
        dias_retencao=args.dias, dry_run=dry
    )
    print(f"  Quantidade que seria EXCLUÍDA (SQLite) : {del_sql}")
    print(f"  Quantidade que seria EXCLUÍDA (JSONL)  : {del_jsonl}")
    print()
    if dry:
        print("> MODO SIMULAÇÃO: nenhum dado foi apagado.")
        print("> Para EXECUTAR purge real, rode novamente com flag --aplicar.")
    else:
        print(f"> Purge CONCLUÍDO. Total eventos AGORA: {logger.total_eventos()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
