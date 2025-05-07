# shamann/main.py

import typer
import sys
import os
import subprocess

# Ajustar o sys.path para permitir importações do diretório raiz do projeto
# Isso é útil se o script for rodado diretamente, mas o ideal é rodar como módulo python -m shamann.main
# No entanto, para compatibilidade, podemos manter essa linha.
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
# if project_root not in sys.path:
#      sys.path.append(project_root)
# print(f"Adicionado ao PATH: {project_root}") # Para depuração


# Importações de Guardiões da nova localização
# Agora importamos do pacote 'shamann'
# Certifique-se de que as pastas shamann/modules e shamann/core
# contêm arquivos __init__.py e os módulos whois_guardian.py e nmap_guardian.py estão em shamann/modules/
try:
    from shamann.modules import whois_guardian
    # Verifique se a classe WhoisGuardian existe dentro do módulo whois_guardian
    if not hasattr(whois_guardian, 'WhoisGuardian'):
        print("Aviso: Módulo whois_guardian encontrado, mas a classe WhoisGuardian não.")
        whois_guardian = None # Desabilita o guardião se a classe não for encontrada
except ImportError:
    print("Erro: Não foi possível importar o módulo whois_guardian de shamann.modules.")
    whois_guardian = None

try:
    from shamann.modules import nmap_guardian # Importação ajustada para a nova estrutura
    # Verifique se a classe NmapGuardian existe dentro do módulo nmap_guardian
    if not hasattr(nmap_guardian, 'NmapGuardian'):
         print("Aviso: Módulo nmap_guardian encontrado, mas a classe NmapGuardian não.")
         nmap_guardian = None # Desabilita o guardião se a classe não for encontrada
except ImportError:
     print("Erro: Não foi possível importar o módulo nmap_guardian de shamann.modules.")
     nmap_guardian = None


# TODO: Importar outros Guardiões aqui conforme forem criados
# Ex: from shamann.modules import dirb_guardian

# TODO: Importar módulos de core (logger, output_manager, etc.) da nova localização
# Ex: from shamann.core import logger
# Ex: from shamann.core import output_manager

# --- Configuração do Typer (CLI) ---
# Aqui definimos a interface de linha de comando usando Typer
# Manteremos a estrutura aqui. Podemos retornar para depurar ou refinar esta parte depois.

app = typer.Typer()

# Exemplo de comando Typer para Whois
@app.command()
def whois_scan(target: str):
    """
    Executa um scan WHOIS para o target especificado.
    """
    print(f"Comando CLI recebido: whois_scan target={target}") # Depuração
    result = execute_guardian_scan("whois", target) # Chamar a função de orquestração do Mestre
    print("\nResultado do Scan WHOIS (via CLI placeholder):")
    # TODO: Formatar e apresentar o resultado de forma amigável
    print(result) # Imprime o dict completo por enquanto
    # TODO: Integrar com output_manager para salvar o resultado


# Exemplo de comando Typer para Nmap
@app.command()
def nmap_scan(target: str, options: str = typer.Option("-sV", help="Opções adicionais para o scan nmap")):
    """
    Executa um scan Nmap para o target especificado.
    """
    print(f"Comando CLI recebido: nmap_scan target={target}, options={options}") # Depuração
    # Chamaremos a função de orquestração do Mestre aqui
    result = execute_guardian_scan("nmap", target, options)
    print("\nResultado do Scan Nmap (via CLI placeholder):")
    # TODO: Formatar e apresentar o resultado de forma amigável
    print(result) # Imprime o dict completo por enquanto
    # TODO: Integrar com output_manager para salvar o resultado


# TODO: Adicionar comandos Typer para outros Guardiões aqui (ex: dirb_scan)

# --- Lógica do Mestre (Orquestração) ---
# Funções e lógica principal que coordena os Guardiões
# Geralmente chamada pelos comandos Typer ou por outros módulos

