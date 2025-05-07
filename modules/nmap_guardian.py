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

        # --- Prints de depuração solicitados ---
        print(f"DEBUG: NmapGuardian.run_scan iniciado para {target} com opções {options}")
        # ----------------------------------------

        print(f"Iniciando scan Nmap em {target} com opções: {options}") # Print existente, pode ser removido/alterado depois


        # Construir o comando nmap. Usar lista de argumentos é mais seguro (evita shell=True).
        # Dividimos as opções em uma lista para passar corretamente ao subprocess.
        command = ["nmap"] # Começa com o nome do comando
        # Adiciona as opções, dividindo a string por espaços. Cuidado com opções com espaços internos.
        if options:
            command.extend(options.split())
        command.append(target)

        # Opcional: Adicionar a opção -oX - para saída XML que pode ser mais fácil de parsear
        # command.extend(["-oX", "-"])

        # --- Prints de depuração solicitados ---
        print(f"DEBUG: Executando comando Nmap: {' '.join(command)}")
        # ----------------------------------------

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True, stderr=subprocess.PIPE)

            # Processar a saída bruta
            raw_output = result.stdout
            raw_error = result.stderr

            # --- Prints de depuração solicitados ---
            # Mostrar apenas os primeiros 200 caracteres para evitar poluir muito o terminal
            print(f"DEBUG: Resultado bruto do Nmap (primeiros 200 chars): {raw_output[:200]}...")
            # ----------------------------------------

            # Chamar a função interna para parsear a saída bruta
            parsed_data = NmapGuardian._parse_nmap_output(raw_output)

            # Retornar os resultados completos
            return {
                "target": target,
                "options": options,
                "command_executed": " ".join(command),
                "stdout": raw_output,
                "stderr": raw_error,
                "returncode": result.returncode,
                "status": "completed",
                "parsed_data": parsed_data
            }

        except FileNotFoundError:
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
        # --- Prints de depuração podem ser adicionados aqui também se necessário ---
        # print("DEBUG: _parse_nmap_output iniciado...")
        # print(f"DEBUG: Input para parsing (primeiros 200 chars): {raw_output[:200]}...")
        # --------------------------------------------------------------------------
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

        port_section_started = False
        for line in lines:
            line = line.strip()
            if line.startswith("PORT"):
                port_section_started = True
                continue

            if port_section_started and line:
                parts = line.split(maxsplit=3)

                if len(parts) >= 3:
                    port_info = {
                        "port_id": parts[0],
                        "state": parts[1],
                        "service": parts[2],
                        "version": parts[3] if len(parts) > 3 else ""
                    }
                    if port_info["state"] in ["open", "filtered", "closed"]:
                         parsed_data["ports"].append(port_info)

            if line.startswith("Nmap scan report for"):
                 if " for " in line and "(" in line and ")" in line:
                      parts = line.split(" for ", 1)
                      if len(parts) > 1:
                           host_part = parts[1].strip()
                           if "(" in host_part and host_part.endswith(")"):
                                hostname = host_part.split(" (")[0]
                                ip_address = host_part.split(" (")[1].strip(")")
                                parsed_data["host"] = {"hostname": hostname, "ip_address": ip_address}
                           else:
                                parsed_data["host"] = {"hostname": host_part, "ip_address": None}
                 elif "(" in line and line.endswith(")"):
                      ip_address = line.split("(")[1].strip(")")
                      parsed_data["host"] = {"hostname": None, "ip_address": ip_address}

        # --- Prints de depuração podem ser adicionados aqui também se necessário ---
        # print(f"DEBUG: _parse_nmap_output finished. Parsed data (brief): {list(parsed_data.keys())}")
        # --------------------------------------------------------------------------

        return parsed_data

# (Bloco __main__ comentado aqui, pois ele será chamado do main.py)
# if __name__ == "__main__":
#    pass
