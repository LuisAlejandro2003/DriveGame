import pygame
import sys
import random

# Configuraciones del juego
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Clase para representar la bolita
class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed_x = random.choice([5, -5])
        self.speed_y = random.choice([5, -5])

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Rebotar en los bordes superior e inferior
        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.speed_y = -self.speed_y

# Clase para representar los palitos
class Paddle(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pygame.Surface((20, 100))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, SCREEN_HEIGHT // 2)
        self.speed_y = 0

    def update(self):
        self.rect.y += self.speed_y

        # Mantener el palito en la pantalla
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

# Función para reiniciar la posición de la bolita
def reset_ball():
    ball.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    ball.speed_x = random.choice([5, -5])
    ball.speed_y = random.choice([5, -5])

# Inicialización de Pygame
pygame.init()

# Configuración de la pantalla
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong Game")

# Grupos de sprites
all_sprites = pygame.sprite.Group()
paddles = pygame.sprite.Group()
ball = Ball()

# Creación de palitos
paddle1 = Paddle(20)
paddle2 = Paddle(SCREEN_WIDTH - 20)

all_sprites.add(paddle1, paddle2, ball)
paddles.add(paddle1, paddle2)

# Reloj para controlar la velocidad de actualización
clock = pygame.time.Clock()

# Contadores de goles
score_paddle1 = 0
score_paddle2 = 0
font = pygame.font.Font(None, 36)

# Bucle principal del juego
running = True
while running:
    # Manejo de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                paddle2.speed_y = -5
            elif event.key == pygame.K_DOWN:
                paddle2.speed_y = 5
            elif event.key == pygame.K_w:
                paddle1.speed_y = -5
            elif event.key == pygame.K_s:
                paddle1.speed_y = 5

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                paddle2.speed_y = 0
            elif event.key == pygame.K_w or event.key == pygame.K_s:
                paddle1.speed_y = 0

    # Actualización de sprites
    all_sprites.update()

    # Colisiones con palitos
    hits = pygame.sprite.spritecollide(ball, paddles, False)
    for hit in hits:
        ball.speed_x = -ball.speed_x

    # Rebotar en los bordes izquierdo y derecho
    if ball.rect.left < 0:
        score_paddle2 += 1
        reset_ball()
    elif ball.rect.right > SCREEN_WIDTH:
        score_paddle1 += 1
        reset_ball()

    # Dibujar en la pantalla
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # Dibujar contadores de goles
    score_text = font.render(f"{score_paddle1} - {score_paddle2}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - 50, 10))

    pygame.display.flip()

    # Controlar la velocidad de actualización
    clock.tick(60)

# Cierre de Pygame al salir
pygame.quit()
sys.exit()
