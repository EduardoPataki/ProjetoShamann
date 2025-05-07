# shamann/main.py

# --- Adicionando de Volta Imports e Bloco __main__ ---

import sys
import os
import subprocess # Necessário para o NmapGuardian, mesmo que não seja chamado diretamente aqui
import typer # Importar Typer, mas não inicializaremos ainda

print(">>> DEBUG INCREMENTAL: Início do script <<<") # Deve imprimir no começo

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

print(">>> DEBUG INCREMENTAL: Tentando importar Guardiões e Core <<<") # Deve imprimir antes das imports

try:
    # Importação do módulo core.__init__ para teste
    # Certifique-se que shamann/core/__init__.py existe
    from shamann.core import __init__ as core_init_test
    print(">>> DEBUG INCREMENTAL: Import shamann.core.__init__ successful <<<") # Deve imprimir se importar
except ImportError as e:
    print(f">>> DEBUG INCREMENTAL: Import shamann.core.__init__ failed: {e} <<<") # Deve imprimir se falhar


try:
    from shamann.modules import whois_guardian
    print(">>> DEBUG INCREMENTAL: Import whois_guardian successful <<<") # Deve imprimir se importar
    # Verifique se a classe WhoisGuardian existe dentro do módulo whois_guardian
    if not hasattr(whois_guardian, 'WhoisGuardian'):
        print(">>> DEBUG INCREMENTAL: Aviso: Classe WhoisGuardian NÃO encontrada no módulo. <<<") # Deve imprimir se o módulo importar mas a classe não existir
        whois_guardian = None # Desabilita o guardião se a classe não for encontrada
    else:
        print(">>> DEBUG INCREMENTAL: Classe WhoisGuardian encontrada. <<<") # Deve imprimir se a classe for encontrada
except ImportError as e:
    print(f">>> DEBUG INCREMENTAL: Import whois_guardian failed: {e} <<<") # Deve imprimir se a importação falhar
    whois_guardian = None


try:
    from shamann.modules import nmap_guardian # Importação ajustada para a nova estrutura
    print(">>> DEBUG INCREMENTAL: Import nmap_guardian successful <<<") # Deve imprimir se importar
    # Verifique se a classe NmapGuardian existe dentro do módulo nmap_guardian
    if not hasattr(nmap_guardian, 'NmapGuardian'):
         print(">>> DEBUG INCREMENTAL: Aviso: Classe NmapGuardian NÃO encontrada no módulo. <<<") # Deve imprimir se o módulo importar mas a classe não existir
         nmap_guardian = None # Desabilita o guardião se a classe não for encontrada
    else:
        print(">>> DEBUG INCREMENTAL: Classe NmapGuardian encontrada. <<<") # Deve imprimir se a classe for encontrada
except ImportError as e:
     print(f">>> DEBUG INCREMENTAL: Import nmap_guardian failed: {e} <<<") # Deve imprimir se a importação falhar
     nmap_guardian = None

print(">>> DEBUG INCREMENTAL: Importações de Guardiões e Core tentadas <<<") # Deve imprimir após as imports


# TODO: Importar outros Guardiões aqui conforme forem criados
# Ex: from shamann.modules import dirb_guardian

# TODO: Importar módulos de core (logger, output_manager, etc.) da nova localização
# Ex: from shamann.core import logger
# Ex: from shamann.core import output_manager

# --- Configuração do Typer (CLI) ---
# Manter a estrutura Typer, mas não inicializá-la no __main__ ainda
# app = typer.Typer() # Inicializaremos depois
# @app.command()... # Manter comandos comentados ou ignorados por enquanto


# --- Lógica do Mestre (Orquestração) ---
# Manter as funções de orquestração, mas não chamá-las ainda
# def execute_guardian_scan(...): ...


# --- Ponto de Entrada Principal ---
# Onde a aplicação começa a rodar.

print(">>> DEBUG INCREMENTAL: Chegando ao bloco if __name__ == '__main__': <<<") # Deve imprimir antes do __main__

if __name__ == "__main__":
    print(">>> DEBUG INCREMENTAL: Dentro do bloco __main__ <<<") # Este print deve aparecer se o script é o ponto de entrada
    # TODO: Aqui é onde o Typer.run() ou app() será chamado eventualmente.
    # Mantenha esta parte simples por enquanto.
    print(">>> DEBUG INCREMENTAL: Fim do bloco __main__ <<<") # Deve imprimir se o __main__ executar até o fim

print(">>> DEBUG INCREMENTAL: Fim do script (após __main__ se não for o ponto de entrada) <<<") # Este print deve aparecer se o script for importado (não executado diretamente). Em execução direta, __main__ rodará antes disso.
