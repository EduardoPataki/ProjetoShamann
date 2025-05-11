# shamann/modules/__init__.py

# Inicializa o pacote shamann.modules

# Importações explícitas para os módulos guardiões.
# Isso pode ajudar o Python a encontrá-los ao importar o pacote.
try:
    from .whois_guardian import WhoisGuardian
except ImportError:
    print("Erro ao importar WhoisGuardian dentro de __init__.py")

try:
    from .nmap_guardian import NmapGuardian
except ImportError:
    print("Erro ao importar NmapGuardian dentro de __init__.py")

try:
    from .dirb_guardian import DirbGuardian  # Adicionado import para DirbGuardian
except ImportError:
    print("Erro ao importar DirbGuardian dentro de __init__.py")
