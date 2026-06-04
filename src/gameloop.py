import pygame
import math
import random
import sys

pygame.init()
LARGURA, ALTURA = 1200, 700
PAINEL_X = 930
PAINEL_LARGURA = 270
AREA_MAPA_LARGURA = 900

BARRA_INFERIOR_ALTURA = 145
BARRA_INFERIOR_Y = ALTURA - BARRA_INFERIOR_ALTURA

TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("CATAN")
FONTE_NUMEROS = pygame.font.SysFont("Arial", 24, bold=True)
FONTE_TEXTO = pygame.font.SysFont("Arial", 22)
FONTE_TITULO = pygame.font.SysFont("Arial", 26, bold=True)
FONTE_CONTROLES = pygame.font.SysFont("Arial", 18)

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
            "pontos_vitoria_ocultos": 0,
            "ultima_aldeia_inicial": None,
            "cartas_dev": [],
            "cartas_dev_compradas_turno": [],
            "cavaleiros_usados": 0,
            "maior_exercito": False,
            "maior_estrada": False,
            "usou_carta_dev_turno": False
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

def desenhar_barra_inferior(tela):
    pygame.draw.rect(
        tela,
        (220, 235, 240),
        (0, BARRA_INFERIOR_Y, PAINEL_X, BARRA_INFERIOR_ALTURA)
    )
    pygame.draw.line(
        tela,
        PRETO,
        (0, BARRA_INFERIOR_Y),
        (PAINEL_X, BARRA_INFERIOR_Y),
        2
    )

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
    
    centro_tela_x = AREA_MAPA_LARGURA // 2
    centro_tela_y = 175
    
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

    



def desenhar_interface(tela, ultimo_dado, game_mode, jogador_atual, vencedor, fase_inicial, jogadores, mensagem_jogo, escolhendo_vitima_ladrao, vitimas_ladrao, descartando_recursos, jogador_descartando, quantidade_descartar, quantidade_descartada, trocando_banco, recurso_entregar_banco, trocando_jogador, etapa_troca_jogador, troca_jogador, portos, usando_construcao_estradas, estradas_gratis_restantes, usando_ano_fartura, recursos_ano_fartura, usando_monopolio, historico_dados, escolhendo_ladrao, banco_recursos):
    pygame.draw.rect(tela, (180, 220, 235), (PAINEL_X, 0, PAINEL_LARGURA, ALTURA))
    pygame.draw.line(tela, PRETO, (PAINEL_X, 0), (PAINEL_X, ALTURA), 2)
    desenhar_barra_inferior(tela)

    if len(historico_dados) == 0:
        texto_hist = FONTE_TITULO.render(
            "Historico dos dados: nenhum dado rolado ainda.",
            True,
            PRETO
        )
        tela.blit(texto_hist, (20, 20))
        y_dados = 55
    else:
        tela.blit(FONTE_TITULO.render("Historico dos dados:", True, PRETO), (20, 20))
        y_dados = 55

        for item in historico_dados[-5:]:
            texto_dado = FONTE_TEXTO.render(item, True, PRETO)
            tela.blit(texto_dado, (20, y_dados))
            y_dados += 24

    linhas_status = []

    if descartando_recursos:
        linhas_status.append(
            f"Descarte: {jogadores[jogador_descartando]['nome']} deve descartar "
            f"{quantidade_descartar - quantidade_descartada} recurso(s)."
        )
        linhas_status.append("Escolha: 1 Madeira | 2 Tijolo | 3 Ovelha | 4 Trigo | 5 Minerio")
    
    elif escolhendo_ladrao:
        linhas_status.append("Ladrao: clique em um terreno diferente para mover o ladrao.")

    elif escolhendo_vitima_ladrao:
        linhas_status.append("Ladrao: escolha a vitima.")
        opcoes = []
        numero = 1
        for vitima in vitimas_ladrao:
            opcoes.append(f"{numero}-{jogadores[vitima]['nome']}")
            numero += 1
        if opcoes:
            linhas_status.append(" | ".join(opcoes))

    elif trocando_banco:
        if recurso_entregar_banco is None:
            linhas_status.append("Banco/Porto: escolha o recurso para entregar.")
            linhas_status.append("1 Madeira | 2 Tijolo | 3 Ovelha | 4 Trigo | 5 Minerio")
        else:
            taxa = taxa_troca_banco(jogador_atual["indice"], recurso_entregar_banco, portos)
            linhas_status.append(f"Banco {taxa}:1 - entregando {recurso_entregar_banco}.")
            linhas_status.append("Escolha o recurso para receber: 1 Mad | 2 Tij | 3 Ove | 4 Tri | 5 Min")

    elif trocando_jogador:
        textos_etapas = {
            "escolher_alvo": "Troca entre jogadores: escolha com quem deseja trocar",
            "recurso_oferecido": "Troca entre jogadores: escolha o recurso que voce vai oferecer",
            "quantidade_oferecida": "Troca entre jogadores: escolha quanto voce vai oferecer",
            "recurso_pedido": "Troca entre jogadores: escolha o recurso que voce quer receber",
            "quantidade_pedida": "Troca entre jogadores: escolha quanto voce quer receber",
            "confirmar": "Troca entre jogadores: aguardando resposta"
        }

        linhas_status.append(textos_etapas.get(etapa_troca_jogador, "Troca entre jogadores"))

        if etapa_troca_jogador == "escolher_alvo":
            nomes = []
            numero_opcao = 1
            for i, jogador in enumerate(jogadores):
                if i != jogador_atual["indice"]:
                    nomes.append(f"{numero_opcao}-{jogador['nome']}")
                    numero_opcao += 1
            linhas_status.append(" | ".join(nomes))

        elif etapa_troca_jogador in ["recurso_oferecido", "recurso_pedido"]:
            linhas_status.append("1 Madeira | 2 Tijolo | 3 Ovelha | 4 Trigo | 5 Minerio")

        elif etapa_troca_jogador in ["quantidade_oferecida", "quantidade_pedida"]:
            linhas_status.append("Escolha quantidade: 1 a 9")

        elif etapa_troca_jogador == "confirmar":
            alvo = jogadores[troca_jogador["alvo"]]
            linhas_status.append(
                f"{alvo['nome']}: S aceita | N recusa"
            )

    elif usando_construcao_estradas:
        linhas_status.append(f"Construcao de Estradas ativa: faltam {estradas_gratis_restantes} estrada(s).")

    elif usando_ano_fartura:
        faltam = 2 - len(recursos_ano_fartura)

        if mensagem_jogo != "":
            linhas_status.append(mensagem_jogo)
        else:
            linhas_status.append(f"Ano de Fartura: escolha {faltam} recurso(s).")

        linhas_status.append("1 Madeira | 2 Tijolo | 3 Ovelha | 4 Trigo | 5 Minerio")
        
    elif usando_monopolio:
        linhas_status.append("Monopolio: escolha o recurso.")
        linhas_status.append("1 Madeira | 2 Tijolo | 3 Ovelha | 4 Trigo | 5 Minerio")

    elif fase_inicial:
        linhas_status.append("Fase inicial: construa 2 aldeias e 2 estradas.")
        aldeias_iniciais = contar_construcoes_tipo_do_jogador(jogador_atual["indice"], "aldeia")
        estradas_iniciais = contar_estradas_iniciais_do_jogador(jogador_atual["indice"])
        linhas_status.append(f"Iniciais: {aldeias_iniciais}/2 aldeias | {estradas_iniciais}/2 estradas")

    elif mensagem_jogo != "":
        linhas_status.append(mensagem_jogo)
        
    y_status = BARRA_INFERIOR_Y + 12
    for linha in linhas_status[:2]:
        texto_status = FONTE_TEXTO.render(linha, True, PRETO)
        tela.blit(texto_status, (20, y_status))
        y_status += 26 

    # =========================
    # PAINEL LATERAL
    # =========================

    # titulo jogador atual
    tela.blit(FONTE_TITULO.render("Jogador atual", True, PRETO), (PAINEL_X + 20, 20))

    pygame.draw.circle(tela, jogador_atual["cor"], (PAINEL_X + 30, 60), 10)
    texto_nome_atual = FONTE_TEXTO.render(
        f"{jogador_atual['nome']} ({jogador_atual['tipo']})",
        True,
        PRETO
    )
    tela.blit(texto_nome_atual, (PAINEL_X + 50, 48))

    texto_pts_atual = FONTE_TEXTO.render(f"Pontos: {jogador_atual['pontos']}", True, PRETO)
    tela.blit(texto_pts_atual, (PAINEL_X + 20, 80))

    # inventario
    tela.blit(FONTE_TITULO.render("Inventario", True, PRETO), (PAINEL_X + 20, 120))
    y_inv = 155
    for recurso, quantidade in jogador_atual["inventario"].items():
        texto_rec = FONTE_TEXTO.render(f"{recurso}: {quantidade}", True, PRETO)
        tela.blit(texto_rec, (PAINEL_X + 20, y_inv))
        y_inv += 28

    # desenvolvimento
    tela.blit(FONTE_TITULO.render("Desenvolvimento", True, PRETO), (PAINEL_X + 20, 295))

    cartas = jogador_atual["cartas_dev"]
    cavaleiros_na_mao = cartas.count("Cavaleiro")
    pontos_vitoria_dev = cartas.count("Ponto de Vitoria")
    construcao_estradas = cartas.count("Construcao de Estradas")
    ano_fartura = cartas.count("Ano de Fartura")
    monopolio = cartas.count("Monopolio")

    linhas_dev = [
        f"Cartas totais: {len(cartas)}",
        f"Cavaleiro na mao: {cavaleiros_na_mao}",
        f"Cavaleiros usados: {jogador_atual['cavaleiros_usados']}",
        f"Ponto de Vitoria: {pontos_vitoria_dev}",
        f"Construcao de Estradas: {construcao_estradas}",
        f"Ano de Fartura: {ano_fartura}",
        f"Monopolio: {monopolio}",
        f"Maior Exercito: {nome_dono_maior_exercito(jogadores)}",
        f"Maior Estrada: {nome_dono_maior_estrada(jogadores)}",
    ]

    y_dev = 330
    for linha in linhas_dev:
        texto_linha = FONTE_TEXTO.render(linha, True, PRETO)
        tela.blit(texto_linha, (PAINEL_X + 20, y_dev))
        y_dev += 22

    # todos os jogadores
    tela.blit(FONTE_TITULO.render("Jogadores", True, PRETO), (PAINEL_X + 20, 545))

    y_jogs = 580
    for jogador in jogadores:
        pygame.draw.circle(tela, jogador["cor"], (PAINEL_X + 30, y_jogs + 8), 8)

        extras = []
        if jogador["maior_exercito"]:
            extras.append("ME")
        if jogador["maior_estrada"]:
            extras.append("MR")

        sufixo = ""
        if extras:
            sufixo = " [" + ", ".join(extras) + "]"

        texto_j = FONTE_TEXTO.render(
            f"{jogador['nome']} ({jogador['tipo']}): {jogador['pontos']} pts{sufixo}",
            True,
            PRETO
        )
        tela.blit(texto_j, (PAINEL_X + 50, y_jogs))
        y_jogs += 26

    texto_controles_1 = FONTE_CONTROLES.render(
        "Turno: ESPACO rolar dados | ENTER passar turno",
        True,
        PRETO
    )
    tela.blit(texto_controles_1, (20, BARRA_INFERIOR_Y + 70))

    texto_controles_2 = FONTE_CONTROLES.render(
        "Construir e trocar: C cidade | B banco/porto | P troca com jogador",
        True,
        PRETO
    )
    tela.blit(texto_controles_2, (20, BARRA_INFERIOR_Y + 94))

    texto_controles_3 = FONTE_CONTROLES.render(
        "Cartas: D comprar | K Cavaleiro | R Estradas | F Fartura | M Monopolio",
        True,
        PRETO
    )
    tela.blit(texto_controles_3, (20, BARRA_INFERIOR_Y + 118))

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
            if estrada["v1"] == pos:
                origem = estrada["v2"]

                if not vertice_tem_construcao_adversaria(origem, jogador_atual):
                    return True

            if estrada["v2"] == pos:
                origem = estrada["v1"]

                if not vertice_tem_construcao_adversaria(origem, jogador_atual):
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

