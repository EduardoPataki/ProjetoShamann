# shamann/cli/main.py

import argparse
import sys
import os

# Ajusta o PYTHONPATH para que os módulos do Shamann sejam encontrados
# Isso é crucial para que 'python -m shamann.cli.main' funcione de qualquer lugar na raiz do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from shamann.main import run_shamann_orchestrator # Importa a função principal do Shamann

def main():
    parser = argparse.ArgumentParser(
        description="Shamann: Agente de Segurança e Pentest Modular.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "-t", "--target",
        type=str,
        help="""Define o alvo para o scan Nmap. Pode ser:
  - Um IP único (ex: 192.168.1.1)
  - Um range de IPs (ex: 192.168.1.0/24)
  - Múltiplos alvos separados por vírgula (ex: 192.168.1.1,192.168.1.10/30)
  - Caminho para um arquivo contendo alvos (um por linha)"""
    )
    parser.add_argument(
        "-c", "--config",
        type=str,
        default="shamann/config/scan_config.json",
        help="Caminho para o arquivo de configuração JSON. Padrão: shamann/config/scan_config.json"
    )
    parser.add_argument(
        "-p", "--ports",
        type=str,
        help="""Define as portas a serem escaneadas. Pode ser:
  - Portas comuns (ex: 80,443,22)
  - Ranges de portas (ex: 1-1024)
  - 'all' para todas as portas (1-65535)
  Se não especificado, usa a configuração do arquivo JSON."""
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        help="Diretório para salvar os relatórios de saída. Se não especificado, usa a configuração do arquivo JSON ou './output'."
    )
    # Adicionar outros argumentos conforme necessário (ex: --full-scan, --no-db, etc.)

    args = parser.parse_args()

    # Chama a função principal do Shamann (que será ajustada)
    # Passamos os argumentos da CLI para ela
    run_shamann_orchestrator(
        cli_target=args.target,
        config_path=args.config,
        cli_ports=args.ports,
        cli_output_dir=args.output_dir
    )

if __name__ == "__main__":
    main()
