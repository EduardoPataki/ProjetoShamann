import sqlite3
import json
from datetime import datetime, UTC
import logging

# Configuração de logging para este módulo
logger = logging.getLogger(__name__)

# --- ESQUEMA DO BANCO DE DADOS ---
# Este SQL será usado para criar as tabelas no banco de dados.
# Ele inclui tabelas para scans, hosts (Nmap, DNS, etc.), portas (Nmap),
# alertas (geral para qualquer Guardião) e logs internos do sistema.
DB_SCHEMA = """
-- Tabela principal para registrar cada execução de scan
CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guardian_name TEXT NOT NULL,
    target TEXT NOT NULL,
    scan_start_utc TEXT NOT NULL, -- Formato ISO 8601 (UTC)
    scan_end_utc TEXT,            -- Formato ISO 8601 (UTC)
    duration_seconds REAL,
    status TEXT NOT NULL,         -- 'success', 'error', 'warning'
    command_executed TEXT,        -- O comando real executado pela ferramenta
    return_code INTEGER,          -- Código de retorno da ferramenta
    error_message TEXT,           -- Mensagem de erro se houver
    raw_output_stdout TEXT,       -- Saída bruta do stdout da ferramenta (opcional, para debugging)
    raw_output_stderr TEXT        -- Saída bruta do stderr da ferramenta (opcional, para debugging)
);

-- Tabela para armazenar informações de hosts encontrados (ex: Nmap, DNS, Whois)
CREATE TABLE IF NOT EXISTS hosts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id INTEGER NOT NULL,
    ip_address TEXT NOT NULL,
    hostname TEXT,
    mac_address TEXT,
    mac_vendor TEXT,
    os_info TEXT,
    host_status TEXT,             -- 'up', 'down', 'filtered' (do Nmap)
    FOREIGN KEY (scan_id) REFERENCES scans (id) ON DELETE CASCADE,
    UNIQUE(scan_id, ip_address) -- Garante que um IP seja único para um dado scan
);

-- Tabela para portas (principalmente para resultados do Nmap)
CREATE TABLE IF NOT EXISTS ports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host_id INTEGER NOT NULL,
    port_id INTEGER NOT NULL,
    protocol TEXT NOT NULL,
    state TEXT NOT NULL,          -- 'open', 'closed', 'filtered'
    service_name TEXT,
    service_product TEXT,
    service_version TEXT,
    service_extrainfo TEXT,
    severity TEXT,                -- 'CRITICAL', 'MEDIUM', 'LOW', 'INFO' (para portas com vulnerabilidades)
    recommendation TEXT,          -- Recomendação para a porta/serviço
    FOREIGN KEY (host_id) REFERENCES hosts (id) ON DELETE CASCADE,
    UNIQUE(host_id, port_id, protocol) -- Garante que uma porta seja única para um host/protocolo
);

-- Tabela para alertas (generalizada para qualquer Guardião que produza alertas)
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id INTEGER NOT NULL,
    host_id INTEGER,              -- Pode ser NULL se o alerta não for específico de um host
    port_id INTEGER,              -- Pode ser NULL se o alerta não for específico de uma porta
    level TEXT NOT NULL,          -- 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'
    type TEXT NOT NULL,           -- 'OpenPort', 'WeakCredential', 'VulnerabilityDetected', etc.
    description TEXT NOT NULL,    -- Descrição do alerta
    recommendation TEXT,          -- Recomendação para o alerta
    details_json TEXT,            -- Armazenar detalhes adicionais do alerta como JSON
    FOREIGN KEY (scan_id) REFERENCES scans (id) ON DELETE CASCADE,
    FOREIGN KEY (host_id) REFERENCES hosts (id) ON DELETE CASCADE,
    FOREIGN KEY (port_id) REFERENCES ports (id) ON DELETE CASCADE
);

-- Tabela para logs internos de atividade do Mestre ou Guardiões (para rastreamento interno)
CREATE TABLE IF NOT EXISTS internal_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,      -- Formato ISO 8601 (UTC)
    level TEXT NOT NULL,          -- 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    source TEXT NOT NULL,         -- e.g., 'main', 'nmap_guardian', 'db_manager'
    message TEXT NOT NULL,        -- Mensagem do log
    details_json TEXT             -- Quaisquer detalhes extras como JSON
);
"""

