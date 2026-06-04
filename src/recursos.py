from pathlib import Path


def caminho_asset(nome_arquivo):
    pasta_atual = Path(__file__).resolve().parent

    # Quando estiver rodando pelo executável do PyInstaller
    caminho_bundle = pasta_atual / "assets" / nome_arquivo

    if caminho_bundle.exists():
        return str(caminho_bundle)

    # Quando estiver rodando pelo código-fonte em src/
    return str(pasta_atual.parent / "assets" / nome_arquivo)