def tentar_construir_aldeia(pos, vertices_globais, jogador_atual, jogadores, banco_recursos, fase_inicial=False, limite_inicial=2):
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
        gastar_recursos(jogador, CUSTO_ALDEIA, banco_recursos)

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

    print(f"{jogador['nome']} construiu uma aldeia.")
    return True

def vertice_tem_construcao_adversaria(vertice, jogador_atual):
    for construcao in aldeias_construidas:
        if construcao["vertice"] == vertice and construcao["jogador"] != jogador_atual:
            return True

    return False

def estrada_conectada_ao_jogador(pos1, pos2, jogador_atual):
    
    for construcao in aldeias_construidas:
        if construcao["jogador"] == jogador_atual:
            if construcao["vertice"] == pos1 or construcao["vertice"] == pos2:
                return True

    for estrada in estradas_construidas:
        if estrada["jogador"] == jogador_atual:
            if estrada["v1"] == pos1 or estrada["v2"] == pos1:
                if not vertice_tem_construcao_adversaria(pos1, jogador_atual):
                    return True

            if estrada["v1"] == pos2 or estrada["v2"] == pos2:
                if not vertice_tem_construcao_adversaria(pos2, jogador_atual):
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

def tentar_construir_estrada(pos1, pos2, jogador_atual, jogadores, banco_recursos, fase_inicial=False, limite_inicial=2, estrada_gratis=False):
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

    if contar_estradas_do_jogador(jogador_atual) >= LIMITE_ESTRADAS:
        print("Você já atingiu o limite de estradas.")
        return False

    for estrada in estradas_construidas:
        mesma_ordem = estrada["v1"] == pos1 and estrada["v2"] == pos2
        ordem_inversa = estrada["v1"] == pos2 and estrada["v2"] == pos1

        if mesma_ordem or ordem_inversa:
            print("Já existe uma estrada neste caminho.")
            return False

    if not fase_inicial and not estrada_conectada_ao_jogador(pos1, pos2, jogador_atual):
        print("A estrada precisa estar conectada a uma aldeia ou estrada sua.")
        return False

    if not fase_inicial and not estrada_gratis and not tem_recursos(jogador, CUSTO_ESTRADA):
        print("Recursos insuficientes para construir estrada.")
        return False

    if not fase_inicial and not estrada_gratis:
        gastar_recursos(jogador, CUSTO_ESTRADA, banco_recursos)

    estradas_construidas.append({
        "v1": pos1,
        "v2": pos2,
        "jogador": jogador_atual
    })
    mensagem_maior_estrada = atualizar_maior_estrada(jogadores)

    if mensagem_maior_estrada is not None:
        print(mensagem_maior_estrada)

    print(f"{jogador['nome']} construiu uma estrada.")
    return True

def contar_cidades_do_jogador(jogador_atual):
    total = 0

    for construcao in aldeias_construidas:
        if construcao["jogador"] == jogador_atual and construcao["tipo"] == "cidade":
            total += 1

    return total

def tentar_construir_cidade(pos, jogador_atual, jogadores, banco_recursos):
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

            gastar_recursos(jogador, CUSTO_CIDADE, banco_recursos)
            construcao["tipo"] = "cidade"
            jogador["pontos"] += 1

            print(f"{jogador['nome']} construiu uma cidade.")
            return True

    print("Você só pode construir cidade em uma aldeia sua.")
    return False

def distribuir_recursos(tabuleiro, dado, jogadores, ladrao, banco_recursos):
    producao = {}

    for recurso in RECURSOS:
        producao[recurso] = {}

    for peca in tabuleiro:
        if peca == ladrao:
            continue

        if peca["numero"] != dado or peca["cor"] == DESERTO:
            continue

        recurso = MAPA_RECURSOS[peca["cor"]]

        for v in peca["vertices"]:
            for construcao in aldeias_construidas:
                vertice_construcao = construcao["vertice"]

                if math.hypot(
                    v[0] - vertice_construcao.x,
                    v[1] - vertice_construcao.y
                ) < 5:
                    dono = construcao["jogador"]

                    if construcao["tipo"] == "cidade":
                        quantidade = 2
                    else:
                        quantidade = 1

                    if dono not in producao[recurso]:
                        producao[recurso][dono] = 0

                    producao[recurso][dono] += quantidade

    for recurso, jogadores_recebendo in producao.items():
        if len(jogadores_recebendo) == 0:
            continue

        total_necessario = sum(jogadores_recebendo.values())
        disponivel = banco_recursos[recurso]

        if disponivel >= total_necessario:
            for jogador_indice, quantidade in jogadores_recebendo.items():
                retirar_recurso_do_banco(
                    banco_recursos,
                    jogadores[jogador_indice],
                    recurso,
                    quantidade
                )

                print(
                    f"{jogadores[jogador_indice]['nome']} "
                    f"recebeu {quantidade} {recurso}"
                )

        elif len(jogadores_recebendo) == 1:
            jogador_indice = next(iter(jogadores_recebendo))
            quantidade_recebida = retirar_recurso_do_banco(
                banco_recursos,
                jogadores[jogador_indice],
                recurso,
                disponivel
            )

            print(
                f"{jogadores[jogador_indice]['nome']} "
                f"recebeu apenas {quantidade_recebida} {recurso}"
            )

        else:
            print(
                f"Banco sem {recurso} suficiente. "
                f"Nenhum jogador recebeu esse recurso."
            )

def passar_turno(jogador_atual, jogadores):
    jogador_atual = (jogador_atual + 1) % len(jogadores)
    print(f"Agora é a vez de: {jogadores[jogador_atual]['nome']}")
    return jogador_atual

def tem_recursos(jogador, custo):
    for recurso, quantidade in custo.items():
        if jogador["inventario"][recurso] < quantidade:
            return False
    return True


def gastar_recursos(jogador, custo, banco_recursos):
    for recurso, quantidade in custo.items():
        jogador["inventario"][recurso] -= quantidade
        banco_recursos[recurso] += quantidade

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

def pontuacao_total(jogador):
    return jogador["pontos"] + jogador["pontos_vitoria_ocultos"]

def verificar_vencedor(jogadores, jogador_atual):
    jogador = jogadores[jogador_atual]

    if pontuacao_total(jogador) >= PONTOS_PARA_VENCER:
        return jogador

    return None

def dar_recursos_teste(jogador, banco_recursos):
    for recurso in RECURSOS:
        retirar_recurso_do_banco(
            banco_recursos,
            jogador,
            recurso,
            1
        )

def bot_tentar_construir_aldeia(jogador_atual, jogadores, banco_recursos, vertices_globais, fase_inicial=False, limite_inicial=2):
    jogador = jogadores[jogador_atual]

    if not fase_inicial and not tem_recursos(jogador, CUSTO_ALDEIA):
        return False

    vertices_embaralhados = vertices_globais.copy()
    random.shuffle(vertices_embaralhados)

    for v in vertices_embaralhados:
        if tentar_construir_aldeia(v, vertices_globais, jogador_atual, jogadores, banco_recursos, fase_inicial, limite_inicial):
            return True

    return False

