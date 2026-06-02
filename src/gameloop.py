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
            "nome": nome,
            "tipo": tipo,
            "cor": cores[i],
            "inventario": criar_inventario(),
            "pontos": 0
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

def desenhar_tabuleiro(tela, tabuleiro, ultimo_dado):
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

    



def desenhar_interface(tela, ultimo_dado, game_mode, jogador_atual, vencedor):
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
    
    if ultimo_dado > 0:
        msg_dado = FONTE_TITULO.render(f"Dado rolado: {ultimo_dado}", True, PRETO)
        tela.blit(msg_dado, (20, 95))
        
    tela.blit(FONTE_TITULO.render("Inventário:", True, PRETO), (LARGURA - 150, 20))
    y_inv = 60
    for recurso, quantidade in jogador_atual["inventario"].items():
        texto_rec = FONTE_TEXTO.render(f"{recurso}: {quantidade}", True, PRETO)
        tela.blit(texto_rec, (LARGURA - 150, y_inv))
        y_inv += 30

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

def tentar_construir_aldeia(pos, vertices_globais, jogador_atual, jogadores):
    jogador = jogadores[jogador_atual]

    if not tem_recursos(jogador, CUSTO_ALDEIA):
        print("Recursos insuficientes para construir aldeia.")
        return False

    for aldeia in aldeias_construidas:
        if aldeia["vertice"] == pos:
            print("Já existe uma aldeia neste ponto.")
            return False

        if aldeia["vertice"] in pos.vizinhos:
            print("Não pode construir aldeia colada em outra aldeia.")
            return False
    
    if jogador_tem_aldeia(jogador_atual) and not aldeia_conectada_ao_jogador(pos, jogador_atual):
        print("A nova aldeia precisa estar conectada a uma estrada sua.")
        return False

    gastar_recursos(jogador, CUSTO_ALDEIA)

    aldeias_construidas.append({
        "vertice": pos,
        "jogador": jogador_atual,
        "tipo": "aldeia"
    })

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

def tentar_construir_estrada(pos1, pos2, jogador_atual, jogadores):
    jogador = jogadores[jogador_atual]

    if not tem_recursos(jogador, CUSTO_ESTRADA):
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

    gastar_recursos(jogador, CUSTO_ESTRADA)

    estradas_construidas.append({
        "v1": pos1,
        "v2": pos2,
        "jogador": jogador_atual
    })

    print(f"{jogador['nome']} construiu uma estrada.")
    return True

def tentar_construir_cidade(pos, jogador_atual, jogadores):
    jogador = jogadores[jogador_atual]

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

def distribuir_recursos(tabuleiro, dado, jogadores):
    for peca in tabuleiro:
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

def verificar_vencedor(jogadores):
    for jogador in jogadores:
        if jogador["pontos"] >= PONTOS_PARA_VENCER:
            return jogador
    return None

def main(game_mode="custom", num_players=2, num_humanos=2):
    relogio = pygame.time.Clock()
    tabuleiro, vertices_globais = gerar_tabuleiro()
    ultimo_dado = 0
    vertice_selecionado = None
    jogadores = criar_jogadores(num_players, num_humanos)
    jogador_atual = 0
    tempo_turno_bot = 0
    dado_rolado_no_turno = False
    vencedor = None
    
    print(f"Modo de jogo iniciado: {game_mode}")
    print(f"Jogadores criados: {[j['nome'] for j in jogadores]}")
    
    rodando = True
    while rodando:
        TELA.fill(COR_FUNDO)

        vencedor = verificar_vencedor(jogadores)
        jogador = jogadores[jogador_atual]

        if jogador["tipo"] == "bot":
            tempo_turno_bot += 1

            if tempo_turno_bot >= 60:
                ultimo_dado = random.randint(1, 6) + random.randint(1, 6)
                distribuir_recursos(tabuleiro, ultimo_dado, jogadores)

                print(f"{jogador['nome']} rolou o dado: {ultimo_dado}")

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
                    if vertice_selecionado == None:
                        vertice_selecionado = selecionar_ponto(evento.pos, vertices_globais)
                    else:
                        if math.dist(evento.pos, vertice_selecionado.pos) < 10:
                            tentar_construir_aldeia(vertice_selecionado, vertices_globais, jogador_atual, jogadores)
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
                                    tentar_construir_estrada(vertice_selecionado, v, jogador_atual, jogadores)
                                    estrada_tentada = True
                                    break

                            if not estrada_tentada:
                                vertice_selecionado = selecionar_ponto(evento.pos, vertices_globais)
                            else:
                                vertice_selecionado = None
                    
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    if not dado_rolado_no_turno:
                        ultimo_dado = random.randint(1, 6) + random.randint(1, 6)
                        distribuir_recursos(tabuleiro, ultimo_dado, jogadores)
                        dado_rolado_no_turno = True
                        print(f"{jogadores[jogador_atual]['nome']} rolou o dado: {ultimo_dado}")
                    else:
                        print("Você já rolou o dado neste turno.")
                
                elif evento.key == pygame.K_RETURN:
                    jogador_atual = passar_turno(jogador_atual, jogadores)
                    dado_rolado_no_turno = False
                
                elif evento.key == pygame.K_t:
                    jogadores[jogador_atual]["inventario"]["Madeira"] += 1
                    jogadores[jogador_atual]["inventario"]["Tijolo"] += 1
                    jogadores[jogador_atual]["inventario"]["Ovelha"] += 1
                    jogadores[jogador_atual]["inventario"]["Trigo"] += 1
                    jogadores[jogador_atual]["inventario"]["Minério"] += 1
                    print(f"Recursos adicionados para {jogadores[jogador_atual]['nome']}")
                
                elif evento.key == pygame.K_c:
                    if vertice_selecionado is not None:
                        tentar_construir_cidade(vertice_selecionado, jogador_atual, jogadores)
                        vertice_selecionado = None
                    else:
                        print("Selecione uma aldeia sua antes de apertar C.")

        desenhar_tabuleiro(TELA, tabuleiro, ultimo_dado)
        desenhar_vertices_e_aldeias(TELA, vertices_globais, vertice_selecionado, jogadores)
        desenhar_interface(TELA, ultimo_dado, game_mode, jogadores[jogador_atual], vencedor)
        
        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()