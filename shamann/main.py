# shamann/main.py

import typer
import sys
import os
import subprocess

# Ajustar o sys.path (manter comentado - python -m cuida disso)
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
# if project_root not in sys.path:
#      sys.path.append(project_root)

# Importações de Guardiões da nova localização
try:
    from shamann.modules import whois_guardian
except ImportError:
    print("Erro: Não foi possível importar o módulo whois_guardian. Certifique-se que está em shamann/modules/ e que __init__.py existe.")
    whois_guardian = None

try:
    from shamann.modules import nmap_guardian
except ImportError:
     print("Erro: Não foi possível importar o módulo nmap_guardian. Certifique-se que está em shamann/modules/ e que __init__.py existe.")
     nmap_guardian = None

# TODO: Importar outros Guardiões

# TODO: Importar módulos de core

# --- Configuração do Typer (CLI) ---
app = typer.Typer()

# Exemplo de comando Typer para Whois
@app.command()
def whois_scan(target: str):
    """
    Executa um scan WHOIS para o target especificado.
    """
    print(f"Comando CLI recebido: whois_scan target={target}")
    # Chamar a função de orquestração do Mestre
    # Verificar se o guardião foi importado com sucesso antes de chamar
    if whois_guardian and hasattr(whois_guardian, 'WhoisGuardian') and hasattr(whois_guardian.WhoisGuardian, 'run_query'):
         result = execute_guardian_scan("whois", target)
         print("\nResultado do Scan WHOIS:")
         print(result)
         # TODO: Integrar com output_manager para salvar o resultado
    else:
         print("WhoisGuardian não disponível. Não foi possível executar o scan WHOIS.")


# Exemplo de comando Typer para Nmap
@app.command()
def nmap_scan(target: str, options: str = typer.Option("-sV", help="Opções adicionais para o scan nmap")):
    """
    Executa um scan Nmap para o target especificado.
    """
    print(f"Comando CLI recebido: nmap_scan target={target}, options={options}")
    # Chamar a função de orquestração do Mestre
    # Verificar se o guardião foi importado com sucesso antes de chamar
    if nmap_guardian and hasattr(nmap_guardian, 'NmapGuardian') and hasattr(nmap_guardian.NmapGuardian, 'run_scan'):
        result = execute_guardian_scan("nmap", target, options)
        print("\nResultado do Scan Nmap:")
        print(result)
        # TODO: Integrar com output_manager para salvar o resultado
    else:
         print("NmapGuardian não disponível. Não foi possível executar o scan Nmap.")


# TODO: Adicionar comandos Typer para outros Guardiões

# --- Lógica do Mestre (Orquestração) ---
def execute_guardian_scan(guardian_name: str, target: str, options: str = "") -> dict:
    """
    Executa um scan usando o Guardião especificado.
    """
    # Mapeamento dos nomes de guardião para os métodos estáticos de execução
    guardians_map = {
        "whois": whois_guardian.WhoisGuardian.run_query if (whois_guardian and hasattr(whois_guardian, 'WhoisGuardian') and hasattr(whois_guardian.WhoisGuardian, 'run_query')) else None,
        "nmap": nmap_guardian.NmapGuardian.run_scan if (nmap_guardian and hasattr(nmap_guardian, 'NmapGuardian') and hasattr(nmap_guardian.NmapGuardian, 'run_scan')) else None,
        # TODO: Adicionar outros guardiões
    }

    selected_guardian_func = guardians_map.get(guardian_name.lower())

    if selected_guardian_func is None:
        print(f"Erro: Guardião '{guardian_name}' não encontrado, não implementado ou com problemas de carregamento.")
        return {"status": "error", "error_message": f"Guardian '{guardian_name}' not found or not loaded."}

    print(f"Mestre chamando Guardião: {guardian_name} para target: {target}")
    try:
        if guardian_name.lower() == "nmap":
             result = selected_guardian_func(target=target, options=options)
        elif guardian_name.lower() == "whois":
             result = selected_guardian_func(target=target)
        else:
             print(f"Chamada para guardião '{guardian_name}' com argumentos padrão.")
             return {"status": "error", "error_message": f"Argument mapping not defined for guardian '{guardian_name}'"}

        return result

    except Exception as e:
        print(f"Erro ao executar o Guardião '{guardian_name}' através do Mestre: {e}")
        return {"status": "master_error", "error_message": f"Error executing guardian '{guardian_name}' via master: {e}"}


# --- Ponto de Entrada Principal ---
# Onde a aplicação começa a rodar. Typer assume o controle aqui.

if __name__ == "__main__":
    # Remova ou comente o bloco de testes diretos
    # print("Iniciando Shamann Mestre...")
    # print("\n--- Testes Diretos (Ativado para Depuração) ---")
    # print("\n--- Teste Direto: Chamando Guardião Nmap ---")
    # if nmap_guardian: ... else: ...

    # --- Habilitar Typer CLI ---
    # Esta linha passa o controle para o Typer, que analisará os argumentos da linha de comando
    app()
