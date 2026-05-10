import pygame

class Menu():
    def __init__(self, game):
        self.game = game
        self.mid_w, self.mid_h = self.game.DISPLAY_W / 2 , self.game.DISPLAY_H / 2
        self.run_display = True
        self.cursor_rect = pygame.Rect(0,0,20,20)
        self.offset = -100

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
        self.optionsx, self.optionsy = self.mid_w, self.mid_h + 50
        self.creditsx, self.creditsy = self.mid_w, self.mid_h + 70
        self.cursor_rect.midtop = (self.startx + self.offset, self.starty)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill(self.game.BLACK)
            self.game.draw_text("Menu principal", 20, self.game.DISPLAY_W/2,self.game.DISPLAY_H/2 - 20)
            self.game.draw_text("Iniciar Jogo", 20, self.startx,self.starty)
            self.game.draw_text("Configurações", 20, self.optionsx,self.optionsy)
            self.game.draw_text("Creditos", 20, self.creditsx,self.creditsy)
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
        self.controlsx, self.controlsy = self.mid_w, self.mid_h + 40
        self.cursor_rect.midtop = (self.volx + self.offset, self.voly)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill((0,0,0))
            self.game.draw_text("Opcoes", 20, self.game.DISPLAY_W /2, self.game.DISPLAY_H /2 - 30)
            self.game.draw_text("Volume", 15, self.volx, self.voly)
            self.game.draw_text("Controles", 15, self.controlsx, self.controlsy)
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

            self.game.display.fill(self.game.BLACK)

            music_percent = round(self.game.music_volume * 100)
            effects_percent = round(self.game.effects_volume * 100)

            self.game.draw_text("Volume", 20, self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2 - 40)
            self.game.draw_text(f"Música: {music_percent}%", 15, self.musicx, self.musicy)
            self.game.draw_text(f"Efeitos: {effects_percent}%", 15, self.effectsx, self.effectsy)
            self.game.draw_text("Use as setas para alterar", 12, self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2 + 100)
            self.game.draw_text("ESC para voltar", 12, self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2 + 120)

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
                self.game.music_volume = round(self.game.music_volume - 0.01, 2)

                if self.game.music_volume < 0:
                    self.game.music_volume = 0

                pygame.mixer.music.set_volume(self.game.music_volume)
            elif self.state == 'Effects':
                self.game.effects_volume = round(self.game.effects_volume - 0.01, 2)

                if self.game.effects_volume < 0:
                    self.game.effects_volume = 0

        elif self.game.RIGHT_KEY:
            if self.state == 'Music':
                self.game.music_volume = round(self.game.music_volume + 0.01, 2)

                if self.game.music_volume > 1:
                    self.game.music_volume = 1

                pygame.mixer.music.set_volume(self.game.music_volume)
            elif self.state == 'Effects':
                self.game.effects_volume = round(self.game.effects_volume + 0.01, 2)

                if self.game.effects_volume > 1:
                    self.game.effects_volume = 1

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
            self.game.display.fill(self.game.BLACK)
            self.game.draw_text('Creditos', 20, self.game.DISPLAY_W/2, self.game.DISPLAY_H /2 - 20)
            self.game.draw_text('Autoria de Gatos Pingados', 15, self.game.DISPLAY_W/2, self.game.DISPLAY_H/2 + 10)
            self.blit_screen()