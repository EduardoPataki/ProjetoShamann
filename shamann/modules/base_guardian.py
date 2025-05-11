class BaseGuardian:
    @staticmethod
    def run_scan(target: str, options: str = "") -> dict:
        raise NotImplementedError("Todo guardião deve implementar run_scan()")

    @staticmethod
    def get_metadata() -> dict:
        return {
            "name": "Base",
            "description": "Classe base abstrata para todos os guardiões.",
            "parameters": {},
            "version": "0.1"
        }
