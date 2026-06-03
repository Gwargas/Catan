import pygame
import math
import random
import sys

pygame.init()
LARGURA, ALTURA = 800, 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("CATAN")
FONTE_NUMEROS = pygame.font.SysFont("Arial", 24, bold=True)
FONTE_TEXTO = pygame.font.SysFont("Arial", 22)
FONTE_TITULO = pygame.font.SysFont("Arial", 26, bold=True)

PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
COR_FUNDO = (135, 206, 235)

FLORESTA = (34, 139, 34)  
COLINA = (210, 105, 30)   
PASTO = (154, 205, 50)    
PLANTACAO = (255, 215, 0) 
MONTANHA = (112, 128, 144)
DESERTO = (244, 164, 96)  

MAPA_RECURSOS = {
    FLORESTA: 'Madeira', #Catnip?
    COLINA: 'Tijolo',
    PASTO: 'Ovelha', #Novelo de lã?
    PLANTACAO: 'Trigo', #Ração? Peixe?
    MONTANHA: 'Minério'
}

TAMANHO_HEX = 45 

TERRENOS = [FLORESTA]*4 + [COLINA]*3 + [PASTO]*4 + [PLANTACAO]*4 + [MONTANHA]*3 + [DESERTO]*1
random.shuffle(TERRENOS)
FICHAS = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
random.shuffle(FICHAS)

aldeias_construidas = []
estradas_construidas = []
inventario = {
    'Madeira': 0,
    'Tijolo': 0,
    'Ovelha': 0,
    'Trigo': 0,
    'Minério': 0
}

VERMELHO_JOGADOR = (255, 0, 0)
AZUL_JOGADOR = (0, 0, 255)
VERDE_JOGADOR = (0, 180, 0)
AMARELO_JOGADOR = (255, 215, 0)

def criar_inventario():
    return {
        'Madeira': 0,
        'Tijolo': 0,
        'Ovelha': 0,
        'Trigo': 0,
        'Minério': 0
    }

def criar_jogadores(num_players, num_humanos):
    cores = [
        AZUL_JOGADOR,
        VERMELHO_JOGADOR,
        VERDE_JOGADOR,
        AMARELO_JOGADOR
    ]

    jogadores = []

    for i in range(num_players):
        if i < num_humanos:
            tipo = "humano"
            nome = f"Jogador {i + 1}"
        else:
            tipo = "bot"
            numero_bot = i - num_humanos + 1
            nome = f"Bot {numero_bot}"

        jogadores.append({
            "indice": i,
            "nome": nome,
            "tipo": tipo,
            "cor": cores[i],
            "inventario": criar_inventario(),
            "pontos": 0,
            "ultima_aldeia_inicial": None
        })

    return jogadores

class vertice:
    def __init__(self, pos):
        self.pos = pos
        self.x = pos[0]
        self.y = pos[1]
        self.vizinhos = []

    def add_vizinho(self, v):
        self.vizinhos.append(v)

def calcular_pontos_hexagono(centro_x, centro_y, tamanho):
    pontos = []
    for i in range(6):
        angulo_deg = 60 * i - 30
        angulo_rad = math.pi / 180 * angulo_deg
        x = int(centro_x + tamanho * math.cos(angulo_rad))
        y = int(centro_y + tamanho * math.sin(angulo_rad))
        pontos.append((x, y))
    return pontos

def gerar_tabuleiro():
    largura_hex = math.sqrt(3) * TAMANHO_HEX
    altura_hex = 2 * TAMANHO_HEX
    padrao_linhas = [3, 4, 5, 4, 3]
    tabuleiro = []
    vertices_globais = []
    
    centro_tela_x = LARGURA // 2
    centro_tela_y = ALTURA // 2 - (2 * altura_hex * 0.75)
    
    idx_terreno = 0
    idx_ficha = 0
    
    for linha, num_hexes in enumerate(padrao_linhas):
        offset_x = centro_tela_x - (num_hexes * largura_hex) / 2 + (largura_hex / 2)
        offset_y = centro_tela_y + linha * (altura_hex * 0.75)
        
        for col in range(num_hexes):
            cx = offset_x + col * largura_hex
            cy = offset_y
            cor = TERRENOS[idx_terreno]
            numero = None
            if cor != DESERTO:
                numero = FICHAS[idx_ficha]
                idx_ficha += 1
            
            pontos = calcular_pontos_hexagono(cx, cy, TAMANHO_HEX)
            
            for px, py in pontos:
                existe = False
                for v in vertices_globais:
                    if math.hypot(px - v.x, py - v.y) < 5:
                        existe = True
                        break
                if not existe:
                    vertices_globais.append(vertice([px, py]))
            for vert in vertices_globais:
                for viz in vertices_globais:
                    if math.dist(vert.pos, viz.pos) <= TAMANHO_HEX * 1.1 and vert != viz:
                        vert.add_vizinho(viz)
                
            tabuleiro.append({
                'centro': (cx, cy),
                'cor': cor,
                'numero': numero,
                'vertices': pontos
            })
            idx_terreno += 1
            
    return tabuleiro, vertices_globais

def desenhar_tabuleiro(tela, tabuleiro, ultimo_dado, ladrao):
    for peca in tabuleiro:
        pontos = peca['vertices']
        pygame.draw.polygon(tela, peca['cor'], pontos)
        pygame.draw.polygon(tela, PRETO, pontos, 2)
        
        if peca['numero'] is not None:
            cor_circulo = BRANCO if peca['numero'] != ultimo_dado else (255, 255, 0)
            pygame.draw.circle(tela, cor_circulo, (int(peca['centro'][0]), int(peca['centro'][1])), 18)
            pygame.draw.circle(tela, PRETO, (int(peca['centro'][0]), int(peca['centro'][1])), 18, 1)
            
            cor_texto = (220, 20, 60) if peca['numero'] in (6, 8) else PRETO
            texto = FONTE_NUMEROS.render(str(peca['numero']), True, cor_texto)
            retangulo_texto = texto.get_rect(center=peca['centro'])
            tela.blit(texto, retangulo_texto)

        if peca == ladrao:
            pygame.draw.circle(
                tela,
                PRETO,
                (int(peca["centro"][0]), int(peca["centro"][1])),
                10
            )

