import pygame
import random
import threading
import time

SCREEN_WIDTH = 800      # Dimensiones de la pantalla
SCREEN_HEIGHT = 600

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

collision_event = pygame.event.Event(pygame.USEREVENT + 1)
score_event = pygame.event.Event(pygame.USEREVENT + 2)      # Creación de eventos
game_over_event = pygame.event.Event(pygame.USEREVENT + 3)

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

class Player(pygame.sprite.Sprite):    # Clase para el jugadorcito
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
class Obstacle(pygame.sprite.Sprite):    # Clase para el obstaculito en el jueguito
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
class PlayerMovementSemaphore(threading.Thread): # Clasesita de un hilito para controlar el movimiento del jugador
    def __init__(self, semaphore, delay):
        super().__init__()
        self.semaphore = semaphore
        self.delay = delay
        self.running = True

    def run(self):
        while self.running:
            time.sleep(self.delay)
            self.semaphore.release()

class ObstacleMovementSemaphore(threading.Thread):   # Clasesita de un hilito para controlar el movimiento de los obstáculos
    def __init__(self, semaphore, delay):
        super().__init__()
        self.semaphore = semaphore
        self.delay = delay
        self.running = True

    def run(self):
        while self.running:
            time.sleep(self.delay)
            self.semaphore.release()
class Barrier(pygame.sprite.Sprite):    # Clase para la barrerita
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = -50
        self.speed_y = 5

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

def main(): 
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pygame Race Game")

    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    barriers = pygame.sprite.Group()  # Nuevo grupo para las barreras

    player = Player()
    all_sprites.add(player)

    player_semaphores = [threading.Semaphore(1) for _ in range(10)]     # Creacióncita de semáforos y hilos para controlar el movimiento del jugador
    player_movement_semaphores = [PlayerMovementSemaphore(semaphore, 0.1) for semaphore in player_semaphores]

    obstacle_semaphores = [threading.Semaphore(3) for _ in range(2)]    # Creación de semáforos y hilos para controlar el movimiento de los obstáculos
    obstacle_movement_semaphores = [ObstacleMovementSemaphore(semaphore, 0.5) for semaphore in obstacle_semaphores]

    # Iniciar todos los hilos
    for semaphore in player_movement_semaphores + obstacle_movement_semaphores:
        semaphore.start()

    clock = pygame.time.Clock()
    running = True
    score = 0
    counter = 0
    font = pygame.font.Font(None, 36)
    notification1 = ""
    notification2 = ""
    notification3 = ""

    start_time = time.time()  #  Medir el tiempo de juego

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        all_sprites.update()

        if pygame.sprite.spritecollide(player, obstacles, False):    # Si el jugador ha colisionado con un obstáculo
            pygame.event.post(collision_event)

        for obstacle in obstacles:                # Si los obstáculos han pasado por debajo del jugador
            if obstacle.rect.top > SCREEN_HEIGHT:
                score += 1
                obstacle.rect.x = random.randrange(SCREEN_WIDTH - obstacle.rect.width)
                obstacle.rect.y = random.randrange(-100, -40)
                obstacle.speed_y = random.randrange(1, 8)

        if score % 15 == 0 and score > 0:         # Comprobar si el jugador ha esquivado 15 bloques
            pygame.event.post(score_event)
            counter += 1
            score = 0        # Restablecer la puntuación
            notification1 = "¡Felicidades! Has esquivado 15 bloques."
            for _ in range(3):  # Creación de 3 barreras
                barrier = Barrier()
                all_sprites.add(barrier)
                barriers.add(barrier)

        if any(obstacle_semaphore.acquire(blocking=False) for obstacle_semaphore in obstacle_semaphores):    # Controlar la generación de obstáculos con semáforo
            obstacle = Obstacle()
            all_sprites.add(obstacle)
            obstacles.add(obstacle)

        elapsed_time = time.time() - start_time         # Tiempo transcurrido
        if elapsed_time >= 10 and elapsed_time < 20:
            notification2 = "¡Has jugado 10 segundos!"
        elif elapsed_time >= 20 and elapsed_time < 30:
            notification2 = "¡WOW! Llevas 20 segundos jugando."
        elif elapsed_time >= 30:
            notification2 = "¡Eres un master! Llevas 30 segundos jugando."

        draw_screen(screen, all_sprites, counter, notification1, notification2, notification3)
        for event in pygame.event.get():
            if event.type == collision_event.type:                          # Eventito de colisión
                notification3 = "¡Colisión detectada! Continúa jugando."
                SLOW_DOWN = True                                            # Actitititititivación de la desaceleración
                pygame.time.set_timer(pygame.USEREVENT + 4, 5000)           # Desactivar la desaceleración después de 5 segundos
            elif event.type == pygame.USEREVENT + 4:
                SLOW_DOWN = False  
            elif event.type == score_event.type:          # Eventito de puntaje
                pass
            elif event.type == game_over_event.type:
                running = False
       
        if pygame.sprite.spritecollide(player, barriers, True):  # Usito de barrera cuando colisiona con bloquecito azul
            running = False

    pygame.quit()

if __name__ == "__main__":
    main()