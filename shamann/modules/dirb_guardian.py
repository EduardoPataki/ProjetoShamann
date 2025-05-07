# shamann/modules/dirb_guardian.py

import subprocess
import sys
import json # Adicionado para lidar com a saída, embora dirb não seja json

class DirbGuardian:
    """
    Guardião responsável por interagir com a ferramenta Dirb.
    """

    @staticmethod
    def run_scan(target: str, options: str = "") -> dict:
        """
        Executa um scan Dirb para um target e retorna os resultados.
        """
        print(f"DEBUG: DirbGuardian.run_scan iniciado para {target} com opções {options}")

        # --- Lógica real de execução do Dirb ---
        # Certifique-se de que a ferramenta 'dirb' está instalada no sistema.
        # Monta o comando base: dirb <target>
        command = ["dirb", target]

        # Adiciona as opções, tratando a string como uma lista de argumentos
        if options:
            command.extend(options.split()) # Divide a string de opções em argumentos separados

        print(f"DEBUG: Executando comando Dirb: {' '.join(command)}")

        try:
            # Executa o comando Dirb CAPTURANDO a saída novamente, mas adicionando um timeout
            # O timeout impede que o script trave indefinidamente se o Dirb travar com a captura.
            # Ajuste o valor do timeout conforme necessário (em segundos).
            timeout_seconds = 300 # 5 minutos de timeout

            process = subprocess.run(command, capture_output=True, text=True, check=False, timeout=timeout_seconds) # Adicionado timeout

            stdout = process.stdout
            stderr = process.stderr
            returncode = process.returncode

            print("DEBUG: Resultado bruto do Dirb (primeiros 200 chars):", stdout[:200])
            print("DEBUG: Erro bruto do Dirb (se houver, primeiros 200 chars):", stderr[:200])


            # TODO: Implementar o parsing real da saída do Dirb aqui
            # Parsing agora é possível porque a saída é capturada novamente.
            parsed_data = {
                "target": target,
                "options": options,
                "stdout_summary": stdout.splitlines()[:10], # Primeiras 10 linhas do stdout
                "stderr_summary": stderr.splitlines()[:10], # Primeiras 10 linhas do stderr
                 # Você precisará analisar o 'stdout' para extrair os diretórios/arquivos encontrados
                "files_found_count": stdout.count('+'), # Contagem simples baseada em '+ ' nas linhas de saída
            }


            return {
                "target": target,
                "options": options,
                "command_executed": ' '.join(command),
                "stdout": stdout,
                "stderr": stderr,
                "returncode": returncode,
                "status": "completed" if returncode == 0 else "error",
                "parsed_data": parsed_data
            }

        except FileNotFoundError:
            print("Erro: O comando 'dirb' não foi encontrado. Certifique-se de que o Dirb está instalado e no PATH.")
            return {"target": target, "options": options, "command_executed": ' '.join(command), "status": "error", "error_message": "Comando Dirb não encontrado"}
        except subprocess.TimeoutExpired:
            print(f"Erro: O comando Dirb excedeu o tempo limite ({timeout_seconds} segundos). Ele pode ter travado ao capturar a saída.")
            # Tenta retornar o output capturado até o timeout, se houver
            # process.stdout e process.stderr podem estar disponíveis mesmo com TimeoutExpired
            stdout_partial = process.stdout if 'process' in locals() else None
            stderr_partial = process.stderr if 'process' in locals() else None
            return {
                "target": target, "options": options, "command_executed": ' '.join(command),
                "status": "timeout_error", "error_message": "Comando Dirb excedeu o tempo limite.",
                "stdout_partial": stdout_partial, "stderr_partial": stderr_partial
            }
        except Exception as e:
            print(f"Ocorreu um erro ao executar o Dirb: {e}")
            return {"target": target, "options": options, "command_executed": ' '.join(command), "status": "error", "error_message": str(e)}

# (Bloco __main__ comentado aqui)
# if __name__ == "__main__":
#    # Exemplo de como rodar diretamente para teste (opcional)
#    # result = DirbGuardian.run_scan("http://testphp.vulnweb.com", "-w")
#    # import json
#    # print(json.dumps(result, indent=4))
#    pass
