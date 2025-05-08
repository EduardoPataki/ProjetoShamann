# shamann/main.py

import argparse
import sys
import json
# Importar os Guardiões via o pacote modules
from shamann.modules import GUARDIANS

class Mestre:
    """
    O Mestre (Master) do framework Shamann.
    Orquestra os Guardiões e a interação via CLI.
    """

    @staticmethod
    def execute_scan(guardian_name: str, target: str, options: str = "") -> dict:
        """
        Localiza o Guardião apropriado e executa o scan.
        """
        print(f"Mestre chamando Guardião: {guardian_name} para target: {target} com opções: {options}")
        if guardian_name in GUARDIANS:
            guardian_class = GUARDIANS[guardian_name]
            # Instanciar e rodar o Guardião. Os Guardiões devem ter um método run_scan estático.
            # Assumimos que run_scan retorna um dicionário com os resultados.
            try:
                results = guardian_class.run_scan(target, options)
                return results
            except Exception as e:
                print(f"Erro ao executar o Guardião {guardian_name}: {e}", file=sys.stderr)
                # Opcional: Imprimir traceback completo para depuração
                # import traceback
                # traceback.print_exc()
                return {
                    "target": target,
                    "guardian": guardian_name,
                    "status": "error",
                    "error_message": str(e)
                }
        else:
            print(f"Erro: Guardião '{guardian_name}' não encontrado.", file=sys.stderr)
            return {
                "target": target,
                "guardian": guardian_name,
                "status": "error",
                "error_message": f"Guardião '{guardian_name}' não encontrado."
            }


    @staticmethod
    def parse_cli():
        """
        Analisa os argumentos da linha de comando e dispara as ações.
        """
        # Cria o parser principal
        parser = argparse.ArgumentParser(description="Shamann - Pentest Automation Framework Master")

        # Adiciona um argumento opcional para listar guardiões
        parser.add_argument("--list-guardians", action="store_true", help="List available Guardians")


        # Cria subparsers para os diferentes comandos
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Subparser para nmap-scan
        nmap_parser = subparsers.add_parser("nmap-scan", help="Perform an Nmap scan.")
        nmap_parser.add_argument("target", help="Target for Nmap scan.")
        nmap_parser.add_argument("-o", "--options", default="", help="Additional Nmap options as a single string.")
        # nmap_parser.set_defaults(func=Mestre.execute_scan, guardian_name="nmap") # Vamos lidar com a execução aqui

        # Subparser para whois-lookup
        whois_parser = subparsers.add_parser("whois-lookup", help="Perform a WHOIS lookup.")
        whois_parser.add_argument("target", help="Target for WHOIS lookup.")
        # whois_parser.set_defaults(func=Mestre.execute_scan, guardian_name="whois") # Vamos lidar com a execução aqui

        # Subparser para dirb-scan (mantido, mas pode ser removido ou apontar para dirfuzz)
        # dirb_parser = subparsers.add_parser("dirb-scan", help="Perform a Dirb scan (using external dirb binary, may be unstable).")
        # dirb_parser.add_argument("target", help="Target for Dirb scan.")
        # dirb_parser.add_argument("-o", "--options", default="", help="Additional Dirb options as a single string.")

        # Subparser para dirfuzz-scan (NOVO)
        dirfuzz_parser = subparsers.add_parser("dirfuzz-scan", help="Perform directory fuzzing using internal requests-based tool.")
        dirfuzz_parser.add_argument("target", help="Target URL (e.g., http://example.com)")
        dirfuzz_parser.add_argument("-w", "--wordlist", required=True, help="Path to wordlist file")
        dirfuzz_parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads (default: 10)")


        args = parser.parse_args()

        # Se --list-guardians foi usado, imprimir a lista e sair
        if args.list_guardians:
            print("Guardiões Disponíveis:")
            # Garantir que o import de GUARDIANS ocorreu sem erro
            if GUARDIANS is not None:
                for name in GUARDIANS.keys():
                    print(f"- {name}")
            else:
                print("Erro: Não foi possível carregar a lista de Guardiões.")
            return # Sair após listar

        if not hasattr(args, 'command') or args.command is None:
            parser.print_help()
            return


        # Processa o comando e chama o Guardião apropriado
        # Removendo 'func' e 'guardian_name' da impressão se existirem
        arg_dict = vars(args)
        # Criar uma cópia para evitar modificar o dicionário durante a iteração se necessário
        arg_print_dict = {k:v for k,v in arg_dict.items() if k not in ['command', 'func']}
        print(f"Comando CLI recebido: {args.command} " + ", ".join([f"{k}={v}" for k,v in arg_print_dict.items()]))


        try:
            if args.command == "nmap-scan":
                guardian_name = "nmap"
                target = args.target
                options = args.options
                results = Mestre.execute_scan(guardian_name, target, options)
                print("\nResultado do Scan:")
                print(json.dumps(results, indent=4))

            elif args.command == "whois-lookup":
                guardian_name = "whois"
                target = args.target
                options = "" # WHOIS não tem opções de linha de comando complexas neste ponto
                results = Mestre.execute_scan(guardian_name, target, options)
                print("\nResultado do Scan:")
                print(json.dumps(results, indent=4))

            # Opcional: Lógica para o antigo dirb-scan se mantido
            # elif args.command == "dirb-scan":
            #     print("Aviso: O comando 'dirb-scan' pode ser instável. Considere usar 'dirfuzz-scan'.")
            #     guardian_name = "dirb" # Manter para fins de demonstração/documentação
            #     target = args.target
            #     options = args.options
            #     results = Mestre.execute_scan(guardian_name, target, options)
            #     print("\nResultado do Scan:")
            #     print(json.dumps(results, indent=4))


            # Lógica para o NOVO comando dirfuzz-scan
            elif args.command == "dirfuzz-scan":
                guardian_name = "dirfuzz"
                target = args.target
                # Montar a string de opções no formato que o DirFuzzGuardian espera
                # baseado nos argumentos separados do parser
                # Citar o caminho da wordlist caso contenha espaços
                options = f"-w \"{args.wordlist}\" -t {args.threads}"

                results = Mestre.execute_scan(guardian_name, target, options)
                print("\nResultado do Scan:")
                print(json.dumps(results, indent=4))


            # Adicionar mais comandos elif aqui para outros Guardiões futuros

            else:
                # Isso não deve acontecer se subparsers estiver configurado corretamente,
                # mas é uma segurança. O argparse já cuida da maioria dos casos.
                print(f"Erro: Comando '{args.command}' não reconhecido.", file=sys.stderr)
                parser.print_help()


        except Exception as e:
            print(f"\nOcorreu um erro geral durante a execução do comando: {e}", file=sys.stderr)
            # Opcional: Imprimir traceback completo para depuração em caso de erro inesperado no Mestre
            # import traceback
            # traceback.print_exc()


# Bloco principal para execução
if __name__ == "__main__":
    Mestre.parse_cli()
