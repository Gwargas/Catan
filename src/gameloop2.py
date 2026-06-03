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
AZUL_JOGADOR = (0, 0, 255)
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

class vertice:
    def __init__(self, pos):
        self.pos = pos
        self.x = pos[0]
        self.y = pos[1]
        self.vizinhos = []

    def add_vizinho(self, v):
        if v not in self.vizinhos:
            self.vizinhos.append(v)

    def __eq__(self, other):
        return isinstance(other, vertice) and self.pos == other.pos

    def __hash__(self):
        return hash(self.pos)

def calcular_pontos_hexagono(centro_x, centro_y, tamanho):
    pontos = []
    for i in range(6):
        angulo_deg = 60 * i - 30
        angulo_rad = math.pi / 180 * angulo_deg
        x = int(centro_x + tamanho * math.cos(angulo_rad))
        y = int(centro_y + tamanho * math.sin(angulo_rad))
        pontos.append((x, y))
    return pontos

def _gerar_novo_tabuleiro():
    terrenos_embaralhados = TERRENOS[:]
    random.shuffle(terrenos_embaralhados)
    fichas_embaralhadas = FICHAS[:]
    random.shuffle(fichas_embaralhadas)

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
            cor = terrenos_embaralhados[idx_terreno]
            numero = None
            if cor != DESERTO:
                numero = fichas_embaralhadas[idx_ficha]
                idx_ficha += 1
            
            pontos = calcular_pontos_hexagono(cx, cy, TAMANHO_HEX)
            
            for px, py in pontos:
                pos_arredondado = (round(px), round(py))
                v = vertice(pos_arredondado)
                if v not in vertices_globais:
                    vertices_globais.append(v)
                
            tabuleiro.append({
                'id': idx_terreno,
                'centro': (cx, cy),
                'cor': cor,
                'numero': numero,
                'vertices': pontos
            })
            idx_terreno += 1
    
    # Adicionar vizinhos
    for i, v1 in enumerate(vertices_globais):
        for j, v2 in enumerate(vertices_globais):
            if i != j:
                dist = math.dist(v1.pos, v2.pos)
                if dist < TAMANHO_HEX + 5:
                    v1.add_vizinho(v2)
                    v2.add_vizinho(v1)
            
    return tabuleiro, vertices_globais

def _verificar_adjacencia_seis_oito(tabuleiro):
    posicoes_seis_oito = []
    for i, peca in enumerate(tabuleiro):
        if peca['numero'] in [6, 8]:
            posicoes_seis_oito.append(peca['centro'])

    distancia_minima_sq = (math.sqrt(3) * TAMANHO_HEX + 5) ** 2

    for i in range(len(posicoes_seis_oito)):
        for j in range(i + 1, len(posicoes_seis_oito)):
            cx1, cy1 = posicoes_seis_oito[i]
            cx2, cy2 = posicoes_seis_oito[j]
            dist_sq = (cx1 - cx2)**2 + (cy1 - cy2)**2
            if dist_sq < distancia_minima_sq:
                return False  # Encontrou adjacência inválida
    return True

def gerar_tabuleiro():
    while True:
        tabuleiro, vertices_globais = _gerar_novo_tabuleiro()
        if _verificar_adjacencia_seis_oito(tabuleiro):
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
            
            cor_texto = PRETO
            texto = FONTE_NUMEROS.render(str(peca['numero']), True, cor_texto)
            retangulo_texto = texto.get_rect(center=peca['centro'])
            tela.blit(texto, retangulo_texto)