def bot_tentar_construir_estrada(jogador_atual, jogadores, banco_recursos, fase_inicial=False, limite_inicial=2, estrada_gratis=False):
    jogador = jogadores[jogador_atual]

    if not fase_inicial and not estrada_gratis and not tem_recursos(jogador, CUSTO_ESTRADA):
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
        if tentar_construir_estrada(pos1, pos2, jogador_atual, jogadores, banco_recursos, fase_inicial, limite_inicial, estrada_gratis):
            return True

    return False

def bot_tentar_construir_cidade(jogador_atual, jogadores, banco_recursos):
    jogador = jogadores[jogador_atual]

    if not tem_recursos(jogador, CUSTO_CIDADE):
        return False

    aldeias_do_bot = []

    for construcao in aldeias_construidas:
        if construcao["jogador"] == jogador_atual and construcao["tipo"] == "aldeia":
            aldeias_do_bot.append(construcao["vertice"])

    random.shuffle(aldeias_do_bot)

    for vertice in aldeias_do_bot:
        if tentar_construir_cidade(vertice, jogador_atual, jogadores, banco_recursos):
            return True

    return False

def dar_recursos_teste_para_todos(jogadores, banco_recursos):
    for jogador in jogadores:
        dar_recursos_teste(jogador, banco_recursos)

    print("Recursos de teste adicionados para todos.")

def fase_inicial_completa(jogadores):
    for i in range(len(jogadores)):
        tem_aldeia = contar_construcoes_tipo_do_jogador(i, "aldeia") >= 2
        tem_estrada = contar_estradas_iniciais_do_jogador(i) >= 2

        if not tem_aldeia or not tem_estrada:
            return False

    return True

def distribuir_recursos_iniciais(tabuleiro, jogadores, banco_recursos):
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
                    quantidade_recebida = retirar_recurso_do_banco(
                        banco_recursos,
                        jogadores[dono],
                        recurso,
                        1
                    )

                    if quantidade_recebida > 0:
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

QUANTIDADE_INICIAL_BANCO = 19

def criar_banco_recursos():
    return {
        recurso: QUANTIDADE_INICIAL_BANCO
        for recurso in RECURSOS
    }

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


def bot_descartar_recursos(jogador, banco_recursos):
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
        banco_recursos[recurso_escolhido] += 1
        descartados.append(recurso_escolhido)
        quantidade -= 1

    mensagem = f"{jogador['nome']} descartou {len(descartados)} recurso(s)."
    print(mensagem)
    return mensagem


def preparar_proximo_descarte(fila_descarte, jogadores, banco_recursos):
    mensagens_bot = []

    while len(fila_descarte) > 0 and jogadores[fila_descarte[0]]["tipo"] == "bot":
        bot_indice = fila_descarte.pop(0)
        mensagem_bot = bot_descartar_recursos(jogadores[bot_indice], banco_recursos)
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

def trocar_com_banco(jogador_atual, jogadores, recurso_entregar, recurso_receber, portos, banco_recursos):
    jogador = jogadores[jogador_atual]
    
    if banco_recursos[recurso_receber] < 1:
        mensagem = f"O banco nao tem {recurso_receber} disponivel."
        print(mensagem)
        return mensagem

    if recurso_entregar == recurso_receber:
        mensagem = "Escolha recursos diferentes para a troca."
        print(mensagem)
        return mensagem

    taxa = taxa_troca_banco(jogador_atual, recurso_entregar, portos)

    if jogador["inventario"][recurso_entregar] < taxa:
        mensagem = f"{jogador['nome']} nao tem {taxa} {recurso_entregar} para trocar."
        print(mensagem)
        return mensagem

    jogador["inventario"][recurso_entregar] -= taxa
    banco_recursos[recurso_entregar] += taxa

    banco_recursos[recurso_receber] -= 1
    jogador["inventario"][recurso_receber] += 1

    mensagem = f"{jogador['nome']} trocou {taxa} {recurso_entregar} por 1 {recurso_receber}."
    print(mensagem)
    return mensagem

def resetar_troca_jogador():
    return {
        "alvo": None,
        "recurso_oferecido": None,
        "quantidade_oferecida": 0,
        "recurso_pedido": None,
        "quantidade_pedida": 0
    }


def validar_e_fazer_troca_jogadores(jogador_atual, troca, jogadores):
    jogador = jogadores[jogador_atual]
    alvo = jogadores[troca["alvo"]]

    recurso_oferecido = troca["recurso_oferecido"]
    quantidade_oferecida = troca["quantidade_oferecida"]
    recurso_pedido = troca["recurso_pedido"]
    quantidade_pedida = troca["quantidade_pedida"]

    if jogador["inventario"][recurso_oferecido] < quantidade_oferecida:
        mensagem = f"{jogador['nome']} nao tem recursos suficientes para oferecer."
        print(mensagem)
        return mensagem

    if alvo["inventario"][recurso_pedido] < quantidade_pedida:
        mensagem = f"{alvo['nome']} nao tem recursos suficientes para aceitar."
        print(mensagem)
        return mensagem

    jogador["inventario"][recurso_oferecido] -= quantidade_oferecida
    alvo["inventario"][recurso_oferecido] += quantidade_oferecida

    alvo["inventario"][recurso_pedido] -= quantidade_pedida
    jogador["inventario"][recurso_pedido] += quantidade_pedida

    mensagem = (
        f"{jogador['nome']} trocou {quantidade_oferecida} {recurso_oferecido} "
        f"por {quantidade_pedida} {recurso_pedido} com {alvo['nome']}."
    )
    print(mensagem)
    return mensagem

TIPOS_PORTOS = ["3:1", "3:1", "3:1", "3:1", "Madeira", "Tijolo", "Ovelha", "Trigo", "Minério"]


def chave_aresta(p1, p2):
    return tuple(sorted([p1, p2]))


def encontrar_vertice_por_pos(pos, vertices_globais):
    for v in vertices_globais:
        if math.hypot(v.x - pos[0], v.y - pos[1]) < 5:
            return v

    return None


def gerar_portos(tabuleiro, vertices_globais):
    contagem_arestas = {}

    for peca in tabuleiro:
        pontos = peca["vertices"]

        for i in range(6):
            p1 = pontos[i]
            p2 = pontos[(i + 1) % 6]
            chave = chave_aresta(p1, p2)

            if chave not in contagem_arestas:
                contagem_arestas[chave] = 0

            contagem_arestas[chave] += 1

    arestas_borda = []

    for chave, contagem in contagem_arestas.items():
        if contagem == 1:
            p1, p2 = chave
            mx = (p1[0] + p2[0]) / 2
            my = (p1[1] + p2[1]) / 2
            angulo = math.atan2(my - ALTURA / 2, mx - AREA_MAPA_LARGURA / 2)

            arestas_borda.append({
                "p1": p1,
                "p2": p2,
                "angulo": angulo
            })

    arestas_borda.sort(key=lambda a: a["angulo"])

    random.shuffle(TIPOS_PORTOS)

    portos = []
    quantidade_portos = 9

    for i in range(quantidade_portos):
        indice = int(i * len(arestas_borda) / quantidade_portos)
        aresta = arestas_borda[indice]

        v1 = encontrar_vertice_por_pos(aresta["p1"], vertices_globais)
        v2 = encontrar_vertice_por_pos(aresta["p2"], vertices_globais)

        if v1 is None or v2 is None:
            continue

        mx = (v1.x + v2.x) / 2
        my = (v1.y + v2.y) / 2

        dx = mx - AREA_MAPA_LARGURA / 2
        dy = my - ALTURA / 2
        dist = math.hypot(dx, dy)

        if dist == 0:
            dist = 1

        texto_x = int(mx + (dx / dist) * 35)
        texto_y = int(my + (dy / dist) * 35)

        portos.append({
            "v1": v1,
            "v2": v2,
            "tipo": TIPOS_PORTOS[i],
            "texto_pos": (texto_x, texto_y)
        })

    return portos


def jogador_tem_porto(jogador_atual, porto):
    for construcao in aldeias_construidas:
        if construcao["jogador"] == jogador_atual:
            if construcao["vertice"] == porto["v1"] or construcao["vertice"] == porto["v2"]:
                return True

    return False


def taxa_troca_banco(jogador_atual, recurso_entregar, portos):
    melhor_taxa = 4

    for porto in portos:
        if jogador_tem_porto(jogador_atual, porto):
            if porto["tipo"] == "3:1":
                melhor_taxa = min(melhor_taxa, 3)

            elif porto["tipo"] == recurso_entregar:
                melhor_taxa = min(melhor_taxa, 2)

    return melhor_taxa

def desenhar_portos(tela, portos):
    for porto in portos:
        pygame.draw.line(tela, PRETO, porto["v1"].pos, porto["v2"].pos, 4)

        texto = FONTE_TEXTO.render(porto["tipo"], True, PRETO)
        rect = texto.get_rect(center=porto["texto_pos"])
        tela.blit(texto, rect)

CUSTO_DESENVOLVIMENTO = {
    "Ovelha": 1,
    "Trigo": 1,
    "Minério": 1
}

CARTAS_DESENVOLVIMENTO_BASE = (
    ["Cavaleiro"] * 14 +
    ["Ponto de Vitoria"] * 5 +
    ["Construcao de Estradas"] * 2 +
    ["Ano de Fartura"] * 2 +
    ["Monopolio"] * 2
)

def criar_baralho_desenvolvimento():
    baralho = CARTAS_DESENVOLVIMENTO_BASE.copy()
    random.shuffle(baralho)
    return baralho


def comprar_carta_desenvolvimento(jogador, baralho, banco_recursos):
    if len(baralho) == 0:
        mensagem = "Nao ha mais cartas de desenvolvimento."
        print(mensagem)
        return mensagem

    if not tem_recursos(jogador, CUSTO_DESENVOLVIMENTO):
        mensagem = "Recursos insuficientes para comprar carta de desenvolvimento."
        print(mensagem)
        return mensagem

    gastar_recursos(jogador, CUSTO_DESENVOLVIMENTO, banco_recursos)

    carta = baralho.pop()
    jogador["cartas_dev"].append(carta)
    jogador["cartas_dev_compradas_turno"].append(carta)

    if carta == "Ponto de Vitoria":
        jogador["pontos_vitoria_ocultos"] += 1

    mensagem = f"{jogador['nome']} comprou uma carta de desenvolvimento."

    print(mensagem)
    return mensagem


