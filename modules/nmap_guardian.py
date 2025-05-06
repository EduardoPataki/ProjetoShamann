# shamann/modules/nmap_guardian.py

import subprocess # Para executar comandos externos (Nmap)
import sys # Para verificar a plataforma
# Precisaremos de logging, vamos importar ou usar um logger centralizado depois
# from shamann.core import logger # Importação ajustada para a nova estrutura

# logger = logger.get_logger(__name__) if logger else print # Usar print se logger não carregar


class NmapGuardian:
    """
    Guardião responsável por interagir com a ferramenta Nmap.
    """

    @staticmethod
    def run_scan(target: str, options: str = "-sV") -> dict:
        """
        Executa um scan Nmap em um target e retorna os resultados.

        Args:
            target: O host ou IP alvo do scan Nmap.
            options: Opções adicionais para o comando nmap (ex: "-p 80,443").

        Returns:
            Um dicionário contendo os resultados do scan, incluindo dados parseados.
            Retorna um dicionário de erro em caso de falha.
        """
        # TODO: Usar logging apropriado em vez de print para erros/info

        print(f"Iniciando scan Nmap em {target} com opções: {options}")

        # Construir o comando nmap. Usar lista de argumentos é mais seguro (evita shell=True).
        # Dividimos as opções em uma lista para passar corretamente ao subprocess.
        command = ["nmap"] # Começa com o nome do comando
        # Adiciona as opções, dividindo a string por espaços. Cuidado com opções com espaços internos.
        # Para opções com espaços (ex: --script "script args"), seria necessário um parsing mais sofisticado.
        # Por enquanto, assumimos opções separadas por espaço.
        if options:
            # Adicionar opções, lidando com possíveis espaços no valor da opção
            # Uma forma mais robusta seria usar shlex.split(), mas options.split() é mais simples para começar
            command.extend(options.split())

        command.append(target) # Adiciona o target no final

        # Opcional: Adicionar a opção -oX - para saída XML que pode ser mais fácil de parsear
        # command.extend(["-oX", "-"]) # Adiciona saída XML para stdout

        try:
            # Executar o comando nmap
            # capture_output=True captura stdout e stderr
            # text=True decodifica stdout/stderr como texto usando encoding padrão
            # check=True levanta CalledProcessError se o comando retornar código de erro não zero
            # timeout=... pode ser útil para scans que travam
            # stderr é importante para ver erros do Nmap
            result = subprocess.run(command, capture_output=True, text=True, check=True, stderr=subprocess.PIPE)

            # Processar a saída bruta
            raw_output = result.stdout
            raw_error = result.stderr # Capturar stderr

            # Chamar a função interna para parsear a saída bruta
            parsed_data = NmapGuardian._parse_nmap_output(raw_output)

            # Retornar os resultados completos
            return {
                "target": target,
                "options": options,
                "command_executed": " ".join(command),
                "stdout": raw_output,
                "stderr": raw_error, # Incluir stderr no resultado
                "returncode": result.returncode,
                "status": "completed",
                "parsed_data": parsed_data # Incluir os dados parseados
            }

        except FileNotFoundError:
            # Erro se o comando 'nmap' não for encontrado (Nmap não instalado ou não no PATH)
            print(f"Erro: Nmap não encontrado. Certifique-se de que o Nmap está instalado e no PATH.")
            # TODO: Usar logging.error aqui
            return {
                "target": target,
                "options": options,
                "command_executed": " ".join(command),
                "status": "error",
                "error_type": "FileNotFoundError",
                "error_message": "Nmap tool not found. Is Nmap installed and in your system's PATH?"
            }
        except subprocess.CalledProcessError as e:
            # Erro se o Nmap retornar um código de saída diferente de zero (erro durante a execução do scan)
            # Capturar stderr do erro para ver a mensagem do Nmap
            error_message = f"Nmap command failed (Return Code {e.returncode}): {e.stderr.strip()}"
            print(f"Erro ao executar Nmap: {error_message}")
            # TODO: Usar logging.error aqui
            return {
                "target": target,
                "options": options,
                "command_executed": " ".join(command),
                "status": "error",
                "error_type": "CalledProcessError",
                "returncode": e.returncode,
                "stdout": e.stdout, # Incluir stdout mesmo em caso de erro (pode ter warnings)
                "stderr": e.stderr,
                "error_message": error_message
            }
        except Exception as e:
            # Captura quaisquer outros erros inesperados
            error_message = f"Ocorreu um erro inesperado ao executar Nmap: {e}"
            print(f"Erro inesperado: {error_message}")
            # TODO: Usar logging.error aqui
            return {
                "target": target,
                "options": options,
                "command_executed": " ".join(command),
                "status": "error",
                "error_type": "UnexpectedError",
                "error_message": error_message
            }

    @staticmethod
    def _parse_nmap_output(raw_output: str) -> dict:
        """
        Função interna para parsear a saída bruta do Nmap (formato padrão)
        e extrair informações chave.

        Args:
            raw_output: A string contendo a saída bruta do Nmap.

        Returns:
            Um dicionário contendo os dados parseados (portas, serviços, estado, etc.).
            Retorna um dicionário vazio ou com erros de parsing se houver problemas.
        """
        # Este é um parser BÁSICO. Parsing robusto de Nmap é complexo!
        # Considerar usar bibliotecas como python-nmap ou processar saída XML (-oX)
        # para um parsing mais confiável.

        parsed_data = {
            "host": None,
            "ports": [],
            "os_info": None,
            "raw_parsing_output": raw_output # Incluir a saída bruta para referência
        }

        lines = raw_output.splitlines()

        # Exemplo de parsing simples: procurar por linhas de porta aberta
        # Nmap output linhas de porta geralmente parecem assim:
        # PORT     STATE SERVICE VERSION
        # 22/tcp   open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.6 (Ubuntu)
        # 80/tcp   open  http    nginx 1.18.0 (Ubuntu)
        # 443/tcp  open  ssl/http nginx 1.18.0 (Ubuntu)

        port_section_started = False
        for line in lines:
            line = line.strip()
            if line.startswith("PORT"):
                port_section_started = True
                continue # Ignora a linha de cabeçalho

            if port_section_started and line:
                # Tentar parsear linhas de porta. Isso é muito simplificado.
                # Pode falhar com diferentes formatos de saída do Nmap.
                parts = line.split(maxsplit=3) # Divide no máximo 3 vezes

                if len(parts) >= 3:
                    port_info = {
                        "port_id": parts[0],
                        "state": parts[1],
                        "service": parts[2],
                        "version": parts[3] if len(parts) > 3 else ""
                    }
                    # Adicionar a porta apenas se o estado indicar que é relevante (ex: 'open', 'filtered')
                    # Adapte conforme o que você considera importante
                    if port_info["state"] in ["open", "filtered", "closed"]: # Incluindo closed/filtered para ver mais detalhes
                         parsed_data["ports"].append(port_info)

            # Exemplo de parsing simples para informação de host/OS (ainda mais complexo no Nmap real)
            if line.startswith("Nmap scan report for"):
                 # Ex: "Nmap scan report for scanme.nmap.org (45.33.32.140)"
                 if " for " in line and "(" in line and ")" in line:
                      parts = line.split(" for ", 1)
                      if len(parts) > 1:
                           host_part = parts[1].strip()
                           if "(" in host_part and host_part.endswith(")"):
                                # Extrai hostname e IP
                                hostname = host_part.split(" (")[0]
                                ip_address = host_part.split(" (")[1].strip(")")
                                parsed_data["host"] = {"hostname": hostname, "ip_address": ip_address}
                           else:
                                parsed_data["host"] = {"hostname": host_part, "ip_address": None} # Apenas hostname
                 elif "(" in line and line.endswith(")"): # Apenas IP em parênteses
                      ip_address = line.split("(")[1].strip(")")
                      parsed_data["host"] = {"hostname": None, "ip_address": ip_address}


            # TODO: Adicionar parsing para informações de OS, serviços detalhados, scripts, etc.
            # Ex: "Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel"
            # Ex: "OS details: Linux 2.6.32 - 4.10"


        # TODO: Lidar com saída XML (-oX -) para parsing mais robusto
        # Se usarmos -oX -, esta função precisaria processar XML em vez de texto plano.

        return parsed_data

