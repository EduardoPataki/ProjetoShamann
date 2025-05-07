# shamann/modules/whois_guardian.py

# Você pode remover estas importações se não forem usadas
import subprocess
import sys

# Importar a biblioteca Whois real - IMPORT CORRIGIDA
import whois # Importa a biblioteca usando o nome correto do módulo instalado

class WhoisGuardian:
    """
    Guardião responsável por interagir com a ferramenta WHOIS.
    """

    @staticmethod
    def run_query(target: str) -> dict:
        """
        Executa uma consulta WHOIS para um target e retorna os resultados.
        """
        print(f"DEBUG: WHOIS Guardian run_query iniciado para {target}")

        # --- Lógica real de consulta WHOIS ---
        # Certifique-se de que 'python-whois' está no seu requirements.txt
        # e que você rodou 'pip install -r requirements.txt'

        try:
            # Use a biblioteca whois (agora importada corretamente) aqui
            details = whois.get_whois(target)
            return {
                "target": target,
                "status": "completed",
                "raw_whois_data": details, # 'details' é um dicionário/objeto retornado pela lib
                # TODO: Adicionar parsing mais aprofundado de 'details' se necessário
                "parsed_data": details # Por enquanto, retorne os detalhes brutos também como "parsed"
            }
        except Exception as e:
            print(f"Erro na consulta WHOIS: {e}")
            return {"target": target, "status": "error", "error_message": str(e)}

        # --- REMOVA ou COMENTE O BLOCO ABAIXO para usar a lógica acima ---
        # return {
        #     "target": target,
        #     "status": "completed_simulated",
        #     "raw_whois_data": f"Resultados WHOIS simulados para {target}",
        #     "parsed_data": {"domain": target, "registrar": "Simulado"}
        # }

# (Bloco __main__ comentado aqui)
# if __name__ == "__main__":
#    pass # Este guardião não é o ponto de entrada principal
