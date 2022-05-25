# Key 입력으로 도형 움직이는 코드

import pygame
import sys

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

white = (255, 255, 255)
black = (0, 0, 0)

pygame.init()
pygame.display.set_caption("Simple PyGame Example")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # 화면 크기 set

pos_x = 300
pos_y = 300

clock = pygame.time.Clock()
while True:
    clock.tick(60)
    for event in pygame.event.get():  # pygame 화면 실행
        if event.type == pygame.QUIT:
            sys.exit()

    # 키보드 이벤트 입력
    key_event = pygame.key.get_pressed()
    if key_event[pygame.K_LEFT]:
        pos_x -= 1

    if key_event[pygame.K_RIGHT]:
        pos_x += 1

    if key_event[pygame.K_UP]:
        pos_y -= 1

    if key_event[pygame.K_DOWN]:
        pos_y += 1

    screen.fill(black)
    pygame.draw.circle(screen, white, (pos_x, pos_y), 20)  # 원형 그리기
    pygame.display.update()