def jogador_tem_carta_usavel(jogador, carta):
    quantidade_total = jogador["cartas_dev"].count(carta)
    quantidade_comprada_turno = jogador["cartas_dev_compradas_turno"].count(carta)

    return quantidade_total > quantidade_comprada_turno


def usar_cavaleiro(jogador):
    if not jogador_tem_carta_usavel(jogador, "Cavaleiro"):
        mensagem = "Voce nao tem Cavaleiro disponivel para usar."
        print(mensagem)
        return False, mensagem

    jogador["cartas_dev"].remove("Cavaleiro")
    jogador["cavaleiros_usados"] += 1

    mensagem = f"{jogador['nome']} usou um Cavaleiro."
    print(mensagem)
    return True, mensagem


def limpar_cartas_compradas_turno(jogador):
    jogador["cartas_dev_compradas_turno"] = []

def atualizar_maior_exercito(jogadores):
    dono_atual = None

    for i, jogador in enumerate(jogadores):
        if jogador["maior_exercito"]:
            dono_atual = i
            break

    melhor_jogador = None
    maior_quantidade = 0

    for i, jogador in enumerate(jogadores):
        if jogador["cavaleiros_usados"] >= 3:
            if jogador["cavaleiros_usados"] > maior_quantidade:
                maior_quantidade = jogador["cavaleiros_usados"]
                melhor_jogador = i

    if melhor_jogador is None:
        return None

    if dono_atual is None:
        jogadores[melhor_jogador]["maior_exercito"] = True
        jogadores[melhor_jogador]["pontos"] += 2
        mensagem = f"{jogadores[melhor_jogador]['nome']} ganhou Maior Exercito!"
        print(mensagem)
        return mensagem

    if melhor_jogador != dono_atual:
        if jogadores[melhor_jogador]["cavaleiros_usados"] > jogadores[dono_atual]["cavaleiros_usados"]:
            jogadores[dono_atual]["maior_exercito"] = False
            jogadores[dono_atual]["pontos"] -= 2

            jogadores[melhor_jogador]["maior_exercito"] = True
            jogadores[melhor_jogador]["pontos"] += 2

            mensagem = f"{jogadores[melhor_jogador]['nome']} tomou Maior Exercito!"
            print(mensagem)
            return mensagem

    return None

def nome_dono_maior_exercito(jogadores):
    for jogador in jogadores:
        if jogador["maior_exercito"]:
            return jogador["nome"]

    return "Ninguem"

def nome_dono_maior_estrada(jogadores):
    for jogador in jogadores:
        if jogador["maior_estrada"]:
            return jogador["nome"]

    return "Ninguem"


def estradas_do_jogador(jogador_atual):
    lista = []

    for estrada in estradas_construidas:
        if estrada["jogador"] == jogador_atual:
            lista.append(estrada)

    return lista


def vertices_iguais(v1, v2):
    return v1 == v2


def calcular_maior_caminho_estradas(jogador_atual):
    estradas = estradas_do_jogador(jogador_atual)

    if len(estradas) == 0:
        return 0

    maior = 0

    def buscar(vertice_atual, estradas_usadas):
        melhor_local = len(estradas_usadas)

        for i, estrada in enumerate(estradas):
            if i in estradas_usadas:
                continue

            proximo = None

            if vertices_iguais(estrada["v1"], vertice_atual):
                proximo = estrada["v2"]
            elif vertices_iguais(estrada["v2"], vertice_atual):
                proximo = estrada["v1"]

            if proximo is None:
                continue

            if vertice_tem_construcao_adversaria(vertice_atual, jogador_atual):
                continue

            novo_usadas = estradas_usadas.copy()
            novo_usadas.add(i)

            tamanho = buscar(proximo, novo_usadas)

            if tamanho > melhor_local:
                melhor_local = tamanho

        return melhor_local

    for estrada in estradas:
        tamanho_1 = buscar(estrada["v1"], set())
        tamanho_2 = buscar(estrada["v2"], set())

        if tamanho_1 > maior:
            maior = tamanho_1

        if tamanho_2 > maior:
            maior = tamanho_2

    return maior


def atualizar_maior_estrada(jogadores):
    dono_atual = None

    for i, jogador in enumerate(jogadores):
        if jogador["maior_estrada"]:
            dono_atual = i
            break

    melhor_jogador = None
    maior_tamanho = 0

    for i, jogador in enumerate(jogadores):
        tamanho = calcular_maior_caminho_estradas(i)

        if tamanho >= 5 and tamanho > maior_tamanho:
            maior_tamanho = tamanho
            melhor_jogador = i

    if melhor_jogador is None:
        return None

    if dono_atual is None:
        jogadores[melhor_jogador]["maior_estrada"] = True
        jogadores[melhor_jogador]["pontos"] += 2

        mensagem = f"{jogadores[melhor_jogador]['nome']} ganhou Maior Estrada!"
        print(mensagem)
        return mensagem

    tamanho_dono = calcular_maior_caminho_estradas(dono_atual)

    if melhor_jogador != dono_atual and maior_tamanho > tamanho_dono:
        jogadores[dono_atual]["maior_estrada"] = False
        jogadores[dono_atual]["pontos"] -= 2

        jogadores[melhor_jogador]["maior_estrada"] = True
        jogadores[melhor_jogador]["pontos"] += 2

        mensagem = f"{jogadores[melhor_jogador]['nome']} tomou Maior Estrada!"
        print(mensagem)
        return mensagem

    return None

def usar_construcao_de_estradas(jogador):
    if not jogador_tem_carta_usavel(jogador, "Construcao de Estradas"):
        mensagem = "Voce nao tem Construcao de Estradas disponivel para usar."
        print(mensagem)
        return False, mensagem

    jogador["cartas_dev"].remove("Construcao de Estradas")

    mensagem = f"{jogador['nome']} usou Construcao de Estradas."
    print(mensagem)
    return True, mensagem

def usar_ano_de_fartura(jogador):
    if not jogador_tem_carta_usavel(jogador, "Ano de Fartura"):
        mensagem = "Voce nao tem Ano de Fartura disponivel para usar."
        print(mensagem)
        return False, mensagem

    jogador["cartas_dev"].remove("Ano de Fartura")

    mensagem = f"{jogador['nome']} usou Ano de Fartura."
    print(mensagem)
    return True, mensagem

def usar_monopolio(jogador):
    if not jogador_tem_carta_usavel(jogador, "Monopolio"):
        mensagem = "Voce nao tem Monopolio disponivel para usar."
        print(mensagem)
        return False, mensagem

    jogador["cartas_dev"].remove("Monopolio")

    mensagem = f"{jogador['nome']} usou Monopolio."
    print(mensagem)
    return True, mensagem


def aplicar_monopolio(jogador_atual, jogadores, recurso):
    jogador = jogadores[jogador_atual]
    total_roubado = 0

    for i, outro_jogador in enumerate(jogadores):
        if i == jogador_atual:
            continue

        quantidade = outro_jogador["inventario"][recurso]

        if quantidade > 0:
            outro_jogador["inventario"][recurso] -= quantidade
            jogador["inventario"][recurso] += quantidade
            total_roubado += quantidade

    mensagem = f"{jogador['nome']} pegou {total_roubado} {recurso} com Monopolio."
    print(mensagem)
    return mensagem

def existe_acao_pendente(
    escolhendo_ladrao,
    escolhendo_vitima_ladrao,
    descartando_recursos,
    trocando_banco,
    trocando_jogador,
    usando_construcao_estradas,
    usando_ano_fartura,
    usando_monopolio
):
    return (
        escolhendo_ladrao
        or escolhendo_vitima_ladrao
        or descartando_recursos
        or trocando_banco
        or trocando_jogador
        or usando_construcao_estradas
        or usando_ano_fartura
        or usando_monopolio
    )

def bot_escolher_recurso_ano_fartura(jogador, banco_recursos):
    prioridade = ["Minério", "Trigo", "Madeira", "Tijolo", "Ovelha"]
    recursos_escolhidos = []

    for recurso in prioridade:
        while banco_recursos[recurso] > 0 and len(recursos_escolhidos) < 2:
            retirar_recurso_do_banco(
                banco_recursos,
                jogador,
                recurso,
                1
            )

            recursos_escolhidos.append(recurso)

        if len(recursos_escolhidos) == 2:
            break

    if len(recursos_escolhidos) == 0:
        mensagem = (
            f"{jogador['nome']} usou Ano de Fartura, "
            "mas o banco nao tinha recursos disponiveis."
        )

    elif len(recursos_escolhidos) == 1:
        mensagem = (
            f"{jogador['nome']} usou Ano de Fartura e recebeu "
            f"apenas 1 {recursos_escolhidos[0]}."
        )

    else:
        mensagem = (
            f"{jogador['nome']} usou Ano de Fartura e recebeu "
            f"{recursos_escolhidos[0]} e {recursos_escolhidos[1]}."
        )

    print(mensagem)
    return mensagem

def bot_escolher_recurso_monopolio(jogador_atual, jogadores):
    melhor_recurso = "Madeira"
    maior_quantidade = -1

    for recurso in RECURSOS:
        total = 0

        for i, jogador in enumerate(jogadores):
            if i != jogador_atual:
                total += jogador["inventario"][recurso]

        if total > maior_quantidade:
            maior_quantidade = total
            melhor_recurso = recurso

    return melhor_recurso

