# modules/nmap_guardian.py

import subprocess # Para executar comandos externos (Nmap)
# Precisaremos de logging, vamos importar ou usar um logger centralizado depois
# from core.logger import get_logger

# logger = get_logger(__name__)

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
            Um dicionário contendo os resultados brutos ou básicos do scan.
            Eventualmente, retornará dados parseados e estruturados.
        """
        # TODO: Implementar o parsing da saída do nmap em _parse_nmap_output
        # TODO: Usar logging apropriado em vez de print para erros/info

        print(f"Iniciando scan Nmap em {target} com opções: {options}") # Logging básico por enquanto

        # Construir o comando nmap. Usar lista de argumentos é mais seguro (evita shell=True).
        # Dividimos as opções em uma lista para passar corretamente ao subprocess.
        command = ["nmap"] # Começa com o nome do comando
        # Adiciona as opções, dividindo a string por espaços. Cuidado com opções com espaços internos.
        # Para opções com espaços (ex: --script "script args"), seria necessário um parsing mais sofisticado.
        # Por enquanto, assumimos opções separadas por espaço.
        if options:
            command.extend(options.split())
        command.append(target) # Adiciona o target no final


        try:
            # Executar o comando nmap
            # capture_output=True captura stdout e stderr
            # text=True decodifica stdout/stderr como texto usando encoding padrão
            # check=True levanta CalledProcessError se o comando retornar código de erro não zero
            result = subprocess.run(command, capture_output=True, text=True, check=True)

            # Retornar a saída bruta e informações básicas por enquanto.
            # O parsing detalhado virá depois.
            return {
                "target": target,
                "options": options,
                "command_executed": " ".join(command), # Salva o comando completo executado para referência
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "status": "completed",
                "parsed_data": {} # Placeholder para os dados parseados
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
            print(f"Erro ao executar Nmap (Código de Retorno {e.returncode}):\n{e.stderr}")
            # TODO: Usar logging.error aqui
            return {
                "target": target,
                "options": options,
                "command_executed": " ".join(command),
                "status": "error",
                "error_type": "CalledProcessError",
                "returncode": e.returncode,
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error_message": "Nmap command failed during execution."
            }
        except Exception as e:
            # Captura quaisquer outros erros inesperados
            print(f"Ocorreu um erro inesperado ao executar Nmap: {e}")
            # TODO: Usar logging.error aqui
            return {
                "target": target,
                "options": options,
                "command_executed": " ".join(command),
                "status": "error",
                "error_type": "UnexpectedError",
                "error_message": str(e)
            }

# Exemplo de como pode ser chamado (isso ficará no script Mestre, shamann.py)
# if __name__ == "__main__":
#     # Certifique-se de ter o Nmap instalado para testar!
#     # Use um target seguro como scanme.nmap.org para testes legítimos.
#     # Não escaneie redes sem permissão!
#     print("--- Teste Básico Whois ---")
#     # Supondo que whois_guardian.py tem uma classe WhoisGuardian com run_query
#     # from modules.whois_guardian import WhoisGuardian
#     # resultado_whois = WhoisGuardian.run_query("example.com")
#     # print(resultado_whois)

#     print("\n--- Teste Básico Nmap ---")
#     # Use um target de teste legítimo e simples
#     target_teste_nmap = "scanme.nmap.org"
#     opcoes_teste_nmap = "-F" # Fast scan - mais rápido para teste
#     # ou opcoes_teste_nmap = "-p 80,443" # Portas específicas
#     # ou opcoes_teste_nmap = "-sV" # Service version detection (pode demorar um pouco)

#     # Verifique se o Nmap está instalado antes de rodar este teste
#     try:
#         subprocess.run(["nmap", "--version"], check=True, capture_output=True)
#         print(f"Nmap encontrado. Rodando scan de teste em {target_teste_nmap}...")
#         resultado_teste_nmap = NmapGuardian.run_scan(target_teste_nmap, opcoes_teste_nmap)
#         print("\nResultado Bruto do Nmap:")
#         print(resultado_teste_nmap.get("stdout", "N/A"))
#         if resultado_teste_nmap.get("stderr"):
#              print("\nErro (stderr):")
#              print(resultado_teste_nmap["stderr"])
#         print("\nResumo do Resultado (dict):")
#         print(resultado_teste_nmap)

#     except FileNotFoundError:
#         print("\n--- Teste Nmap Ignorado: Nmap não encontrado ---")
#     except Exception as e:
#          print(f"\n--- Erro durante o Teste Nmap: {e} ---")
