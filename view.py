import pygame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def init_screen():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pong Game")
    return screen

def draw(screen, all_sprites, score_paddle1, score_paddle2):
    screen.fill(BLACK)
    all_sprites.draw(screen)
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"{score_paddle1} - {score_paddle2}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - 50, 10))
    pygame.display.flip()