def desenhar_vertices_e_aldeias(tela, vertices_globais, vertice_selecionado, jogadores):
    for v in vertices_globais:
        pygame.draw.circle(tela, BRANCO, (v.x, v.y), 4)

    for estrada in estradas_construidas:
        v1 = estrada["v1"]
        v2 = estrada["v2"]
        cor_jogador = jogadores[estrada["jogador"]]["cor"]

        pygame.draw.line(tela, PRETO, v1.pos, v2.pos, width=8)
        pygame.draw.line(tela, cor_jogador, v1.pos, v2.pos, width=6)

    for aldeia in aldeias_construidas:
        v = aldeia["vertice"]
        cor_jogador = jogadores[aldeia["jogador"]]["cor"]

        if aldeia["tipo"] == "cidade":
            retangulo = pygame.Rect(0, 0, 22, 18)
            retangulo.center = (v.x, v.y + 3)

            telhado = [
                (v.x - 13, v.y - 4),
                (v.x, v.y - 17),
                (v.x + 13, v.y - 4)
            ]

            pygame.draw.rect(tela, cor_jogador, retangulo)
            pygame.draw.polygon(tela, cor_jogador, telhado)

            pygame.draw.rect(tela, PRETO, retangulo, 2)
            pygame.draw.polygon(tela, PRETO, telhado, 2)

        else:
            retangulo = pygame.Rect(0, 0, 16, 16)
            retangulo.center = (v.x, v.y)
            pygame.draw.rect(tela, cor_jogador, retangulo)
            pygame.draw.rect(tela, PRETO, retangulo, 2)
        

    if vertice_selecionado != None:
        for v in vertice_selecionado.vizinhos:
            pygame.draw.line(tela, PRETO, vertice_selecionado.pos, v.pos, width=8)
            pygame.draw.line(tela, BRANCO, vertice_selecionado.pos, v.pos, width=6)

        pygame.draw.circle(tela, BRANCO, vertice_selecionado.pos, 10)
        pygame.draw.circle(tela, PRETO, vertice_selecionado.pos, 10, width=1)

    