def bot_tentar_usar_carta_desenvolvimento(jogador_atual, jogadores, banco_recursos, tabuleiro, ladrao, vertices_globais):
    jogador = jogadores[jogador_atual]

    if jogador["usou_carta_dev_turno"]:
        return ladrao, None

    # 1. Cavaleiro
    if jogador_tem_carta_usavel(jogador, "Cavaleiro"):
        sucesso, mensagem = usar_cavaleiro(jogador)

        if sucesso:
            jogador["usou_carta_dev_turno"] = True

            mensagem_maior_exercito = atualizar_maior_exercito(jogadores)

            ladrao = mover_ladrao_aleatorio(tabuleiro, ladrao)
            vitimas = encontrar_vitimas_ladrao(ladrao, jogador_atual)

            if len(vitimas) > 0:
                vitima = random.choice(vitimas)
                mensagem_roubo = roubar_recurso_de_vitima(jogador_atual, vitima, jogadores)
                mensagem = f"{mensagem} {mensagem_roubo}"
            else:
                mensagem = f"{mensagem} Ladrao movido. Nao ha vitimas."

            if mensagem_maior_exercito is not None:
                mensagem = f"{mensagem_maior_exercito} {mensagem}"

            return ladrao, mensagem

    # 2. Construção de Estradas
    if jogador_tem_carta_usavel(jogador, "Construcao de Estradas"):
        sucesso, mensagem = usar_construcao_de_estradas(jogador)

        if sucesso:
            jogador["usou_carta_dev_turno"] = True
            estradas_construidas_bot = 0

            for _ in range(2):
                construiu = bot_tentar_construir_estrada(
                    jogador_atual,
                    jogadores,
                    banco_recursos,
                    False,
                    2,
                    True
                )

                if construiu:
                    estradas_construidas_bot += 1

            mensagem = f"{jogador['nome']} usou Construcao de Estradas e construiu {estradas_construidas_bot} estrada(s)."
            print(mensagem)
            return ladrao, mensagem

    # 3. Ano de Fartura
    if jogador_tem_carta_usavel(jogador, "Ano de Fartura"):
        sucesso, mensagem = usar_ano_de_fartura(jogador)

        if sucesso:
            jogador["usou_carta_dev_turno"] = True
            mensagem = bot_escolher_recurso_ano_fartura(jogador, banco_recursos)
            return ladrao, mensagem

    # 4. Monopólio
    if jogador_tem_carta_usavel(jogador, "Monopolio"):
        sucesso, mensagem = usar_monopolio(jogador)

        if sucesso:
            jogador["usou_carta_dev_turno"] = True
            recurso = bot_escolher_recurso_monopolio(jogador_atual, jogadores)
            mensagem = aplicar_monopolio(jogador_atual, jogadores, recurso)
            return ladrao, mensagem

    return ladrao, None

def bot_tentar_comprar_carta_desenvolvimento(jogador, baralho, banco_recursos):
    if tem_recursos(jogador, CUSTO_DESENVOLVIMENTO):
        mensagem = comprar_carta_desenvolvimento(jogador, baralho, banco_recursos)
        return mensagem

    return None

def bot_tentar_troca_banco(jogador_atual, jogadores, banco_recursos, portos):
    jogador = jogadores[jogador_atual]

    recursos_prioridade_receber = ["Minério", "Trigo", "Madeira", "Tijolo", "Ovelha"]

    for recurso_entregar in RECURSOS:
        taxa = taxa_troca_banco(jogador_atual, recurso_entregar, portos)

        if jogador["inventario"][recurso_entregar] >= taxa:
            for recurso_receber in recursos_prioridade_receber:
                if recurso_receber != recurso_entregar:
                    mensagem = trocar_com_banco(
                        jogador_atual,
                        jogadores,
                        recurso_entregar,
                        recurso_receber,
                        portos,
                        banco_recursos
                    )
                    return mensagem

    return None

def deve_mostrar_tela_passagem(jogador_atual, proximo_jogador, jogadores):
    return (
        jogadores[jogador_atual]["tipo"] == "humano"
        and jogadores[proximo_jogador]["tipo"] == "humano"
    )

