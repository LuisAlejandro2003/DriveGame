import socket
import pygame
import sys
from model import Ball, Paddle, SCREEN_WIDTH, SCREEN_HEIGHT
from view import init_screen, draw

# Crear el cliente
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 55556))

def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            score_paddle1, score_paddle2 = map(int, message.split())
    
        except:
            print('Error! Could not receive message.')
            client.close()
            break

def reset_ball(ball):
    ball.rect.x = SCREEN_WIDTH / 2
    ball.rect.y = SCREEN_HEIGHT / 2
    ball.speed_x = -ball.speed_x
    ball.speed_y = -ball.speed_y

def main():
    screen = init_screen()
    all_sprites = pygame.sprite.Group()
    paddles = pygame.sprite.Group()
    ball = Ball()
    paddle1 = Paddle(20)
    paddle2 = Paddle(SCREEN_WIDTH - 20)
    all_sprites.add(paddle1, paddle2, ball)
    paddles.add(paddle1, paddle2)
    clock = pygame.time.Clock()
    score_paddle1 = 0
    score_paddle2 = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    paddle2.speed_y = -5
                elif event.key == pygame.K_DOWN:
                    paddle2.speed_y = 5
                elif event.key == pygame.K_w:
                    client.send('w_down'.encode('ascii'))  # Enviar 'w_down' en lugar de 'w'
                elif event.key == pygame.K_s:
                    client.send('s_down'.encode('ascii'))  # Enviar 's_down' en lugar de 's'
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    paddle2.speed_y = 0
                elif event.key == pygame.K_w:
                    client.send('w_up'.encode('ascii'))  # Enviar 'w_up' cuando se suelta la tecla 'w'
                    paddle1.speed_y = 0
                elif event.key == pygame.K_s:
                    client.send('s_up'.encode('ascii'))  # Enviar 's_up' cuando se suelta la tecla 's'
                    paddle1.speed_y = 0
        all_sprites.update()
        hits = pygame.sprite.spritecollide(ball, paddles, False)
        for hit in hits:
            ball.speed_x = -ball.speed_x
        if ball.rect.left < 0:
            score_paddle2 += 1
            reset_ball(ball)
        elif ball.rect.right > SCREEN_WIDTH:
            score_paddle1 += 1
            reset_ball(ball)
        if score_paddle1 >= 10 or score_paddle2 >= 10:
            running = False
        draw(screen, all_sprites, score_paddle1, score_paddle2)
        clock.tick(60)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()