# Exemplo de como pode ser chamado (isso será feito pela função execute_guardian_scan no shamann/main.py)
# if __name__ == "__main__":
#     # Certifique-se de ter o Nmap instalado para testar!
#     # Use um target seguro como scanme.nmap.org para testes legítimos.
#     # Não escaneie redes sem permissão!
#     print("\n--- Teste Direto de Parsing Nmap ---")
#
#     # Exemplo de saída bruta de Nmap para testar a função _parse_nmap_output
#     exemplo_saida_bruta = """
# Starting Nmap 7.80 ( https://nmap.org ) at 2023-10-27 10:00 CEST
# Nmap scan report for scanme.nmap.org (45.33.32.140)
# Host is up (0.030s latency).
# Other addresses for scanme.nmap.org (not scanned): 64:ff9b::2d21:208c
# Not shown: 997 filtered ports
# PORT   STATE SERVICE VERSION
# 22/tcp open  ssh     OpenSSH 6.6p1 Ubuntu 2ubuntu2.13 (Ubuntu Linux; protocol 2.0)
# 80/tcp open  http    Apache httpd 2.4.7 ((Ubuntu))
# 9929/tcp open  nping   Nping echo
# Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
#
# Nmap done: 1 IP address (1 host up) scanned in 0.85 seconds
# """
#
#     print("Testando parsing com saída de exemplo:")
#     parsed_result_example = NmapGuardian._parse_nmap_output(exemplo_saida_bruta)
#     print(parsed_result_example)
#
#     print("\n--- Teste Direto de Execução e Parsing Nmap (Requer Nmap instalado) ---")
#     # Para rodar este teste real, descomente as linhas abaixo e rode o script diretamente
#     # Certifique-se de NÃO escanear alvos sem permissão!
#     # try:
#     #     subprocess.run(["nmap", "--version"], check=True, capture_output=True, text=True)
#     #     print("Nmap encontrado. Rodando scan de teste em scanme.nmap.org...")
#     #     resultado_scan_real = NmapGuardian.run_scan("scanme.nmap.org", "-F") # Fast scan
#     #     print("\nResultado do Scan Nmap Real:")
#     #     print(resultado_scan_real) # Mostrar o dict completo
#
#     # except FileNotFoundError:
#     #     print("\n--- Teste Nmap Real Ignorado: Nmap não encontrado ---")
#     # except Exception as e:
#     #     print(f"\n--- Erro durante o Teste Nmap Real: {e} ---")
