import pygame

class Menu():
    def __init__(self, game):
        self.game = game

        # Carrega a imagem original do fundo
        imagem_original = pygame.image.load("assets/CATTAN menu inicial.png").convert()
        self.background = pygame.transform.scale(imagem_original, (self.game.DISPLAY_W, self.game.DISPLAY_H))
        
        self.mid_w, self.mid_h = self.game.DISPLAY_W / 2 , self.game.DISPLAY_H / 2
        self.run_display = True
        self.cursor_rect = pygame.Rect(0,0,20,20)
        
        self.DARK_PURPLE = (48, 25, 52) 
        self.TEXT_COLOR = (48, 25, 52)
        self.TITLE_COLOR = (35, 15, 40)
        self.CURSOR_COLOR = (255, 190, 40)
        self.PANEL_COLOR = (245, 235, 220, 225)
        self.PANEL_BORDER = (48, 25, 52)

        self.offset = -125

        # --- Lógica do Gato Animado ---
        # Carrega os frames (1, 2 e 3 conforme os arquivos na pasta assets)
        self.cat_frames = []
        for frame_num in range(1, 4): # Isso vai gerar os números 1, 2 e 3
            img = pygame.image.load(f"assets/gt.{frame_num}.png").convert_alpha()
            # Redimensiona mantendo o aspecto, com altura 40
            largura_original, altura_original = img.get_size()
            proporcao = largura_original / altura_original
            img_redimensionada = pygame.transform.smoothscale(img, (int(40 * proporcao), 40))
            self.cat_frames.append(img_redimensionada)

        self.cat_index = 0
        self.cat_animation_speed = 0.01 # Velocidade da troca de frames
        self.cat_frame_counter = 0
        
        self.cat_x = 0
        # Centraliza o gato verticalmente na barra de 60px (Barra começa em H-60, gato tem 40, sobra 10 de margem)
        self.cat_y = self.game.DISPLAY_H - 50 
        self.cat_speed = 0.2
        self.cat_facing_right = True

    def draw_bottom_bar(self):
        pygame.draw.rect(self.game.display, self.DARK_PURPLE, (0, self.game.DISPLAY_H - 60, self.game.DISPLAY_W, 60))

    def draw_menu_instructions(self, texto):
        self.game.draw_text(
            texto,
            16,
            self.game.DISPLAY_W // 2,
            self.game.DISPLAY_H - 30,
            self.game.WHITE
        )

    def draw_menu_panel(self, largura=420, altura=320, y_offset=40):
        painel = pygame.Surface((largura, altura), pygame.SRCALPHA)
        painel.fill(self.PANEL_COLOR)

        x = int(self.mid_w - largura / 2)
        y = int(self.mid_h - altura / 2 + y_offset)

        self.game.display.blit(painel, (x, y))

        pygame.draw.rect(
            self.game.display,
            self.PANEL_BORDER,
            (x, y, largura, altura),
            3,
            border_radius=12
        )

    def update_cat(self):
        # 1. Movimentação
        self.cat_x += self.cat_speed
        
        # 2. Colisão com as bordas e inversão
        if self.cat_x + self.cat_frames[0].get_width() > self.game.DISPLAY_W:
            self.cat_speed *= -1
            self.cat_facing_right = False
        elif self.cat_x < 0:
            self.cat_speed *= -1
            self.cat_facing_right = True

        # 3. Animação (troca de frame)
        self.cat_frame_counter += self.cat_animation_speed
        if self.cat_frame_counter >= len(self.cat_frames):
            self.cat_frame_counter = 0
        self.cat_index = int(self.cat_frame_counter)

        # 4. Desenho com inversão de imagem (flip)
        current_frame = self.cat_frames[self.cat_index]
        if not self.cat_facing_right:
            current_frame = pygame.transform.flip(current_frame, True, False)
        
        self.game.display.blit(current_frame, (self.cat_x, self.cat_y))

    def draw_cursor(self):
        x = int(self.cursor_rect.centerx)
        y = int(self.cursor_rect.top)

        pontos = [
            (x - 10, y - 8),
            (x - 10, y + 8),
            (x + 4, y)
        ]

        pygame.draw.polygon(
            self.game.display,
            self.PANEL_BORDER,
            pontos
        )

        pontos_internos = [
            (x - 7, y - 5),
            (x - 7, y + 5),
            (x + 1, y)
        ]

        pygame.draw.polygon(
            self.game.display,
            self.CURSOR_COLOR,
            pontos_internos
        )

    def play_cursor_sound(self):
        self.game.play_cursor_sound()

    def play_confirm_sound(self):
        self.game.play_confirm_sound()

    def blit_screen(self):
        self.game.window.blit(self.game.display,(0,0))
        pygame.display.update()
        self.game.reset_keys()


class MainMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)

        self.state = "Start"

        self.start_x, self.start_y = self.mid_w, self.mid_h + 30
        self.options_x, self.options_y = self.mid_w, self.mid_h + 90
        self.credits_x, self.credits_y = self.mid_w, self.mid_h + 150
        self.exit_x, self.exit_y = self.mid_w, self.mid_h + 210

        self.cursor_rect.midtop = (
            self.start_x + self.offset,
            self.start_y
        )

        btn_w, btn_h = 150, 55

        self.title_image = pygame.image.load(
            "assets/Menu-principal.png"
        ).convert_alpha()
        self.title_image = pygame.transform.smoothscale(
            self.title_image,
            (250, 75)
        )
        self.title_rect = self.title_image.get_rect(
            center=(self.mid_w, self.mid_h - 100)
        )

        self.start_img = pygame.image.load(
            "assets/Iniciar-jogo.png"
        ).convert_alpha()
        self.start_img = pygame.transform.smoothscale(
            self.start_img,
            (btn_w, btn_h)
        )
        self.start_img_rect = self.start_img.get_rect(
            center=(self.start_x, self.start_y)
        )

        self.options_img = pygame.image.load(
            "assets/configurações.png"
        ).convert_alpha()
        self.options_img = pygame.transform.smoothscale(
            self.options_img,
            (btn_w, btn_h)
        )
        self.options_img_rect = self.options_img.get_rect(
            center=(self.options_x, self.options_y)
        )

        self.credits_img = pygame.image.load(
            "assets/Creditos.png"
        ).convert_alpha()
        self.credits_img = pygame.transform.smoothscale(
            self.credits_img,
            (btn_w, btn_h)
        )
        self.credits_img_rect = self.credits_img.get_rect(
            center=(self.credits_x, self.credits_y)
        )

        self.exit_img = pygame.image.load(
            "assets/Sair.png"
        ).convert_alpha()
        self.exit_img = pygame.transform.smoothscale(
            self.exit_img,
            (btn_w, btn_h)
        )
        self.exit_img_rect = self.exit_img.get_rect(
            center=(self.exit_x, self.exit_y)
        )

    def display_menu(self):
        self.run_display = True

        while self.run_display:
            self.game.check_events()
            self.check_input()

            self.game.display.blit(self.background, (0, 0))
            self.game.display.blit(self.title_image, self.title_rect)

            self.game.display.blit(self.start_img, self.start_img_rect)
            self.game.display.blit(self.options_img, self.options_img_rect)
            self.game.display.blit(self.credits_img, self.credits_img_rect)
            self.game.display.blit(self.exit_img, self.exit_img_rect)

            self.draw_bottom_bar()
            self.draw_menu_instructions(
                "↑ ↓ navegar | ENTER confirmar"
            )
            self.update_cat()
            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self):
        if self.game.DOWN_KEY:
            self.game.play_cursor_sound()

            if self.state == "Start":
                self.state = "Options"
                posicao = (self.options_x, self.options_y)

            elif self.state == "Options":
                self.state = "Credits"
                posicao = (self.credits_x, self.credits_y)

            elif self.state == "Credits":
                self.state = "Exit"
                posicao = (self.exit_x, self.exit_y)

            else:
                self.state = "Start"
                posicao = (self.start_x, self.start_y)

            self.cursor_rect.midtop = (
                posicao[0] + self.offset,
                posicao[1]
            )

        elif self.game.UP_KEY:
            self.game.play_cursor_sound()

            if self.state == "Start":
                self.state = "Exit"
                posicao = (self.exit_x, self.exit_y)

            elif self.state == "Options":
                self.state = "Start"
                posicao = (self.start_x, self.start_y)

            elif self.state == "Credits":
                self.state = "Options"
                posicao = (self.options_x, self.options_y)

            else:
                self.state = "Credits"
                posicao = (self.credits_x, self.credits_y)

            self.cursor_rect.midtop = (
                posicao[0] + self.offset,
                posicao[1]
            )

    def check_input(self):
        self.move_cursor()

        if self.game.START_KEY:
            self.game.play_confirm_sound()

            if self.state == "Start":
                self.game.game_mode = "custom"
                self.game.curr_menu = self.game.player_count_menu

            elif self.state == "Options":
                self.game.curr_menu = self.game.options

            elif self.state == "Credits":
                self.game.curr_menu = self.game.credits

            elif self.state == "Exit":
                self.game.running = False
                self.game.playing = False

            self.run_display = False

class PlayerCountMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = "2"

        self.two_x, self.two_y = self.mid_w, self.mid_h + 20
        self.three_x, self.three_y = self.mid_w, self.mid_h + 60
        self.four_x, self.four_y = self.mid_w, self.mid_h + 100

        self.cursor_rect.midtop = (self.two_x + self.offset, self.two_y)

    def display_menu(self):
        self.run_display = True

        while self.run_display:
            self.game.check_events()
            self.check_input()

            self.game.display.blit(self.background, (0, 0))

            self.draw_menu_panel(
                largura=470,
                altura=300,
                y_offset=25
            )

            self.game.draw_text(
                "Quantidade de participantes",
                24,
                self.mid_w,
                self.mid_h - 55,
                self.TITLE_COLOR,
                bold=True
            )

            self.game.draw_text(
                "2 jogadores",
                20,
                self.two_x,
                self.two_y,
                self.TEXT_COLOR
            )

            self.game.draw_text(
                "3 jogadores",
                20,
                self.three_x,
                self.three_y,
                self.TEXT_COLOR
            )

            self.game.draw_text(
                "4 jogadores",
                20,
                self.four_x,
                self.four_y,
                self.TEXT_COLOR
            )

            self.draw_bottom_bar()
            self.draw_menu_instructions(
                "↑ ↓ escolher | ENTER confirmar | ESC voltar"
            )
            self.update_cat()
            self.draw_cursor()
            self.blit_screen()

    def check_input(self):
        if self.game.BACK_KEY:
            self.game.play_back_sound()
            self.game.curr_menu = self.game.main_menu
            self.run_display = False

        elif self.game.DOWN_KEY:
            self.game.play_cursor_sound()

            if self.state == "2":
                self.state = "3"
                self.cursor_rect.midtop = (self.three_x + self.offset, self.three_y)
            elif self.state == "3":
                self.state = "4"
                self.cursor_rect.midtop = (self.four_x + self.offset, self.four_y)
            elif self.state == "4":
                self.state = "2"
                self.cursor_rect.midtop = (self.two_x + self.offset, self.two_y)

        elif self.game.UP_KEY:
            self.game.play_cursor_sound()

            if self.state == "2":
                self.state = "4"
                self.cursor_rect.midtop = (self.four_x + self.offset, self.four_y)
            elif self.state == "3":
                self.state = "2"
                self.cursor_rect.midtop = (self.two_x + self.offset, self.two_y)
            elif self.state == "4":
                self.state = "3"
                self.cursor_rect.midtop = (self.three_x + self.offset, self.three_y)

        elif self.game.START_KEY:
            self.game.play_confirm_sound()
            self.game.num_players = int(self.state)
            self.game.num_humanos = 1
            self.game.curr_menu = self.game.human_count_menu
            self.run_display = False

class HumanCountMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = 1
        self.option_positions = []

    def display_menu(self):
        self.run_display = True
        self.state = 1

        while self.run_display:
            self.game.check_events()
            self.check_input()

            self.game.display.blit(self.background, (0, 0))

            self.draw_menu_panel(
                largura=500,
                altura=340,
                y_offset=25
            )

            self.game.draw_text(
                "Quantidade de jogadores humanos",
                24,
                self.mid_w,
                self.mid_h - 75,
                self.TITLE_COLOR,
                bold=True
            )

            self.option_positions = []

            for i in range(1, self.game.num_players + 1):
                x = self.mid_w
                y = self.mid_h - 15 + (i - 1) * 42

                self.option_positions.append((x, y))

                self.game.draw_text(
                    f"{i} humano(s)",
                    20,
                    x,
                    y,
                    self.TEXT_COLOR
                )

            cursor_x, cursor_y = self.option_positions[self.state - 1]

            self.cursor_rect.midtop = (
                cursor_x + self.offset,
                cursor_y
            )

            self.draw_bottom_bar()
            self.draw_menu_instructions(
                "↑ ↓ escolher | ENTER confirmar | ESC voltar"
            )
            self.update_cat()
            self.draw_cursor()
            self.blit_screen()

    def check_input(self):
        if self.game.BACK_KEY:
            self.game.play_back_sound()
            self.game.curr_menu = self.game.player_count_menu
            self.run_display = False

        elif self.game.DOWN_KEY:
            self.game.play_cursor_sound()
            self.state += 1
            if self.state > self.game.num_players:
                self.state = 1

        elif self.game.UP_KEY:
            self.game.play_cursor_sound()
            self.state -= 1
            if self.state < 1:
                self.state = self.game.num_players

        elif self.game.START_KEY:
            self.game.play_confirm_sound()
            self.game.num_humanos = self.state
            self.game.curr_menu = self.game.confirmation_menu
            self.run_display = False

class ConfirmationMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)

        self.state = "Start"

        self.start_x, self.start_y = self.mid_w, self.mid_h + 140
        self.back_x, self.back_y = self.mid_w, self.mid_h + 185

        self.cursor_rect.midtop = (
            self.start_x + self.offset,
            self.start_y
        )

    def display_menu(self):
        self.run_display = True
        self.state = "Start"

        while self.run_display:
            self.game.check_events()
            self.check_input()

            self.game.display.blit(self.background, (0, 0))

            self.draw_menu_panel(
                largura=500,
                altura=420,
                y_offset=30
            )

            quantidade_bots = (
                self.game.num_players - self.game.num_humanos
            )

            self.game.draw_text(
                "Confirmar partida",
                28,
                self.mid_w,
                self.mid_h - 130,
                self.TITLE_COLOR,
                bold=True
            )

            self.game.draw_text(
                f"Jogadores totais: {self.game.num_players}",
                21,
                self.mid_w,
                self.mid_h - 65,
                self.TEXT_COLOR
            )

            self.game.draw_text(
                f"Humanos: {self.game.num_humanos}",
                21,
                self.mid_w,
                self.mid_h - 25,
                self.TEXT_COLOR
            )

            self.game.draw_text(
                f"Bots: {quantidade_bots}",
                21,
                self.mid_w,
                self.mid_h + 15,
                self.TEXT_COLOR
            )

            self.game.draw_text(
                "Iniciar partida",
                21,
                self.start_x,
                self.start_y,
                self.TEXT_COLOR,
                bold=True
            )

            self.game.draw_text(
                "Voltar",
                21,
                self.back_x,
                self.back_y,
                self.TEXT_COLOR
            )

            if self.state == "Start":
                posicao = (self.start_x, self.start_y)
            else:
                posicao = (self.back_x, self.back_y)

            self.cursor_rect.midtop = (
                posicao[0] + self.offset,
                posicao[1]
            )

            self.draw_bottom_bar()
            self.draw_menu_instructions(
                "↑ ↓ escolher | ENTER confirmar | ESC voltar"
            )
            self.update_cat()
            self.draw_cursor()
            self.blit_screen()

    def check_input(self):
        if self.game.BACK_KEY:
            self.game.play_back_sound()
            self.game.curr_menu = self.game.human_count_menu
            self.run_display = False

        elif self.game.UP_KEY or self.game.DOWN_KEY:
            self.game.play_cursor_sound()

            if self.state == "Start":
                self.state = "Back"
            else:
                self.state = "Start"

        elif self.game.START_KEY:
            self.game.play_confirm_sound()

            if self.state == "Start":
                self.game.playing = True

            else:
                self.game.curr_menu = self.game.human_count_menu

            self.run_display = False

class OptionsMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = 'Volume'
        self.volx, self.voly = self.mid_w, self.mid_h + 20
        self.controlsx, self.controlsy = self.mid_w, self.mid_h + 60
        self.cursor_rect.midtop = (self.volx + self.offset, self.voly)

    def display_menu(self):
        self.run_display = True

        while self.run_display:
            self.game.check_events()
            self.check_input()

            self.game.display.blit(self.background, (0, 0))

            self.draw_menu_panel(
                largura=420,
                altura=280,
                y_offset=20
            )

            self.game.draw_text(
                "Opcoes",
                28,
                self.mid_w,
                self.mid_h - 70,
                self.TITLE_COLOR,
                bold=True
            )

            self.game.draw_text(
                "Volume",
                21,
                self.volx,
                self.voly,
                self.TEXT_COLOR
            )

            self.game.draw_text(
                "Controles",
                21,
                self.controlsx,
                self.controlsy,
                self.TEXT_COLOR
            )

            self.draw_bottom_bar()
            self.draw_menu_instructions(
                "↑ ↓ navegar | ENTER confirmar | ESC voltar"
            )
            self.update_cat()
            self.draw_cursor()
            self.blit_screen()
    
    def check_input(self):
        if self.game.BACK_KEY:
            self.game.play_back_sound()
            self.game.curr_menu = self.game.main_menu
            self.run_display = False
        elif self.game.UP_KEY or self.game.DOWN_KEY:
            self.play_cursor_sound()
            if self.state == 'Volume':
                self.state = 'Controls'
                self.cursor_rect.midtop = (self.controlsx + self.offset, self.controlsy)
            elif self.state == 'Controls':
                self.state = 'Volume'
                self.cursor_rect.midtop = (self.volx + self.offset, self.voly)
        elif self.game.START_KEY:
            self.play_confirm_sound()
            if self.state == 'Volume':
                self.game.curr_menu = self.game.volume
            elif self.state == 'Controls':
                self.game.curr_menu = self.game.controls
            self.run_display = False
        

class VolumeMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = 'Music'
        self.musicx, self.musicy = self.mid_w, self.mid_h + 20
        self.effectsx, self.effectsy = self.mid_w, self.mid_h + 45
        self.cursor_rect.midtop = (self.musicx + self.offset, self.musicy)

    def display_menu(self):
        self.run_display = True

        while self.run_display:
            self.game.check_events()
            self.check_input()

            self.game.display.blit(self.background, (0, 0))

            self.draw_menu_panel(
                largura=500,
                altura=260,
                y_offset=20
            )

            music_percent = round(self.game.music_volume * 100)
            effects_percent = round(self.game.effects_volume * 100)

            self.game.draw_text(
                "Volume",
                28,
                self.mid_w,
                self.mid_h - 90,
                self.TITLE_COLOR,
                bold=True
            )

            self.game.draw_text(
                f"Musica: {music_percent}%",
                21,
                self.musicx,
                self.musicy,
                self.TEXT_COLOR
            )

            self.game.draw_text(
                f"Efeitos: {effects_percent}%",
                21,
                self.effectsx,
                self.effectsy,
                self.TEXT_COLOR
            )

            self.draw_bottom_bar()
            self.draw_menu_instructions(
                "↑ ↓ selecionar | ← → alterar | ESC voltar"
            )
            self.update_cat()
            self.draw_cursor()
            self.blit_screen()

    def check_input(self):
        if self.game.BACK_KEY:
            self.game.play_back_sound()
            self.game.curr_menu = self.game.options
            self.run_display = False
        elif self.game.UP_KEY or self.game.DOWN_KEY:
            self.play_cursor_sound()
            if self.state == 'Music':
                self.state = 'Effects'
                self.cursor_rect.midtop = (self.effectsx + self.offset, self.effectsy)
            elif self.state == 'Effects':
                self.state = 'Music'
                self.cursor_rect.midtop = (self.musicx + self.offset, self.musicy)
        elif self.game.LEFT_KEY:
            if self.state == 'Music':
                self.game.music_volume = max(0, round(self.game.music_volume - 0.01, 2))
                pygame.mixer.music.set_volume(self.game.music_volume)
            elif self.state == 'Effects':
                self.game.effects_volume = max(0, round(self.game.effects_volume - 0.01, 2))
        elif self.game.RIGHT_KEY:
            if self.state == 'Music':
                self.game.music_volume = min(1, round(self.game.music_volume + 0.01, 2))
                pygame.mixer.music.set_volume(self.game.music_volume)
            elif self.state == 'Effects':
                self.game.effects_volume = min(1, round(self.game.effects_volume + 0.01, 2))

class ControlsMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)

    def display_menu(self):
        self.run_display = True

        while self.run_display:
            self.game.check_events()

            if self.game.START_KEY or self.game.BACK_KEY:
                self.game.play_back_sound()
                self.game.curr_menu = self.game.options
                self.run_display = False

            self.game.display.blit(self.background, (0, 0))

            self.draw_menu_panel(
                largura=700,
                altura=500,
                y_offset=10
            )

            self.game.draw_text(
                "Controles",
                30,
                self.mid_w,
                self.mid_h - 205,
                self.TITLE_COLOR,
                bold=True
            )

            linhas = [
                "ESPACO - rolar os dados",
                "ENTER - passar o turno",
                "TAB - pausar a partida",
                "C - construir cidade",
                "D - comprar carta de desenvolvimento",
                "B - trocar com banco ou porto",
                "P - propor troca com outro jogador",
                "K - usar Cavaleiro",
                "R - usar Construcao de Estradas",
                "F - usar Ano de Fartura",
                "M - usar Monopolio",
                "Mouse - construir aldeias, estradas e mover o ladrao"
            ]

            y = self.mid_h - 145

            for linha in linhas:
                self.game.draw_text(
                    linha,
                    19,
                    self.mid_w,
                    y,
                    self.TEXT_COLOR
                )
                y += 32

            self.draw_bottom_bar()
            self.draw_menu_instructions(
                "ENTER ou ESC voltar"
            )
            self.update_cat()
            self.blit_screen()

class CreditsMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)

    def display_menu(self):
        self.run_display = True

        while self.run_display:
            self.game.check_events()

            if self.game.START_KEY or self.game.BACK_KEY:
                self.game.play_back_sound()
                self.game.curr_menu = self.game.main_menu
                self.run_display = False

            self.game.display.blit(self.background, (0, 0))

            self.draw_menu_panel(
                largura=520,
                altura=300,
                y_offset=20
            )

            self.game.draw_text(
                "Creditos",
                28,
                self.mid_w,
                self.mid_h - 75,
                self.TITLE_COLOR,
                bold=True
            )

            self.game.draw_text(
                "Autoria de Gatos Pingados",
                21,
                self.mid_w,
                self.mid_h - 10,
                self.TEXT_COLOR
            )

            self.draw_bottom_bar()
            self.draw_menu_instructions(
                "ENTER ou ESC voltar"
            )
            self.update_cat()
            self.blit_screen()