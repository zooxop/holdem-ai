import pygame
import random

PLAYER_CARD = 'player_card'
COMMUNITY_CARD = 'community_card'
AI_CARD = 'ai_card'
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
BUTTON_COLOR_LIGHT = (170, 170, 170)
BUTTON_COLOR_DARK = (100, 100, 100)


# ------------------------------------------------------
# Sprites
# Sprite는 게임에서 나타내는 모든 캐릭터, 장애물등을 표현할 때 사용하는 Surface이다.
class CardSprite(pygame.sprite.Sprite):
    SPEED = 0.6

    def __init__(self, card, src_pos, dest_pos, type, group=None):
        pygame.sprite.Sprite.__init__(self, group)
        self.card = card
        self.type = type
        self.src_image = pygame.image.load(self.GetCardImageName(card))
        self.image = self.src_image
        self.pos = [0.0, 0.0]
        self.pos[0] = src_pos[0] * 1.0  # float
        self.pos[1] = src_pos[1] * 1.0  # float
        self.dest_pos = dest_pos
        self.src_pos = src_pos
        # self.type = type
        self.rect = self.src_image.get_rect()

    def update(self, seconds):
        # updated position over the destination pos
        # calibrate the final pos not over the dest_pos
        if self.type == PLAYER_CARD or self.type == COMMUNITY_CARD or self.type == AI_CARD:
            if self.dest_pos[0] - self.src_pos[0] < 0 \
                    and self.dest_pos[0] <= self.pos[0]:
                self.pos[0] += self.GetDelX(self.SPEED, seconds)
                if self.pos[0] <= self.dest_pos[0]:
                    self.pos[0] = self.dest_pos[0]
            if self.dest_pos[0] - self.src_pos[0] >= 0 \
                    and self.dest_pos[0] >= self.pos[0]:
                self.pos[0] += self.GetDelX(self.SPEED, seconds)
                if self.pos[0] >= self.dest_pos[0]:
                    self.pos[0] = self.dest_pos[0]
            if self.dest_pos[1] - self.src_pos[1] < 0 \
                    and self.dest_pos[1] <= self.pos[1]:
                self.pos[1] += self.GetDelY(self.SPEED, seconds)
                if self.pos[1] <= self.dest_pos[1]:
                    self.pos[1] = self.dest_pos[1]
            if self.dest_pos[1] - self.src_pos[1] >= 0 \
                    and self.dest_pos[1] >= self.pos[1]:
                self.pos[1] += self.GetDelY(self.SPEED, seconds)
                if self.pos[1] >= self.dest_pos[1]:
                    self.pos[1] = self.dest_pos[1]

        self.rect.centerx = round(self.pos[0], 0)
        self.rect.centery = round(self.pos[1], 0)

    def GetDelX(self, speed, seconds):
        return (-1.0) * (self.src_pos[0] - self.dest_pos[0]) / seconds / speed

    def GetDelY(self, speed, seconds):
        return (-1.0) * (self.src_pos[1] - self.dest_pos[1]) / seconds / speed

    def GetCardImageName(self, card):
        rank = card.GetRank()

        rank_str = str(rank + 1)

        if self.type == PLAYER_CARD:
            return 'assets/Card_Back.png'
        elif self.type == AI_CARD or self.type == COMMUNITY_CARD:
            return 'assets/Card_' + rank_str + '.png'

    def ChangeCardImage(self):
        rank = self.card.GetRank()
        rank_str = 'assets/Card_' + str(rank + 1) + '.png'
        self.src_image = pygame.image.load(rank_str)
        self.image = self.src_image
        self.rect = self.src_image.get_rect()


class ChipSprite(pygame.sprite.Sprite):
    def __init__(self, src_pos, group=None):
        pygame.sprite.Sprite.__init__(self, group)
        self.src_image = pygame.image.load('assets/Chip.png')
        self.image = self.src_image
        self.pos = [0.0, 0.0]
        self.pos[0] = src_pos[0] * 1.0  # float
        self.pos[1] = src_pos[1] * 1.0  # float
        self.src_pos = src_pos
        self.rect = self.src_image.get_rect()

    def update(self, seconds):
        self.rect.centerx = round(self.pos[0], 0)
        self.rect.centery = round(self.pos[1], 0)


