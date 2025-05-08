# shamann/modules/dirfuzz_guardian.py

import requests
import argparse # Mantido caso queira rodar este arquivo diretamente para teste
from concurrent.futures import ThreadPoolExecutor
import json
import os
import concurrent.futures # Explicitamente importado para as_completed

class DirFuzzGuardian:
    """
    Guardião responsável por realizar fuzzing de diretórios/arquivos usando requests.
    Implementação baseada em sugestão externa.
    """

    @staticmethod
    def run_scan(target: str, options: str = "") -> dict:
        """
        Executa o fuzzing para um target usando a lógica baseada em requests.
        Espera options como uma string similar a CLI: "-w wordlist.txt -t 20".
        """
        print(f"DEBUG: DirFuzzGuardian.run_scan iniciado para {target} com opções {options}")

        wordlist_path = None
        threads = 10 # Default threads

        # Parsing básico da string de opções
        option_list = options.split()
        try:
            # Encontra o caminho da wordlist após -w
            if "-w" in option_list:
                w_index = option_list.index("-w") + 1
                if w_index < len(option_list):
                    wordlist_path = option_list[w_index]

            # Encontra o número de threads após -t
            if "-t" in option_list:
                 t_index = option_list.index("-t") + 1
                 if t_index < len(option_list):
                     try:
                         threads = int(option_list[t_index])
                     except ValueError:
                         print(f"WARNING: Número de threads inválido '{option_list[t_index]}', usando padrão {threads}")

        except Exception as e:
            print(f"ERROR: Falha ao parsear string de opções '{options}': {e}")
            return {"target": target, "options": options, "status": "error", "error_message": f"Falha ao parsear opções: {e}"}


        if not wordlist_path:
             print("ERROR: Caminho para a wordlist não especificado nas opções (-w).")
             return {"target": target, "options": options, "status": "error", "error_message": "Caminho para a wordlist não especificado (-w)."}

        # Verificar se o arquivo da wordlist existe e é legível
        if not os.path.exists(wordlist_path):
            print(f"ERROR: Arquivo da wordlist não encontrado: {wordlist_path}")
            return {"target": target, "options": options, "status": "error", "error_message": f"Arquivo da wordlist não encontrado: {wordlist_path}"}

        if not os.access(wordlist_path, os.R_OK):
             print(f"ERROR: Sem permissão de leitura para o arquivo da wordlist: {wordlist_path}")
             return {"target": target, "options": options, "status": "error", "error_message": f"Sem permissão de leitura para o arquivo da wordlist: {wordlist_path}"}


        paths = []
        try:
            with open(wordlist_path, "r", encoding="utf-8") as f:
                paths = [line.strip() for line in f if line.strip()]
        except Exception as e:
             print(f"ERROR: Falha ao ler arquivo da wordlist '{wordlist_path}': {e}")
             return {"target": target, "options": options, "status": "error", "error_message": f"Falha ao ler wordlist: {e}"}

        if not paths:
             print(f"WARNING: A wordlist '{wordlist_path}' está vazia.")
             # Pode retornar como completed, mas com lista de found_endpoints vazia
             parsed_data_empty = {
                "target": target,
                "options": options,
                "wordlist": wordlist_path,
                "threads": threads,
                "found_endpoints": [],
                "files_found_count": 0,
             }
             return {
                "target": target, "options": options,
                "command_executed": f"Internal DirFuzz scan on {target} with empty wordlist {wordlist_path}",
                "stdout": "Wordlist vazia, scan não executado.",
                "stderr": "", "returncode": 0, "status": "completed",
                "parsed_data": parsed_data_empty
             }


        print(f"[*] Fuzzing {len(paths)} paths em {target} com {threads} threads...\n")

        found_endpoints = []
        # Adaptar a lógica test_url do script sugerido
        def test_url_request(base_url, path):
            # Construir a URL, removendo a barra final da base_url se presente
            url = f"{base_url.rstrip('/')}/{path.strip()}"
            try:
                # Usando um timeout razoável para cada requisição
                response = requests.get(url, timeout=10) # Timeout aumentado para 10s

                # Coletar códigos de status relevantes (não apenas 200)
                # A sugestão filtra 404 e 400. Vamos manter isso.
                if response.status_code not in [404, 400]:
                    # Printar o resultado imediatamente, similar ao dirb/dirfuzz
                    print(f"[{response.status_code}] {url}")
                    # Retornar mais detalhes para o dicionário final
                    return {"url": url, "status_code": response.status_code, "size": len(response.content)}
            except requests.exceptions.RequestException as e:
                # Tratar erros de requisição (ex: conexão recusada, timeout por requisição)
                # Opcional: imprimir erros de requisição para debug
                # print(f"DEBUG (Request Error): {url} - {e}")
                pass # Ignorar erros de requisição individuais para não poluir a saída

            return None # Indica que nenhum endpoint relevante foi encontrado para este caminho


        # Executar com ThreadPoolExecutor
        # Usamos as_completed para processar os resultados assim que estiverem prontos
        with ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_path = {executor.submit(test_url_request, target, path): path for path in paths}
            for future in concurrent.futures.as_completed(future_to_path):
                # path = future_to_path[future] # Podemos recuperar o caminho original se necessário
                try:
                    result = future.result()
                    if result:
                        found_endpoints.append(result)
                except Exception as exc:
                    # Opcional: Tratar exceções que ocorrem dentro das threads
                    print(f"DEBUG (Thread Exception): Tarefa gerou exceção: {exc}")


        print("\n[+] Scan completo.")

        # Preparar o dicionário de resultado no formato esperado pelo Mestre
        parsed_data = {
            "target": target,
            "options": options,
            "wordlist": wordlist_path,
            "threads": threads,
            "found_endpoints": found_endpoints, # Lista de dicionários com url, status_code, size
            "files_found_count": len(found_endpoints),
            # Como usamos requests, não há stdout/stderr direto do subprocesso,
            # mas podemos colocar os found_endpoints no stdout para consistência com outros Guardiões
        }

        # Formatar found_endpoints para o campo stdout, similar à saída do Dirb
        stdout_output_lines = [f"[{ep['status_code']}] {ep['url']} (SIZE: {ep['size']})" for ep in found_endpoints]
        stdout_output = "\n".join(stdout_output_lines)


        return {
            "target": target,
            "options": options,
            "command_executed": f"Internal DirFuzz scan on {target} with wordlist {wordlist_path} ({len(paths)} paths, {threads} threads)",
            "stdout": stdout_output, # Coloca a lista de endpoints encontrados aqui
            "stderr": "", # Sem stderr neste método
            "returncode": 0, # Assumimos 0 se o scan rodou sem erros internos do script
            "status": "completed",
            "parsed_data": parsed_data
        }

# Este arquivo por si só não deve ser executado diretamente no fluxo do Mestre,
# mas a classe DirFuzzGuardian será importada e utilizada.
