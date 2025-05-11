"""
Este módulo registra os Guardiões disponíveis para o framework Shamann.
Ele busca automaticamente todos os arquivos *_guardian.py, importa as classes herdadas de BaseGuardian
e registra no dicionário GUARDIANS, mapeando nomes CLI para as respectivas classes.
"""

import os
import importlib
import inspect
from pathlib import Path
from .base_guardian import BaseGuardian
from .shamann_guardian import ShamannGuardian

GUARDIAN_REGISTRY = {
    # outros guardiões...
    "shamann": ShamannGuardian,
}


# Dicionário global de guardiões registrados
GUARDIANS = {}

def load_guardians():
    """
    Carrega dinamicamente todos os guardiões disponíveis no diretório atual.
    Arquivos válidos devem terminar com _guardian.py e conter uma subclasse de BaseGuardian.
    """
    current_dir = Path(__file__).parent
    for file in os.listdir(current_dir):
        if file.endswith("_guardian.py") and file != "base_guardian.py":
            module_name = file[:-3]  # remove .py
            module_path = f"{__package__}.{module_name}"

            try:
                module = importlib.import_module(module_path)
            except Exception as e:
                print(f"[!] Erro ao importar {module_path}: {e}")
                continue

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseGuardian) and obj is not BaseGuardian:
                    try:
                        guardian_name = obj.name()
                        if guardian_name:
                            GUARDIANS[guardian_name] = obj
                            print(f"[✓] Guardião registrado: {guardian_name}")
                        else:
                            print(f"[!] Classe {name} não retornou nome válido.")
                    except Exception as e:
                        print(f"[!] Erro ao obter nome do guardião {name}: {e}")