def desenhar_interface(tela, ultimo_dado, game_mode, jogador_atual, vencedor, fase_inicial, jogadores, mensagem_jogo, escolhendo_vitima_ladrao, vitimas_ladrao, descartando_recursos, jogador_descartando, quantidade_descartar, quantidade_descartada):
    if fase_inicial:
        texto_fase = FONTE_TEXTO.render("Fase inicial: construa 2 aldeias e 2 estradas", True, PRETO)
        tela.blit(texto_fase, (20, 120))

        aldeias_iniciais = contar_construcoes_tipo_do_jogador(jogador_atual["indice"], "aldeia")
        estradas_iniciais = contar_estradas_iniciais_do_jogador(jogador_atual["indice"])

        texto_contagem = FONTE_TEXTO.render(
            f"Iniciais: {aldeias_iniciais}/2 aldeias, {estradas_iniciais}/2 estradas",
            True,
            PRETO
        )
        tela.blit(texto_contagem, (20, 145))

    texto_modo = FONTE_TEXTO.render(f"Modo: {game_mode}", True, PRETO)
    tela.blit(texto_modo, (20, 20))

    texto_jogador = FONTE_TEXTO.render(
    f"Vez de: {jogador_atual['nome']} ({jogador_atual['tipo']})",
    True,
    PRETO
    )
    tela.blit(texto_jogador, (20, 45))

    texto_pontos = FONTE_TEXTO.render(f"Pontos: {jogador_atual['pontos']}", True, PRETO)
    tela.blit(texto_pontos, (20, 70))
    
    indice_jogador = jogador_atual["indice"]

    aldeias_restantes = LIMITE_ALDEIAS - contar_aldeias_do_jogador(indice_jogador)
    cidades_restantes = LIMITE_CIDADES - contar_cidades_do_jogador(indice_jogador)
    estradas_restantes = LIMITE_ESTRADAS - contar_estradas_do_jogador(indice_jogador)

    texto_pecas = FONTE_TEXTO.render(
        f"Peças: {aldeias_restantes} aldeias, {cidades_restantes} cidades, {estradas_restantes} estradas",
        True,
        PRETO
    )
    tela.blit(texto_pecas, (20, 95))

    if ultimo_dado > 0:
        msg_dado = FONTE_TITULO.render(f"Dado rolado: {ultimo_dado}", True, PRETO)
        tela.blit(msg_dado, (20, 170))

    if descartando_recursos and jogador_descartando is not None:
        jogador_descarte = jogadores[jogador_descartando]
        faltam = quantidade_descartar - quantidade_descartada

        texto_descarte = FONTE_TEXTO.render(
            f"{jogador_descarte['nome']} descartando: faltam {faltam}",
            True,
            PRETO
        )
        tela.blit(texto_descarte, (20, ALTURA - 115))

        texto_opcoes = FONTE_TEXTO.render(
            "1 Madeira | 2 Tijolo | 3 Ovelha | 4 Trigo | 5 Minerio",
            True,
            PRETO
        )
        tela.blit(texto_opcoes, (20, ALTURA - 90))

    if mensagem_jogo != "":
        texto_mensagem = FONTE_TITULO.render(mensagem_jogo, True, PRETO)
        tela.blit(texto_mensagem, (20, ALTURA - 60))
    
    if escolhendo_vitima_ladrao:
        y_vitima = ALTURA - 175

        texto_instrucao = FONTE_TEXTO.render("Escolha a vitima do ladrao:", True, PRETO)
        tela.blit(texto_instrucao, (20, y_vitima))

        y_vitima += 25

        for i, vitima_indice in enumerate(vitimas_ladrao):
            jogador_vitima = jogadores[vitima_indice]

            texto_vitima = FONTE_TEXTO.render(
                f"{i + 1} - {jogador_vitima['nome']}",
                True,
                PRETO
            )
            tela.blit(texto_vitima, (20, y_vitima))
            y_vitima += 25
    
    tela.blit(FONTE_TITULO.render("Pontuação:", True, PRETO), (LARGURA - 150, 210))

    y_pontos = 250
    for jogador in jogadores:
        texto_ponto = FONTE_TEXTO.render(
            f"{jogador['nome']}: {jogador['pontos']}",
            True,
            PRETO
        )
        tela.blit(texto_ponto, (LARGURA - 150, y_pontos))
        y_pontos += 25

    tela.blit(FONTE_TITULO.render("Inventário:", True, PRETO), (LARGURA - 150, 20))
    y_inv = 60
    for recurso, quantidade in jogador_atual["inventario"].items():
        texto_rec = FONTE_TEXTO.render(f"{recurso}: {quantidade}", True, PRETO)
        tela.blit(texto_rec, (LARGURA - 150, y_inv))
        y_inv += 30
    
    texto_controles = FONTE_TEXTO.render(
        "ESPACO: rolar dado | ENTER: passar turno | C: construir cidade",
        True,
        PRETO
    )
    tela.blit(texto_controles, (20, ALTURA - 30))

    if vencedor is not None:
        texto_vitoria = FONTE_TITULO.render(
            f"{vencedor['nome']} venceu o jogo!",
            True,
            PRETO
        )
        tela.blit(texto_vitoria, (LARGURA // 2 - 140, ALTURA - 80))

def selecionar_ponto(pos_mouse, vertices_globais):
    mx, my = pos_mouse
    for v in vertices_globais:
        if math.hypot(v.x - mx, v.y - my) < 15:
            return v
    return None

def jogador_tem_aldeia(jogador_atual):
    for aldeia in aldeias_construidas:
        if aldeia["jogador"] == jogador_atual:
            return True
    return False


def aldeia_conectada_ao_jogador(pos, jogador_atual):
    for estrada in estradas_construidas:
        if estrada["jogador"] == jogador_atual:
            if estrada["v1"] == pos or estrada["v2"] == pos:
                return True

    return False

def contar_aldeias_do_jogador(jogador_atual):
    total = 0

    for construcao in aldeias_construidas:
        if construcao["jogador"] == jogador_atual and construcao["tipo"] == "aldeia":
            total += 1

    return total

def contar_construcoes_tipo_do_jogador(jogador_atual, tipo):
    total = 0

    for construcao in aldeias_construidas:
        if construcao["jogador"] == jogador_atual and construcao["tipo"] == tipo:
            total += 1

    return total

def tentar_construir_aldeia(pos, vertices_globais, jogador_atual, jogadores, fase_inicial=False, limite_inicial=2):
    jogador = jogadores[jogador_atual]

    if fase_inicial and contar_construcoes_tipo_do_jogador(jogador_atual, "aldeia") >= limite_inicial:
        print("Na fase inicial, este jogador já construiu suas 2 aldeias.")
        return False

    if contar_aldeias_do_jogador(jogador_atual) >= LIMITE_ALDEIAS:
        print("Você já atingiu o limite de aldeias.")
        return False

    if not fase_inicial and not tem_recursos(jogador, CUSTO_ALDEIA):
        print("Recursos insuficientes para construir aldeia.")
        return False

    for aldeia in aldeias_construidas:
        if aldeia["vertice"] == pos:
            print("Já existe uma aldeia neste ponto.")
            return False

        if aldeia["vertice"] in pos.vizinhos:
            print("Não pode construir aldeia colada em outra aldeia.")
            return False
    
    if not fase_inicial and jogador_tem_aldeia(jogador_atual) and not aldeia_conectada_ao_jogador(pos, jogador_atual):
        print("A nova aldeia precisa estar conectada a uma estrada sua.")
        return False

    if not fase_inicial:
        gastar_recursos(jogador, CUSTO_ALDEIA)

    numero_aldeia_inicial = None

    if fase_inicial:
        numero_aldeia_inicial = contar_construcoes_tipo_do_jogador(jogador_atual, "aldeia") + 1

    aldeias_construidas.append({
        "vertice": pos,
        "jogador": jogador_atual,
        "tipo": "aldeia",
        "inicial": numero_aldeia_inicial
    })

    if fase_inicial:
        jogador["ultima_aldeia_inicial"] = pos

    jogador["pontos"] += 1

    if jogador["pontos"] >= PONTOS_PARA_VENCER:
        print(f"{jogador['nome']} venceu o jogo!")

    print(f"{jogador['nome']} construiu uma aldeia.")
    return True

def estrada_conectada_ao_jogador(pos1, pos2, jogador_atual):
    for aldeia in aldeias_construidas:
        if aldeia["jogador"] == jogador_atual:
            if aldeia["vertice"] == pos1 or aldeia["vertice"] == pos2:
                return True

    for estrada in estradas_construidas:
        if estrada["jogador"] == jogador_atual:
            if estrada["v1"] == pos1 or estrada["v2"] == pos1:
                return True
            if estrada["v1"] == pos2 or estrada["v2"] == pos2:
                return True

    return False

def contar_estradas_do_jogador(jogador_atual):
    total = 0

    for estrada in estradas_construidas:
        if estrada["jogador"] == jogador_atual:
            total += 1

    return total

def contar_estradas_iniciais_do_jogador(jogador_atual):
    total = 0

    for estrada in estradas_construidas:
        if estrada["jogador"] == jogador_atual:
            total += 1

    return total

def tentar_construir_estrada(pos1, pos2, jogador_atual, jogadores, fase_inicial=False, limite_inicial=2):
    jogador = jogadores[jogador_atual]

    if fase_inicial:
        aldeias_do_jogador = contar_construcoes_tipo_do_jogador(jogador_atual, "aldeia")
        estradas_do_jogador = contar_estradas_iniciais_do_jogador(jogador_atual)

        if aldeias_do_jogador <= estradas_do_jogador:
            print("Construa a aldeia desta rodada antes da estrada.")
            return False

        ultima_aldeia = jogador["ultima_aldeia_inicial"]

        if ultima_aldeia is None:
            print("Construa uma aldeia antes da estrada inicial.")
            return False

        if pos1 != ultima_aldeia and pos2 != ultima_aldeia:
            print("Na fase inicial, a estrada precisa sair da aldeia recém-construída.")
            return False
    
    if fase_inicial and contar_estradas_iniciais_do_jogador(jogador_atual) >= limite_inicial:
        print("Na fase inicial, este jogador já construiu suas 2 estradas.")
        return False

    if contar_estradas_do_jogador(jogador_atual) >= LIMITE_ESTRADAS:
        print("Você já atingiu o limite de estradas.")
        return False

    if not fase_inicial and not tem_recursos(jogador, CUSTO_ESTRADA):
        print("Recursos insuficientes para construir estrada.")
        return False
    
    if not estrada_conectada_ao_jogador(pos1, pos2, jogador_atual):
        print("A estrada precisa estar conectada a uma aldeia ou estrada sua.")
        return False

    for estrada in estradas_construidas:
        mesma_ordem = estrada["v1"] == pos1 and estrada["v2"] == pos2
        ordem_inversa = estrada["v1"] == pos2 and estrada["v2"] == pos1

        if mesma_ordem or ordem_inversa:
            print("Já existe uma estrada neste caminho.")
            return False
    
    if not fase_inicial:
        gastar_recursos(jogador, CUSTO_ESTRADA)

    estradas_construidas.append({
        "v1": pos1,
        "v2": pos2,
        "jogador": jogador_atual
    })

    print(f"{jogador['nome']} construiu uma estrada.")
    return True

def contar_cidades_do_jogador(jogador_atual):
    total = 0

    for construcao in aldeias_construidas:
        if construcao["jogador"] == jogador_atual and construcao["tipo"] == "cidade":
            total += 1

    return total

def tentar_construir_cidade(pos, jogador_atual, jogadores):
    jogador = jogadores[jogador_atual]

    if contar_cidades_do_jogador(jogador_atual) >= LIMITE_CIDADES:
        print("Você já atingiu o limite de cidades.")
        return False

    for construcao in aldeias_construidas:
        if construcao["vertice"] == pos and construcao["jogador"] == jogador_atual:
            if construcao["tipo"] == "cidade":
                print("Este local já é uma cidade.")
                return False

            if not tem_recursos(jogador, CUSTO_CIDADE):
                print("Recursos insuficientes para construir cidade.")
                return False

            gastar_recursos(jogador, CUSTO_CIDADE)
            construcao["tipo"] = "cidade"
            jogador["pontos"] += 1

            print(f"{jogador['nome']} construiu uma cidade.")
            return True

    print("Você só pode construir cidade em uma aldeia sua.")
    return False

def distribuir_recursos(tabuleiro, dado, jogadores, ladrao):
    for peca in tabuleiro:
        if peca == ladrao:
            continue

        if peca['numero'] == dado and peca['cor'] != DESERTO:
            recurso = MAPA_RECURSOS[peca['cor']]

            for v in peca['vertices']:
                for aldeia in aldeias_construidas:
                    vertice_aldeia = aldeia["vertice"]
                    dono = aldeia["jogador"]

                    if math.hypot(v[0] - vertice_aldeia.x, v[1] - vertice_aldeia.y) < 5:
                        if aldeia["tipo"] == "cidade":
                            quantidade = 2
                        else:
                            quantidade = 1

                        jogadores[dono]["inventario"][recurso] += quantidade
                        print(f"{jogadores[dono]['nome']} recebeu {quantidade} {recurso}")

def passar_turno(jogador_atual, jogadores):
    jogador_atual = (jogador_atual + 1) % len(jogadores)
    print(f"Agora é a vez de: {jogadores[jogador_atual]['nome']}")
    return jogador_atual

def tem_recursos(jogador, custo):
    for recurso, quantidade in custo.items():
        if jogador["inventario"][recurso] < quantidade:
            return False
    return True


def gastar_recursos(jogador, custo):
    for recurso, quantidade in custo.items():
        jogador["inventario"][recurso] -= quantidade

CUSTO_ALDEIA = {
    "Madeira": 1,
    "Tijolo": 1,
    "Ovelha": 1,
    "Trigo": 1
}

CUSTO_ESTRADA = {
    "Madeira": 1,
    "Tijolo": 1
}

CUSTO_CIDADE = {
    "Trigo": 2,
    "Minério": 3
}

PONTOS_PARA_VENCER = 10
LIMITE_ALDEIAS = 5
LIMITE_CIDADES = 4
LIMITE_ESTRADAS = 15

def verificar_vencedor(jogadores):
    for jogador in jogadores:
        if jogador["pontos"] >= PONTOS_PARA_VENCER:
            return jogador
    return None

def dar_recursos_teste(jogador):
    jogador["inventario"]["Madeira"] += 1
    jogador["inventario"]["Tijolo"] += 1
    jogador["inventario"]["Ovelha"] += 1
    jogador["inventario"]["Trigo"] += 1
    jogador["inventario"]["Minério"] += 1

def bot_tentar_construir_aldeia(jogador_atual, jogadores, vertices_globais, fase_inicial=False, limite_inicial=2):
    jogador = jogadores[jogador_atual]

    if not fase_inicial and not tem_recursos(jogador, CUSTO_ALDEIA):
        return False

    vertices_embaralhados = vertices_globais.copy()
    random.shuffle(vertices_embaralhados)

    for v in vertices_embaralhados:
        if tentar_construir_aldeia(v, vertices_globais, jogador_atual, jogadores, fase_inicial, limite_inicial):
            return True

    return False

def bot_tentar_construir_estrada(jogador_atual, jogadores, fase_inicial=False, limite_inicial=2):
    jogador = jogadores[jogador_atual]

    if not fase_inicial and not tem_recursos(jogador, CUSTO_ESTRADA):
        return False

    caminhos_possiveis = []

    for aldeia in aldeias_construidas:
        if aldeia["jogador"] == jogador_atual:
            v_origem = aldeia["vertice"]

            for vizinho in v_origem.vizinhos:
                caminhos_possiveis.append((v_origem, vizinho))

    for estrada in estradas_construidas:
        if estrada["jogador"] == jogador_atual:
            for vizinho in estrada["v1"].vizinhos:
                caminhos_possiveis.append((estrada["v1"], vizinho))

            for vizinho in estrada["v2"].vizinhos:
                caminhos_possiveis.append((estrada["v2"], vizinho))

    random.shuffle(caminhos_possiveis)

    for pos1, pos2 in caminhos_possiveis:
        if tentar_construir_estrada(pos1, pos2, jogador_atual, jogadores, fase_inicial, limite_inicial):
            return True

    return False

def bot_tentar_construir_cidade(jogador_atual, jogadores):
    jogador = jogadores[jogador_atual]

    if not tem_recursos(jogador, CUSTO_CIDADE):
        return False

    aldeias_do_bot = []

    for construcao in aldeias_construidas:
        if construcao["jogador"] == jogador_atual and construcao["tipo"] == "aldeia":
            aldeias_do_bot.append(construcao["vertice"])

    random.shuffle(aldeias_do_bot)

    for vertice in aldeias_do_bot:
        if tentar_construir_cidade(vertice, jogador_atual, jogadores):
            return True

    return False

def dar_recursos_teste_para_todos(jogadores):
    for jogador in jogadores:
        dar_recursos_teste(jogador)

    print("Recursos de teste adicionados para todos.")

def fase_inicial_completa(jogadores):
    for i in range(len(jogadores)):
        tem_aldeia = contar_construcoes_tipo_do_jogador(i, "aldeia") >= 2
        tem_estrada = contar_estradas_iniciais_do_jogador(i) >= 2

        if not tem_aldeia or not tem_estrada:
            return False

    return True

def distribuir_recursos_iniciais(tabuleiro, jogadores):
    for aldeia in aldeias_construidas:
        if aldeia.get("inicial") != 2:
            continue

        vertice_aldeia = aldeia["vertice"]
        dono = aldeia["jogador"]

        for peca in tabuleiro:
            if peca["cor"] == DESERTO:
                continue

            recurso = MAPA_RECURSOS[peca["cor"]]

            for v in peca["vertices"]:
                if math.hypot(v[0] - vertice_aldeia.x, v[1] - vertice_aldeia.y) < 5:
                    jogadores[dono]["inventario"][recurso] += 1
                    print(f"{jogadores[dono]['nome']} recebeu 1 {recurso} inicial")

def criar_ordem_fase_inicial(jogadores):
    ordem_ida = list(range(len(jogadores)))
    ordem_volta = list(reversed(range(len(jogadores))))
    return ordem_ida + ordem_volta

def limite_fase_inicial_atual(indice_fase_inicial, jogadores):
    if indice_fase_inicial < len(jogadores):
        return 1
    return 2

def jogador_completou_rodada_inicial(jogador_atual, indice_fase_inicial, jogadores):
    limite_inicial = limite_fase_inicial_atual(indice_fase_inicial, jogadores)

    aldeias = contar_construcoes_tipo_do_jogador(jogador_atual, "aldeia")
    estradas = contar_estradas_iniciais_do_jogador(jogador_atual)

    return aldeias >= limite_inicial and estradas >= limite_inicial

def limpar_dados_fase_inicial(jogadores):
    for jogador in jogadores:
        jogador["ultima_aldeia_inicial"] = None

def encontrar_deserto(tabuleiro):
    for peca in tabuleiro:
        if peca["cor"] == DESERTO:
            return peca
    return None

def mover_ladrao_aleatorio(tabuleiro, ladrao_atual):
    opcoes = []

    for peca in tabuleiro:
        if peca != ladrao_atual:
            opcoes.append(peca)

    if len(opcoes) > 0:
        return random.choice(opcoes)

    return ladrao_atual

def roubar_recurso_ladrao(ladrao, jogador_atual, jogadores):
    possiveis_vitimas = []

    for aldeia in aldeias_construidas:
        dono = aldeia["jogador"]

        if dono == jogador_atual:
            continue

        vertice_aldeia = aldeia["vertice"]

        for v in ladrao["vertices"]:
            if math.hypot(v[0] - vertice_aldeia.x, v[1] - vertice_aldeia.y) < 5:
                possiveis_vitimas.append(dono)
                break

    if len(possiveis_vitimas) == 0:
        mensagem = "Nao ha jogadores para roubar neste hexagono."
        print(mensagem)
        return mensagem

    vitima_indice = random.choice(possiveis_vitimas)
    vitima = jogadores[vitima_indice]
    jogador = jogadores[jogador_atual]

    recursos_disponiveis = []

    for recurso, quantidade in vitima["inventario"].items():
        if quantidade > 0:
            recursos_disponiveis.append(recurso)

    if len(recursos_disponiveis) == 0:
        mensagem = f"{vitima['nome']} nao tinha recursos para roubar."
        print(mensagem)
        return mensagem

    recurso_roubado = random.choice(recursos_disponiveis)

    vitima["inventario"][recurso_roubado] -= 1
    jogador["inventario"][recurso_roubado] += 1

    mensagem = f"{jogador['nome']} roubou 1 {recurso_roubado} de {vitima['nome']}."
    print(mensagem)
    return mensagem

def ponto_dentro_poligono(x, y, pontos):
    dentro = False
    j = len(pontos) - 1

    for i in range(len(pontos)):
        xi, yi = pontos[i]
        xj, yj = pontos[j]

        if (yi > y) != (yj > y):
            x_intersecao = (xj - xi) * (y - yi) / (yj - yi) + xi

            if x < x_intersecao:
                dentro = not dentro

        j = i

    return dentro


def selecionar_hexagono(pos_mouse, tabuleiro):
    mx, my = pos_mouse

    for peca in tabuleiro:
        if ponto_dentro_poligono(mx, my, peca["vertices"]):
            return peca

    return None

def encontrar_vitimas_ladrao(ladrao, jogador_atual):
    vitimas = []

    for aldeia in aldeias_construidas:
        dono = aldeia["jogador"]

        if dono == jogador_atual:
            continue

        vertice_aldeia = aldeia["vertice"]

        for v in ladrao["vertices"]:
            if math.hypot(v[0] - vertice_aldeia.x, v[1] - vertice_aldeia.y) < 5:
                if dono not in vitimas:
                    vitimas.append(dono)
                break

    return vitimas

def roubar_recurso_de_vitima(jogador_atual, vitima_indice, jogadores):
    jogador = jogadores[jogador_atual]
    vitima = jogadores[vitima_indice]

    recursos_disponiveis = []

    for recurso, quantidade in vitima["inventario"].items():
        if quantidade > 0:
            recursos_disponiveis.append(recurso)

    if len(recursos_disponiveis) == 0:
        mensagem = f"{vitima['nome']} nao tinha recursos para roubar."
        print(mensagem)
        return mensagem

    recurso_roubado = random.choice(recursos_disponiveis)

    vitima["inventario"][recurso_roubado] -= 1
    jogador["inventario"][recurso_roubado] += 1

    mensagem = f"{jogador['nome']} roubou 1 {recurso_roubado} de {vitima['nome']}."
    print(mensagem)
    return mensagem

RECURSOS = ["Madeira", "Tijolo", "Ovelha", "Trigo", "Minério"]

def total_recursos(jogador):
    return sum(jogador["inventario"].values())


def quantidade_para_descartar(jogador):
    return total_recursos(jogador) // 2


def criar_fila_descarte(jogadores):
    fila = []

    for i, jogador in enumerate(jogadores):
        if total_recursos(jogador) > 7:
            fila.append(i)

    return fila


def bot_descartar_recursos(jogador):
    quantidade = quantidade_para_descartar(jogador)
    descartados = []

    while quantidade > 0:
        recursos_disponiveis = []

        for recurso in RECURSOS:
            if jogador["inventario"][recurso] > 0:
                recursos_disponiveis.append(recurso)

        if len(recursos_disponiveis) == 0:
            break

        recurso_escolhido = random.choice(recursos_disponiveis)
        jogador["inventario"][recurso_escolhido] -= 1
        descartados.append(recurso_escolhido)
        quantidade -= 1

    mensagem = f"{jogador['nome']} descartou {len(descartados)} recurso(s)."
    print(mensagem)
    return mensagem


def preparar_proximo_descarte(fila_descarte, jogadores):
    mensagens_bot = []

    while len(fila_descarte) > 0 and jogadores[fila_descarte[0]]["tipo"] == "bot":
        bot_indice = fila_descarte.pop(0)
        mensagem_bot = bot_descartar_recursos(jogadores[bot_indice])
        mensagens_bot.append(mensagem_bot)

    if len(fila_descarte) > 0:
        jogador_indice = fila_descarte[0]
        quantidade = quantidade_para_descartar(jogadores[jogador_indice])

        return {
            "descartando": True,
            "jogador_descartando": jogador_indice,
            "quantidade_para_descartar": quantidade,
            "quantidade_descartada": 0,
            "mensagem": f"{jogadores[jogador_indice]['nome']} deve descartar {quantidade} recurso(s)."
        }

    mensagem = "Descarte concluido."

    if len(mensagens_bot) > 0:
        mensagem = " ".join(mensagens_bot) + " " + mensagem

    return {
        "descartando": False,
        "jogador_descartando": None,
        "quantidade_para_descartar": 0,
        "quantidade_descartada": 0,
        "mensagem": mensagem
    }

def main(game_mode="custom", num_players=2, num_humanos=2):
    relogio = pygame.time.Clock()
    tabuleiro, vertices_globais = gerar_tabuleiro()
    ladrao = encontrar_deserto(tabuleiro)
    escolhendo_ladrao = False
    jogador_movendo_ladrao = None
    escolhendo_vitima_ladrao = False
    vitimas_ladrao = []
    descartando_recursos = False
    fila_descarte = []
    jogador_descartando = None
    quantidade_descartar = 0
    quantidade_descartada = 0
    jogador_que_rolou_7 = None
    ultimo_dado = 0
    mensagem_jogo = ""
    vertice_selecionado = None
    jogadores = criar_jogadores(num_players, num_humanos)
    jogador_atual = 0
    tempo_turno_bot = 0
    dado_rolado_no_turno = False
    vencedor = None
    fase_inicial = True
    ordem_fase_inicial = criar_ordem_fase_inicial(jogadores)
    indice_fase_inicial = 0
    jogador_atual = ordem_fase_inicial[indice_fase_inicial]
    
    def iniciar_ladrao_apos_descarte():
        nonlocal escolhendo_ladrao
        nonlocal jogador_movendo_ladrao
        nonlocal ladrao
        nonlocal mensagem_jogo
        nonlocal escolhendo_vitima_ladrao
        nonlocal vitimas_ladrao
        nonlocal jogador_que_rolou_7

        if jogadores[jogador_que_rolou_7]["tipo"] == "humano":
            escolhendo_ladrao = True
            jogador_movendo_ladrao = jogador_que_rolou_7
            mensagem_jogo = "Clique em um terreno para mover o ladrao."
        else:
            ladrao = mover_ladrao_aleatorio(tabuleiro, ladrao)

            vitimas_ladrao_bot = encontrar_vitimas_ladrao(ladrao, jogador_que_rolou_7)

            if len(vitimas_ladrao_bot) == 0:
                mensagem_jogo = "Saiu 7! Ladrao movido. Nao ha vitimas para roubar."
            else:
                vitima_escolhida = random.choice(vitimas_ladrao_bot)
                mensagem_roubo = roubar_recurso_de_vitima(
                    jogador_que_rolou_7,
                    vitima_escolhida,
                    jogadores
                )
                mensagem_jogo = f"Saiu 7! Ladrao movido. {mensagem_roubo}"

            jogador_que_rolou_7 = None

    print(f"Modo de jogo iniciado: {game_mode}")
    print(f"Jogadores criados: {[j['nome'] for j in jogadores]}")
    
    rodando = True
    while rodando:
        TELA.fill(COR_FUNDO)

        vencedor = verificar_vencedor(jogadores)

        if fase_inicial and fase_inicial_completa(jogadores):
            distribuir_recursos_iniciais(tabuleiro, jogadores)
            limpar_dados_fase_inicial(jogadores)
            fase_inicial = False
            print("Fase inicial encerrada automaticamente. O jogo normal começou.")
            
        jogador = jogadores[jogador_atual]

        if jogador["tipo"] == "bot" and vencedor is None:
            tempo_turno_bot += 1

            if tempo_turno_bot >= 60:
                if fase_inicial:
                    print(f"{jogador['nome']} está posicionando peças iniciais.")
                    limite_inicial = 2

                    if fase_inicial:
                        limite_inicial = limite_fase_inicial_atual(indice_fase_inicial, jogadores)

                    bot_tentar_construir_aldeia(
                        jogador_atual,
                        jogadores,
                        vertices_globais,
                        fase_inicial,
                        limite_inicial
                    )

                    bot_tentar_construir_estrada(
                        jogador_atual,
                        jogadores,
                        fase_inicial,
                        limite_inicial
                    )

                    if not jogador_completou_rodada_inicial(jogador_atual, indice_fase_inicial, jogadores):
                        print(f"{jogador['nome']} ainda não conseguiu posicionar tudo.")
                        tempo_turno_bot = 0
                        continue

                else:
                    ultimo_dado = random.randint(1, 6) + random.randint(1, 6)
                    
                    if ultimo_dado == 7:
                        jogador_que_rolou_7 = jogador_atual
                        fila_descarte = criar_fila_descarte(jogadores)

                        estado_descarte = preparar_proximo_descarte(fila_descarte, jogadores)

                        descartando_recursos = estado_descarte["descartando"]
                        jogador_descartando = estado_descarte["jogador_descartando"]
                        quantidade_descartar = estado_descarte["quantidade_para_descartar"]
                        quantidade_descartada = estado_descarte["quantidade_descartada"]
                        mensagem_jogo = estado_descarte["mensagem"]

                        if not descartando_recursos:
                            iniciar_ladrao_apos_descarte()
                    else:
                        mensagem_jogo = ""
                        distribuir_recursos(tabuleiro, ultimo_dado, jogadores, ladrao)

                    print(f"{jogador['nome']} rolou o dado: {ultimo_dado}")

                    if not bot_tentar_construir_cidade(jogador_atual, jogadores):
                        if not bot_tentar_construir_aldeia(
                            jogador_atual,
                            jogadores,
                            vertices_globais,
                            fase_inicial
                        ):
                            bot_tentar_construir_estrada(
                                jogador_atual,
                                jogadores,
                                fase_inicial
                            )

                if fase_inicial:
                    indice_fase_inicial += 1

                    if indice_fase_inicial < len(ordem_fase_inicial):
                        jogador_atual = ordem_fase_inicial[indice_fase_inicial]
                        print(f"Fase inicial: agora é a vez de {jogadores[jogador_atual]['nome']}")
                    else:
                        print("Todos já fizeram suas jogadas iniciais.")
                else:
                    jogador_atual = passar_turno(jogador_atual, jogadores)
                    dado_rolado_no_turno = False

                tempo_turno_bot = 0
        else:
            tempo_turno_bot = 0

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            elif vencedor is not None:
                continue
                
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    if descartando_recursos:
                        mensagem_jogo = "Termine o descarte antes de continuar."
                        continue
                    if escolhendo_ladrao:
                        novo_ladrao = selecionar_hexagono(evento.pos, tabuleiro)

                        if novo_ladrao is not None and novo_ladrao != ladrao:
                            ladrao = novo_ladrao

                            vitimas_ladrao = encontrar_vitimas_ladrao(ladrao, jogador_movendo_ladrao)
                            print("Vitimas possiveis:", [jogadores[i]["nome"] for i in vitimas_ladrao])

                            if len(vitimas_ladrao) == 0:
                                mensagem_jogo = "Ladrao movido. Nao ha vitimas para roubar."
                                escolhendo_ladrao = False
                                jogador_movendo_ladrao = None

                            elif len(vitimas_ladrao) == 1:
                                mensagem_roubo = roubar_recurso_de_vitima(
                                    jogador_movendo_ladrao,
                                    vitimas_ladrao[0],
                                    jogadores
                                )
                                mensagem_jogo = f"Ladrao movido. {mensagem_roubo}"
                                escolhendo_ladrao = False
                                jogador_movendo_ladrao = None

                            else:
                                escolhendo_vitima_ladrao = True
                                mensagem_jogo = "Escolha a vitima: pressione 1, 2, 3..."
                                escolhendo_ladrao = False

                        elif novo_ladrao == ladrao:
                            mensagem_jogo = "Escolha um terreno diferente."

                        else:
                            mensagem_jogo = "Clique em um terreno valido."

                        continue

                    if vertice_selecionado == None:
                        vertice_selecionado = selecionar_ponto(evento.pos, vertices_globais)
                    else:
                        if math.dist(evento.pos, vertice_selecionado.pos) < 10:
                            limite_inicial = 2

                            if fase_inicial:
                                limite_inicial = limite_fase_inicial_atual(indice_fase_inicial, jogadores)

                            if not fase_inicial and not dado_rolado_no_turno:
                                print("Você precisa rolar o dado antes de construir.")
                            else:
                                tentar_construir_aldeia(
                                    vertice_selecionado,
                                    vertices_globais,
                                    jogador_atual,
                                    jogadores,
                                    fase_inicial,
                                    limite_inicial
                                )

                            vertice_selecionado = None

                        else:
                            estrada_tentada = False

                            for v in vertice_selecionado.vizinhos:
                                dist = abs(
                                    (vertice_selecionado.y - v.y) * evento.pos[0]
                                    - (vertice_selecionado.x - v.x) * evento.pos[1]
                                    + vertice_selecionado.x * v.y
                                    - vertice_selecionado.y * v.x
                                ) / math.dist(v.pos, vertice_selecionado.pos)

                                if dist <= 5:
                                    limite_inicial = 2

                                    if fase_inicial:
                                        limite_inicial = limite_fase_inicial_atual(indice_fase_inicial, jogadores)

                                    if not fase_inicial and not dado_rolado_no_turno:
                                        print("Você precisa rolar o dado antes de construir.")
                                    else:
                                        tentar_construir_estrada(
                                            vertice_selecionado,
                                            v,
                                            jogador_atual,
                                            jogadores,
                                            fase_inicial,
                                            limite_inicial
                                        )  
                                    estrada_tentada = True
                                    break

                            if not estrada_tentada:
                                vertice_selecionado = selecionar_ponto(evento.pos, vertices_globais)
                            else:
                                vertice_selecionado = None
                    
            elif evento.type == pygame.KEYDOWN:
                if escolhendo_vitima_ladrao:
                    if pygame.K_1 <= evento.key <= pygame.K_9:
                        escolha = evento.key - pygame.K_1

                        if escolha < len(vitimas_ladrao):
                            vitima_indice = vitimas_ladrao[escolha]

                            mensagem_roubo = roubar_recurso_de_vitima(
                                jogador_movendo_ladrao,
                                vitima_indice,
                                jogadores
                            )

                            mensagem_jogo = mensagem_roubo
                            escolhendo_vitima_ladrao = False
                            vitimas_ladrao = []
                            jogador_movendo_ladrao = None
                        else:
                            mensagem_jogo = "Vitima invalida."

                    continue
                
                if descartando_recursos:
                    teclas_recursos = {
                        pygame.K_1: "Madeira",
                        pygame.K_2: "Tijolo",
                        pygame.K_3: "Ovelha",
                        pygame.K_4: "Trigo",
                        pygame.K_5: "Minério"
                    }

                    if evento.key in teclas_recursos:
                        recurso = teclas_recursos[evento.key]
                        jogador_descarte = jogadores[jogador_descartando]

                        if jogador_descarte["inventario"][recurso] > 0:
                            jogador_descarte["inventario"][recurso] -= 1
                            quantidade_descartada += 1

                            restante = quantidade_descartar - quantidade_descartada
                            mensagem_jogo = f"{jogador_descarte['nome']} descartou 1 {recurso}. Faltam {restante}."

                            if quantidade_descartada >= quantidade_descartar:
                                fila_descarte.pop(0)

                                estado_descarte = preparar_proximo_descarte(fila_descarte, jogadores)

                                descartando_recursos = estado_descarte["descartando"]
                                jogador_descartando = estado_descarte["jogador_descartando"]
                                quantidade_descartar = estado_descarte["quantidade_para_descartar"]
                                quantidade_descartada = estado_descarte["quantidade_descartada"]
                                mensagem_jogo = estado_descarte["mensagem"]

                                if not descartando_recursos:
                                    iniciar_ladrao_apos_descarte()
                        else:
                            mensagem_jogo = f"{jogador_descarte['nome']} nao tem {recurso} para descartar."

                    continue

                if evento.key == pygame.K_SPACE:
                    if fase_inicial:
                        print("Não é possível rolar dados durante a fase inicial.")

                    elif not dado_rolado_no_turno:
                        ultimo_dado = random.randint(1, 6) + random.randint(1, 6)
                        
                        if ultimo_dado == 7:
                            jogador_que_rolou_7 = jogador_atual
                            fila_descarte = criar_fila_descarte(jogadores)

                            estado_descarte = preparar_proximo_descarte(fila_descarte, jogadores)

                            descartando_recursos = estado_descarte["descartando"]
                            jogador_descartando = estado_descarte["jogador_descartando"]
                            quantidade_descartar = estado_descarte["quantidade_para_descartar"]
                            quantidade_descartada = estado_descarte["quantidade_descartada"]
                            mensagem_jogo = estado_descarte["mensagem"]

                            if not descartando_recursos:
                                iniciar_ladrao_apos_descarte()
                        else:
                            mensagem_jogo = ""
                            distribuir_recursos(tabuleiro, ultimo_dado, jogadores, ladrao)
                        
                        dado_rolado_no_turno = True
                        print(f"{jogadores[jogador_atual]['nome']} rolou o dado: {ultimo_dado}")

                    else:
                        print("Você já rolou o dado neste turno.")
                
                elif evento.key == pygame.K_RETURN:
                        if fase_inicial:
                            if not jogador_completou_rodada_inicial(jogador_atual, indice_fase_inicial, jogadores):
                                print("Você precisa construir 1 aldeia e 1 estrada antes de passar.")
                            else:
                                indice_fase_inicial += 1

                                if indice_fase_inicial < len(ordem_fase_inicial):
                                    jogador_atual = ordem_fase_inicial[indice_fase_inicial]
                                    print(f"Fase inicial: agora é a vez de {jogadores[jogador_atual]['nome']}")
                                else:
                                    print("Todos já fizeram suas jogadas iniciais.")

                        else:
                            if not dado_rolado_no_turno:
                                print("Você precisa rolar o dado antes de passar o turno.")
                            else:
                                jogador_atual = passar_turno(jogador_atual, jogadores)
                                dado_rolado_no_turno = False
                
                elif evento.key == pygame.K_t:
                    dar_recursos_teste(jogadores[jogador_atual])
                    print(f"Recursos adicionados para {jogadores[jogador_atual]['nome']}")
                
                elif evento.key == pygame.K_y:
                    dar_recursos_teste_para_todos(jogadores)
                
                elif evento.key == pygame.K_i:
                    fase_inicial = False
                    print("Fase inicial encerrada. O jogo normal começou.")

                elif evento.key == pygame.K_c:
                    if fase_inicial:
                        print("Não é possível construir cidade durante a fase inicial.")

                    elif vertice_selecionado is not None:
                        if not dado_rolado_no_turno:
                            print("Você precisa rolar o dado antes de construir.")
                        else:
                            tentar_construir_cidade(vertice_selecionado, jogador_atual, jogadores)

                        vertice_selecionado = None

                    else:
                        print("Selecione uma aldeia sua antes de apertar C.")

        desenhar_tabuleiro(TELA, tabuleiro, ultimo_dado, ladrao)
        desenhar_vertices_e_aldeias(TELA, vertices_globais, vertice_selecionado, jogadores)
        jogador_interface = jogadores[jogador_atual]

        if descartando_recursos and jogador_descartando is not None:
            jogador_interface = jogadores[jogador_descartando]

        desenhar_interface(
            TELA,
            ultimo_dado,
            game_mode,
            jogador_interface,
            vencedor,
            fase_inicial,
            jogadores,
            mensagem_jogo,
            escolhendo_vitima_ladrao,
            vitimas_ladrao,
            descartando_recursos,
            jogador_descartando,
            quantidade_descartar,
            quantidade_descartada
        )
        
        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()