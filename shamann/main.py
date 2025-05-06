# shamann/main.py

import argparse
from shamann.modules.whois_guardian import perform_whois_lookup
import socket

def run_whois(domain):
    result = perform_whois_lookup(domain)
    print("\n=== INFORMAÇÕES WHOIS ===")
    for key, value in result.items():
        print(f"{key.lower()}: {value}")

def run_dns(domain):
    try:
        name, aliases, addresses = socket.gethostbyname_ex(domain)
        print("\n=== INFORMAÇÕES DNS ===")
        print(f"Domínio: {name}")
        print(f"Apelidos: {aliases}")
        print(f"Endereços IP: {addresses}")
    except socket.gaierror:
        print("❌ Erro ao resolver o domínio.")

def main():
    parser = argparse.ArgumentParser(description="🔍 Shamann - Módulo de reconhecimento")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Comando WHOIS
    parser_whois = subparsers.add_parser('whois', help='Executa consulta WHOIS')
    parser_whois.add_argument('domain', help='Domínio a ser consultado')

    # Comando DNS
    parser_dns = subparsers.add_parser('dns', help='Executa resolução DNS')
    parser_dns.add_argument('domain', help='Domínio a ser resolvido')

    args = parser.parse_args()

    if args.command == 'whois':
        run_whois(args.domain)
    elif args.command == 'dns':
        run_dns(args.domain)

if __name__ == '__main__':
    main()