class DBManager:
    def __init__(self, db_path):
        """
        Inicializa o DBManager e cria as tabelas do banco de dados se elas não existirem.
        :param db_path: Caminho completo para o arquivo SQLite (ex: 'agent_ia.db').
        """
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """
        Cria as tabelas do banco de dados se elas não existirem.
        Conecta ao banco, executa o script SQL para criação das tabelas e fecha a conexão.
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Garante que as chaves estrangeiras estão ativadas para integridade referencial
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.executescript(DB_SCHEMA)
            conn.commit()
            logger.info(f"Banco de dados SQLite inicializado/verificado em: {self.db_path}")
        except sqlite3.Error as e:
            logger.critical(f"Erro CRÍTICO ao inicializar o banco de dados: {e}", exc_info=True)
            # Re-lança a exceção para que o Mestre saiba que o DB não está funcional
            raise
        finally:
            if conn:
                conn.close()

    def _connect(self):
        """
        Retorna uma nova conexão com o banco de dados.
        Ativa o modo WAL (Write-Ahead Logging) para melhor concorrência e resiliência.
        """
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;") # Garante chaves estrangeiras ativadas por conexão
        conn.execute("PRAGMA journal_mode=WAL;") # Ativa o modo WAL
        return conn

    def insert_scan_results(self, guardian_name: str, target: str, scan_result: dict) -> int | None:
        """
        Insere os resultados processados de um scan no banco de dados.
        Retorna o ID do scan inserido na tabela 'scans' ou None em caso de erro.
        :param guardian_name: Nome do Guardião que executou o scan (ex: 'nmap').
        :param target: O alvo do scan (IP, hostname, domínio).
        :param scan_result: O dicionário JSON retornado pelo Guardião.
        """
        conn = None
        scan_id = None
        try:
            conn = self._connect()
            cursor = conn.cursor()

            # --- Extrair e inserir dados na tabela 'scans' ---
            # Validações básicas de campos essenciais
            # CORREÇÃO APLICADA AQUI: Mudando 'status' para 'success' na validação
            if not all(k in scan_result for k in ["success", "command", "returncode"]):
                logger.error(f"Resultado de scan inválido para '{guardian_name}' em '{target}'. Faltando chaves essenciais: {scan_result.keys()}")
                raise ValueError("Resultado de scan JSON incompleto.")

            # Informações gerais do scan
            scan_info_raw = scan_result.get("scan_info", {}) # Nmap Guardian tem um 'scan_info'

            scan_start_utc = scan_info_raw.get("timestamp_scan_start", datetime.now(UTC).isoformat())
            # Usa o timestamp de parse/fim do scan como end_utc
            scan_end_utc = scan_info_raw.get("timestamp_parse_utc", datetime.now(UTC).isoformat())

            # Ajuste para obter duration_seconds corretamente
            duration_seconds = scan_info_raw.get("duration_seconds")
            if duration_seconds is None: # Tenta fallback para "summary" se "duration_seconds" não estiver direto no scan_info
                duration_seconds = scan_info_raw.get("summary", {}).get("scan_elapsed_time_seconds")


            status = scan_result.get("success", False) # Nmap Guardian usa 'success'
            status_text = "success" if status else "error"
            if scan_result.get("error_message"):
                status_text = "warning" # Se teve erro mas sucesso parcial, ou apenas erro

            command_executed = json.dumps(scan_result.get("command", [])) # Salva como JSON string
            return_code = scan_result.get("returncode", -1)
            error_message = scan_result.get("error_message")
            raw_stdout = scan_result.get("stdout")
            raw_stderr = scan_result.get("stderr")

            cursor.execute("""
                INSERT INTO scans (guardian_name, target, scan_start_utc, scan_end_utc, duration_seconds,
                                   status, command_executed, return_code, error_message,
                                   raw_output_stdout, raw_output_stderr)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (guardian_name, target, scan_start_utc, scan_end_utc, duration_seconds,
                  status_text, command_executed, return_code, error_message,
                  raw_stdout, raw_stderr))

            scan_id = cursor.lastrowid # Pega o ID do scan recém-inserido

            # --- Lógica de inserção para resultados específicos de Guardiões ---
            # Esta parte precisa ser adaptada para cada tipo de Guardião
            # Começamos com o Nmap Guardian (que retorna 'hosts' e 'ports')
            if guardian_name == "nmap" and "hosts" in scan_result:
                for host_data in scan_result["hosts"]:
                    # Validação mínima do host
                    if not host_data.get("ip_address"):
                        logger.warning(f"Host sem IP em scan_id {scan_id}, pulando: {host_data}")
                        continue

                    cursor.execute("""
                        INSERT INTO hosts (scan_id, ip_address, hostname, mac_address, mac_vendor, os_info, host_status)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (scan_id, host_data.get("ip_address"), host_data.get("hostname"),
                          host_data.get("mac_address"), host_data.get("mac_vendor"),
                          host_data.get("os_info"), host_data.get("status")))
                    host_id = cursor.lastrowid # Pega o ID do host recém-inserido

                    # Inserir portas para este host (se existirem)
                    for port_data in host_data.get("ports", []):
                        # Validação mínima da porta
                        if not all(k in port_data for k in ["port_id", "protocol", "state"]):
                            logger.warning(f"Porta inválida para host_id {host_id}, pulando: {port_data}")
                            continue

                        cursor.execute("""
                            INSERT INTO ports (host_id, port_id, protocol, state, service_name, service_product,
                                               service_version, service_extrainfo, severity, recommendation)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (host_id, port_data.get("port_id"), port_data.get("protocol"),
                              port_data.get("state"), port_data.get("service_name"),
                              port_data.get("product"), port_data.get("version"),
                              port_data.get("extrainfo"), port_data.get("severity"), # Nmap Guardian já pode ter esses campos
                              port_data.get("recommendation")))
                        # port_id_db = cursor.lastrowid # Se precisar para alertas muito específicos de script de porta

            # --- Inserir alertas (pode ser geral para qualquer Guardião que retorne 'alerts') ---
            if "alerts" in scan_result:
                for alert_data in scan_result["alerts"]:
                    # Validação básica de alerta: precisa ter nível, tipo e descrição
                    if not all(k in alert_data for k in ["level", "type", "description"]):
                        logger.warning(f"Alerta inválido encontrado para scan_id {scan_id}, pulando: {alert_data}")
                        continue

                    # Tentar associar host_id e port_id se o alerta tiver IP/Porta
                    alert_host_id = None
                    alert_port_id = None
                    # Lógica para associar alerta ao host/porta, se aplicável
                    if "host" in alert_data and scan_id:
                        cursor.execute("SELECT id FROM hosts WHERE scan_id = ? AND ip_address = ?",
                                       (scan_id, alert_data["host"]))
                        result = cursor.fetchone()
                        if result:
                            alert_host_id = result[0]
                    if "port" in alert_data and "protocol" in alert_data and alert_host_id:
                         cursor.execute("SELECT id FROM ports WHERE host_id = ? AND port_id = ? AND protocol = ?",
                                        (alert_host_id, alert_data["port"], alert_data["protocol"]))
                         result = cursor.fetchone()
                         if result:
                             alert_port_id = result[0]

                    cursor.execute("""
                        INSERT INTO alerts (scan_id, host_id, port_id, level, type, description, recommendation, details_json)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (scan_id, alert_host_id, alert_port_id,
                          alert_data.get("level"), alert_data.get("type"),
                          alert_data.get("description"), alert_data.get("recommendation"),
                          json.dumps(alert_data.get("details", {})) if alert_data.get("details") else None ))

            conn.commit() # Confirma todas as operações de inserção
            logger.info(f"Resultados do scan '{guardian_name}' para '{target}' (DB ID: {scan_id}) inseridos com sucesso.")
            return scan_id

        except sqlite3.Error as e:
            if conn:
                conn.rollback() # Desfaz todas as operações em caso de erro no DB
            logger.error(f"Erro SQLite ao inserir resultados do scan no DB para '{target}': {e}", exc_info=True)
            self.add_internal_log("ERROR", "db_manager", f"Erro ao inserir resultados do scan no DB: {e}", {"target": target})
            return None
        except ValueError as e:
            if conn:
                conn.rollback()
            logger.error(f"Erro de validação de dados ao inserir resultados: {e}", exc_info=True)
            self.add_internal_log("ERROR", "db_manager", f"Erro de validação ao inserir resultados: {e}", {"target": target})
            return None
        except Exception as e:
            if conn:
                conn.rollback()
            logger.critical(f"Erro INESPERADO ao processar e inserir resultados no DB para '{target}': {e}", exc_info=True)
            self.add_internal_log("CRITICAL", "db_manager", f"Erro inesperado ao inserir resultados no DB: {e}", {"target": target})
            return None
        finally:
            if conn:
                conn.close() # Sempre fecha a conexão

    def add_internal_log(self, level: str, source: str, message: str, details: dict = None):
        """
        Adiciona um log interno de atividade ao banco de dados.
        Usado para rastrear operações do sistema, erros, etc.
        :param level: Nível do log (INFO, WARNING, ERROR, CRITICAL).
        :param source: Onde o log foi gerado (ex: 'main', 'nmap_guardian', 'db_manager').
        :param message: A mensagem principal do log.
        :param details: Dicionário com detalhes adicionais, será armazenado como JSON.
        """
        conn = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            timestamp = datetime.now(UTC).isoformat()
            cursor.execute("""
                INSERT INTO internal_logs (timestamp, level, source, message, details_json)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, level, source, message, json.dumps(details) if details else None))
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Erro ao adicionar log interno ao DB: {e}", exc_info=True)
        finally:
            if conn:
                conn.close()

    # --- Métodos de Consulta (Para futuros relatórios e Oracle) ---
    def get_scan_by_id(self, scan_id: int) -> dict | None:
        """Busca um scan pelo ID."""
        conn = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
            row = cursor.fetchone()
            if row:
                # Retorna como dicionário para facilitar o uso
                cols = [description[0] for description in cursor.description]
                return dict(zip(cols, row))
            return None
        except sqlite3.Error as e:
            logger.error(f"Erro ao buscar scan por ID {scan_id}: {e}", exc_info=True)
            return None
        finally:
            if conn:
                conn.close()

    def get_alerts_by_scan_id(self, scan_id: int) -> list[dict]:
        """Busca todos os alertas para um dado scan_id."""
        conn = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM alerts WHERE scan_id = ?", (scan_id,))
            rows = cursor.fetchall()
            cols = [description[0] for description in cursor.description]
            return [dict(zip(cols, row)) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Erro ao buscar alertas para scan ID {scan_id}: {e}", exc_info=True)
            return []
        finally:
            if conn:
                conn.close()

    def get_hosts_by_scan_id(self, scan_id: int) -> list[dict]:
        """Busca todos os hosts para um dado scan_id."""
        conn = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM hosts WHERE scan_id = ?", (scan_id,))
            rows = cursor.fetchall()
            cols = [description[0] for description in cursor.description]
            return [dict(zip(cols, row)) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Erro ao buscar hosts para scan ID {scan_id}: {e}", exc_info=True)
            return []
        finally:
            if conn:
                conn.close()

    def get_ports_by_host_id(self, host_id: int) -> list[dict]:
        """Busca todas as portas para um dado host_id."""
        conn = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ports WHERE host_id = ?", (host_id,))
            rows = cursor.fetchall()
            cols = [description[0] for description in cursor.description]
            return [dict(zip(cols, row)) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Erro ao buscar portas para host ID {host_id}: {e}", exc_info=True)
            return []
        finally:
            if conn:
                conn.close()
