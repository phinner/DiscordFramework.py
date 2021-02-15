# from discord import Guild
#
#
# class Coll:
#     test = list()
#     def __init__(self):
#         pass
#
#
# class Test(object):
#     def __init__(self):
#         self.x = 25
#         self.y = 65
#         Coll.test.append(self)
#
#     def setX(self, new_x):
#         self.x = new_x
#
#
# class Sub(Test):
#     def __init__(self):
#         super().__init__()
#         self.r = 74
#
# g = Test()
# print(vars(Test))
# print(Test.__dict__)
# print(Test.__class__)
# print("=========================")
# print(vars(g))
# print(g.__dict__)
# print(g.__class__)
# g.__dict__.pop("x")
# print(g.__dict__)
# print("=========================<<<<<<<<<<<<<<<<<<<")
# g = GuildData(Guild)
# print(vars(GuildData))
# print(GuildData.__dict__)
# print(GuildData.__class__)
# print("=========================")
# print(vars(g))
# print(g.__dict__)
# print(g.__class__)
# print(g.__dict__)
# print(g.toJSON())
# print(g.guild.id)
#
# c = Sub()
# print(Coll.test)


import pygame, sys
from pygame.locals import *

mainClock = pygame.time.Clock()
pygame.init()
display_size = (500, 500)  # < look
a = pygame.display.set_mode(display_size)
pygame.display.set_caption("Hello World")


class Square(object):
    def __init__(self):
        self.x = 0    # pos_x
        self.y = 0    # pos_y
        self.w = 20   # width
        self.h = 20   # height

    def collisions(self):
        if self.x > display_size[0] - self.w:
            self.x = display_size[0] - self.w
        if self.x < 0:
            self.x = 0
        if self.y > display_size[1] - self.h:
            self.y = display_size[1] - self.h
        if self.y < 0:
            self.y = 0

    def draw(self):
        pygame.draw.rect(a, (255, 255, 0), ((self.x, self.y), (self.w, self.h)))


Bob = Square()

while True:
    a.fill((255, 0, 0))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYUP:
            if event.key in (K_LEFT, K_a):
                Bob.x -= 20
            if event.key in (K_RIGHT, K_d):
                Bob.x += 20
            if event.key in (K_DOWN, K_s):
                Bob.y += 20
            if event.key in (K_UP, K_w):
                Bob.y -= 20

    Bob.collisions()
    Bob.draw()

    mainClock.tick(60)
    pygame.display.update()
