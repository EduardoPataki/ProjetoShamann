# shamann/modules/dirb_guardian.py

import subprocess
import sys

# Note: json import is not needed if not parsing/formatting output here

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
            # Executa o comando Dirb SEM capturar a saída.
            # A saída do Dirb aparecerá diretamente no terminal.
            # check=False para não levantar exceção em erro
            # text=True (ou encoding='utf-8') ainda útil para subprocess
            process = subprocess.run(command, check=False, text=True) # Removido capture_output=True

            # stdout e stderr serão None aqui, pois não foram capturados.
            # Podemos imprimir uma mensagem indicando isso.
            print("\nDEBUG: Saída do Dirb apareceu diretamente no terminal (capture_output=False).")

            returncode = process.returncode

            # TODO: Implementar o parsing real da saída do Dirb aqui
            # Parsing da saída *não é possível* neste modo, pois não capturamos.
            # Retornamos um dicionário básico indicando que rodou.
            parsed_data = {
                "target": target,
                "options": options,
                "note": "Saída bruta do Dirb não capturada neste modo de teste.",
                "returncode_dirb": returncode,
            }


            return {
                "target": target,
                "options": options,
                "command_executed": ' '.join(command),
                "stdout": None, # Não capturado
                "stderr": None, # Não capturado
                "returncode": returncode,
                "status": "completed" if returncode == 0 else "error",
                "parsed_data": parsed_data
            }

        except FileNotFoundError:
            print("Erro: O comando 'dirb' não foi encontrado. Certifique-se de que o Dirb está instalado e no PATH.")
            return {"target": target, "options": options, "command_executed": ' '.join(command), "status": "error", "error_message": "Comando Dirb não encontrado"}
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
