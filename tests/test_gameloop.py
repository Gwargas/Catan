import random
import sys
import os
import math
import pytest
# Adiciona o diretório src ao sys.path para permitir a importação de gameloop
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from gameloop import (
    MAPA_RECURSOS, gerar_tabuleiro, DESERTO, FLORESTA, COLINA, PASTO, PLANTACAO, MONTANHA,
    criar_jogadores, criar_banco_recursos, CUSTO_ALDEIA, CUSTO_ESTRADA, CUSTO_DESENVOLVIMENTO,
    tem_recursos, gastar_recursos, pontuacao_total, distribuir_recursos, passar_turno,
    tentar_construir_aldeia, tentar_construir_estrada, comprar_carta_desenvolvimento,
    criar_fila_descarte, quantidade_para_descartar, bot_descartar_recursos,
    trocar_com_banco, verificar_vencedor, PONTOS_PARA_VENCER, fase_inicial_completa,
    criar_ordem_fase_inicial, jogador_completou_rodada_inicial, aldeias_construidas,
    estradas_construidas, limpar_dados_fase_inicial
)

def test_gerar_tabuleiro_sem_6_e_8_adjacentes():
    """
    Testa se a função gerar_tabuleiro cria um tabuleiro onde nenhum
    hexágono com número 6 ou 8 é adjacente a outro com 6 ou 8.
    """
    for _ in range(50): # Roda o teste várias vezes para garantir consistência
        tabuleiro, _ = gerar_tabuleiro()

        # 1. Mapear a posição de cada peça e seus vizinhos
        pecas_com_centro = {}
        for i, peca in enumerate(tabuleiro):
            pecas_com_centro[i] = {
                'numero': peca.get('numero'),
                'centro': peca['centro'],
                'vizinhos': []
            }

        distancia_vizinho = math.sqrt(3) * 45 * 1.1
        for i in range(len(tabuleiro)):
            for j in range(i + 1, len(tabuleiro)):
                dist = math.dist(pecas_com_centro[i]['centro'], pecas_com_centro[j]['centro'])
                if dist < distancia_vizinho:
                    pecas_com_centro[i]['vizinhos'].append(j)
                    pecas_com_centro[j]['vizinhos'].append(i)

        # 2. Encontrar todas as peças com 6 ou 8
        pecas_criticas = []
        for i, peca in pecas_com_centro.items():
            if peca['numero'] in [6, 8]:
                pecas_criticas.append(i)

        # 3. Verificar os vizinhos das peças críticas
        for i in pecas_criticas:
            peca_atual = pecas_com_centro[i]
            for vizinho_idx in peca_atual['vizinhos']:
                peca_vizinha = pecas_com_centro[vizinho_idx]
                # A asserção falhará se um vizinho também tiver 6 ou 8
                assert peca_vizinha['numero'] not in [6, 8], \
                    f"Erro de adjacência: Peça {i} (nº {peca_atual['numero']}) " \
                    f"é vizinha da peça {vizinho_idx} (nº {peca_vizinha['numero']})"

def test_quantidade_terrenos_e_fichas():
    """
    Testa se o tabuleiro gerado tem a quantidade correta de cada tipo de terreno e ficha.
    """
    tabuleiro, _ = gerar_tabuleiro()

    # Contagem de terrenos
    contagem_terrenos = {}
    for peca in tabuleiro:
        cor = peca['cor']
        contagem_terrenos[cor] = contagem_terrenos.get(cor, 0) + 1

    from gameloop import FLORESTA, COLINA, PASTO, PLANTACAO, MONTANHA
    assert contagem_terrenos.get(FLORESTA, 0) == 4
    assert contagem_terrenos.get(COLINA, 0) == 3
    assert contagem_terrenos.get(PASTO, 0) == 4
    assert contagem_terrenos.get(PLANTACAO, 0) == 4
    assert contagem_terrenos.get(MONTANHA, 0) == 3
    assert contagem_terrenos.get(DESERTO, 0) == 1
    assert len(tabuleiro) == 19

    # Contagem de fichas
    fichas = [peca['numero'] for peca in tabuleiro if peca['numero'] is not None]
    assert fichas.count(2) == 1
    assert fichas.count(3) == 2
    assert fichas.count(4) == 2
    assert fichas.count(5) == 2
    assert fichas.count(6) == 2
    assert fichas.count(8) == 2
    assert fichas.count(9) == 2
    assert fichas.count(10) == 2
    assert fichas.count(11) == 2
    assert fichas.count(12) == 1
    assert len(fichas) == 18