# Exemplo de como o Mestre pode chamar Guardiões (uma forma de implementar a orquestração)
def execute_guardian_scan(guardian_name: str, target: str, options: str = "") -> dict:
    """
    Executa um scan usando o Guardião especificado.

    Args:
        guardian_name: Nome do guardião a ser usado (ex: "nmap", "whois").
        target: O alvo do scan.
        options: Opções adicionais para o guardião/ferramenta.

    Returns:
        Um dicionário contendo os resultados do guardião, ou um dicionário de erro.
    """
    # Mapeamento dos nomes de guardião para os métodos estáticos de execução
    guardians_map = {
        "whois": whois_guardian.WhoisGuardian.run_query if (whois_guardian and hasattr(whois_guardian, 'WhoisGuardian') and hasattr(whois_guardian.WhoisGuardian, 'run_query')) else None,
        "nmap": nmap_guardian.NmapGuardian.run_scan if (nmap_guardian and hasattr(nmap_guardian, 'NmapGuardian') and hasattr(nmap_guardian.NmapGuardian, 'run_scan')) else None,
        # TODO: Adicionar outros guardiões aqui (ex: "dirb": dirb_guardian.DirbGuardian.run_scan)
    }

    selected_guardian_func = guardians_map.get(guardian_name.lower())

    if selected_guardian_func is None:
        print(f"Erro: Guardião '{guardian_name}' não encontrado, não implementado ou com problemas de carregamento.")
        # TODO: Usar logging apropriado
        return {"status": "error", "error_message": f"Guardian '{guardian_name}' not found or not loaded."}

    print(f"Mestre chamando Guardião: {guardian_name} para target: {target}")
    try:
        # Chamar a função do guardião com os argumentos apropriados
        if guardian_name.lower() == "nmap":
             # NmapGuardian.run_scan espera target e options
            result = selected_guardian_func(target=target, options=options)
        elif guardian_name.lower() == "whois":
             # Assumindo que WhoisGuardian.run_query espera apenas target
             result = selected_guardian_func(target=target) # Adapte se a função whois tiver outros args
        else:
             # Lógica para outros guardiões com argumentos diferentes
             print(f"Chamada para guardião '{guardian_name}' com argumentos padrão.")
             return {"status": "error", "error_message": f"Argument mapping not defined for guardian '{guardian_name}'"}


        # TODO: Processar o resultado retornado pelo guardião (salvar, logar, apresentar)
        # print(f"Resultado recebido do {guardian_name}: {result}") # Impressão básica


        # TODO: Chamar output_manager.save_output(result, f"{target}_{guardian_name}")
        # Exemplo (requer output_manager implementado e importado de shamann.core)
        # from shamann.core import output_manager
        # if output_manager and result.get("status") != "error":
        #      try:
        #          safe_filename_target = target.replace('.', '_').replace('/', '_').replace('\\', '_')
        #          output_manager.save_output(result, f"{safe_filename_target}_{guardian_name}")
        #          print(f"Resultado do {guardian_name} para {target} salvo.")
        #      except Exception as save_e:
        #          print(f"Erro ao salvar resultado do {guardian_name}: {save_e}")
        # else:
        #      pass

        return result

    except Exception as e:
        print(f"Erro ao executar o Guardião '{guardian_name}' através do Mestre: {e}")
        # TODO: Usar logging apropriado
        return {"status": "master_error", "error_message": f"Error executing guardian '{guardian_name}' via master: {e}"}


# --- Ponto de Entrada Principal ---
# Onde a aplicação começa a rodar.

# Remover prints incrementais anteriores
# print(">>> DEBUG INCREMENTAL: Chegando ao bloco if __name__ == '__main__': <<<")
# print(">>> DEBUG INCREMENTAL: Dentro do bloco __main__ <<<")
# print(">>> DEBUG INCREMENTAL: Fim do bloco __main__ <<<")
# print(">>> DEBUG INCREMENTAL: Fim do script (após __main__ se não for o ponto de entrada) <<<")

# Reintroduzir o bloco __main__ com o teste direto do Nmap
if __name__ == "__main__":
    print("Iniciando Shamann Mestre...") # Este print deve aparecer

    # --- Testes Diretos (Ativado para Depuração) ---
    # Descomente o bloco ABAIXO para testar a execução direta do Guardião Nmap.

    print("\n--- Testes Diretos (Ativado para Depuração) ---") # Este print deve aparecer
    # print("Para rodar testes CLI, comente este bloco e descomente 'app()' acima.")

    # Teste direto do Guardião Nmap (descomentado)
    print("\n--- Teste Direto: Chamando Guardião Nmap ---") # Este print deve aparecer
    if nmap_guardian:
         # Use um target de teste seguro
         nmap_test_target_direct = "scanme.nmap.org"
         nmap_test_options_direct = "-F" # Fast scan, rápido para teste
         print(f"Testando Nmap Diretamente para {nmap_test_target_direct} com opções {nmap_test_options_direct}...") # Este print deve aparecer
         try:
             # Chamar a função de orquestração execute_guardian_scan diretamente
             # Esta chamada levará à execução do NmapGuardian.run_scan
             nmap_result_direct_call = execute_guardian_scan(
                 "nmap", # Nome do guardião
                 target=nmap_test_target_direct,
                 options=nmap_test_options_direct
             )
             print("\nResultado Direto da Chamada ao Mestre (Nmap):") # Este print deve aparecer
             print(nmap_result_direct_call) # Este print deve mostrar o dicionário de resultados (com prints de debug do Guardião se ele rodar)

         except AttributeError:
              print("Erro: Função execute_guardian_scan não encontrada.") # Improvável agora
         except Exception as e:
              print(f"Erro no teste direto Nmap via Mestre: {e}")

    else:
         print("NmapGuardian não carregado para teste direto via Mestre.") # Deve aparecer se nmap_guardian for None (impr
