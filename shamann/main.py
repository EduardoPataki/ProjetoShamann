# shamann/main.py

import os
import logging
import json
from datetime import datetime
import csv # Para escrever CSV

# Importações dos seus módulos
from shamann.modules.nmap_guardian import NmapGuardian
# from shamann.persistence.db_manager import DBManager # Descomente se for usar DB
# from shamann.utils.notifier import Notifier # Descomente se for usar Notifier

# --- Configuração de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Função para carregar configurações ---
def load_config(config_path: str = 'shamann/config/scan_config.json') -> dict:
    # Tenta carregar o config.json, caso não haja um path CLI específico
    absolute_config_path = os.path.abspath(config_path)
    if not os.path.exists(absolute_config_path):
        logger.warning(f"Arquivo de configuração não encontrado em '{absolute_config_path}'. Usando configurações padrão ou CLI.")
        return {} # Retorna dicionário vazio para que as opções CLI ou padrões sejam aplicadas
    with open(absolute_config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    logger.info(f"Configuração carregada de '{absolute_config_path}'.")
    return config

# --- Função para gerar relatórios (CSV/JSON) ---
def generate_reports(scan_results: dict, output_settings: dict):
    output_dir = output_settings.get("output_directory", "./output")
    report_formats = output_settings.get("report_format", ["json"])

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Gerar JSON (detalhes completos do scan)
    if "json" in report_formats:
        json_filename_prefix = output_settings.get("json_filename_prefix", "shamann_scan_details")
        json_filepath = os.path.join(output_dir, f"{json_filename_prefix}_{timestamp}.json")
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(scan_results, f, indent=4, ensure_ascii=False)
        logger.info(f"Relatório JSON completo salvo em: {json_filepath}")

    # Gerar CSV de Alertas (foco nos alertas para validação manual)
    if "csv" in report_formats:
        csv_filename_prefix = output_settings.get("csv_filename_prefix", "shamann_alert_report")
        csv_filepath = os.path.join(output_dir, f"{csv_filename_prefix}_{timestamp}.csv")

        # Cabeçalhos do CSV
        headers = ["Nivel", "Tipo", "IP", "Hostname", "OS", "Porta", "Protocolo", "Servico", "Versao_Servico", "Descricao_Alerta", "Recomendacao"]

        with open(csv_filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers) # Escreve o cabeçalho

            for host_data in scan_results.get('hosts', []):
                host_ip = host_data.get('ip_address', 'N/A')
                host_hostname = host_data.get('hostname', 'N/A')
                host_os = host_data.get('os_match', 'N/A')

                # Se há alertas, escreve cada um
                if host_data.get('alerts'):
                    for alert in host_data['alerts']:
                        port_details = alert.get('details', {})
                        port_id = port_details.get('port_id', 'N/A')
                        protocol = port_details.get('protocol', 'N/A')
                        service_name = port_details.get('service_name', 'N/A')
                        service_product = port_details.get('service_product', 'N/A')
                        service_version = port_details.get('service_version', 'N/A')

                        writer.writerow([
                            alert.get('level', 'INFO'),
                            alert.get('type', 'Alerta Desconhecido'),
                            host_ip,
                            host_hostname,
                            host_os,
                            str(port_id),
                            protocol,
                            service_name,
                            f"{service_product} {service_version}".strip(),
                            alert.get('description', ''),
                            alert.get('recommendation', '')
                        ])
                else: # Se não há alertas para o host, registra uma linha informativa
                    writer.writerow([
                        "INFO", "Nenhum Alerta Direto", host_ip, host_hostname, host_os,
                        "N/A", "N/A", "N/A", "N/A", "Host online e escaneado, sem alertas de prioridade detectados.", ""
                    ])
        logger.info(f"Relatório CSV de alertas salvo em: {csv_filepath}")


# --- Função principal do orquestrador (chamada pela CLI) ---
def run_shamann_orchestrator(cli_target: str = None, config_path: str = 'shamann/config/scan_config.json',
                              cli_ports: str = None, cli_output_dir: str = None):
    try:
        config = load_config(config_path)

        # Mesclar configurações da CLI com as do arquivo JSON
        scan_profile = config.get("scan_profile", {})
        alert_rules = config.get("alert_rules", [])
        output_settings = config.get("output_settings", {})

        # Alvo: Prioridade para a CLI
        target_network = cli_target if cli_target else scan_profile.get("target")
        if not target_network:
            logger.error("Alvo de scan não especificado. Use -t/--target ou configure em scan_config.json.")
            return

        # Portas: Prioridade para a CLI
        ports_to_scan = cli_ports if cli_ports else scan_profile.get("ports", "1-1000")
        if ports_to_scan.lower() == 'all':
            ports_to_scan = "1-65535"

        # Opções Nmap: Vêm do config.json
        nmap_options = scan_profile.get("nmap_options", "-sS -sV -O -A -T4")
        include_default_scripts = scan_profile.get("include_default_scripts", True)
        custom_scripts = scan_profile.get("custom_scripts", [])

        # Diretório de Saída: Prioridade para a CLI
        if cli_output_dir:
            output_settings["output_directory"] = cli_output_dir

        logger.info(f"Iniciando operação do Shamann para o alvo: {target_network}")
        logger.info(f"Portas a escanear: {ports_to_scan}")

        # 1. Inicializar NmapGuardian com o target da CLI/config
        nmap_guardian = NmapGuardian(target=target_network)

        # 2. Executar o scan
        scan_results = nmap_guardian.run_scan(
            nmap_options=nmap_options,
            ports_to_scan=ports_to_scan,
            include_default_scripts=include_default_scripts,
            custom_scripts=custom_scripts
        )

        if not scan_results or not scan_results.get('hosts'):
            logger.warning(f"Nenhum resultado ou hosts encontrados para o alvo {target_network}.")
            return

        # 3. Classificar alertas com base nas regras do JSON
        processed_scan_results = nmap_guardian.classify_alerts_with_rules(scan_results, alert_rules)

        # 4. Gerar relatórios para validação manual
        generate_reports(processed_scan_results, output_settings)

        logger.info(f"Operação do Shamann para o alvo {target_network} concluída. Relatórios gerados.")

    except FileNotFoundError as e:
        logger.error(f"Erro de configuração: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao ler arquivo JSON de configuração: {e}")
    except Exception as e:
        logger.error(f"Ocorreu um erro inesperado na execução do Shamann: {e}", exc_info=True)

# Este bloco não é mais o ponto de entrada principal,
# mas mantém a compatibilidade se alguém o executar diretamente (não recomendado).
if __name__ == "__main__":
    logger.warning("Executando shamann/main.py diretamente. Use 'python -m shamann.cli.main --help' para a CLI.")
    run_shamann_orchestrator(config_path='shamann/config/scan_config.json') # Exemplo de uso direto
