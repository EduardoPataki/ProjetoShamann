# shamann/modules/guardian_registry.py

# Importe as classes de Guardiões.
# Note: Você importou NmapGuardian duas vezes na versão que enviou, removi a duplicação.
from .nmap_guardian import NmapGuardian
from .dirb_guardian import DirbGuardian
from .dirfuzz_guardian import DirFuzzGuardian
from .dns_guardian import DNSGuardian
from .whois_guardian import WhoisGuardian
from .shamann_guardian import ShamannGuardian # Assumindo que este é o componente de alertas/decisão
from .example_guardian import ExampleGuardian

# Lista central de guardiões registrados:
# Formato: (nome, classe, ativo?)
GUARDIAN_CLASSES = [
    ("nmap", NmapGuardian, True),
    ("dirb", DirbGuardian, True),
    ("dirfuzz", DirFuzzGuardian, True),
    ("dns", DNSGuardian, True),
    ("whois", WhoisGuardian, True),
    ("shamann", ShamannGuardian, True),  # Ativado por padrão (componente de alerta/decisão?)
    ("example", ExampleGuardian, False), # Exemplo desativado
]

# --- ADIÇÃO: Crie o dicionário GUARDIANS para acesso direto por nome ---
# Este dicionário incluirá apenas os guardiões marcados como ativos em GUARDIAN_CLASSES
# O Mestre e outros módulos podem usar este dicionário para obter a classe de um Guardião pelo seu nome.
GUARDIANS = {name: cls for name, cls, active in GUARDIAN_CLASSES if active}

# --- Opcional: Se precisar de um dicionário com TODOS os guardiões (ativos ou não)
# ALL_GUARDIANS_DICT = {name: cls for name, cls, active in GUARDIAN_CLASSES}

# --- Funções que você já tinha (nomes ajustados para maior clareza) ---

def get_active_guardian_classes(): # Nome ajustado para maior clareza
    """
    Retorna uma lista das classes de guardiões ativos.
    """
    return [cls for name, cls, active in GUARDIAN_CLASSES if active]


def get_all_guardian_info(): # Nome ajustado para maior clareza
    """
    Retorna uma lista de dicionários com informações (nome, classe, ativo) de todos os guardiões.
    """
    return [
        {
            "name": name,
            "class": cls,
            "active": active
        }
        for name, cls, active in GUARDIAN_CLASSES
    ]


def get_guardian_by_name(name: str):
    """
    Retorna a classe de um guardião ATIVO pelo nome usando o dicionário GUARDIANS.
    Retorna None se o guardião não for encontrado ou não estiver ativo.
    """
    # Use o dicionário GUARDIANS criado acima para uma busca eficiente apenas entre os ativos.
    return GUARDIANS.get(name)

# Note: A importação 'from ... import load_guardians' no seu main.py não corresponde a nenhuma função aqui.
# Se a função load_guardians não existe ou não é necessária neste arquivo, você deve removê-la do import no main.py.
# Se load_guardians era para popular o dicionário GUARDIANS, a adição acima já faz isso de forma estática.