def desenhar_tela_passagem_turno(tela, jogador, mensagem=""):
    tela.fill(COR_FUNDO)

    texto_1 = FONTE_TITULO.render("Passe o controle para:", True, PRETO)
    rect_1 = texto_1.get_rect(center=(LARGURA // 2, ALTURA // 2 - 80))
    tela.blit(texto_1, rect_1)

    texto_2 = FONTE_TITULO.render(jogador["nome"], True, PRETO)
    rect_2 = texto_2.get_rect(center=(LARGURA // 2, ALTURA // 2 - 30))
    tela.blit(texto_2, rect_2)

    if mensagem != "":
        texto_msg = FONTE_TEXTO.render(mensagem, True, PRETO)
        rect_msg = texto_msg.get_rect(center=(LARGURA // 2, ALTURA // 2 + 25))
        tela.blit(texto_msg, rect_msg)

    texto_3 = FONTE_TEXTO.render("Pressione ENTER para continuar", True, PRETO)
    rect_3 = texto_3.get_rect(center=(LARGURA // 2, ALTURA // 2 + 80))
    tela.blit(texto_3, rect_3)

def deve_mostrar_tela_descarte(jogador_descartando, jogador_atual, jogadores):
    return (
        jogador_descartando is not None
        and jogador_descartando != jogador_atual
        and jogadores[jogador_descartando]["tipo"] == "humano"
    )

def desenhar_tela_vitoria(tela, vencedor, jogadores):
    tela.fill(COR_FUNDO)

    texto_titulo = FONTE_TITULO.render("Fim de jogo!", True, PRETO)
    rect_titulo = texto_titulo.get_rect(center=(LARGURA // 2, 100))
    tela.blit(texto_titulo, rect_titulo)

    texto_vencedor = FONTE_TITULO.render(f"{vencedor['nome']} venceu!", True, PRETO)
    rect_vencedor = texto_vencedor.get_rect(center=(LARGURA // 2, 160))
    tela.blit(texto_vencedor, rect_vencedor)

    texto_sub = FONTE_TEXTO.render("Pontuacao final:", True, PRETO)
    rect_sub = texto_sub.get_rect(center=(LARGURA // 2, 230))
    tela.blit(texto_sub, rect_sub)

    y = 270
    for jogador in jogadores:
        texto_pontos = FONTE_TEXTO.render(
            f"{jogador['nome']}: {pontuacao_total(jogador)} pontos",
            True,
            PRETO
        )
        rect_pontos = texto_pontos.get_rect(center=(LARGURA // 2, y))
        tela.blit(texto_pontos, rect_pontos)
        y += 35

    texto_sair = FONTE_TEXTO.render("Pressione ESC para sair", True, PRETO)
    rect_sair = texto_sair.get_rect(center=(LARGURA // 2, ALTURA - 80))
    tela.blit(texto_sair, rect_sair)

def banco_tem_recursos(banco_recursos, recurso, quantidade):
    return banco_recursos[recurso] >= quantidade


def retirar_recurso_do_banco(banco_recursos, jogador, recurso, quantidade):
    quantidade_disponivel = banco_recursos[recurso]
    quantidade_retirada = min(quantidade, quantidade_disponivel)

    banco_recursos[recurso] -= quantidade_retirada
    jogador["inventario"][recurso] += quantidade_retirada

    return quantidade_retirada


def devolver_recurso_ao_banco(banco_recursos, jogador, recurso, quantidade):
    quantidade_devolvida = min(
        quantidade,
        jogador["inventario"][recurso]
    )

    jogador["inventario"][recurso] -= quantidade_devolvida
    banco_recursos[recurso] += quantidade_devolvida

    return quantidade_devolvida

def desenhar_banco_recursos(tela, banco_recursos):
    largura_caixa = 210
    altura_caixa = 180

    x = PAINEL_X - largura_caixa - 15
    y = 20

    pygame.draw.rect(
        tela,
        (220, 235, 240),
        (x, y, largura_caixa, altura_caixa)
    )

    pygame.draw.rect(
        tela,
        PRETO,
        (x, y, largura_caixa, altura_caixa),
        2
    )

    titulo = FONTE_TITULO.render("Banco", True, PRETO)
    tela.blit(titulo, (x + 15, y + 10))

    y_recurso = y + 50

    for recurso, quantidade in banco_recursos.items():
        texto = FONTE_CONTROLES.render(
            f"{recurso}: {quantidade}",
            True,
            PRETO
        )
        tela.blit(texto, (x + 15, y_recurso))
        y_recurso += 24

def main(game_mode="custom", num_players=2, num_humanos=2):
    relogio = pygame.time.Clock()
    tabuleiro, vertices_globais = gerar_tabuleiro()
    baralho_desenvolvimento = criar_baralho_desenvolvimento()
    portos = gerar_portos(tabuleiro, vertices_globais)
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
    trocando_banco = False
    recurso_entregar_banco = None
    trocando_jogador = False
    etapa_troca_jogador = None
    troca_jogador = {
        "alvo": None,
        "recurso_oferecido": None,
        "quantidade_oferecida": 0,
        "recurso_pedido": None,
        "quantidade_pedida": 0
    }
    usando_construcao_estradas = False
    estradas_gratis_restantes = 0
    usando_ano_fartura = False
    recursos_ano_fartura = []
    usando_monopolio = False
    tela_passagem_turno = False
    proximo_jogador_pendente = None
    tipo_tela_passagem = None
    mensagem_tela_passagem = ""
    acao_pos_passagem = None
    jogador_visivel = jogador_atual
    bot_aguardando_resolucao_7 = False
    historico_dados = []
    banco_recursos = criar_banco_recursos()

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

    def solicitar_passagem_tela(destino, tipo, mensagem, acao_depois=None):
        nonlocal tela_passagem_turno
        nonlocal proximo_jogador_pendente
        nonlocal tipo_tela_passagem
        nonlocal mensagem_tela_passagem
        nonlocal acao_pos_passagem
        nonlocal mensagem_jogo
        nonlocal jogador_visivel

        if destino is None:
            return False

        if jogadores[destino]["tipo"] == "bot":
            if acao_depois == "iniciar_ladrao":
                iniciar_ladrao_apos_descarte()
            return False

        if jogador_visivel == destino:
            if acao_depois == "iniciar_ladrao":
                iniciar_ladrao_apos_descarte()
            return False

        proximo_jogador_pendente = destino
        tipo_tela_passagem = tipo
        mensagem_tela_passagem = mensagem
        acao_pos_passagem = acao_depois
        tela_passagem_turno = True
        mensagem_jogo = ""
        return True

    print(f"Modo de jogo iniciado: {game_mode}")
    print(f"Jogadores criados: {[j['nome'] for j in jogadores]}")
    
    rodando = True
    while rodando:
        TELA.fill(COR_FUNDO)

        vencedor = verificar_vencedor(jogadores, jogador_atual)

        if vencedor is not None:
            desenhar_tela_vitoria(TELA, vencedor, jogadores)

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False

                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        rodando = False

            pygame.display.flip()
            relogio.tick(60)
            continue

        if tela_passagem_turno:
            desenhar_tela_passagem_turno(TELA, jogadores[proximo_jogador_pendente], mensagem_tela_passagem)

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False

                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_RETURN:
                        if tipo_tela_passagem == "turno":
                            jogador_atual = proximo_jogador_pendente
                            dado_rolado_no_turno = False

                        jogador_visivel = proximo_jogador_pendente

                        acao_para_executar = acao_pos_passagem

                        proximo_jogador_pendente = None
                        tipo_tela_passagem = None
                        mensagem_tela_passagem = ""
                        acao_pos_passagem = None
                        tela_passagem_turno = False
                        mensagem_jogo = ""

                        if acao_para_executar == "iniciar_ladrao":
                            iniciar_ladrao_apos_descarte()

            pygame.display.flip()
            relogio.tick(60)
            continue

        if fase_inicial and fase_inicial_completa(jogadores):
            distribuir_recursos_iniciais(tabuleiro, jogadores, banco_recursos)
            limpar_dados_fase_inicial(jogadores)
            fase_inicial = False
            print("Fase inicial encerrada automaticamente. O jogo normal começou.")
            
        jogador = jogadores[jogador_atual]

        if jogador["tipo"] == "bot" and vencedor is None:
            if bot_aguardando_resolucao_7 and not existe_acao_pendente(
                escolhendo_ladrao,
                escolhendo_vitima_ladrao,
                descartando_recursos,
                trocando_banco,
                trocando_jogador,
                usando_construcao_estradas,
                usando_ano_fartura,
                usando_monopolio
            ):
                bot_aguardando_resolucao_7 = False
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
                        banco_recursos,
                        vertices_globais,
                        fase_inicial,
                        limite_inicial
                    )

                    bot_tentar_construir_estrada(
                        jogador_atual,
                        jogadores,
                        banco_recursos,
                        fase_inicial,
                        limite_inicial
                    )

                    if not jogador_completou_rodada_inicial(jogador_atual, indice_fase_inicial, jogadores):
                        print(f"{jogador['nome']} ainda não conseguiu posicionar tudo.")
                        tempo_turno_bot = 0
                        continue

                else:
                    if not dado_rolado_no_turno:
                        ultimo_dado = random.randint(1, 6) + random.randint(1, 6)
                        dado_rolado_no_turno = True

                        historico_dados.append(f"{jogador['nome']} tirou {ultimo_dado} no dado")
                        historico_dados = historico_dados[-5:]
                        
                        if ultimo_dado == 7:
                            jogador_que_rolou_7 = jogador_atual
                            fila_descarte = criar_fila_descarte(jogadores)

                            estado_descarte = preparar_proximo_descarte(fila_descarte, jogadores, banco_recursos)

                            descartando_recursos = estado_descarte["descartando"]
                            jogador_descartando = estado_descarte["jogador_descartando"]
                            quantidade_descartar = estado_descarte["quantidade_para_descartar"]
                            quantidade_descartada = estado_descarte["quantidade_descartada"]
                            mensagem_jogo = estado_descarte["mensagem"]

                            if descartando_recursos:
                                solicitar_passagem_tela(
                                    jogador_descartando,
                                    "descarte",
                                    f"Saiu 7! {jogadores[jogador_descartando]['nome']} deve descartar recursos."
                                )
                            else:
                                solicitar_passagem_tela(
                                    jogador_que_rolou_7,
                                    "ladrao",
                                    f"Descarte concluido. {jogadores[jogador_que_rolou_7]['nome']} deve mover o ladrao.",
                                    "iniciar_ladrao"
                                )

                            if descartando_recursos or tela_passagem_turno or escolhendo_ladrao or escolhendo_vitima_ladrao:
                                tempo_turno_bot = 0
                                continue

                        else:
                            mensagem_jogo = ""
                            distribuir_recursos(tabuleiro, ultimo_dado, jogadores, ladrao, banco_recursos)

                        print(f"{jogador['nome']} rolou o dado: {ultimo_dado}")

                    if existe_acao_pendente(
                        escolhendo_ladrao,
                        escolhendo_vitima_ladrao,
                        descartando_recursos,
                        trocando_banco,
                        trocando_jogador,
                        usando_construcao_estradas,
                        usando_ano_fartura,
                        usando_monopolio
                    ):
                        tempo_turno_bot = 0
                        continue

                    ladrao, mensagem_carta_bot = bot_tentar_usar_carta_desenvolvimento(
                        jogador_atual,
                        jogadores,
                        banco_recursos,
                        tabuleiro,
                        ladrao,
                        vertices_globais
                    )

                    if mensagem_carta_bot is not None:
                        mensagem_jogo = mensagem_carta_bot

                    construiu_algo = False

                    if bot_tentar_construir_cidade(jogador_atual, jogadores, banco_recursos):
                        construiu_algo = True
                    elif bot_tentar_construir_aldeia(jogador_atual, jogadores, banco_recursos, vertices_globais, fase_inicial):
                        construiu_algo = True
                    elif bot_tentar_construir_estrada(jogador_atual, jogadores, banco_recursos, fase_inicial):
                        construiu_algo = True

                    if not construiu_algo:
                        mensagem_compra = bot_tentar_comprar_carta_desenvolvimento(
                            jogador,
                            baralho_desenvolvimento,
                            banco_recursos
                        )

                        if mensagem_compra is not None:
                            mensagem_jogo = mensagem_compra

                        else:
                            mensagem_troca = bot_tentar_troca_banco(
                                jogador_atual,
                                jogadores,
                                banco_recursos,
                                portos
                            )

                            if mensagem_troca is not None:
                                mensagem_jogo = mensagem_troca

                if fase_inicial:
                    indice_fase_inicial += 1

                    if indice_fase_inicial < len(ordem_fase_inicial):
                        proximo_jogador = ordem_fase_inicial[indice_fase_inicial]
                        print(f"Fase inicial: agora é a vez de {jogadores[proximo_jogador]['nome']}")

                        if deve_mostrar_tela_passagem(jogador_atual, proximo_jogador, jogadores):
                            proximo_jogador_pendente = proximo_jogador
                            tipo_tela_passagem = "turno"
                            tela_passagem_turno = True
                        else:
                            jogador_atual = proximo_jogador
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
                    
                    if existe_acao_pendente(
                        escolhendo_ladrao,
                        escolhendo_vitima_ladrao,
                        descartando_recursos,
                        trocando_banco,
                        trocando_jogador,
                        usando_construcao_estradas,
                        usando_ano_fartura,
                        usando_monopolio
                    ):
                        mensagem_jogo = "Finalize a acao atual antes de fazer outra."
                        continue

                    if trocando_banco:
                        mensagem_jogo = "Termine ou cancele a troca com banco antes de continuar."
                        continue

                    if trocando_jogador:
                        mensagem_jogo = "Termine ou cancele a troca entre jogadores antes de continuar."
                        continue

                    if usando_ano_fartura:
                        mensagem_jogo = "Termine o Ano de Fartura antes de continuar."
                        continue

                    if usando_monopolio:
                        mensagem_jogo = "Termine o Monopolio antes de continuar."
                        continue

                    if vertice_selecionado == None:
                        vertice_selecionado = selecionar_ponto(evento.pos, vertices_globais)
                    else:
                        if math.dist(evento.pos, vertice_selecionado.pos) < 10:
                            limite_inicial = 2

                            if fase_inicial:
                                limite_inicial = limite_fase_inicial_atual(indice_fase_inicial, jogadores)

                            if usando_construcao_estradas:
                                mensagem_jogo = "Voce esta usando Construcao de Estradas. Construa estradas, nao aldeias."
                                vertice_selecionado = None

                            if not fase_inicial and not dado_rolado_no_turno:
                                print("Você precisa rolar o dado antes de construir.")
                            else:
                                tentar_construir_aldeia(
                                    vertice_selecionado,
                                    vertices_globais,
                                    jogador_atual,
                                    jogadores,
                                    banco_recursos,
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
                                        if usando_construcao_estradas:
                                            construiu = tentar_construir_estrada(
                                                vertice_selecionado,
                                                v,
                                                jogador_atual,
                                                jogadores,
                                                banco_recursos,
                                                fase_inicial,
                                                limite_inicial,
                                                True
                                            )

                                            if construiu:
                                                estradas_gratis_restantes -= 1

                                                if estradas_gratis_restantes > 0:
                                                    mensagem_jogo = f"Construcao de Estradas: faltam {estradas_gratis_restantes} estrada(s)."
                                                else:
                                                    usando_construcao_estradas = False
                                                    mensagem_jogo = "Construcao de Estradas concluida."

                                        else:
                                            if not fase_inicial and not dado_rolado_no_turno:
                                                print("Você precisa rolar o dado antes de construir.")
                                            else:
                                                tentar_construir_estrada(
                                                    vertice_selecionado,
                                                    v,
                                                    jogador_atual,
                                                    jogadores,
                                                    banco_recursos,
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
                            banco_recursos[recurso] += 1
                            quantidade_descartada += 1

                            restante = quantidade_descartar - quantidade_descartada
                            mensagem_jogo = f"{jogador_descarte['nome']} descartou 1 {recurso}. Faltam {restante}."

                            if quantidade_descartada >= quantidade_descartar:
                                fila_descarte.pop(0)

                                estado_descarte = preparar_proximo_descarte(fila_descarte, jogadores, banco_recursos)

                                descartando_recursos = estado_descarte["descartando"]
                                jogador_descartando = estado_descarte["jogador_descartando"]
                                quantidade_descartar = estado_descarte["quantidade_para_descartar"]
                                quantidade_descartada = estado_descarte["quantidade_descartada"]
                                mensagem_jogo = estado_descarte["mensagem"]

                                if descartando_recursos:
                                    solicitar_passagem_tela(
                                        jogador_descartando,
                                        "descarte",
                                        f"Saiu 7! {jogadores[jogador_descartando]['nome']} deve descartar recursos."
                                    )
                                else:
                                    solicitar_passagem_tela(
                                        jogador_que_rolou_7,
                                        "ladrao",
                                        f"Descarte concluido. {jogadores[jogador_que_rolou_7]['nome']} deve mover o ladrao.",
                                        "iniciar_ladrao"
                                    )
                        else:
                            mensagem_jogo = f"{jogador_descarte['nome']} nao tem {recurso} para descartar."

                    continue
                
                if trocando_banco:
                    teclas_recursos = {
                        pygame.K_1: "Madeira",
                        pygame.K_2: "Tijolo",
                        pygame.K_3: "Ovelha",
                        pygame.K_4: "Trigo",
                        pygame.K_5: "Minério"
                    }

                    if evento.key in teclas_recursos:
                        recurso_escolhido = teclas_recursos[evento.key]

                        if recurso_entregar_banco is None:
                            recurso_entregar_banco = recurso_escolhido
                            mensagem_jogo = f"Banco: entregar {recurso_entregar_banco}. Agora escolha o recurso para receber."
                        else:
                            mensagem_jogo = trocar_com_banco(
                                jogador_atual,
                                jogadores,
                                recurso_entregar_banco,
                                recurso_escolhido,
                                portos, 
                                banco_recursos
                            )

                            trocando_banco = False
                            recurso_entregar_banco = None

                    elif evento.key == pygame.K_ESCAPE:
                        trocando_banco = False
                        recurso_entregar_banco = None
                        mensagem_jogo = "Troca com banco cancelada."

                    continue
                if trocando_jogador:
                    teclas_recursos = {
                        pygame.K_1: "Madeira",
                        pygame.K_2: "Tijolo",
                        pygame.K_3: "Ovelha",
                        pygame.K_4: "Trigo",
                        pygame.K_5: "Minério"
                    }

                    if evento.key == pygame.K_ESCAPE:
                        trocando_jogador = False
                        etapa_troca_jogador = None
                        troca_jogador = resetar_troca_jogador()
                        mensagem_jogo = "Troca entre jogadores cancelada."
                        continue

                    if etapa_troca_jogador == "escolher_alvo":
                        if pygame.K_1 <= evento.key <= pygame.K_9:
                            escolha = evento.key - pygame.K_1

                            alvos_possiveis = []
                            for i in range(len(jogadores)):
                                if i != jogador_atual:
                                    alvos_possiveis.append(i)

                            if escolha < len(alvos_possiveis):
                                troca_jogador["alvo"] = alvos_possiveis[escolha]
                                etapa_troca_jogador = "recurso_oferecido"
                                mensagem_jogo = "Escolha recurso para oferecer: 1 Mad, 2 Tij, 3 Ove, 4 Tri, 5 Min."
                            else:
                                mensagem_jogo = "Jogador alvo invalido."

                        continue

                    if etapa_troca_jogador == "recurso_oferecido":
                        if evento.key in teclas_recursos:
                            troca_jogador["recurso_oferecido"] = teclas_recursos[evento.key]
                            etapa_troca_jogador = "quantidade_oferecida"
                            mensagem_jogo = "Escolha quantidade oferecida: 1 a 9."
                        continue

                    if etapa_troca_jogador == "quantidade_oferecida":
                        if pygame.K_1 <= evento.key <= pygame.K_9:
                            troca_jogador["quantidade_oferecida"] = evento.key - pygame.K_0
                            etapa_troca_jogador = "recurso_pedido"
                            mensagem_jogo = "Escolha recurso pedido: 1 Mad, 2 Tij, 3 Ove, 4 Tri, 5 Min."
                        continue

                    if etapa_troca_jogador == "recurso_pedido":
                        if evento.key in teclas_recursos:
                            troca_jogador["recurso_pedido"] = teclas_recursos[evento.key]
                            etapa_troca_jogador = "quantidade_pedida"
                            mensagem_jogo = "Escolha quantidade pedida: 1 a 9."
                        continue

                    if etapa_troca_jogador == "quantidade_pedida":
                        if pygame.K_1 <= evento.key <= pygame.K_9:
                            troca_jogador["quantidade_pedida"] = evento.key - pygame.K_0
                            etapa_troca_jogador = "confirmar"
                            alvo = jogadores[troca_jogador["alvo"]]

                            mensagem_jogo = (
                                f"{alvo['nome']}: S aceita / N recusa. "
                                f"Recebe {troca_jogador['quantidade_oferecida']} {troca_jogador['recurso_oferecido']} "
                                f"e entrega {troca_jogador['quantidade_pedida']} {troca_jogador['recurso_pedido']}."
                            )
                        continue

                    if etapa_troca_jogador == "confirmar":
                        if evento.key == pygame.K_s:
                            mensagem_jogo = validar_e_fazer_troca_jogadores(
                                jogador_atual,
                                troca_jogador,
                                jogadores
                            )
                            trocando_jogador = False
                            etapa_troca_jogador = None
                            troca_jogador = resetar_troca_jogador()

                        elif evento.key == pygame.K_n:
                            mensagem_jogo = "Troca recusada."
                            trocando_jogador = False
                            etapa_troca_jogador = None
                            troca_jogador = resetar_troca_jogador()

                        continue

                    continue

                if usando_ano_fartura:
                    teclas_recursos = {
                        pygame.K_1: "Madeira",
                        pygame.K_2: "Tijolo",
                        pygame.K_3: "Ovelha",
                        pygame.K_4: "Trigo",
                        pygame.K_5: "Minério"
                    }

                    if evento.key in teclas_recursos:
                        recurso = teclas_recursos[evento.key]
                        
                        if banco_recursos[recurso] <= 0:
                            mensagem_jogo = f"O banco nao tem {recurso} disponivel."
                            continue

                        retirar_recurso_do_banco(
                            banco_recursos,
                            jogadores[jogador_atual],
                            recurso,
                            1
                        )

                        recursos_ano_fartura.append(recurso)

                        if len(recursos_ano_fartura) < 2:
                            mensagem_jogo = f"Voce recebeu 1 {recurso}. Escolha mais 1 recurso."
                        else:
                            usando_ano_fartura = False
                            mensagem_jogo = (
                                f"Ano de Fartura concluido: recebeu "
                                f"{recursos_ano_fartura[0]} e {recursos_ano_fartura[1]}."
                            )
                            recursos_ano_fartura = []

                    elif evento.key == pygame.K_ESCAPE:
                        mensagem_jogo = "Nao e possivel cancelar apos iniciar Ano de Fartura."

                    continue

                if usando_monopolio:
                    teclas_recursos = {
                        pygame.K_1: "Madeira",
                        pygame.K_2: "Tijolo",
                        pygame.K_3: "Ovelha",
                        pygame.K_4: "Trigo",
                        pygame.K_5: "Minério"
                    }

                    if evento.key in teclas_recursos:
                        recurso = teclas_recursos[evento.key]
                        mensagem_jogo = aplicar_monopolio(jogador_atual, jogadores, recurso)
                        usando_monopolio = False

                    continue
                
                if existe_acao_pendente(
                    escolhendo_ladrao,
                    escolhendo_vitima_ladrao,
                    descartando_recursos,
                    trocando_banco,
                    trocando_jogador,
                    usando_construcao_estradas,
                    usando_ano_fartura,
                    usando_monopolio
                ):
                    mensagem_jogo = "Finalize a acao atual antes de fazer outra."
                    continue

                if evento.key == pygame.K_SPACE:
                    if fase_inicial:
                        print("Não é possível rolar dados durante a fase inicial.")

                    elif not dado_rolado_no_turno:
                        ultimo_dado = random.randint(1, 6) + random.randint(1, 6)
                        
                        historico_dados.append(f"{jogadores[jogador_atual]['nome']} tirou {ultimo_dado} no dado")
                        historico_dados = historico_dados[-5:]
                        
                        if ultimo_dado == 7:
                            jogador_que_rolou_7 = jogador_atual
                            fila_descarte = criar_fila_descarte(jogadores)

                            estado_descarte = preparar_proximo_descarte(fila_descarte, jogadores, banco_recursos)

                            descartando_recursos = estado_descarte["descartando"]
                            jogador_descartando = estado_descarte["jogador_descartando"]
                            quantidade_descartar = estado_descarte["quantidade_para_descartar"]
                            quantidade_descartada = estado_descarte["quantidade_descartada"]
                            mensagem_jogo = estado_descarte["mensagem"]

                            if descartando_recursos:
                                solicitar_passagem_tela(
                                    jogador_descartando,
                                    "descarte",
                                    f"Saiu 7! {jogadores[jogador_descartando]['nome']} deve descartar recursos."
                                )
                            else:
                                solicitar_passagem_tela(
                                    jogador_que_rolou_7,
                                    "ladrao",
                                    f"Descarte concluido. {jogadores[jogador_que_rolou_7]['nome']} deve mover o ladrao.",
                                    "iniciar_ladrao"
                                )
                        else:
                            mensagem_jogo = ""
                            distribuir_recursos(tabuleiro, ultimo_dado, jogadores, ladrao, banco_recursos)
                        
                        dado_rolado_no_turno = True
                        print(f"{jogadores[jogador_atual]['nome']} rolou o dado: {ultimo_dado}")

                    else:
                        print("Você já rolou o dado neste turno.")
                
                elif evento.key == pygame.K_RETURN:
                        if (
                            escolhendo_ladrao
                            or escolhendo_vitima_ladrao
                            or descartando_recursos
                            or trocando_banco
                            or trocando_jogador
                            or usando_construcao_estradas
                            or usando_ano_fartura
                            or usando_monopolio
                        ):
                            mensagem_jogo = "Finalize a acao atual antes de passar o turno."
                        
                        elif fase_inicial:
                            if not jogador_completou_rodada_inicial(jogador_atual, indice_fase_inicial, jogadores):
                                print("Você precisa construir 1 aldeia e 1 estrada antes de passar.")
                            else:
                                indice_fase_inicial += 1

                                if indice_fase_inicial < len(ordem_fase_inicial):
                                    proximo_jogador = ordem_fase_inicial[indice_fase_inicial]
                                    print(f"Fase inicial: agora é a vez de {jogadores[proximo_jogador]['nome']}")

                                    if deve_mostrar_tela_passagem(jogador_atual, proximo_jogador, jogadores):
                                        proximo_jogador_pendente = proximo_jogador
                                        tipo_tela_passagem = "turno"
                                        tela_passagem_turno = True
                                    else:
                                        jogador_atual = proximo_jogador
                                else:
                                    print("Todos já fizeram suas jogadas iniciais.")

                        else:
                            if not dado_rolado_no_turno:
                                print("Você precisa rolar o dado antes de passar o turno.")
                            else:
                                limpar_cartas_compradas_turno(jogadores[jogador_atual])
                                jogadores[jogador_atual]["usou_carta_dev_turno"] = False

                                proximo_jogador = (jogador_atual + 1) % len(jogadores)

                                if deve_mostrar_tela_passagem(jogador_atual, proximo_jogador, jogadores):
                                    proximo_jogador_pendente = proximo_jogador
                                    tipo_tela_passagem = "turno"
                                    tela_passagem_turno = True
                                else:
                                    jogador_atual = passar_turno(jogador_atual, jogadores)
                                    dado_rolado_no_turno = False
                                                
                elif evento.key == pygame.K_p:
                    if fase_inicial:
                        mensagem_jogo = "Nao e possivel trocar durante a fase inicial."
                    elif not dado_rolado_no_turno:
                        mensagem_jogo = "Role o dado antes de trocar."
                    else:
                        trocando_jogador = True
                        etapa_troca_jogador = "escolher_alvo"
                        troca_jogador = resetar_troca_jogador()
                        mensagem_jogo = "Escolha jogador para trocar: pressione 1, 2, 3..."
                
                elif evento.key == pygame.K_d:
                    if fase_inicial:
                        mensagem_jogo = "Nao e possivel comprar desenvolvimento durante a fase inicial."
                    elif not dado_rolado_no_turno:
                        mensagem_jogo = "Role o dado antes de comprar desenvolvimento."
                    else:
                        mensagem_jogo = comprar_carta_desenvolvimento(
                            jogadores[jogador_atual],
                            baralho_desenvolvimento,
                            banco_recursos
                        )
                elif evento.key == pygame.K_m:
                    jogador = jogadores[jogador_atual]

                    if fase_inicial:
                        mensagem_jogo = "Nao e possivel usar Monopolio durante a fase inicial."

                    elif escolhendo_ladrao or escolhendo_vitima_ladrao:
                        mensagem_jogo = "Finalize a acao do ladrao antes de usar outra carta."

                    elif jogador["usou_carta_dev_turno"]:
                        mensagem_jogo = "Voce ja usou uma carta de desenvolvimento neste turno."

                    else:
                        sucesso, mensagem = usar_monopolio(jogador)
                        mensagem_jogo = mensagem

                        if sucesso:
                            jogador["usou_carta_dev_turno"] = True
                            usando_monopolio = True
                            mensagem_jogo = "Monopolio: escolha recurso. 1 Mad, 2 Tij, 3 Ove, 4 Tri, 5 Min."
                            
                elif evento.key == pygame.K_f:
                    jogador = jogadores[jogador_atual]

                    if fase_inicial:
                        mensagem_jogo = "Nao e possivel usar Ano de Fartura durante a fase inicial."

                    elif escolhendo_ladrao or escolhendo_vitima_ladrao:
                        mensagem_jogo = "Finalize a acao do ladrao antes de usar outra carta."

                    elif jogador["usou_carta_dev_turno"]:
                        mensagem_jogo = "Voce ja usou uma carta de desenvolvimento neste turno."

                    else:
                        sucesso, mensagem = usar_ano_de_fartura(jogador)
                        mensagem_jogo = mensagem

                        if sucesso:
                            jogador["usou_carta_dev_turno"] = True
                            usando_ano_fartura = True
                            recursos_ano_fartura = []
                            mensagem_jogo = ""

                elif evento.key == pygame.K_k:
                    jogador = jogadores[jogador_atual]

                    if fase_inicial:
                        mensagem_jogo = "Nao e possivel usar Cavaleiro durante a fase inicial."

                    elif escolhendo_ladrao or escolhendo_vitima_ladrao:
                        mensagem_jogo = "Finalize a acao do ladrao antes de usar outra carta."

                    elif jogador["usou_carta_dev_turno"]:
                        mensagem_jogo = "Voce ja usou uma carta de desenvolvimento neste turno."

                    else:
                        sucesso, mensagem = usar_cavaleiro(jogador)
                        mensagem_jogo = mensagem

                        if sucesso:
                            jogador["usou_carta_dev_turno"] = True

                            mensagem_maior_exercito = atualizar_maior_exercito(jogadores)

                            escolhendo_ladrao = True
                            jogador_movendo_ladrao = jogador_atual

                            if mensagem_maior_exercito is not None:
                                mensagem_jogo = f"{mensagem_maior_exercito} Clique em um terreno para mover o ladrao."
                            else:
                                mensagem_jogo = "Cavaleiro usado! Clique em um terreno para mover o ladrao."

                elif evento.key == pygame.K_r:
                    jogador = jogadores[jogador_atual]

                    if fase_inicial:
                        mensagem_jogo = "Nao e possivel usar Construcao de Estradas durante a fase inicial."

                    elif escolhendo_ladrao or escolhendo_vitima_ladrao:
                        mensagem_jogo = "Finalize a acao do ladrao antes de usar outra carta."

                    elif jogador["usou_carta_dev_turno"]:
                        mensagem_jogo = "Voce ja usou uma carta de desenvolvimento neste turno."

                    else:
                        sucesso, mensagem = usar_construcao_de_estradas(jogador)
                        mensagem_jogo = mensagem

                        if sucesso:
                            jogador["usou_carta_dev_turno"] = True
                            usando_construcao_estradas = True
                            estradas_gratis_restantes = 2
                            mensagem_jogo = "Construcao de Estradas: construa 2 estradas gratis."

                elif evento.key == pygame.K_t:
                    dar_recursos_teste(jogadores[jogador_atual], banco_recursos)
                    print(f"Recursos adicionados para {jogadores[jogador_atual]['nome']}")
                
                elif evento.key == pygame.K_y:
                    dar_recursos_teste_para_todos(jogadores, banco_recursos)
                
                elif evento.key == pygame.K_i:
                    fase_inicial = False
                    print("Fase inicial encerrada. O jogo normal começou.")

                elif evento.key == pygame.K_b:
                    if fase_inicial:
                        mensagem_jogo = "Nao e possivel trocar durante a fase inicial."
                    elif not dado_rolado_no_turno:
                        mensagem_jogo = "Role o dado antes de trocar."
                    else:
                        trocando_banco = True
                        recurso_entregar_banco = None
                        mensagem_jogo = "Banco - escolha recurso para entregar."

                elif evento.key == pygame.K_c:
                    if fase_inicial:
                        print("Não é possível construir cidade durante a fase inicial.")

                    elif vertice_selecionado is not None:
                        if not dado_rolado_no_turno:
                            print("Você precisa rolar o dado antes de construir.")
                        else:
                            tentar_construir_cidade(vertice_selecionado, jogador_atual, jogadores, banco_recursos)

                        vertice_selecionado = None

                    else:
                        print("Selecione uma aldeia sua antes de apertar C.")

        desenhar_tabuleiro(TELA, tabuleiro, ultimo_dado, ladrao)
        desenhar_portos(TELA, portos)
        desenhar_vertices_e_aldeias(TELA, vertices_globais, vertice_selecionado, jogadores)
        desenhar_banco_recursos(TELA, banco_recursos)
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
            quantidade_descartada,
            trocando_banco, 
            recurso_entregar_banco,
            trocando_jogador, 
            etapa_troca_jogador, 
            troca_jogador,
            portos, 
            usando_construcao_estradas, 
            estradas_gratis_restantes,
            usando_ano_fartura,
            recursos_ano_fartura,
            usando_monopolio,
            historico_dados,
            escolhendo_ladrao,
            banco_recursos
        )

        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()