# ===================================
# ===== TESTES DE UNIDADE (NOVOS) =====
# ===================================

def test_unit_tem_recursos():
    """Testa se a função tem_recursos funciona corretamente."""
    jogador = {"inventario": {"Madeira": 1, "Tijolo": 1, "Ovelha": 1, "Trigo": 1}}
    
    assert tem_recursos(jogador, CUSTO_ALDEIA) == True
    assert tem_recursos(jogador, CUSTO_ESTRADA) == True
    assert tem_recursos(jogador, {"Madeira": 2}) == False
    assert tem_recursos(jogador, {"Minério": 1}) == False

def test_unit_gastar_recursos():
    """Testa se a função gastar_recursos deduz os recursos corretamente."""
    jogador = {"inventario": {"Madeira": 2, "Tijolo": 2, "Ovelha": 0, "Trigo": 0, "Minério": 0}}
    banco = criar_banco_recursos()
    
    gastar_recursos(jogador, CUSTO_ESTRADA, banco)
    
    assert jogador["inventario"]["Madeira"] == 1
    assert jogador["inventario"]["Tijolo"] == 1
    assert banco["Madeira"] > 19 # Verifica se o recurso voltou ao banco

def test_unit_pontuacao_total():
    """Testa o cálculo da pontuação total, incluindo pontos de vitória ocultos."""
    jogador = {"pontos": 2, "pontos_vitoria_ocultos": 1}
    assert pontuacao_total(jogador) == 3

def test_unit_distribuir_recursos():
    """Testa a distribuição de recursos após uma rolagem de dados."""
    # Limpa construções de testes anteriores
    aldeias_construidas.clear()
    estradas_construidas.clear()

    jogadores = criar_jogadores(2, 2)
    banco = criar_banco_recursos()
    tabuleiro, vertices = gerar_tabuleiro()

    # Encontra um hexágono que não seja deserto para o teste
    peca_teste = None
    for peca in tabuleiro:
        if peca['cor'] != DESERTO:
            peca_teste = peca
            break
    
    assert peca_teste is not None, "Nenhuma peça válida para teste encontrada."

    # Adiciona uma aldeia para o jogador 0 no primeiro vértice da peça
    vertice_aldeia = encontrar_vertice_por_pos(peca_teste['vertices'][0], vertices)
    aldeias_construidas.append({"vertice": vertice_aldeia, "jogador": 0, "tipo": "aldeia"})
    
    dado = peca_teste['numero']
    ladrao = encontrar_deserto(tabuleiro)

    distribuir_recursos(tabuleiro, dado, jogadores, ladrao, banco)
    
    recurso_esperado = MAPA_RECURSOS[peca_teste['cor']]
    assert jogadores[0]["inventario"][recurso_esperado] == 1
    assert jogadores[1]["inventario"][recurso_esperado] == 0

def test_unit_passar_turno():
    """Testa se a função passar_turno avança corretamente para o próximo jogador."""
    jogadores = criar_jogadores(3, 3)
    jogador_atual = 0
    
    jogador_atual = passar_turno(jogador_atual, jogadores)
    assert jogador_atual == 1
    
    jogador_atual = passar_turno(jogador_atual, jogadores)
    assert jogador_atual == 2
    
    jogador_atual = passar_turno(jogador_atual, jogadores)
    assert jogador_atual == 0

