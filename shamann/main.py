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
    # Mapeamento dos nomes de guardião para as classes Guardião (ou métodos estáticos se preferir)
    # Mapeando para as CLASSES por enquanto para flexibilidade (podemos instanciar se necessário)
    # No entanto, nossos métodos são estáticos, então mapear para o método diretamente é mais direto
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
        # É importante que as funções run_scan/run_query dos guardiões aceitem os argumentos que o Mestre passa
        if guardian_name.lower() == "nmap":
             # NmapGuardian.run_scan espera target e options
            result = selected_guardian_func(target=target, options=options)
        elif guardian_name.lower() == "whois":
             # Assumindo que WhoisGuardian.run_query espera apenas target
             result = selected_guardian_func(target=target) # Adapte se a função whois tiver outros args
        else:
             # Lógica para outros guardiões com argumentos diferentes
             # result = selected_guardian_func(target=target, options=options) # Exemplo padrão, adapte
             print(f"Chamada para guardião '{guardian_name}' com argumentos padrão.")
             return {"status": "error", "error_message": f"Argument mapping not defined for guardian '{guardian_name}'"}


        # TODO: Processar o resultado retornado pelo guardião (salvar, logar, apresentar)
        # print(f"Resultado recebido do {guardian_name}: {result}") # Impressão básica


        # TODO: Chamar output_manager.save_output(result, f"{target}_{guardian_name}")
        # Exemplo (requer output_manager implementado e importado de shamann.core)
        # from shamann.core import output_manager
        # if output_manager and result.get("status") != "error": # Só tenta salvar se o módulo existir e não for um resultado de erro na execução da ferramenta
        #      try:
        #          # Cuidado: target pode conter caracteres não permitidos em nome de arquivo
        #          safe_filename_target = target.replace('.', '_').replace('/', '_').replace('\\', '_')
        #          output_manager.save_output(result, f"{safe_filename_target}_{guardian_name}") # Nome do arquivo
        #          print(f"Resultado do {guardian_name} para {target} salvo.")
        #      except Exception as save_e:
        #          print(f"Erro ao salvar resultado do {guardian_name}: {save_e}")
        #          # TODO: Logar erro ao salvar
        # else:
        #      # print("Módulo output_manager não carregado ou resultado foi um erro, pulando salvamento.")
        #      pass # Não imprima nada se apenas pulou o salvamento

        return result

    except Exception as e:
        print(f"Erro ao executar o Guardião '{guardian_name}' através do Mestre: {e}")
        # TODO: Usar logging apropriado
        return {"status": "master_error", "error_message": f"Error executing guardian '{guardian_name}' via master: {e}"}


# --- Ponto de Entrada Principal ---
# Onde a aplicação começa a rodar. Typer assume o controle aqui.

if __name__ == "__main__":
    # Para rodar a aplicação com a nova estrutura, você geralmente executará
    # o módulo principal a partir da raiz do projeto:
    # python -m shamann.main <comandos_typer>

    print("Iniciando Shamann Mestre...")

    # A chamada app() no final é o que inicializa o Typer e processa os argumentos CLI.
    # Mantenha-a aqui para que o Typer funcione quando o script for executado.
    try:
        app()
    except SystemExit:
         # Typer levanta SystemExit após executar um comando ou mostrar help
         pass # É o comportamento normal, não imprima erro
    except Exception as e:
         # Captura outros erros que podem ocorrer na inicialização ou durante a execução dos comandos Typer
        print(f"Erro geral na execução da aplicação Typer: {e}")
