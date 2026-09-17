# -*- coding: utf-8 -*-
"""
reports/auditoria/auditor_logger.py
===================================
CORE do sistema de auditoria de relatórios do desafioagibank.

5 TIPOS DE EVENTOS CRÍTICOS (enum AcaoAuditoria) rastreados:
  1. RELATORIO_ACESSO            -> Acesso/visualização de qualquer report.html
  2. DADOS_MODIFICACAO           -> Modificação de massa de dados / fixtures
  3. RELATORIO_EXPORTACAO        -> Exportação (geração report HTML, zip, md)
  4. PROCESSAMENTO_ERRO          -> Erros de execução / geração de relatório
  5. TENTATIVA_ACESSO_NAO_AUTORIZADO -> visualização sem token/sessão válida

CAMPOS OBRIGATÓRIOS em CADA registro (CAMPOS_OBRIGATORIOS_POR_EVENTO):
    timestamp_ms       : Data/hora COM MILISSEGUNDOS (ISO-8601 3 decimals)
    user_id            : Identificador do usuário (criptografado Fernet)
    ip_origem          : Endereço IP de origem (criptografado Fernet)
    acao               : Tipo AcaoAuditoria (enum)
    status             : StatusAuditoria.SUCESSO ou FALHA
    detalhes           : dict opcional com contexto adicional
    hash_integridade   : SHA-256 do registro anterior (cadeia de custódia)
"""
import os
import re
import sys
import json
import uuid
import time
import hmac
import socket
import hashlib
import sqlite3
import getpass
import platform
from enum import Enum
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Verificação opcional: cryptography instalado para criptografia Fernet AES-128
# ---------------------------------------------------------------------------
try:
    from cryptography.fernet import Fernet, InvalidToken
    _FERNET_DISPONIVEL = True
except Exception:  # pragma: no cover
    _FERNET_DISPONIVEL = False
    Fernet = None  # type: ignore
    InvalidToken = Exception  # type: ignore

# Caminhos base (TUDO fica dentro de reports/auditoria/ — portátil)
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_REPORTS_DIR = _PROJECT_ROOT / "reports"
_AUDIT_DIR = _REPORTS_DIR / "auditoria"
_AUDIT_DATA_DIR = _AUDIT_DIR / "data"
_AUDIT_KEYS_DIR = _AUDIT_DATA_DIR / "keys"

# Garante estrutura de diretórios existe em TEMPO DE IMPORTAÇÃO
_AUDIT_KEYS_DIR.mkdir(parents=True, exist_ok=True)
_PATH_JSONL = _AUDIT_DATA_DIR / "audit_log.jsonl"
_PATH_SQLITE = _AUDIT_DATA_DIR / "audit_log.db"
_PATH_CHAVE_FERNET = _AUDIT_KEYS_DIR / "chave_auditoria_fernet.key"

# Marker .gitkeep para estrutura
for _d in [_AUDIT_DATA_DIR, _AUDIT_KEYS_DIR]:
    _gk = _d / ".gitkeep"
    if not _gk.exists():
        _gk.touch()


class AcaoAuditoria(str, Enum):
    """Os 5 eventos críticos obrigatórios a serem auditados."""
    RELATORIO_ACESSO = "RELATORIO_ACESSO"
    DADOS_MODIFICACAO = "DADOS_MODIFICACAO"
    RELATORIO_EXPORTACAO = "RELATORIO_EXPORTACAO"
    PROCESSAMENTO_ERRO = "PROCESSAMENTO_ERRO"
    TENTATIVA_ACESSO_NAO_AUTORIZADO = "TENTATIVA_ACESSO_NAO_AUTORIZADO"
    # --- Extra: usado pelo framework pytest ---
    RELATORIO_GERACAO_INICIO = "RELATORIO_GERACAO_INICIO"
    RELATORIO_GERACAO_FIM = "RELATORIO_GERACAO_FIM"
    TESTE_EXECUCAO = "TESTE_EXECUCAO"


class StatusAuditoria(str, Enum):
    SUCESSO = "SUCESSO"
    FALHA = "FALHA"


