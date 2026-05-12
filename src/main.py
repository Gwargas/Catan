import pygame
from menu2 import *
import gameloop


class Game():
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.key.set_repeat(300, 40)
        self.running, self.playing = True, False
        self.UP_KEY = False
        self.DOWN_KEY = False
        self.LEFT_KEY = False
        self.RIGHT_KEY = False
        self.START_KEY = False
        self.BACK_KEY = False
        self.DISPLAY_W, self.DISPLAY_H = 800, 600
        self.display = pygame.Surface((self.DISPLAY_W, self.DISPLAY_H))
        self.window = pygame.display.set_mode(((self.DISPLAY_W, self.DISPLAY_H)))
        self.font_name = pygame.font.get_default_font()
        self.BLACK, self.WHITE = (0,0,0), (255,255,255)

        self.music_volume = 0.5
        self.effects_volume = 0.5

        self.cursor_sound = pygame.mixer.Sound("assets/cursor.wav")
        self.confirm_sound = pygame.mixer.Sound("assets/miado_confirmar.ogg")
        self.back_sound = pygame.mixer.Sound("assets/miado_voltar.ogg")
        self.cursor_sound.set_volume(self.effects_volume)
        self.confirm_sound.set_volume(self.effects_volume)

        pygame.mixer.music.load("assets/catanwaltz.wav")
        pygame.mixer.music.set_volume(self.music_volume)
        pygame.mixer.music.play(-1)

        self.main_menu = MainMenu(self)
        self.options = OptionsMenu(self)
        self.volume = VolumeMenu(self)
        self.credits = CreditsMenu(self)
        self.curr_menu = self.main_menu

    def game_loop(self):
        while self.playing:
            self.check_events()
            if self.START_KEY:
                self.playing = False

            voltar_menu = gameloop.main()
            self.playing = False

            if not voltar_menu:
                self.running = False
            
            self.window.fill(self.BLACK)
            self.window.blit(self.display,(0,0))
            pygame.display.update()
            self.reset_keys()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running, self.playing = False, False
                self.curr_menu.run_display = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.START_KEY = True
                if event.key == pygame.K_ESCAPE:
                    self.BACK_KEY = True
                if event.key == pygame.K_DOWN:
                    self.DOWN_KEY = True
                if event.key == pygame.K_UP:
                    self.UP_KEY = True
                if event.key == pygame.K_LEFT:
                    self.LEFT_KEY = True
                if event.key == pygame.K_RIGHT:
                    self.RIGHT_KEY = True

    def reset_keys(self):
        self.UP_KEY = False
        self.DOWN_KEY = False
        self.LEFT_KEY = False
        self.RIGHT_KEY = False
        self.START_KEY = False
        self.BACK_KEY = False
    
    def play_cursor_sound(self):
        self.cursor_sound.set_volume(self.effects_volume)
        self.cursor_sound.play()


    def play_confirm_sound(self):
        self.confirm_sound.set_volume(self.effects_volume)
        self.confirm_sound.play()

    def play_back_sound(self):
        self.back_sound.set_volume(self.effects_volume)
        self.back_sound.play()

    def draw_text(self, text, size, x, y):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (x,y)
        self.display.blit(text_surface, text_rect)

if __name__ == "__main__":
    g = Game()
    while g.running:
        g.curr_menu.display_menu()
        g.game_loop()