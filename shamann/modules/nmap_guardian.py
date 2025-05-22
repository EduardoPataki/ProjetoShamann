# shamann/modules/nmap_guardian.py

import nmap
import json
import logging
import datetime
import re # Para expressões regulares na avaliação de regras

logger = logging.getLogger(__name__)

class NmapGuardian:
    def __init__(self, target: str):
        self.target = target
        self.scanner = nmap.PortScanner()

    def run_scan(self, nmap_options: str = "-sS -sV -O -A -T4", ports_to_scan: str = "1-1000",
                 include_default_scripts: bool = True, custom_scripts: list = None) -> dict:
        """
        Executa um scan Nmap no alvo/rede com opções configuráveis.
        """
        logger.info(f"Iniciando scan Nmap para o alvo/rede: {self.target}")
        logger.info(f"Opções Nmap: {nmap_options} - Portas: {ports_to_scan}")

        full_nmap_arguments = nmap_options
        if include_default_scripts and "--script=default" not in full_nmap_arguments:
            full_nmap_arguments += " --script=default"
        if custom_scripts:
            for script in custom_scripts:
                # Adicionar scripts personalizados, evitando duplicidade e formatando corretamente
                if f"--script={script}" not in full_nmap_arguments:
                    full_nmap_arguments += f" --script={script}"

        try:
            self.scanner.scan(self.target, ports=ports_to_scan, arguments=full_nmap_arguments)
            scan_results = self._parse_nmap_results()
            logger.info(f"Scan Nmap para {self.target} concluído. Encontrados {len(scan_results.get('hosts', []))} hosts com portas.")
            return scan_results

        except nmap.PortScannerError as e:
            logger.error(f"Erro no Nmap: {e}")
            return {}
        except Exception as e:
            logger.error(f"Erro inesperado ao executar scan Nmap: {e}", exc_info=True)
            return {}

    def _parse_nmap_results(self) -> dict:
        """
        Analisa os resultados brutos do Nmap e os estrutura em um dicionário padronizado.
        NÃO CLASSIFICA ALERTAS AQUI; a classificação é feita por `classify_alerts_with_rules`.
        """
        parsed_results = {
            "scan_time": datetime.datetime.now().isoformat(),
            "hosts": []
        }

        for host in self.scanner.all_hosts():
            host_data = {
                "ip_address": host,
                "hostname": self.scanner[host].hostname() if self.scanner[host].hostname() else "N/A",
                "status": self.scanner[host].state(),
                "os_match": "N/A",
                "os_accuracy": "N/A",
                "vendor": "N/A",
                "ports": []
            }

            if 'osmatch' in self.scanner[host] and self.scanner[host]['osmatch']:
                best_os = self.scanner[host]['osmatch'][0]
                host_data['os_match'] = best_os['name']
                host_data['os_accuracy'] = best_os['accuracy']

            # Verifica se o host possui informações de endereço MAC e vendor
            if 'addresses' in self.scanner[host] and 'mac' in self.scanner[host]['addresses']:
                try:
                    # nmap.PortScanner().get_mac_vendor() pode ser usado se o host está no contexto
                    # Ou diretamente self.scanner[host]['vendor']() se disponível
                    # O python-nmap já popula host.vendor()
                    host_data['vendor'] = self.scanner[host].vendor(host)
                except Exception:
                    host_data['vendor'] = "Unknown"


            if self.scanner[host].state() == 'up':
                for proto in self.scanner[host].all_protocols():
                    for port in self.scanner[host][proto].keys():
                        port_info = self.scanner[host][proto][port]
                        port_data = {
                            "port_id": port,
                            "protocol": proto,
                            "state": port_info.get('state', 'N/A'),
                            "service_name": port_info.get('name', 'N/A'),
                            "service_product": port_info.get('product', 'N/A'),
                            "service_version": port_info.get('version', 'N/A'),
                            "extrainfo": port_info.get('extrainfo', 'N/A'),
                            "cpe": port_info.get('cpe', 'N/A'),
                            "scripts": port_info.get('script', {}) # NSE script output
                        }
                        host_data['ports'].append(port_data)

            parsed_results['hosts'].append(host_data)
        return parsed_results

    def classify_alerts_with_rules(self, scan_results: dict, alert_rules: list) -> dict:
        """
        Classifica os alertas com base nas regras fornecidas na configuração.
        Modifica scan_results in-place para adicionar a lista de alertas a cada host.
        """
        logger.info("Classificando alertas com base nas regras de configuração...")
        for host_data in scan_results.get('hosts', []):
            # Inicializa a lista de alertas para este host.
            host_data['alerts'] = []

            # Adiciona alerta se o host está offline ou filtrado
            if host_data['status'] != 'up':
                host_data['alerts'].append({
                    "level": "INFO",
                    "type": "Host Offline ou Filtrado",
                    "description": f"O host {host_data['ip_address']} está {host_data['status']} e não pôde ser escaneado detalhadamente.",
                    "recommendation": "Verificar o status do host ou as regras de firewall que podem estar impedindo o scan.",
                    "details": {"status": host_data['status']}
                })
                # Não continua processando portas para hosts que não estão 'up'.
                continue

            # Alerta para SO não identificado
            if host_data['os_match'] == "N/A" and host_data['status'] == 'up':
                host_data['alerts'].append({
                    "level": "INFO",
                    "type": "Sistema Operacional Não Identificado",
                    "description": f"Sistema Operacional do host {host_data['ip_address']} não pôde ser identificado pelo Nmap.",
                    "recommendation": "Investigar manualmente o host. Pode ser um dispositivo IoT obscuro, roteador, ou um firewall.",
                    "details": {}
                })

            for port_data in host_data.get('ports', []):
                # Criar variáveis de conveniência para avaliação das regras.
                # IMPORTANTE: Essas variáveis são usadas na string 'condition' do JSON.
                ip = host_data.get('ip_address')
                hostname = host_data.get('hostname')
                os_match = host_data.get('os_match')
                os_accuracy = host_data.get('os_accuracy')
                vendor = host_data.get('vendor') # MAC Vendor
                port_id = port_data.get('port_id')
                protocol = port_data.get('protocol')
                state = port_data.get('state')
                service_name = port_data.get('name') # service_name é 'name' no port_data
                service_product = port_data.get('service_product')
                service_version = port_data.get('service_version')
                extrainfo = port_data.get('extrainfo')
                cpe = port_data.get('cpe')
                scripts_output = port_data.get('scripts') # Saída de scripts NSE

                # Versões lower case para facilitar comparações nas regras.
                service_lower = service_name.lower() if service_name else ''
                product_lower = service_product.lower() if service_product else ''
                version_lower = service_version.lower() if service_version else ''
                extrainfo_lower = extrainfo.lower() if extrainfo else ''
                cpe_lower = cpe.lower() if cpe else ''
                vendor_lower = vendor.lower() if vendor else ''
                os_lower = os_match.lower() if os_match else ''


                for rule in alert_rules:
                    condition = rule.get('condition')
                    try:
                        # Avalia a condição.
                        # Segurança: 'eval' é poderoso. Em um ambiente de produção não controlado,
                        # um parser de regras mais seguro seria recomendado. Para pentest pessoal, é funcional.
                        if eval(condition, {
                            # Variáveis disponíveis para as regras no JSON
                            'ip': ip, 'hostname': hostname, 'os_match': os_match, 'os_accuracy': os_accuracy, 'vendor': vendor,
                            'port_id': port_id, 'protocol': protocol, 'state': state, 'service_name': service_name,
                            'service_product': service_product, 'service_version': service_version, 'extrainfo': extrainfo,
                            'cpe': cpe, 'scripts_output': scripts_output, # Inclui saída de scripts
                            'service_lower': service_lower, 'product_lower': product_lower,
                            'version_lower': version_lower, 'extrainfo_lower': extrainfo_lower, 'cpe_lower': cpe_lower,
                            'vendor_lower': vendor_lower, 'os_lower': os_lower
                        }):
                            host_data['alerts'].append({
                                "level": rule.get('level', 'UNKNOWN'),
                                "type": rule.get('type', 'Alerta Personalizado'),
                                "description": rule.get('description', 'Alerta acionado por regra personalizada.'),
                                "recommendation": rule.get('recommendation', 'Verificar a regra de alerta.'),
                                "details": port_data # Detalhes completos da porta/serviço para o anexo
                            })
                            # Se uma regra CRITICAL for acionada, as outras regras para esta porta não precisam ser verificadas,
                            # pois já é o nível mais alto.
                            if rule.get('level') == 'CRITICAL':
                                break # Sai do loop de regras para esta porta

                    except Exception as e:
                        logger.error(f"Erro ao avaliar regra '{condition}': {e}", exc_info=True)

        return scan_results
