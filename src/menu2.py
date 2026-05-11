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
        self.offset = -150 
        
        self.DARK_PURPLE = (48, 25, 52) 

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
        pygame.draw.rect(self.game.display, self.DARK_PURPLE, (0, self.game.DISPLAY_H - 20, self.game.DISPLAY_W, 60))

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
        self.game.draw_text("*", 15, self.cursor_rect.x, self.cursor_rect.y)

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
        Menu.__init__(self,game)
        self.state = "Start"
        self.startx, self.starty = self.mid_w, self.mid_h + 30
        self.optionsx, self.optionsy = self.mid_w, self.mid_h + 90 
        self.creditsx, self.creditsy = self.mid_w, self.mid_h + 150
        self.cursor_rect.midtop = (self.startx + self.offset, self.starty)

        btn_w, btn_h = 150, 55

        self.title_image = pygame.image.load("assets/Menu-principal.png").convert_alpha()
        self.title_image = pygame.transform.smoothscale(self.title_image, (250, 75))
        self.title_rect = self.title_image.get_rect(center=(self.mid_w, self.mid_h - 100))

        self.start_img = pygame.image.load("assets/Iniciar-jogo.png").convert_alpha()
        self.start_img = pygame.transform.smoothscale(self.start_img, (btn_w, btn_h))
        self.start_img_rect = self.start_img.get_rect(center=(self.startx, self.starty))

        self.options_img = pygame.image.load("assets/configurações.png").convert_alpha()
        self.options_img = pygame.transform.smoothscale(self.options_img, (btn_w, btn_h))
        self.options_img_rect = self.options_img.get_rect(center=(self.optionsx, self.optionsy))

        self.credits_img = pygame.image.load("assets/Creditos.png").convert_alpha()
        self.credits_img = pygame.transform.smoothscale(self.credits_img, (btn_w, btn_h))
        self.credits_img_rect = self.credits_img.get_rect(center=(self.creditsx, self.creditsy))

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
            
            # Ordem importante: Barra primeiro, Gato depois
            self.draw_bottom_bar()
            self.update_cat()
            
            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self):
        if self.game.DOWN_KEY:
            self.game.play_cursor_sound()
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.optionsx + self.offset, self.optionsy)
                self.state = 'Options'
            elif self.state == 'Options':
                self.cursor_rect.midtop = (self.creditsx + self.offset, self.creditsy)
                self.state = 'Credits'
            elif self.state == 'Credits':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                self.state = 'Start'
        elif self.game.UP_KEY:
            self.game.play_cursor_sound()
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.creditsx + self.offset, self.creditsy)
                self.state = 'Credits'
            elif self.state == 'Options':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                self.state = 'Start'
            elif self.state == 'Credits':
                self.cursor_rect.midtop = (self.optionsx + self.offset, self.optionsy)
                self.state = 'Options'

    def check_input(self):
        self.move_cursor()
        if self.game.START_KEY:
            self.game.play_confirm_sound()
            if self.state == 'Start':
                self.game.playing = True
            elif self.state == 'Options':
                self.game.curr_menu = self.game.options
            elif self.state == 'Credits':
                self.game.curr_menu = self.game.credits
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
            self.game.draw_text("Opcoes", 20, self.game.DISPLAY_W /2, self.game.DISPLAY_H /2 - 30)
            self.game.draw_text("Volume", 15, self.volx, self.voly)
            self.game.draw_text("Controles", 15, self.controlsx, self.controlsy)
            
            self.draw_bottom_bar()
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
                pass
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

            music_percent = round(self.game.music_volume * 100)
            effects_percent = round(self.game.effects_volume * 100)

            self.game.draw_text("Volume", 20, self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2 - 40)
            self.game.draw_text(f"Música: {music_percent}%", 15, self.musicx, self.musicy)
            self.game.draw_text(f"Efeitos: {effects_percent}%", 15, self.effectsx, self.effectsy)
            self.game.draw_text("Use as setas para alterar", 12, self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2 + 100)
            self.game.draw_text("ESC para voltar", 12, self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2 + 120)

            self.draw_bottom_bar()
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
            self.game.draw_text('Creditos', 20, self.game.DISPLAY_W/2, self.game.DISPLAY_H /2 - 20)
            self.game.draw_text('Autoria de Gatos Pingados', 15, self.game.DISPLAY_W/2, self.game.DISPLAY_H/2 + 10)
            
            self.draw_bottom_bar()
            self.update_cat()
            
            self.blit_screen()