class TableSprite(pygame.sprite.Sprite):
    def __init__(self, group=None):
        pygame.sprite.Sprite.__init__(self, group)
        tableSurf = pygame.Surface((1300, 700))
        tableSurf = tableSurf.convert_alpha()
        tableSurf.fill((0, 0, 0, 0))  # make transparent
        pygame.draw.ellipse(tableSurf, (10, 100, 10), [195, 140, 910, 420])

        self.image = tableSurf
        self.rect = (0, 0)

    def update(self, seconds):
        pass


class TextSprite(pygame.sprite.Sprite):
    MAX_MOVE_X = 100
    MAX_FONT_SIZE = 60
    SPEED = 0.5

    def __init__(self, text, position, size, color, group=None):
        pygame.sprite.Sprite.__init__(self, group)
        self.fontcolor = color
        self.fontsize = size
        self.text = text

        textSurf = self.writeSomething(self.text)
        self.image = textSurf
        self.rect = textSurf.get_rect()
        self.position = position
        self.rect.centerx = self.position[0]
        self.rect.centery = self.position[1]

        # about font move animation
        self.canMove = False
        self.prev_x_pos = None

        # about font size animation
        self.canMakeBiggerFont = False
        self.repeat_cnt = 0
        self.prev_font_size = self.fontsize
        self.dest_font_size = self.MAX_FONT_SIZE

    def writeSomething(self, msg=""):
        myfont = pygame.font.SysFont("None", self.fontsize)
        mytext = myfont.render(msg, True, self.fontcolor)
        mytext = mytext.convert_alpha()
        return mytext

    @staticmethod
    def newColor(self):
        # any colour but black or white
        return random.randint(10, 250), random.randint(10, 250), random.randint(10, 250)

    def update(self, seconds):
        textSurf = self.writeSomething(self.text)
        self.image = textSurf
        self.rect = textSurf.get_rect()
        self.rect.centerx = self.position[0]
        self.rect.centery = self.position[1]

        if self.canMove:
            self.rect.centerx += self.MAX_MOVE_X / seconds
            if self.rect.centerx >= self.prev_x_pos + self.MAX_MOVE_X:
                self.ChangeMoveTo()

        if self.canMakeBiggerFont:
            self.DoBiggerEffect(seconds)

    def ChangeMoveTo(self):
        if not self.canMove:
            self.canMove = True
            self.prev_x_pos = self.rect.centerx
        else:
            self.canMove = False
            self.prev_x_pos = None

    def ChangeMakeBigger(self):
        if not self.canMakeBiggerFont:
            self.canMakeBiggerFont = True
        else:
            self.canMakeBiggerFont = False

    def DoBiggerEffect(self, seconds):
        font_diff = self.dest_font_size - self.prev_font_size

        if self.repeat_cnt <= 2:
            if (font_diff >= 0 and self.fontsize >= self.dest_font_size) \
                    or (font_diff <= 0 and self.fontsize <= self.dest_font_size):
                tmp_font_size = self.prev_font_size
                self.prev_font_size = self.dest_font_size
                self.dest_font_size = tmp_font_size
                font_diff = self.dest_font_size - self.prev_font_size
                self.repeat_cnt += 1

            del_f_size = font_diff / seconds / self.SPEED

            # if the delta font size is bigger than 5% of current font size
            # just use 5%
            if del_f_size > 0.1 * self.fontsize:
                del_f_size = 0.1 * self.fontsize

            self.fontsize += int(del_f_size)
        else:
            self.ChangeMakeBigger()


