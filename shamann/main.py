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
     pass # Explicitamente não fazer nada se o caminho não for adicionado

# Tentar importar os módulos guardiões
# Se um guardião falhar ao importar, o valor correspondente na hierarquia será None

try:
    from shamann.modules import nmap_guardian
except ImportError as e:
    print(f"Erro: Não foi possível importar o módulo nmap_guardian. Certifique-se que está em shamann/modules/ e que __init__.py existe. Detalhes: {e}")
    nmap_guardian = None # Atribuir None aqui se a importação falhar


try:
    from shamann.modules import whois_guardian
except ImportError as e:
     # Este erro deve ter sido resolvido, mas mantemos a proteção
    print(f"Erro: Não foi possível importar o módulo whois_guardian. Certifique-se que está em shamann/modules/ e que __init__.py existe. Detalhes: {e}")
    whois_guardian = None # Atribuir None aqui se a importação falhar


# TODO: Importar outros Guardiões aqui
try:
    from shamann.modules import dirb_guardian # Importar o novo Guardião Dirb
except ImportError as e:
    print(f"Erro: Não foi possível importar o módulo dirb_guardian. Certifique-se que está em shamann/modules/ e que __init__.py existe. Detalhes: {e}")
    dirb_guardian = None # Atribuir None aqui se a importação falhar


app = typer.Typer()

# Mapeamento das tarefas/Guardiões. O Mestre usaria isso para saber qual Guardião chamar.
# Por enquanto, a CLI chama diretamente, mas a estrutura está aqui.
# A chave do dicionário é o nome da tarefa (usado internamente pelo Mestre).
# O valor é a função run_scan/run_query do Guardião correspondente,
# ou None se o Guardião não pôde ser importado.
guardians_map = {
    # Verifica se o módulo importou E se a classe/função esperada existe nele
    # Acesso seguro usando getattr e operador ternário
    "nmap": getattr(nmap_guardian, 'NmapGuardian', None) and getattr(nmap_guardian.NmapGuardian, 'run_scan', None),
    "whois": getattr(whois_guardian, 'WhoisGuardian', None) and getattr(whois_guardian.WhoisGuardian, 'run_query', None),
    # TODO: Adicionar outros Guardiões ao mapa aqui
    "dirb": getattr(dirb_guardian, 'DirbGuardian', None) and getattr(dirb_guardian.DirbGuardian, 'run_scan', None), # Adicionado Dirb
}

def execute_guardian_scan(guardian_name: str, target: str, options: str = ""):
    """
    Função interna que simula o Mestre chamando o Guardião apropriado.
    """
    guardian_function = guardians_map.get(guardian_name)

    if guardian_function is None:
        # Verifica qual guardião específico falhou a importação ou não existe
        # Melhorar a verificação para ser mais genérica se possível
        if guardian_name == "nmap" and nmap_guardian is None:
             print(f"NmapGuardian não disponível (erro de importação). Não foi possível executar o scan Nmap.")
        elif guardian_name == "whois" and whois_guardian is None:
             print(f"WhoisGuardian não disponível (erro de importação). Não foi possível executar o scan WHOIS.")
        # TODO: Adicionar checks para outros Guardiões aqui
        elif guardian_name == "dirb" and dirb_guardian is None: # Adicionado check para Dirb
             print(f"DirbGuardian não disponível (erro de importação). Não foi possível executar o scan Dirb.")
        # Verifica se o módulo importou mas a classe/função esperada não foi encontrada
        elif guardian_name == "nmap" and not getattr(nmap_guardian, 'NmapGuardian', None):
             print(f"NmapGuardian indisponível (Classe NmapGuardian ou função run_scan não encontrada).")
        elif guardian_name == "whois" and not getattr(whois_guardian, 'WhoisGuardian', None):
             print(f"WhoisGuardian indisponível (Classe WhoisGuardian ou função run_query não encontrada).")
        elif guardian_name == "dirb" and not getattr(dirb_guardian, 'DirbGuardian', None):
             print(f"DirbGuardian indisponível (Classe DirbGuardian ou função run_scan não encontrada).")
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
