# shamann/modules/__init__.py

# Este arquivo é necessário para que Python reconheça o diretório como um pacote.
# Ele também permite importações relativas dentro deste pacote.

# Podemos usar este arquivo para facilitar a importação de módulos e classes
# dos guardiões diretamente do pacote shamann.modules.

# Por exemplo, em vez de:
# from shamann.modules.whois_guardian import WhoisGuardian
# poderíamos fazer:
# from shamann.modules import WhoisGuardian
# se adicionarmos a linha:
# from .whois_guardian import WhoisGuardian

# Importação explícita dos guardiões para facilitar o acesso
try:
    from .whois_guardian import WhoisGuardian
except ImportError:
    # O arquivo whois_guardian.py ou a classe WhoisGuardian não existe
    pass

# Tentamos importar nmap_guardian se existir no pacote atual
try:
    from .nmap_guardian import NmapGuardian
except ImportError:
    # O arquivo nmap_guardian.py ou a classe NmapGuardian não existe no pacote atual
    pass

# Você pode adicionar outras importações de guardiões aqui no futuro
# Ex: from .dirb_guardian import DirbGuardian
