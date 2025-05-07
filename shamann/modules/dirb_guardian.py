# shamann/modules/dirb_guardian.py

import sys
import json
# Importar pexpect (necessita 'pip install pexpect')
try:
    import pexpect
except ImportError:
    print("Erro: A biblioteca 'pexpect' não está instalada. Por favor, instale-a usando 'pip install pexpect'")
    pexpect = None # Define pexpect como None se não puder importar

class DirbGuardian:
    """
    Guardião responsável por interagir com a ferramenta Dirb usando pexpect.
    """

    @staticmethod
    def run_scan(target: str, options: str = "") -> dict:
        """
        Executa um scan Dirb para um target usando pexpect e retorna os resultados.
        """
        print(f"DEBUG: DirbGuardian.run_scan iniciado para {target} com opções {options}")

        # Verificar se pexpect foi importado com sucesso
        if pexpect is None:
            return {"target": target, "options": options, "status": "error", "error_message": "A biblioteca 'pexpect' não está disponível."}

        # --- Lógica real de execução do Dirb usando pexpect ---
        # Certifique-se de que a ferramenta 'dirb' está instalada no sistema.
        # Monta o comando completo como uma string para pexpect.spawn
        # pexpect.spawn lida melhor com caminhos e argumentos
        command_string = f"dirb {target}"
        if options:
            command_string += f" {options}"

        print(f"DEBUG: Executando comando Dirb com pexpect: {command_string}")

        # Adicionar timeout para a execução do pexpect
        timeout_seconds = 300 # 5 minutos de timeout
        child = None # Inicializar child fora do try

        try:
            # Inicia o processo usando pexpect.spawn
            # pexpect tenta simular um TTY, o que pode resolver o problema de hang.
            # encoding='utf-8' para obter saída como string
            child = pexpect.spawn(command_string, encoding='utf-8', timeout=timeout_seconds)

            # pexpect pode interagir com o processo, mas para dirb, geralmente só precisamos ler a saída até o fim (EOF)
            # read() lê toda a saída até o final do arquivo (EOF) ou timeout
            stdout = child.read()
            stderr = "" # pexpect combina stdout e stderr por padrão, a menos que configurado de forma diferente

            # Espera pelo processo terminar e obtém o código de retorno
            child.close() # Fecha os pipes e espera o processo filho terminar
            returncode = child.exitstatus if child.exitstatus is not None else child.signalstatus

            print("DEBUG: Resultado bruto do Dirb (primeiros 200 chars):", stdout[:200])
            print("DEBUG: Erro bruto do Dirb (se houver, capturado no stdout):", stderr[:200]) # Stderr estará vazio aqui

            # TODO: Implementar o parsing real da saída do Dirb aqui
            parsed_data = {
                "target": target,
                "options": options,
                "returncode_dirb": returncode,
                "files_found_count": stdout.count('+'), # Contagem simples baseada em '+ '
                "stdout_summary": stdout.splitlines()[:10], # Primeiras 10 linhas
                # stderr_summary não disponível separadamente com pexpect.read() padrão
            }

            # Determinar o status com base no returncode (e talvez na saída)
            status = "completed"
            if returncode != 0:
                 status = "error"
                 if returncode is None: # Pode ser None se o processo foi encerrado por sinal (ex: timeout)
                     status = "terminated"


            return {
                "target": target,
                "options": options,
                "command_executed": command_string,
                "stdout": stdout, # Contém stdout e stderr combinados
                "stderr": stderr, # Vazio neste método de captura simples
                "returncode": returncode,
                "status": status,
                "parsed_data": parsed_data
            }

        except pexpect.exceptions.TIMEOUT:
            print(f"Erro: O comando Dirb excedeu o tempo limite ({timeout_seconds} segundos) com pexpect.")
            stdout_partial = ""
            if child:
                 try:
                      stdout_partial = child.before + child.buffer # Tenta pegar o que foi lido antes do timeout
                 except Exception as e_partial:
                      print(f"Aviso: Erro ao obter saída parcial de pexpect: {e_partial}")

            # Tenta matar o processo Dirb se ele ainda estiver rodando
            if child and child.isalive():
                 try:
                      child.close() # Tenta fechar normalmente
                      if child.isalive(): # Se ainda vivo
                           child.terminate() # Tenta terminar
                           if child.isalive(): # Se ainda vivo
                                child.kill() # Mata forçosamente
                 except Exception as kill_err:
                      print(f"Aviso: Erro ao tentar matar processo Dirb após timeout: {kill_err}")


            return {
                "target": target, "options": options, "command_executed": command_string,
                "status": "timeout_error", "error_message": f"Comando Dirb excedeu o tempo limite ({timeout_seconds}s) com pexpect.",
                "stdout_partial": stdout_partial, "stderr_partial": None # stderr não separado
            }
        except pexpect.exceptions.ChildNotFound:
             print("Erro: O comando 'dirb' não foi encontrado (pexpect ChildNotFound). Certifique-se de que o Dirb está instalado e no PATH.")
             return {"target": target, "options": options, "command_executed": command_string, "status": "error", "error_message": "Comando Dirb não encontrado (pexpect)"}

        except Exception as e:
            print(f"Ocorreu um erro ao executar o Dirb (via pexpect): {e}")
             # Tenta matar o processo Dirb se ele ainda estiver rodando
            if child and child.isalive():
                 try:
                      child.close() # Tenta fechar normalmente
                      if child.isalive(): # Se ainda vivo
                           child.terminate() # Tenta terminar
                           if child.isalive(): # Se ainda vivo
                                kill() # Mata forçosamente
                 except Exception as kill_err:
                      print(f"Aviso: Erro ao tentar matar processo Dirb: {kill_err}")
            return {"target": target, "options": options, "command_executed": command_string, "status": "error", "error_message": str(e)}

# (Bloco __main__ comentado aqui)
# if __name__ == "__main__":
#    # Exemplo de como rodar diretamente para teste (opcional)
#    # result = DirbGuardian.run_scan("http://testphp.vulnweb.com", "-w")
#    # import json
#    # print(json.dumps(result, indent=4))
#    pass