def desenhar_vertices_e_aldeias(tela, vertices_globais, vertice_selecionado):
    for v in vertices_globais:
        pygame.draw.circle(tela, BRANCO, (v.x, v.y), 4)

    for e in estradas_construidas:
        pygame.draw.line(tela, PRETO, e[0].pos, e[1].pos, width=8)
        pygame.draw.line(tela, AZUL_JOGADOR, e[0].pos, e[1].pos, width=6)

    for v in aldeias_construidas:
        retangulo = pygame.Rect(0, 0, 16, 16)
        retangulo.center = (v.x, v.y)
        pygame.draw.rect(tela, AZUL_JOGADOR, retangulo)
        pygame.draw.rect(tela, PRETO, retangulo, 2)
        

    if vertice_selecionado != None:
        for v in vertice_selecionado.vizinhos:
            pygame.draw.line(tela, PRETO, vertice_selecionado.pos, v.pos, width=8)
            pygame.draw.line(tela, BRANCO, vertice_selecionado.pos, v.pos, width=6)

        pygame.draw.circle(tela, BRANCO, vertice_selecionado.pos, 10)
        pygame.draw.circle(tela, PRETO, vertice_selecionado.pos, 10, width=1)

    



def desenhar_interface(tela, ultimo_dado):
    #instrucao = FONTE_TEXTO.render("Clique nas pontas para construir aldeias. ESPAÇO para rolar dados.", True, PRETO)
    #tela.blit(instrucao, (20, 20))
    
    if ultimo_dado > 0:
        msg_dado = FONTE_TITULO.render(f"Dado rolado: {ultimo_dado}", True, PRETO)
        tela.blit(msg_dado, (20, 60))
        
    tela.blit(FONTE_TITULO.render("Inventário:", True, PRETO), (LARGURA - 150, 20))
    y_inv = 60
    for recurso, quantidade in inventario.items():
        texto_rec = FONTE_TEXTO.render(f"{recurso}: {quantidade}", True, PRETO)
        tela.blit(texto_rec, (LARGURA - 150, y_inv))
        y_inv += 30

def selecionar_ponto(pos_mouse, vertices_globais):
    mx, my = pos_mouse
    for v in vertices_globais:
        if math.hypot(v.x - mx, v.y - my) < 15:
            return v
    return None

def tentar_construir_aldeia(pos, vertices_globais):
    if pos not in aldeias_construidas:
        aldeias_construidas.append(pos)
        return True
    return False

def tentar_construir_estrada(pos1, pos2):
    for e in estradas_construidas:
        if (e[0] == pos1 and e[1] == pos2) or (e[0] == pos2 and e[1] == pos1):
            return False
    estradas_construidas.append([pos1, pos2])
    return True

def distribuir_recursos(tabuleiro, dado):
    for peca in tabuleiro:
        if peca['numero'] == dado and peca['cor'] != DESERTO:
            recurso = MAPA_RECURSOS[peca['cor']]
            for vx, vy in peca['vertices']:
                for v in aldeias_construidas:
                    ax, ay = v.x, v.y
                    if math.hypot(vx - ax, vy - ay) < 5:
                        inventario[recurso] += 1

def main():
    relogio = pygame.time.Clock()
    tabuleiro, vertices_globais = gerar_tabuleiro()
    ultimo_dado = 0
    vertice_selecionado = None
    
    rodando = True
    while rodando:
        TELA.fill(COR_FUNDO)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    if vertice_selecionado == None:
                        vertice_selecionado = selecionar_ponto(evento.pos, vertices_globais)
                    else:
                        if math.dist(evento.pos, vertice_selecionado.pos) < 10:
                            tentar_construir_aldeia(vertice_selecionado, vertices_globais)
                            vertice_selecionado = None

                        else:
                            for v in vertice_selecionado.vizinhos:
                                dist = abs((vertice_selecionado.y - v.y)*evento.pos[0] - (vertice_selecionado.x - v.x)*evento.pos[1] + vertice_selecionado.x * v.y 
                                           - vertice_selecionado.y * v.x)/math.dist(v.pos, vertice_selecionado.pos)
                                if dist <= 5:
                                    tentar_construir_estrada(vertice_selecionado, v)

                            vertice_selecionado = selecionar_ponto(evento.pos, vertices_globais)

                    
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    ultimo_dado = random.randint(1, 6) + random.randint(1, 6)
                    distribuir_recursos(tabuleiro, ultimo_dado)
        
        desenhar_tabuleiro(TELA, tabuleiro, ultimo_dado)
        desenhar_vertices_e_aldeias(TELA, vertices_globais, vertice_selecionado)
        desenhar_interface(TELA, ultimo_dado)
        
        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()