import pytest

def pytest_report_teststatus(report, config):
    """
    Hook do pytest para customizar o status reportado no terminal.
    Só altera a saída durante a execução ('call') e não no setup/teardown.
    """
    if report.when == 'call':
        # 1. Identifica a categoria com base no nome da função (nodeid)
        nome_teste = report.nodeid.lower()
        
        if "test_unit" in nome_teste or "test_gerar_tabuleiro" in nome_teste or "test_quantidade_terrenos" in nome_teste:
            categoria = "UNIDADE"
        elif "test_integration" in nome_teste:
            categoria = "INTEGRAÇÃO"
        elif "test_system" in nome_teste:
            categoria = "SISTEMA"
        elif "test_acceptance" in nome_teste:
            categoria = "ACEITAÇÃO"
        else:
            categoria = "OUTROS"

        # 2. Modifica a mensagem de saída no terminal
        if report.passed:
            # Retorna: (status original, letra curta, mensagem verbosa customizada)
            return report.outcome, ".", f"[{categoria}] PASSOU ✓"
        elif report.failed:
            return report.outcome, "F", f"[{categoria}] FALHOU ✗"
        elif report.skipped:
            return report.outcome, "s", f"[{categoria}] IGNORADO ⚠"