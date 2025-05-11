import argparse
import sys
import json
from shamann.modules.guardian_registry import GUARDIANS

class Mestre:
    """
    O Mestre (Master) do framework Shamann.
    Orquestra os Guardiões e a interação via CLI.
    """

    @staticmethod
    def execute_scan(guardian_name: str, target: str, options: str = "") -> dict:
        print(f"Mestre chamando Guardião: {guardian_name} para target: {target} com opções: {options}")
        guardian_class = GUARDIANS.get(guardian_name)

        if guardian_class is None:
            print(f"Erro: Guardião '{guardian_name}' não encontrado.", file=sys.stderr)
            return {
                "target": target,
                "guardian": guardian_name,
                "status": "error",
                "error_message": f"Guardião '{guardian_name}' não encontrado."
            }

        try:
            return guardian_class.run_scan(target, options)
        except Exception as e:
            print(f"Erro ao executar o Guardião '{guardian_name}': {e}", file=sys.stderr)
            return {
                "target": target,
                "guardian": guardian_name,
                "status": "error",
                "error_message": str(e)
            }

    @staticmethod
    def parse_cli():
        parser = argparse.ArgumentParser(description="Shamann - Pentest Automation Framework Master")
        parser.add_argument("--list-guardians", action="store_true", help="Listar Guardiões disponíveis")

        subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

        # Nmap scan
        nmap_parser = subparsers.add_parser("nmap-scan", help="Executar um scan Nmap.")
        nmap_parser.add_argument("target", help="Alvo do scan Nmap.")
        nmap_parser.add_argument("-o", "--options", default="", help="Opções adicionais do Nmap.")

        # WHOIS lookup
        whois_parser = subparsers.add_parser("whois-lookup", help="Executar uma consulta WHOIS.")
        whois_parser.add_argument("target", help="Alvo da consulta WHOIS.")

        # Dirfuzz scan
        dirfuzz_parser = subparsers.add_parser("dirfuzz-scan", help="Executar fuzzing de diretórios.")
        dirfuzz_parser.add_argument("target", help="URL de destino (ex: http://exemplo.com)")
        dirfuzz_parser.add_argument("-w", "--wordlist", required=True, help="Caminho da wordlist.")
        dirfuzz_parser.add_argument("-t", "--threads", type=int, default=10, help="Número de threads (padrão: 10)")

        args = parser.parse_args()

        if args.list_guardians:
            print("\nGuardiões Disponíveis:")
            if GUARDIANS:
                for name in GUARDIANS.keys():
                    print(f"- {name}")
            else:
                print("Erro: Nenhum guardião foi carregado.")
            return

        if not args.command:
            parser.print_help()
            return

        try:
            if args.command == "nmap-scan":
                results = Mestre.execute_scan("nmap", args.target, args.options)

            elif args.command == "whois-lookup":
                results = Mestre.execute_scan("whois", args.target)

            elif args.command == "dirfuzz-scan":
                options = f'-w "{args.wordlist}" -t {args.threads}'
                results = Mestre.execute_scan("dirfuzz", args.target, options)

            else:
                print(f"Erro: Comando '{args.command}' não reconhecido.", file=sys.stderr)
                parser.print_help()
                return

            print("\nResultado do Scan:")
            print(json.dumps(results, indent=4))

        except Exception as e:
            print(f"\nErro geral durante a execução do comando: {e}", file=sys.stderr)

if __name__ == "__main__":
    Mestre.parse_cli()
