import whois

def perform_whois_lookup(domain):
    try:
        result = whois.whois(domain)
        print("\n=== INFORMAÇÕES WHOIS ===")
        for key, value in result.items():
            print(f"{key}: {value}")
        return str(result)
    except Exception as e:
        print(f"[!] Erro ao consultar WHOIS para {domain}: {e}")
        return ""