# =======================================
# ===== TESTES DE INTEGRAÇÃO (NOVOS) =====
# =======================================

def test_integration_construir_aldeia_sucesso():
    """Testa a integração da construção de uma aldeia, gastando recursos e pontuando."""
    aldeias_construidas.clear()
    estradas_construidas.clear()

    jogadores = criar_jogadores(1, 1)
    jogador = jogadores[0]
    banco = criar_banco_recursos()
    _, vertices = gerar_tabuleiro()

    # Dá recursos ao jogador
    for recurso, quantidade in CUSTO_ALDEIA.items():
        jogador["inventario"][recurso] = quantidade
    
    # Simula uma estrada para conexão
    estradas_construidas.append({"v1": vertices[0], "v2": vertices[0].vizinhos[0], "jogador": 0})

    sucesso = tentar_construir_aldeia(vertices[0].vizinhos[0], vertices, 0, jogadores, banco)

    assert sucesso == True
    assert jogador["pontos"] == 1
    for recurso, quantidade in CUSTO_ALDEIA.items():
        assert jogador["inventario"][recurso] == 0

def test_integration_construir_estrada_conectada():
    """Testa se uma estrada pode ser construída conectada a uma aldeia."""
    aldeias_construidas.clear()
    estradas_construidas.clear()

    jogadores = criar_jogadores(1, 1)
    jogador = jogadores[0]
    banco = criar_banco_recursos()
    _, vertices = gerar_tabuleiro()

    for recurso, quantidade in CUSTO_ESTRADA.items():
        jogador["inventario"][recurso] = quantidade

    # Adiciona uma aldeia inicial
    aldeias_construidas.append({"vertice": vertices[10], "jogador": 0, "tipo": "aldeia"})

    v1 = vertices[10]
    v2 = v1.vizinhos[0]
    
    sucesso = tentar_construir_estrada(v1, v2, 0, jogadores, banco)

    assert sucesso == True
    assert len(estradas_construidas) == 1
    assert estradas_construidas[0]["jogador"] == 0

def test_integration_comprar_carta_desenvolvimento():
    """Testa a compra de uma carta de desenvolvimento, validando o custo."""
    jogadores = criar_jogadores(1, 1)
    jogador = jogadores[0]
    banco = criar_banco_recursos()
    baralho = criar_baralho_desenvolvimento()
    
    for recurso, quantidade in CUSTO_DESENVOLVIMENTO.items():
        jogador["inventario"][recurso] = quantidade

    comprar_carta_desenvolvimento(jogador, baralho, banco)

    assert len(jogador["cartas_dev"]) == 1
    assert len(baralho) == 24
    for recurso, quantidade in CUSTO_DESENVOLVIMENTO.items():
        assert jogador["inventario"][recurso] == 0

def test_integration_descarte_recursos_dado_7():
    """Testa a integração do descarte de recursos quando um jogador tem mais de 7 cartas."""
    jogadores = criar_jogadores(2, 1) # 1 humano, 1 bot
    jogador_humano = jogadores[0]
    jogador_bot = jogadores[1]
    banco = criar_banco_recursos()

    # Dá 8 recursos para cada jogador
    for i in range(8):
        jogador_humano["inventario"]["Madeira"] += 1
        jogador_bot["inventario"]["Ovelha"] += 1
    
    fila_descarte = criar_fila_descarte(jogadores)
    assert fila_descarte == [0, 1] # Ambos devem descartar

    # Bot descarta automaticamente
    mensagem_bot = bot_descartar_recursos(jogador_bot, banco)
    assert "descartou 4 recurso(s)" in mensagem_bot
    assert sum(jogador_bot["inventario"].values()) == 4

    # Prepara para o descarte do humano
    assert quantidade_para_descartar(jogador_humano) == 4

