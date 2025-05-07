# test_whois_import.py

import sys
import os

# Adicionar a pasta raiz do projeto ao sys.path
# Isso é necessário para que o Python encontre o pacote 'shamann'
# quando rodamos o script fora da estrutura do pacote (sem 'python -m')
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

print(f"DEBUG: sys.path inclui: {sys.path}")
print("Tentando importar shamann.modules.whois_guardian...")

try:
    # Tentar importar o módulo WhoisGuardian
    from shamann.modules import whois_guardian
    print("Importação bem-sucedida!")
    print(f"Módulo whois_guardian importado: {whois_guardian}")

    # Verificar se a classe WhoisGuardian existe no módulo
    if hasattr(whois_guardian, 'WhoisGuardian'):
        print("Classe WhoisGuardian encontrada no módulo.")
    else:
        print("Classe WhoisGuardian NÃO encontrada no módulo.")

except ImportError as e:
    print(f"ImportError: Falha ao importar shamann.modules.whois_guardian")
    print(f"Detalhes do erro: {e}")
    print("Verifique o caminho do arquivo, o arquivo __init__.py e o nome do módulo.")
except Exception as e:
    print(f"Ocorreu um erro inesperado durante a importação:")
    print(f"Tipo do erro: {type(e).__name__}")
    print(f"Detalhes do erro: {e}")