class RectSprite(pygame.sprite.Sprite):
    def __init__(self, position, width, height, group=None):
        pygame.sprite.Sprite.__init__(self, group)
        self.width = width
        self.height = height
        self.position = position

        recSurf = pygame.Surface((1300, 700))
        recSurf = recSurf.convert_alpha()
        recSurf.fill((0, 0, 0, 0))  # make transparent
        pygame.draw.rect(recSurf, (250, 250, 100), [self.position[0], self.position[1], self.width, self.height], 5)
        self.image = recSurf
        self.rect = recSurf.get_rect()

    def update(self, seconds):
        pass


class ButtonSprite(pygame.sprite.Sprite):
    def __init__(self, msg, position, width, height, group=None):
        pygame.sprite.Sprite.__init__(self, group)
        self.width = width
        self.height = height
        self.position = position
        self.msg = msg
        self.fontcolor = (200, 30, 10)
        self.fontsize = 30
        self.recSurf = pygame.Surface((1300, 700))
        self.textSurf = self.writeSomething(self.msg)

        self.calX = 0
        self.calY = 8
        if len(msg) == 3:
            self.calX = 7
        elif len(msg) == 4:
            self.calX = 14

        self.drawButton(BUTTON_COLOR_LIGHT)

    def writeSomething(self, msg=""):
        myfont = pygame.font.SysFont("None", self.fontsize)
        mytext = myfont.render(msg, True, self.fontcolor)
        mytext = mytext.convert_alpha()
        return mytext

    def drawButton(self, color):
        self.recSurf = self.recSurf.convert_alpha()
        self.recSurf.fill((0, 0, 0, 0))  # make transparent

        self.image = self.textSurf
        self.rect = self.textSurf.get_rect()
        self.rect.centerx = self.position[0] + (self.width / len(self.msg)) + self.calX
        self.rect.centery = self.position[1] + (self.height / 2) - self.calY

        pygame.draw.rect(self.recSurf, color,
                         [self.position[0], self.position[1], self.width, self.height])
        self.recSurf.blit(self.textSurf, (self.rect.centerx, self.rect.centery))
        self.image = self.recSurf
        self.rect = self.recSurf.get_rect()

    def isHover(self, mouse_pos):
        x = mouse_pos[0]
        y = mouse_pos[1]

        if self.position[0] <= x <= (self.position[0] + self.width) and \
                self.position[1] <= y <= (self.position[1] + self.height):
            self.drawButton(BUTTON_COLOR_DARK)
        else:
            self.drawButton(BUTTON_COLOR_LIGHT)

    def update(self, seconds):
        # ward 여기다가 visible 여부 처리를 해줘야 delay 정상작동이 되나?
        pass


class InputBoxSprite(pygame.sprite.Sprite):

    def __init__(self, position, w, h, group=None):
        pygame.sprite.Sprite.__init__(self, group)
        self.INPUT_FONT = pygame.font.Font(None, 32)
        # self.rect = pygame.Rect(x, y, w, h)
        self.position = position
        self.width = w
        self.height = h
        self.color = COLOR_INACTIVE
        self.text = ''
        self.txt_surface = self.INPUT_FONT.render(self.text, True, self.color)
        self.active = False

        self.recSurf = pygame.Surface((1300, 700))
        self.recSurf = self.recSurf.convert_alpha()
        self.recSurf.fill((0, 0, 0, 0))  # make transparent
        pygame.draw.rect(self.recSurf, self.color, [self.position[0], self.position[1], self.width, self.height], 2)
        self.image = self.recSurf
        self.rect = self.recSurf.get_rect()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = pygame.render(self.text, True, self.color)

    def update(self, seconds):
        pass

    def textClear(self):
        self.text = ''
        self.textProcess()

    def textProcess(self):
        self.txt_surface = self.INPUT_FONT.render(self.text, True, self.color)
        self.draw()

    def draw(self):
        self.recSurf.fill((0, 0, 0, 0))  # make transparent
        self.recSurf.blit(self.txt_surface, (self.position[0] + 5, self.position[1] + 5))
        pygame.draw.rect(self.recSurf, self.color, [self.position[0], self.position[1], self.width, self.height], 2)