def test_integration_troca_com_banco():
    """Testa a troca de recursos com o banco na taxa padrão 4:1."""
    jogadores = criar_jogadores(1, 1)
    jogador = jogadores[0]
    banco = criar_banco_recursos()
    portos = [] # Sem portos para garantir taxa 4:1

    jogador["inventario"]["Madeira"] = 4
    
    mensagem = trocar_com_banco(0, jogadores, "Madeira", "Tijolo", portos, banco)

    assert "trocou 4 Madeira por 1 Tijolo" in mensagem
    assert jogador["inventario"]["Madeira"] == 0
    assert jogador["inventario"]["Tijolo"] == 1

# =====================================
# ===== TESTES DE SISTEMA (NOVOS) =====
# =====================================

def test_system_fase_inicial_completa():
    """Testa o fluxo completo da fase inicial para 2 jogadores."""
    aldeias_construidas.clear()
    estradas_construidas.clear()
    
    jogadores = criar_jogadores(2, 2)
    banco = criar_banco_recursos()
    _, vertices = gerar_tabuleiro()
    limpar_dados_fase_inicial(jogadores)

    ordem_inicial = criar_ordem_fase_inicial(jogadores)
    assert ordem_inicial == [0, 1, 1, 0]

    # Rodada 1 (ida)
    # Jogador 0
    assert tentar_construir_aldeia(vertices[0], vertices, 0, jogadores, banco, fase_inicial=True) == True
    assert tentar_construir_estrada(vertices[0], vertices[0].vizinhos[0], 0, jogadores, banco, fase_inicial=True) == True
    assert jogador_completou_rodada_inicial(0, 0, jogadores) == True
    
    # Jogador 1
    assert tentar_construir_aldeia(vertices[10], vertices, 1, jogadores, banco, fase_inicial=True) == True
    assert tentar_construir_estrada(vertices[10], vertices[10].vizinhos[0], 1, jogadores, banco, fase_inicial=True) == True
    assert jogador_completou_rodada_inicial(1, 1, jogadores) == True

    # Rodada 2 (volta)
    # Jogador 1
    assert tentar_construir_aldeia(vertices[20], vertices, 1, jogadores, banco, fase_inicial=True) == True
    assert tentar_construir_estrada(vertices[20], vertices[20].vizinhos[0], 1, jogadores, banco, fase_inicial=True) == True
    assert jogador_completou_rodada_inicial(1, 2, jogadores) == True

    # Jogador 0
    assert tentar_construir_aldeia(vertices[30], vertices, 0, jogadores, banco, fase_inicial=True) == True
    assert tentar_construir_estrada(vertices[30], vertices[30].vizinhos[0], 0, jogadores, banco, fase_inicial=True) == True
    assert jogador_completou_rodada_inicial(0, 3, jogadores) == True

    assert fase_inicial_completa(jogadores) == True

# ========================================
# ===== TESTES DE ACEITAÇÃO (NOVOS) =====
# ========================================

def test_acceptance_vitoria_por_pontos():
    """Testa se um jogador vence ao atingir a pontuação necessária."""
    jogadores = criar_jogadores(1, 1)
    jogador = jogadores[0]
    
    jogador["pontos"] = PONTOS_PARA_VENCER - 1
    vencedor = verificar_vencedor(jogadores, 0)
    assert vencedor is None

    jogador["pontos"] += 1
    vencedor = verificar_vencedor(jogadores, 0)
    assert vencedor is not None
    assert vencedor["nome"] == jogador["nome"]

# Funções auxiliares para encontrar vértices e peças no tabuleiro de teste
def encontrar_vertice_por_pos(pos, vertices_globais):
    for v in vertices_globais:
        if math.hypot(v.x - pos[0], v.y - pos[1]) < 5:
            return v
    return None

def encontrar_deserto(tabuleiro):
    for peca in tabuleiro:
        if peca["cor"] == DESERTO:
            return peca
    return None

def criar_baralho_desenvolvimento():
    from gameloop import CARTAS_DESENVOLVIMENTO_BASE
    baralho = CARTAS_DESENVOLVIMENTO_BASE.copy()
    random.shuffle(baralho)
    return baralho

