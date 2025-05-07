# shamann/main.py

import typer
import sys
import os
import json # Adicionado para imprimir resultados formatados

# Adicionar a pasta raiz do projeto ao sys.path se necessário
# Isso é útil ao rodar o script diretamente (não via python -m)
# No entanto, ao rodar via 'python -m shamann.main', isso geralmente não é necessário
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if project_root not in sys.path:
     # sys.path.append(project_root) # Comentado, pois python -m deve gerenciar isso

# Tentar importar os módulos guardiões
# Se um guardião falhar ao importar, o valor correspondente na hierarquia será None
nmap_guardian = None
try:
    from shamann.modules import nmap_guardian
except ImportError as e:
    print(f"Erro: Não foi possível importar o módulo nmap_guardian. Certifique-se que está em shamann/modules/ e que __init__.py existe. Detalhes: {e}")
    # sys.exit(1) # Não sair se apenas um guardião falhar

whois_guardian = None
try:
    from shamann.modules import whois_guardian
except ImportError as e:
     # Este erro deve ter sido resolvido, mas mantemos a proteção
    print(f"Erro: Não foi possível importar o módulo whois_guardian. Certifique-se que está em shamann/modules/ e que __init__.py existe. Detalhes: {e}")
    # sys.exit(1) # Não sair se apenas um guardião falhar

# TODO: Importar outros Guardiões aqui
dirb_guardian = None # Definir como None por padrão
try:
    from shamann.modules import dirb_guardian # Importar o novo Guardião Dirb
except ImportError as e:
    print(f"Erro: Não foi possível importar o módulo dirb_guardian. Certifique-se que está em shamann/modules/ e que __init__.py existe. Detalhes: {e}")


app = typer.Typer()

# Mapeamento das tarefas/Guardiões. O Mestre usaria isso para saber qual Guardião chamar.
# Por enquanto, a CLI chama diretamente, mas a estrutura está aqui.
# A chave do dicionário é o nome da tarefa (usado internamente pelo Mestre).
# O valor é a função run_scan/run_query do Guardião correspondente,
# ou None se o Guardião não pôde ser importado.
guardians_map = {
    # Verifica se o módulo importou E se a classe/função esperada existe nele
    "nmap": nmap_guardian.NmapGuardian.run_scan if (nmap_guardian and hasattr(nmap_guardian, 'NmapGuardian') and hasattr(nmap_guardian.NmapGuardian, 'run_scan')) else None,
    "whois": whois_guardian.WhoisGuardian.run_query if (whois_guardian and hasattr(whois_guardian, 'WhoisGuardian') and hasattr(whois_guardian.WhoisGuardian, 'run_query')) else None,
    # TODO: Adicionar outros Guardiões ao mapa aqui
    "dirb": dirb_guardian.DirbGuardian.run_scan if (dirb_guardian and hasattr(dirb_guardian, 'DirbGuardian') and hasattr(dirb_guardian.DirbGuardian, 'run_scan')) else None, # Adicionado Dirb
}

def execute_guardian_scan(guardian_name: str, target: str, options: str = ""):
    """
    Função interna que simula o Mestre chamando o Guardião apropriado.
    """
    guardian_function = guardians_map.get(guardian_name)

    if guardian_function is None:
        # Verifica qual guardião específico falhou a importação ou não existe
        if guardian_name == "nmap" and nmap_guardian is None:
             print(f"NmapGuardian não disponível. Não foi possível executar o scan Nmap.")
        elif guardian_name == "whois" and whois_guardian is None:
             print(f"WhoisGuardian não disponível. Não foi possível executar o scan WHOIS.")
        # TODO: Adicionar checks para outros Guardiões aqui
        elif guardian_name == "dirb" and dirb_guardian is None: # Adicionado check para Dirb
             print(f"DirbGuardian não disponível. Não foi possível executar o scan Dirb.")
        else:
             print(f"Guardião desconhecido ou indisponível: {guardian_name}")
             print("Verifique se o módulo do Guardião foi importado corretamente e se a função 'run_scan' (ou equivalente) existe.")
        return None # Retorna None ou um dicionário de erro padrão

    print(f"Mestre chamando Guardião: {guardian_name} para target: {target}{' com opções: ' + options if options else ''}")

    try:
        # Executa a função do Guardião. Assume que a assinatura é target, options (nem sempre)
        # Precisaremos refinar isso para Guardiões com assinaturas diferentes.
        if guardian_name == "whois":
             result = guardian_function(target=target) # WHOIS não usa options na run_query simulada
        else:
             result = guardian_function(target=target, options=options) # Nmap, Dirb usam target e options


        print("\nResultado do Scan:") # Título genérico para a saída do Guardião
        # Usa json.dumps para imprimir dicionários de forma mais legível
        print(json.dumps(result, indent=4, default=str)) # default=str para lidar com datetime no WHOIS

        return result # Retorna o resultado do Guardião

    except Exception as e:
        print(f"Ocorreu um erro durante a execução do Guardião {guardian_name}: {e}")
        # Retorna um dicionário de erro consistente
        return {"target": target, "guardian": guardian_name, "status": "execution_error", "error_message": str(e)}


@app.command()
def nmap_scan(target: str, options: str = typer.Option("", "-o", help="Opções adicionais para o Nmap, entre aspas duplas. Ex: \"-sV -p-\"")):
    """
    Executa um scan Nmap em um target.
    """
    print(f"Comando CLI recebido: nmap_scan target={target}, options={options}")
    execute_guardian_scan("nmap", target, options)


@app.command()
def whois_scan(target: str):
    """
    Executa uma consulta WHOIS para um target.
    """
    print(f"Comando CLI recebido: whois_scan target={target}")
    execute_guardian_scan("whois", target) # WHOIS não precisa de options na CLI


# TODO: Adicionar comandos para outros Guardiões aqui
@app.command() # Novo comando para o Dirb
def dirb_scan(target: str, options: str = typer.Option("", "-o", help="Opções adicionais para o Dirb, entre aspas duplas. Ex: \"-X .php,.html\"")):
    """
    Executa um scan Dirb em um target (URL).
    """
    print(f"Comando CLI recebido: dirb_scan target={target}, options={options}")
    execute_guardian_scan("dirb", target, options)


if __name__ == "__main__":
    # Este é o ponto de entrada quando rodamos o script diretamente
    # A função app() do Typer analisa os argumentos da linha de comando
    # e chama a função @app.command apropriada.
    # print("DEBUG: Executando main.py") # Debugging inicial
    app()
