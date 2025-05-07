# shamann/modules/__init__.py

# Initialize the shamann.modules package

# Importações explícitas para os módulos guardiões.
# Isso pode ajudar o Python a encontrá-los ao importar o pacote.
try:
    from . import whois_guardian
except ImportError:
    print("Erro ao importar whois_guardian dentro de __init__.py")

try:
    from . import nmap_guardian
except ImportError:
    print("Erro ao importar nmap_guardian dentro de __init__.py")

# TODO: Adicionar importações explícitas para outros guardiões aqui
# try:
#     from . import other_guardian
# except ImportError:
#     print("Erro ao importar other_guardian dentro de __init__.py")
