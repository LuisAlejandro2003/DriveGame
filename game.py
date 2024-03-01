import pygame
import random
import threading
import time

# Dimensiones de la pantalla
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Eventos
collision_event = pygame.event.Event(pygame.USEREVENT + 1)
score_event = pygame.event.Event(pygame.USEREVENT + 2)
game_over_event = pygame.event.Event(pygame.USEREVENT + 3)

# Variable global para controlar la desaceleración
SLOW_DOWN = False

def draw_screen(screen, all_sprites, blocks_esquivados, notification1, notification2, notification3):
    screen.fill(WHITE)
    all_sprites.draw(screen)
    font = pygame.font.Font(None, 36)
    text = font.render("Bloques esquivados: " + str(blocks_esquivados), True, BLACK)
    screen.blit(text, (10, 10))
    if notification1:
        notification_text = font.render(notification1, True, RED)
        screen.blit(notification_text, (10, 50))
    if notification2:
        notification_text = font.render(notification2, True, RED)
        screen.blit(notification_text, (10, 100))
    if notification3:
        notification_text = font.render(notification3, True, RED)
        screen.blit(notification_text, (10, 150))
    pygame.display.flip()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed_x = 0

    def update(self):
        self.speed_x = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speed_x = -5
        if keys[pygame.K_RIGHT]:
            self.speed_x = 5
        self.rect.x += self.speed_x
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = random.randrange(1, 8)

    def update(self):
        global SLOW_DOWN
        if SLOW_DOWN:
            self.rect.y += self.speed_y // 2  # Reducir la velocidad a la mitad
        else:
            self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT + 10:
            self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_y = random.randrange(1, 8)

class PlayerMovementSemaphore(threading.Thread):
    def __init__(self, semaphore, delay):
        super().__init__()
        self.semaphore = semaphore
        self.delay = delay
        self.running = True

    def run(self):
        while self.running:
            time.sleep(self.delay)
            self.semaphore.release()

class ObstacleMovementSemaphore(threading.Thread):
    def __init__(self, semaphore, delay):
        super().__init__()
        self.semaphore = semaphore
        self.delay = delay
        self.running = True

    def run(self):
        while self.running:
            time.sleep(self.delay)
            self.semaphore.release()

def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pygame Race Game")

    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    # Crear semáforo para controlar el movimiento del jugador
    player_semaphore = threading.Semaphore(1)
    player_movement_semaphore = PlayerMovementSemaphore(player_semaphore, 0.1)
    player_movement_semaphore.start()

    # Crear semáforo para controlar el movimiento de los obstáculos
    obstacle_semaphore = threading.Semaphore(3)
    obstacle_movement_semaphore = ObstacleMovementSemaphore(obstacle_semaphore, 0.5)
    obstacle_movement_semaphore.start()

    clock = pygame.time.Clock()
    running = True
    score = 0
    counter = 0
    font = pygame.font.Font(None, 36)
    notification1 = ""
    notification2 = ""
    notification3 = ""

    start_time = time.time()  # Para medir el tiempo de juego

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        all_sprites.update()

        # Comprobar si el jugador ha colisionado con un obstáculo
        if pygame.sprite.spritecollide(player, obstacles, False):
            pygame.event.post(collision_event)

        # Comprobar si los obstáculos han pasado por debajo del jugador
        for obstacle in obstacles:
            if obstacle.rect.top > SCREEN_HEIGHT:
                score += 1
                obstacle.rect.x = random.randrange(SCREEN_WIDTH - obstacle.rect.width)
                obstacle.rect.y = random.randrange(-100, -40)
                obstacle.speed_y = random.randrange(1, 8)

        # Comprobar si el jugador ha esquivado 15 bloques
        if score % 15 == 0 and score > 0:
            pygame.event.post(score_event)
            counter += 1
            score = 0  # Restablecer la puntuación
            notification1 = "¡Felicidades! Has esquivado 15 bloques."

        # Controlar la generación de obstáculos con semáforo
        if obstacle_semaphore.acquire(blocking=False):
            obstacle = Obstacle()
            all_sprites.add(obstacle)
            obstacles.add(obstacle)

        # Verificar el tiempo transcurrido
        elapsed_time = time.time() - start_time
        if elapsed_time >= 10 and elapsed_time < 20:
            notification2 = "¡Has jugado 10 segundos!"
        elif elapsed_time >= 20 and elapsed_time < 30:
            notification2 = "¡WOW! Llevas 20 segundos jugando."
        elif elapsed_time >= 30:
            notification2 = "¡Eres un master! Llevas 30 segundos jugando."

        draw_screen(screen, all_sprites, counter, notification1, notification2, notification3)

        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == collision_event.type:
                # Aquí manejas el evento de colisión
                notification3 = "¡Colisión detectada! Continúa jugando."
                SLOW_DOWN = True  # Activar la desaceleración
                pygame.time.set_timer(pygame.USEREVENT + 4, 5000)  # Desactivar la desaceleración después de 5 segundos
            elif event.type == pygame.USEREVENT + 4:
                SLOW_DOWN = False  # Desactivar la desaceleración
            elif event.type == score_event.type:
                # Aquí manejas el evento de puntaje
                pass
            elif event.type == game_over_event.type:
                # Aquí manejas el evento de fin de juego
                running = False

    pygame.quit()

if __name__ == "__main__":
    main()