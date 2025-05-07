# shamann/modules/dirb_guardian.py

import subprocess
import sys
import os
import json

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

        # Usar Popen e communicate para ter mais controle sobre pipes,
        # pode ajudar a evitar o travamento com capture_output=True
        process = None # Inicializar process fora do try

        try:
            # Inicia o processo usando Popen
            # stdout=subprocess.PIPE e stderr=subprocess.PIPE para capturar as saídas
            # text=True (ou encoding='utf-8') para que communicate retorne strings
            # bufsize=1 pode ajudar com buffering, mas nem sempre necessário
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Comunica com o processo: envia None para stdin, lê stdout e stderr
            # communicate() espera o processo terminar.
            # Adicionar timeout também aqui para evitar travamento indefinido
            timeout_seconds = 300 # 5 minutos de timeout
            stdout, stderr = process.communicate(timeout=timeout_seconds)

            returncode = process.returncode

            print("DEBUG: Resultado bruto do Dirb (primeiros 200 chars):", stdout[:200])
            print("DEBUG: Erro bruto do Dirb (se houver, primeiros 200 chars):", stderr[:200])


            # TODO: Implementar o parsing real da saída do Dirb aqui
            parsed_data = {
                "target": target,
                "options": options,
                "returncode_dirb": returncode,
                "files_found_count": stdout.count('+'), # Contagem simples baseada em '+ '
                "stdout_summary": stdout.splitlines()[:10], # Primeiras 10 linhas
                "stderr_summary": stderr.splitlines()[:10], # Primeiras 10 linhas
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
            print(f"Erro: O comando Dirb excedeu o tempo limite ({timeout_seconds} segundos) durante a comunicação.")
            # Tenta obter o output que pode ter sido capturado até o timeout
            stdout_partial, stderr_partial = None, None
            if process:
                try:
                    # communicate() já tentou ler, mas pode haver saída em buffer
                    # Tenta obter qualquer output que ainda possa estar nos pipes
                    stdout_partial = process.stdout.read() if process.stdout else None
                    stderr_partial = process.stderr.read() if process.stderr else None
                except Exception as comm_err:
                     print(f"Aviso: Erro ao obter saída após timeout: {comm_err}")
                finally:
                     # Garante que o processo é encerrado se ainda estiver rodando
                     if process and process.poll() is None:
                         try:
                             process.kill()
                         except Exception as kill_err:
                             print(f"Aviso: Erro ao matar processo Dirb: {kill_err}")


            return {
                "target": target, "options": options, "command_executed": ' '.join(command),
                "status": "timeout_error", "error_message": f"Comando Dirb excedeu o tempo limite ({timeout_seconds}s).",
                "stdout_partial": stdout_partial, "stderr_partial": stderr_partial
            }
        except Exception as e:
            print(f"Ocorreu um erro ao executar o Dirb (via Popen/communicate): {e}")
            # Mata o processo se ele foi iniciado e ainda está rodando
            if process and process.poll() is None:
                 try:
                     process.kill()
                 except Exception as kill_err:
                     print(f"Aviso: Erro ao matar processo Dirb: {kill_err}")

            return {"target": target, "options": options, "command_executed": ' '.join(command), "status": "error", "error_message": str(e)}


# (Bloco __main__ comentado aqui)
# if __name__ == "__main__":
#    # Exemplo de como rodar diretamente para teste (opcional)
#    # result = DirbGuardian.run_scan("http://testphp.vulnweb.com", "-w")
#    # import json
#    # print(json.dumps(result, indent=4))
#    pass