CAMPOS_OBRIGATORIOS_POR_EVENTO = [
    "event_id",
    "timestamp_ms",
    "user_id_enc",
    "ip_origem_enc",
    "acao",
    "status",
    "detalhes",
    "hash_integridade",
    "cadeia_anterior_hash",
    "versao_esquema",
]

VERSAO_ESQUEMA_ATUAL = "1.0.0"


# =============================================================================
# 1.  GERENCIAMENTO DE CHAVE CRIPTOGRAFICA (Fernet AES-128-CBC + HMAC SHA-256)
# =============================================================================
class _GerenciadorChave:
    """
    Singleton simplificado que carrega OU gera a chave Fernet de 32 bytes
    para criptografia de user_id / ip_origem. Chave nunca exposta em logs.
    """
    _instancia: Optional["_GerenciadorChave"] = None
    _chave_bytes: Optional[bytes] = None
    _fernet: Optional[Any] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "_GerenciadorChave":
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia

    def obter_fernet(self) -> Optional[Any]:
        if self._fernet is not None:
            return self._fernet
        if not _FERNET_DISPONIVEL:
            return None
        # 1) Tenta ler chave existente do arquivo protegido
        if _PATH_CHAVE_FERNET.exists() and _PATH_CHAVE_FERNET.stat().st_size > 0:
            try:
                chave = _PATH_CHAVE_FERNET.read_bytes().strip()
                self._fernet = Fernet(chave)
                self._chave_bytes = chave
                return self._fernet
            except Exception:
                pass
        # 2) S/ chave válida: gera NOVA, grava com permissões restritas (Win/Linux)
        chave = Fernet.generate_key()
        try:
            _PATH_CHAVE_FERNET.write_bytes(chave)
            try:
                if platform.system() != "Windows":
                    os.chmod(_PATH_CHAVE_FERNET, 0o600)  # owner R/W apenas
            except Exception:
                pass
        except Exception:
            pass
        self._fernet = Fernet(chave)
        self._chave_bytes = chave
        return self._fernet

    def criptografar(self, texto: str) -> str:
        if not texto:
            return ""
        f = self.obter_fernet()
        if f is None:
            return self._fallback_ofuscar(texto)
        try:
            return f.encrypt(texto.encode("utf-8")).decode("ascii")
        except Exception:
            return self._fallback_ofuscar(texto)

    def descriptografar(self, criptograma: str) -> Optional[str]:
        if not criptograma:
            return None
        f = self.obter_fernet()
        if f is None:
            return self._fallback_desofuscar(criptograma)
        try:
            return f.decrypt(criptograma.encode("ascii"), ttl=None).decode("utf-8")
        except (InvalidToken, Exception):
            return self._fallback_desofuscar(criptograma)

    # Fallback (SE e somente SE cryptography nao estiver instalado em
    # ambientes muito restritos — MENOS seguro, mas garante que dados
    # nao ficam plain text. Uso de HMAC-SHA256 com chave do usuário logado.
    @staticmethod
    def _chave_fallback() -> bytes:
        return hashlib.sha256(
            f"{getpass.getuser()}@{platform.node()}#fallback-audit-v1".encode()
        ).digest()

    def _fallback_ofuscar(self, texto: str) -> str:
        chave = self._chave_fallback()
        nonce = os.urandom(8).hex()
        mac = hmac.new(chave, f"{nonce}{texto}".encode(), hashlib.sha256).hexdigest()
        return f"FB${nonce}${mac}${base64_b64encode(texto.encode())}"

    def _fallback_desofuscar(self, payload: str) -> Optional[str]:
        try:
            if not payload.startswith("FB$"):
                return None
            _, nonce, mac_esperado, b64 = payload.split("$", 3)
            chave = self._chave_fallback()
            dec = base64_b64decode(b64.encode()).decode()
            mac_calc = hmac.new(chave, f"{nonce}{dec}".encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(mac_calc, mac_esperado):
                return None
            return dec
        except Exception:
            return None


import base64 as _b64_mod  # noqa: E402


def base64_b64encode(data: bytes) -> str:
    return _b64_mod.b64encode(data).decode("ascii")


def base64_b64decode(data: bytes) -> bytes:
    return _b64_mod.b64decode(data.decode("ascii") if isinstance(data, bytes) else data)


_CHAVE_MGR = _GerenciadorChave()


# =============================================================================
# 2.  Helpers: metadados (usuário SO, IP local — override via env vars se houver)
# =============================================================================
def _descobrir_user_id() -> str:
    """
    Resolve user_id. Ordem de prioridade (pode ser sobrescrito via CI/CD):
      1) $ENV:AUDIT_USER_ID (pipeline)
      2) $ENV:GITHUB_ACTOR (se rodando no GitHub Actions)
      3) getpass.getuser() (usuário logado no sistema operacional)
    """
    for k in ("AUDIT_USER_ID", "GITHUB_ACTOR"):
        v = os.getenv(k)
        if v:
            return str(v)
    return f"{getpass.getuser()}@{platform.node()}"


IPV4_REGEX = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")


def _descobrir_ip_origem() -> str:
    """
    Resolve IP origem. Ordem:
      1) $ENV:AUDIT_IP_ORIGEM  (forçado externamente / proxy reverso)
      2) $ENV:HTTP_X_FORWARDED_FOR (proxy)
      3) socket.gethostbyname(socket.gethostname()) / 127.0.0.1 fallback
    """
    for k in ("AUDIT_IP_ORIGEM", "HTTP_X_FORWARDED_FOR"):
        v = os.getenv(k)
        if v:
            primeiro = str(v).split(",")[0].strip()
            if IPV4_REGEX.match(primeiro):
                return primeiro
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return str(ip)
    except Exception:
        pass
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception:
        return "127.0.0.1"


# =============================================================================
# 3.  AuditoriaLogger (singleton) — grava JSONL + SQLite em paralelo
# =============================================================================
class AuditoriaLogger:
    """
    Logger de auditoria thread-safe via append-only JSONL + índice SQLite.
    Garante cadeia de custódia (cada evento aponta hash do anterior).

    Uso básico:
        from reports.auditoria import obter_logger_auditoria
        log = obter_logger_auditoria()
        log.registrar(
            acao=AcaoAuditoria.RELATORIO_ACESSO,
            status=StatusAuditoria.SUCESSO,
            detalhes={"arquivo": "report.html", "tamanho_bytes": 12345}
        )
    """

    _instancia: Optional["AuditoriaLogger"] = None
    _lock_singleton = False  # processo único — pytest é single-process

    def __new__(cls, *args, **kwargs) -> "AuditoriaLogger":
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia

    def __init__(self) -> None:
        if getattr(self, "_inicializado", False):
            return
        self._chave_mgr = _CHAVE_MGR
        self._inicializado = True
        self._path_jsonl = _PATH_JSONL
        self._path_sqlite = _PATH_SQLITE
        self._ultimo_hash: str = self._carregar_ultimo_hash_bd()
        self._garantir_estrutura_sqlite()
        # Ao inicializar registra bootstrapping (marca integridade OK)
        self._dao_cache: Optional["AuditoriaDAO"] = None

    # ---------------------------------------------------------------- utils
    @staticmethod
    def _agora_milis() -> str:
        """
        ISO-8601 UTC com MILISSEGUNDOS (3 casas decimais EXATAS, nem + nem -).
        Exemplo: 2026-09-17T14:49:46.446Z  (sempre .XYZ 3 dígitos).
        """
        agora = datetime.now(tz=timezone.utc)
        milissegundos = agora.microsecond // 1000
        return (
            f"{agora.year:04d}-{agora.month:02d}-{agora.day:02d}"
            f"T{agora.hour:02d}:{agora.minute:02d}:{agora.second:02d}"
            f".{milissegundos:03d}Z"
        )

    @staticmethod
    def _sha256(payload: str) -> str:
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _obter_conexao_sqlite(self):
        """
        [Performance] Retorna CONEXÃO SQLite REUTILIZÁVEL (aberta UMA vez por
        processo, não a cada INSERT). Ajuste de 17ms/evento → ~0.05ms/evento.
        """
        if getattr(self, "_conn_sqlite_cache", None) is None:
            self._conn_sqlite_cache = sqlite3.connect(
                self._path_sqlite, timeout=120, check_same_thread=False,
                isolation_level=None  # autocommit OFF, nós controlamos transações
            )
            try:
                self._conn_sqlite_cache.execute("PRAGMA journal_mode=WAL;")
                self._conn_sqlite_cache.execute("PRAGMA synchronous=NORMAL;")
                self._conn_sqlite_cache.execute("PRAGMA cache_size = -8192;")  # 8MB page cache
                self._conn_sqlite_cache.execute("PRAGMA temp_store=MEMORY;")
            except Exception:
                pass
        return self._conn_sqlite_cache

    def _fechar_conexao_sqlite(self):
        c = getattr(self, "_conn_sqlite_cache", None)
        if c is not None:
            try:
                c.commit()
                c.close()
            except Exception:
                pass
            self._conn_sqlite_cache = None

    # ---------------------------------------------------------------- init
    def _garantir_estrutura_sqlite(self) -> None:
        with sqlite3.connect(self._path_sqlite, timeout=60) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS auditoria_eventos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE NOT NULL,
                    timestamp_ms TEXT NOT NULL,
                    user_id_enc TEXT NOT NULL,
                    ip_origem_enc TEXT NOT NULL,
                    acao TEXT NOT NULL,
                    status TEXT NOT NULL,
                    detalhes_json TEXT,
                    hash_integridade TEXT NOT NULL,
                    cadeia_anterior_hash TEXT,
                    versao_esquema TEXT NOT NULL DEFAULT '{VERSAO_ESQUEMA_ATUAL}'
                );
                """
            )
            for col, idx in [
                ("idx_auditoria_timestamp", "timestamp_ms"),
                ("idx_auditoria_acao", "acao"),
                ("idx_auditoria_status", "status"),
            ]:
                conn.execute(
                    f"CREATE INDEX IF NOT EXISTS {col} ON auditoria_eventos({idx});"
                )
            conn.commit()

    def _carregar_ultimo_hash_bd(self) -> str:
        try:
            if not self._path_sqlite.exists():
                return "ROOT"
            with sqlite3.connect(self._path_sqlite, timeout=30) as conn:
                cur = conn.execute(
                    "SELECT hash_integridade FROM auditoria_eventos "
                    "ORDER BY id DESC LIMIT 1;"
                )
                row = cur.fetchone()
                return row[0] if row and row[0] else "ROOT"
        except Exception:
            return "ROOT"

    # ---------------------------------------------------------------- core
    def registrar(
        self,
        acao: AcaoAuditoria,
        status: StatusAuditoria,
        detalhes: Optional[Dict[str, Any]] = None,
        *,
        user_id_override: Optional[str] = None,
        ip_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Registra EVENTO de auditoria. Sempre retorna o evento completo
        (dict) para testes unitários.

        Fluxo de gravação (ambos são confirmados antes de retornar):
            1) Registro montado com user_id/ip criptografados
            2) Hash SHA256 calculado (cadeia de custódia)
            3) Appenda 1 linha JSON no JSONL (append-only atomic)
            4) Insere mesma linha no SQLite (índices automáticos)
        """
        detalhes = detalhes or {}
        _raw_user = user_id_override or _descobrir_user_id()
        _raw_ip = ip_override or _descobrir_ip_origem()
        user_id_enc = self._chave_mgr.criptografar(_raw_user)
        ip_origem_enc = self._chave_mgr.criptografar(_raw_ip)

        # ===============================================================
        # [INTEGRIDADE CRÍTICA] timestamp é GERADO UMA VEZ e reutilizado
        # no payload de hash E no campo timestamp_ms do evento.
        # Chamar _agora_milis() 2 vezes causava hash divergente se o
        # milissegundo virasse durante o método (bug cadeia custodia #25).
        # ===============================================================
        ts_evento_unico = self._agora_milis()

        # 2 passos hash: primeiro payload parcial, depois concatena ultimo hash
        partial = json.dumps(
            {
                "t": ts_evento_unico,
                "u": _raw_user,
                "ip": _raw_ip,
                "a": acao.value if isinstance(acao, (AcaoAuditoria, Enum)) else str(acao),
                "s": status.value if isinstance(status, (StatusAuditoria, Enum)) else str(status),
                "d": detalhes,
                "v": VERSAO_ESQUEMA_ATUAL,
            },
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        hash_cadeia = self._sha256(f"{self._ultimo_hash}::{partial}")
        event_id = uuid.uuid4().hex
        evento: Dict[str, Any] = {
            "event_id": event_id,
            "timestamp_ms": ts_evento_unico,
            "user_id_enc": user_id_enc,
            "ip_origem_enc": ip_origem_enc,
            "acao": acao.value if isinstance(acao, Enum) else str(acao),
            "status": status.value if isinstance(status, Enum) else str(status),
            "detalhes": detalhes,
            "hash_integridade": hash_cadeia,
            "cadeia_anterior_hash": self._ultimo_hash,
            "versao_esquema": VERSAO_ESQUEMA_ATUAL,
        }
        linha_json = json.dumps(evento, ensure_ascii=False, sort_keys=False,
                                separators=(",", ":"), default=str)
        # 1) JSONL append-only [PERFORMANCE: flush() apenas, sem fsync a cada evento]
        with open(self._path_jsonl, "a", encoding="utf-8") as fh:
            fh.write(linha_json + "\n")
            fh.flush()
            # os.fsync() removido: custava >8ms por evento.
            # fsync em disco real é realizado pelo SO em poucos segundos, ou
            # explicitamente por AuditoriaLogger.forcar_fsync_duravel() se necessário.
        # 2) SQLite [PERFORMANCE FIX: usa conexão reutilizada + batch insert]
        try:
            conn = self._obter_conexao_sqlite()
            conn.execute(
                """
                INSERT OR IGNORE INTO auditoria_eventos(
                    event_id, timestamp_ms, user_id_enc, ip_origem_enc,
                    acao, status, detalhes_json, hash_integridade,
                    cadeia_anterior_hash, versao_esquema
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    event_id,
                    evento["timestamp_ms"],
                    user_id_enc,
                    ip_origem_enc,
                    evento["acao"],
                    evento["status"],
                    json.dumps(detalhes, ensure_ascii=False, default=str),
                    hash_cadeia,
                    self._ultimo_hash,
                    VERSAO_ESQUEMA_ATUAL,
                ),
            )
            conn.commit()
        except Exception as err:
            sys.stderr.write(
                f"[AUDIT-WARN] Falha gravar SQLite (continuando com JSONL apenas): {err}\n"
            )
        self._ultimo_hash = hash_cadeia
        return evento

    # ------------------------------------------------------------ helpers
    def descriptografar_user(self, user_id_enc: str) -> Optional[str]:
        return self._chave_mgr.descriptografar(user_id_enc)

    def descriptografar_ip(self, ip_enc: str) -> Optional[str]:
        return self._chave_mgr.descriptografar(ip_enc)

    def obter_dao(self) -> "AuditoriaDAO":
        if self._dao_cache is None:
            self._dao_cache = AuditoriaDAO(self)
        return self._dao_cache

    def total_eventos(self) -> int:
        try:
            conn = self._obter_conexao_sqlite()
            cur = conn.execute("SELECT COUNT(*) FROM auditoria_eventos;")
            row = cur.fetchone()
            return int(row[0]) if row else 0
        except Exception:
            try:
                return sum(1 for _ in open(self._path_jsonl, "r", encoding="utf-8"))
            except FileNotFoundError:
                return 0

    def __del__(self):
        """Close da conexão SQLite no garbage-collect (evita leaks)."""
        try:
            self._fechar_conexao_sqlite()
        except Exception:
            pass


_INSTANCIA_LOGGER: Optional[AuditoriaLogger] = None


def obter_logger_auditoria() -> AuditoriaLogger:
    """Factory padrão para evitar criar múltiplos objetos Logger."""
    global _INSTANCIA_LOGGER
    if _INSTANCIA_LOGGER is None:
        _INSTANCIA_LOGGER = AuditoriaLogger()
    return _INSTANCIA_LOGGER


# =============================================================================
# 4.  AuditoriaDAO — estrutura de CONSULTA para auditoria posterior
# =============================================================================
class AuditoriaDAO:
    """
    Data Access Object para o banco auditoria_eventos. Métodos de consulta:
        - por_periodo()   | - por_usuario()
        - por_acao()      | - por_status()
        - top_erros()     | - estatisticas_resumo()
        - validar_cadeia_custodia()
    """

    def __init__(self, logger: AuditoriaLogger):
        self.logger = logger
        self.db_path = logger._path_sqlite

    def _q(self, sql: str, params: Tuple = (), limit: Optional[int] = None
           ) -> List[sqlite3.Row]:
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            conn.row_factory = sqlite3.Row
            if limit:
                sql = sql.rstrip().rstrip(";") + f" LIMIT {int(limit)} ;"
            cur = conn.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]

    def por_periodo(self, inicio: datetime, fim: Optional[datetime] = None,
                    limit: int = 5000) -> List[Dict[str, Any]]:
        fim = fim or datetime.now(tz=timezone.utc)
        return self._q(
            "SELECT * FROM auditoria_eventos "
            "WHERE timestamp_ms >= ? AND timestamp_ms <= ? ORDER BY id DESC;",
            params=(inicio.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
                    fim.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")),
            limit=limit,
        )

    def por_acao(self, acao: AcaoAuditoria, limit: int = 1000) -> List[Dict[str, Any]]:
        return self._q(
            "SELECT * FROM auditoria_eventos WHERE acao = ? ORDER BY id DESC;",
            params=(acao.value,), limit=limit,
        )

    def por_status(self, status: StatusAuditoria, limit: int = 1000
                   ) -> List[Dict[str, Any]]:
        return self._q(
            "SELECT * FROM auditoria_eventos WHERE status = ? ORDER BY id DESC;",
            params=(status.value,), limit=limit,
        )

    def por_usuario_raw(self, usuario_raw: str, limit: int = 1000
                        ) -> List[Dict[str, Any]]:
        """
        Não podemos buscar direto por user_id_enc (está criptografado).
        Solução: varre os últimos N registros e descriptografa em memória
        (seguro pois só quem tem a chave Fernet consegue de fato filtrar).
        """
        recentes = self._q("SELECT * FROM auditoria_eventos ORDER BY id DESC LIMIT ?",
                           params=(limit * 5,))
        matches: List[Dict[str, Any]] = []
        for ev in recentes:
            user = self.logger.descriptografar_user(str(ev.get("user_id_enc") or ""))
            if user and usuario_raw.lower() in user.lower():
                matches.append(ev)
                if len(matches) >= limit:
                    break
        return matches

    def top_erros(self, ultimos_dias: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        desde = (datetime.now(tz=timezone.utc) - timedelta(days=ultimos_dias)
                 ).isoformat().replace("+00:00", "Z")
        return self._q(
            "SELECT acao, COUNT(*) qtd, MAX(timestamp_ms) ultimo_erro "
            "FROM auditoria_eventos "
            "WHERE status = ? AND timestamp_ms >= ? "
            "GROUP BY acao ORDER BY qtd DESC;",
            params=(StatusAuditoria.FALHA.value, desde), limit=limit,
        )

    def estatisticas_resumo(self, ultimos_dias: int = 7) -> Dict[str, Any]:
        desde = (datetime.now(tz=timezone.utc) - timedelta(days=ultimos_dias)
                 ).isoformat().replace("+00:00", "Z")
        total = self._q(
            "SELECT COUNT(*) c, SUM(CASE WHEN status='SUCESSO' THEN 1 ELSE 0 END) s, "
            "SUM(CASE WHEN status='FALHA' THEN 1 ELSE 0 END) f "
            "FROM auditoria_eventos WHERE timestamp_ms >= ?;",
            params=(desde,)
        )[0]
        por_acao = self._q(
            "SELECT acao, COUNT(*) qtd FROM auditoria_eventos "
            "WHERE timestamp_ms >= ? GROUP BY acao ORDER BY qtd DESC;",
            params=(desde,)
        )
        return {
            "periodo_dias": ultimos_dias,
            "total_eventos": total.get("c") or 0,
            "sucessos": total.get("s") or 0,
            "falhas": total.get("f") or 0,
            "eventos_por_acao": por_acao,
        }

    def validar_cadeia_custodia(self) -> Tuple[bool, int, str]:
        """
        Valida INTEGRIDADE da cadeia de hashes.
        Retorna: (valido: bool, qtd_registros:int, mensagem detalhada: str)
        """
        try:
            todos = self._q(
                "SELECT id, hash_integridade, cadeia_anterior_hash, event_id, "
                "timestamp_ms, user_id_enc, ip_origem_enc, acao, status, detalhes_json "
                "FROM auditoria_eventos ORDER BY id ASC;"
            )
        except Exception as err:
            return False, 0, f"Falha ao ler banco: {err}"
        prev_hash = "ROOT"
        for idx, ev in enumerate(todos, 1):
            try:
                payload = json.dumps(
                    {
                        "t": ev.get("timestamp_ms"),
                        "u": self.logger.descriptografar_user(str(ev.get("user_id_enc") or "")) or "",
                        "ip": self.logger.descriptografar_ip(str(ev.get("ip_origem_enc") or "")) or "",
                        "a": ev.get("acao"),
                        "s": ev.get("status"),
                        "d": json.loads(ev.get("detalhes_json") or "{}"),
                        "v": VERSAO_ESQUEMA_ATUAL,
                    },
                    sort_keys=True, ensure_ascii=False, separators=(",", ":")
                )
                calc = hashlib.sha256(f"{prev_hash}::{payload}".encode()).hexdigest()
                gravado = str(ev.get("hash_integridade") or "")
                ant_gravado = str(ev.get("cadeia_anterior_hash") or "")
                if ant_gravado != prev_hash:
                    return False, idx, (
                        f"Quebra de cadeia no evento #{idx} (id={ev.get('event_id')}): "
                        f"esperava cadeia_anterior={prev_hash}, gravado={ant_gravado}"
                    )
                if calc != gravado:
                    return False, idx, (
                        f"Hash inválido evento #{idx} (id={ev.get('event_id')}): "
                        f"calc={calc} gravado={gravado}"
                    )
                prev_hash = gravado
            except Exception as err:
                return False, idx, f"Excecao ao validar #{idx}: {err}"
        return True, len(todos), "Cadeia de custodia íntegra — nenhum registro adulterado."

    def aplicar_retencao_lgpd(self, dias_retencao: int = 90,
                              dry_run: bool = True) -> Tuple[int, int]:
        """
        Política LGPD padrão (90 dias): remove eventos mais antigos.
        Retorna (qtd_excluidos_jsonl, qtd_excluidos_sqlite).
        Se dry_run=True (default) NÃO apaga nada, só mostra quantos iria apagar.
        """
        cutoff = (datetime.now(tz=timezone.utc) - timedelta(days=dias_retencao)
                  ).isoformat().replace("+00:00", "Z")
        # 1. SQLite
        del_sql = 0
        try:
            with sqlite3.connect(self.db_path, timeout=30) as conn:
                cur = conn.execute(
                    "SELECT COUNT(*) FROM auditoria_eventos WHERE timestamp_ms < ?;",
                    (cutoff,)
                )
                del_sql = int(cur.fetchone()[0] or 0)
                if not dry_run:
                    conn.execute("DELETE FROM auditoria_eventos WHERE timestamp_ms < ?;",
                                 (cutoff,))
                    conn.commit()
        except Exception:
            pass
        # 2. JSONL
        del_jsonl = 0
        if self.logger._path_jsonl.exists():
            novas_linhas = []
            with open(self.logger._path_jsonl, "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        ev = json.loads(line)
                        if str(ev.get("timestamp_ms") or "") < cutoff:
                            del_jsonl += 1
                            continue
                        novas_linhas.append(line)
                    except Exception:
                        novas_linhas.append(line)
            if not dry_run and del_jsonl > 0:
                tmp_path = str(self.logger._path_jsonl) + ".tmp"
                with open(tmp_path, "w", encoding="utf-8") as fw:
                    fw.write("\n".join(novas_linhas) + ("\n" if novas_linhas else ""))
                os.replace(tmp_path, self.logger._path_jsonl)
        return del_sql, del_jsonl
