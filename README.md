# Catan
Repositório alocado para o trabalho da disciplina de Engenharia de Software 2.


Para criar o executável:
python -m pip install pyinstaller

python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name Catan `
    --add-data "assets:assets" `
    src/main.py
