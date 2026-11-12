import pygame
import sys
import ctypes

pygame.init()
pygame.display.set_caption("MatFyz Blackjack")
icon = pygame.image.load("assets/images/card.png")
pygame.display.set_icon(icon)

if sys.platform == "win32":
    myappid = "marmatakis.matfyzblackjack.0.0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

width, height = 500, 500
screen = pygame.display.set_mode((width, height))
background = pygame.image.load("assets/sprites/table.jpg").convert()
background = pygame.transform.scale(background, (width, height))


clock = pygame.time.Clock()

while True:
    clock.tick(30)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            break


    screen.blit(background, (0, 0))
    pygame.display.flip()
    
pygame.quit()