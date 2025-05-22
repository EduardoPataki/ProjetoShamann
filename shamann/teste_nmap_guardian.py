# arquivo: teste_nmap_guardian.py

from shamann.modules.guardian_registry import GUARDIANS

if __name__ == "__main__":
    nmap = GUARDIANS["nmap"]
    resultado = nmap.run_scan("scanme.nmap.org")
    print(resultado)
