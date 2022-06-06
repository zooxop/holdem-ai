import pygame
from pygame.locals import *
from Events import *
from CardCommon import *

PLAYER_CARD = 'player_card'
COMMUNITY_CARD = 'community_card'
AI_CARD = 'ai_card'
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
BUTTON_COLOR_LIGHT = (170, 170, 170)
BUTTON_COLOR_DARK = (100, 100, 100)


class Game:
    """..."""
    STATE_INITIAL = 'initial'
    STATE_PREPARING = 'preparing'
    STATE_PREFLOP = 'preflop'
    STATE_FLOP = 'flop'
    STATE_SHOWDOWN = 'showdown'
    STATE_BET = 'bet'
    STATE_CALL = 'call'
    STATE_FOLD = 'fold'

    isProgress = False  # 게임 진행중 여부

    def __init__(self, evManager):
        self.pot = None
        self.game_deck = Deck()
        self.players = []
        self.community_cards = []
        self.evManager = evManager
        self.evManager.RegisterListener(self)
        self.master = HoldemMaster()  #
        self.state = Game.STATE_INITIAL

    # Event Notify
    def Notify(self, event):
        if isinstance(event, GameStartRequest):
            if self.state == Game.STATE_INITIAL:
                self.Start()
                self.deal_preflop()
                self.deal_flop()

        if isinstance(event, NextTurnEvent):
            if self.state == Game.STATE_PREPARING:
                self.deal_preflop()
            elif self.state == Game.STATE_PREFLOP:
                self.deal_flop()
            # elif self.state == Game.STATE_FLOP:
            #     self.show_down()
            # elif self.state == Game.STATE_SHOWDOWN:
            #     self.InitializeRound()

        # 여기서 엔터키로 입력한 amount 값을 받아오고, 처리한다.
        if isinstance(event, BetAmountKeyPress):
            self.deal_bet(self.players[1], event.amount)  # player[1]: User
            # to-do 베팅 로직 진행하기

        # 다음 라운드 넘어갈 때: 1. 이름 다시 써주기 2. 칩 금액 업데이트 해주기 3. 카드 새로 깔아주기
        if isinstance(event, DealPreFlops):
            self.deal_preflop()

        # 임시 이벤트(뒤집혀 있는 사용자 카드 보여주기)
        if isinstance(event, AKeyEvent):
            self.open_playerCard()

        if isinstance(event, MouseClickEvent):
            mouse = pygame.mouse.get_pos()

            btnWidth = 150
            btnHeight = 40
            inputWidth = 140

            btnX = 800
            btnBetY = 450
            btnCallY = 510
            btnFoldY = 570

            inputX = 600

            if mouse[0] in range(btnX, btnX + btnWidth):
                if mouse[1] in range(btnBetY, btnBetY + btnHeight):
                    # BET button click
                    self.ClickBetButton()
                elif mouse[1] in range(btnCallY, btnCallY + btnHeight):
                    # CALL button click
                    self.ClickCallButton()
                elif mouse[1] in range(btnFoldY, btnFoldY + btnHeight):
                    # FOLD button click
                    self.ClickFoldButton()
            elif mouse[0] in range(inputX, inputX + inputWidth):  # 베팅 금액 input box
                self.ClickInputBox(mouse)

    def Start(self):
        print('-------------------------------------------------------')
        print('Initialize Game: ')
        self.community_cards = []
        self.InitializePlayers()
        self.InitializeRound()
        self.InitializePot()
        print('InitializeRound')

    def InitializeRound(self):
        self.state = Game.STATE_PREPARING
        # Initialize Round
        self.game_deck.InitializeDeck()
        self.game_deck.ShuffleDeck()
        # self.game_deck.PrintCurrentDeck()
        self.community_cards = []

        # Initialize Players's holecards
        for player in self.players:
            player.init_holecards()

        if not self.isProgress:  # 최초 Initial
            self.evManager.Post(InitializeRoundEvent())
            self.isProgress = True
        else:
            self.evManager.Post(NextRoundEvent(self.players, self.pot))  # 라운드 넘어가는 Event

    def InitializePlayers(self):
        self.players = []
        self.players.append(Player('Computer', 0))
        self.players.append(Player('User', 1))

    def InitializePot(self):
        self.pot = Pot()

    def ClickBetButton(self):
        self.evManager.Post(ClickBetButton())

    def ClickCallButton(self):
        self.evManager.Post(ClickCallButton())
        self.check_top()

    def ClickFoldButton(self):
        self.evManager.Post(ClickFoldButton())

    def ClickInputBox(self, mouse):
        self.evManager.Post(ClickInputBox(mouse))

    def open_playerCard(self):
        self.evManager.Post(OpenPlayerCard(self.players[1]))

    def ReloadDeck(self):
        self.game_deck = None
        self.game_deck = Deck()
        self.game_deck.ShuffleDeck()

    # pre-flop: 플레이어들에게 카드를 1장씩 나눠준다.
    def deal_preflop(self):
        self.state = Game.STATE_PREFLOP
        print('-------------------------------------------------------')
        print('Pre-Flop Stage: Deal 2 Hold Cards for each players')
        player_count = len(self.players)

        for i in range(player_count):
            if len(self.game_deck.deck_cards) == 0:
                self.ReloadDeck()
            self.players[i % player_count].add_cards(self.game_deck.Pop_card())

        for player in self.players:
            self.bet_chips(player, 1)  # 1개씩 칩 베팅.

        self.evManager.Post(PreFlopEvent(self.players, self.pot))
        self.PrintCards()

    # flop : 커뮤니티 카드 2장을 깔아준다.
    def deal_flop(self):
        self.state = Game.STATE_FLOP
        print('-------------------------------------------------------')
        print('Flop Stage: Deal 2 Community Cards')
        for i in range(2):
            self.community_cards.append(self.game_deck.Pop_card())

        self.evManager.Post(FlopEvent(self.community_cards))
        self.PrintCards()

    # 플레이어의 top 확인.
    def check_top(self):
        print(self.players[0].SetCombineTop(self.community_cards))

    def SelectBet(self, num):
        print('-------------------------------------------------------')
        print('Select bet')

        # Player의 베팅 페이즈
        if num == 1:
            print("Player's turn")

    # Chip 베팅
    def bet_chips(self, player, amount):
        player.withdraw_chip(amount)
        self.pot.save_chip(amount)

    # Pot에서 Chip 가져오기
    def get_chips(self, player, amount):
        player.save_chip(amount)
        self.pot.withdraw_chip(amount)

    # bet : 원하는 금액 베팅
    def deal_bet(self, player, amount):
        self.state = Game.STATE_BET
        print('-------------------------------------------------------')
        print('Bet Stage: 베팅할 금액 입력')
        # to-do
        self.bet_chips(player, amount)  # 여기 하는중
        self.evManager.Post(RefreshSprites(self.players, self.pot))

    # call : 추가 베팅 없이 진행
    def deal_call(self):
        self.state = Game.STATE_CALL
        print('-------------------------------------------------------')
        print('Call Stage: 추가 베팅 없이 진행')

    # fold : 현재 턴 포기
    def deal_fold(self):
        self.state = Game.STATE_FOLD
        print('-------------------------------------------------------')
        print('Fold Stage: 현재 턴 포기')

    # show_down : 승자를 확인한다.
    def show_down(self):
        self.state = Game.STATE_SHOWDOWN
        print('-------------------------------------------------------')
        print('ShowDown Stage: Check BestCards and Choose Winner')
        for player in self.players:
            print('Player ' + str(player.position) + ': \n')
            player.choice_best_cards(self.community_cards)
            PokerHelper.PrintCards(player.round_result.hands)

        winner = self.GetWinner()
        self.evManager.Post(ShowDownEvent(winner, self.community_cards, winner.round_result.hands))

    def GetWinner(self):
        players = self.players
        sorted_player = sorted(players, key=PokerHelper.cmp_to_key(PokerHelper.CompareTwoPlayerHands), reverse=True)

        print('--------------------- sorted players ---------------------')
        for player in sorted_player:
            print(player.name)
            print(player.round_result)

        winner = sorted_player[0]

        print('\nWinner => ' + winner.name + ', P' + str(winner.position))
        print(winner.round_result)

        return winner

    def pot_to_winner(self):
        pass

    def PrintCards(self):
        # print hole cards
        print('Hole Cards:')
        for player in self.players:
            for card in player.holecards:
                print('player: ', player.name, card)

        print('Community Cards:')
        for card in self.community_cards:
            print(card)  # ward


class EventManager:
    """this object is responsible for coordinating most communication
    between the Model, View, and Controller."""

    def __init__(self):
        from weakref import WeakKeyDictionary
        self.listeners = WeakKeyDictionary()
        self.eventQueue = []
        self.listenersToAdd = []
        self.listenersToRemove = []

    # ----------------------------------------------------------------------
    def RegisterListener(self, listener):
        self.listenersToAdd.append(listener)

    # ----------------------------------------------------------------------
    def ActuallyUpdateListeners(self):
        for listener in self.listenersToAdd:
            self.listeners[listener] = 1
        for listener in self.listenersToRemove:
            if listener in self.listeners:
                del self.listeners[listener]

    # ----------------------------------------------------------------------
    def UnregisterListener(self, listener):
        self.listenersToRemove.append(listener)

    # ----------------------------------------------------------------------
    def Post(self, event):
        self.eventQueue.append(event)
        if isinstance(event, TickEvent):
            # Consume the event queue every Tick.
            self.ActuallyUpdateListeners()
            self.ConsumeEventQueue()

    # ----------------------------------------------------------------------
    def ConsumeEventQueue(self):
        i = 0
        while i < len(self.eventQueue):
            event = self.eventQueue[i]
            for listener in self.listeners:
                # Note: a side effect of notifying the listener
                # could be that more events are put on the queue
                # or listeners could Register / Unregister
                old = len(self.eventQueue)
                listener.Notify(event)
            i += 1
            if self.listenersToAdd:
                self.ActuallyUpdateListeners()
        # all code paths that could possibly add more events to
        # the eventQueue have been exhausted at this point, so
        # it's safe to empty the queue
        self.eventQueue = []


# ------------------------------------------------------

# ------------------------------------------------------
# Controllers
class CPUSpinnerController:
    """..."""

    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)

        self.keepGoing = 1

    # ----------------------------------------------------------------------
    def Run(self):
        while self.keepGoing:
            event = TickEvent()
            self.evManager.Post(event)

    # ----------------------------------------------------------------------
    def Notify(self, event):
        if isinstance(event, QuitEvent):
            # this will stop the while loop from running
            self.keepGoing = False


class KeyboardController:
    """KeyboardController takes Pygame events generated by the
    keyboard and uses them to control the model, by sending Requests
    or to control the Pygame display directly, as with the QuitEvent
    """

    def __init__(self, evManager, playerName=None):
        '''playerName is an optional argument; when given, this
        keyboardController will control only the specified player
        '''
        self.evManager = evManager
        self.evManager.RegisterListener(self)

        self.activePlayer = None
        self.playerName = playerName
        self.players = []

    # ----------------------------------------------------------------------
    def Notify(self, event):
        if isinstance(event, TickEvent):
            # Handle Input Events
            for event in pygame.event.get():
                ev = None
                if event.type == QUIT:
                    ev = QuitEvent()
                elif event.type == KEYDOWN \
                        and event.key == pygame.K_ESCAPE:
                    ev = QuitEvent()
                elif event.type == KEYDOWN \
                        and event.key == (K_DOWN or K_UP or K_LEFT or K_RIGHT):
                    # print 'key down up left right pressed'
                    ev = NextTurnEvent()
                elif event.type == pygame.KEYDOWN \
                        and event.key == K_SPACE:
                    ev = GameStartRequest()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    ev = MouseClickEvent()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    ev = ReturnKeyPress()  # 베팅 금액 합산 로직 to-do
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                    ev = BackSpaceEvent()
                elif event.type == pygame.KEYDOWN \
                        and event.key in range(K_0, K_9 + 1):
                    ev = InputNumbers(event.key)
                elif event.type == pygame.KEYDOWN \
                        and event.key == K_a:
                    ev = AKeyEvent()  # 임시기능 : A키를 누르면 뒤집힌 카드를 확인한다.

                if ev:
                    self.evManager.Post(ev)


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

    def newcolor(self):
        # any colour but black or white
        return (random.randint(10, 250), random.randint(10, 250), random.randint(10, 250))

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


# ------------------------------------------------------
# PygameView
class PygameView:
    DECK_POSITION = [750, 50]
    isButtonsVisible = False
    inputBox1 = None
    player_bet_amount = 0

    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)
        self.isButtonsVisible = False

        pygame.init()
        self.window = pygame.display.set_mode((1300, 700))
        pygame.display.set_caption('Indian Holdem')
        self.background = pygame.Surface(self.window.get_size())
        self.background.fill((25, 65, 25))

        self.window.blit(self.background, (0, 0))

        font = pygame.font.Font(None, 60)
        textSurf = font.render("""Press SPACE BAR to start""", True, (120, 120, 120))
        textSurf = textSurf.convert_alpha()
        self.window.blit(textSurf, (400, 270))

        teststr = """Press an Arrows to progress"""
        # teststr = u'\u2190'
        textSurf = font.render(teststr, True, (120, 120, 120))
        textSurf = textSurf.convert_alpha()
        self.window.blit(textSurf, (370, 350))

        pygame.display.flip()

        self.backSprites = pygame.sprite.RenderUpdates()
        self.playerSprites = pygame.sprite.RenderUpdates()
        self.communitySprites = pygame.sprite.RenderUpdates()
        self.staticSprites = pygame.sprite.RenderUpdates()
        self.inputBoxSprites = pygame.sprite.RenderUpdates()
        self.buttonSprites = pygame.sprite.RenderUpdates()

    def ShowCommunityCards(self, card_list):
        i = 0
        for card in card_list:
            i += 2
            newSprite = CardSprite(card, self.DECK_POSITION, (350 + i * 100, 350), COMMUNITY_CARD,
                                   self.communitySprites)
            newSprite = None

    def ShowShowDownResult(self, player, community_cards, card_list):

        for aSprite in self.playerSprites:
            if isinstance(aSprite, TextSprite):
                if aSprite.text == player.name:
                    aSprite.ChangeMakeBigger()

        # Remove previouse community fileds
        for cardSprite in self.communitySprites:
            cardSprite.kill()

        # Redraw Comminity Card with small size above Winner Announcing
        newSprite = RectSprite((400, 140), 500, 120, self.communitySprites)
        newSprite = None

        i = 0
        for card in community_cards:
            i += 1
            newSprite = CardSprite(card, self.DECK_POSITION, (350 + i * 100, 200), COMMUNITY_CARD,
                                   self.communitySprites)
            newSprite = None

        i = 0
        for card in card_list:
            i += 1
            newSprite = CardSprite(card, self.DECK_POSITION, (350 + i * 100, 450), COMMUNITY_CARD,
                                   self.communitySprites)
            newSprite = None

        newSprite = TextSprite("The Winner is " + player.name, (550, 300), 60, (200, 30, 10), self.communitySprites)
        newSprite = None
        newSprite = TextSprite("\"" + player.round_result.result_name + "\"", (550, 360), 50, (200, 40, 200),
                               self.communitySprites)

        self.isButtonsVisible = False

    def ShowPreFlopCards(self, players):

        POS_LEFT = 0
        POS_TOP = 0

        for player in players:
            player_pos = player.position
            bottomMultiply = -1
            player_type = ""

            if player_pos == 0:
                POS_LEFT = 235
                POS_TOP = 160
                player_type = AI_CARD
            elif player_pos == 1:
                POS_LEFT = 1200
                POS_TOP = 450
                bottomMultiply = 1
                player_type = PLAYER_CARD

            CardSprite(player.holecards[0], self.DECK_POSITION,
                                   (POS_LEFT - 15, POS_TOP + (bottomMultiply) * 30), player_type, self.playerSprites)
            TextSprite(player.name, (POS_LEFT - 20, POS_TOP - (bottomMultiply) * 40), 30, (150, 150, 150), self.playerSprites)

        self.ShowButtons()
        self.isButtonsVisible = True

    def InitializeFrontSprites(self):
        for cardSprite in self.communitySprites:
            cardSprite.kill()

        for cardSprite in self.playerSprites:
            cardSprite.kill()

        for textSprite in self.communitySprites:
            textSprite.kill()

        for textSprite in self.playerSprites:
            textSprite.kill()

        self.inputBox1 = None
        for inputBoxSprite in self.inputBoxSprites:
            inputBoxSprite.kill()

    def ShowButtons(self):
        ButtonSprite("BET", (800, 450), 150, 40, self.buttonSprites)
        ButtonSprite("CALL", (800, 510), 150, 40, self.buttonSprites)
        ButtonSprite("FOLD", (800, 570), 150, 40, self.buttonSprites)

    def HideButtons(self):
        for buttonSprite in self.buttonSprites:
            buttonSprite.kill()

    def ShowTable(self):
        TableSprite(self.backSprites)

    def ShowChips(self, players, pot):
        for _sprite in self.staticSprites:
            _sprite.kill()

        # AI
        ChipSprite([320, 50], self.staticSprites)
        TextSprite('X', (370, 50), 40, (200, 200, 200), self.staticSprites)

        # Player
        ChipSprite([1100, 600], self.staticSprites)  # Player
        TextSprite('X', (1150, 600), 40, (200, 200, 200), self.staticSprites)

        # Pot
        TextSprite('POT', (1000, 50), 50, (220, 220, 220), self.staticSprites)
        ChipSprite([1100, 50], self.staticSprites)
        TextSprite('X', (1150, 50), 40, (200, 200, 200), self.staticSprites)
        TextSprite(str(pot.pot_chip), (1180, 50), 40, (200, 200, 200), self.staticSprites)

        i = 0
        for player in players:
            if i == 0:
                TextSprite(str(player.current_chips), (400, 50), 40, (200, 200, 200), self.staticSprites)
            elif i == 1:
                TextSprite(str(player.current_chips), (1180, 600), 40, (200, 200, 200), self.staticSprites)
            i += 1

    def ShowInputBox(self):  # 베팅 금액 input box show
        if self.inputBox1 is None:
            self.inputBox1 = InputBoxSprite((600, 450), 140, 32, self.inputBoxSprites)
        else:
            self.inputBox1 = None
            for inputBox in self.inputBoxSprites:
                inputBox.kill()

    def InputBettingAmount(self, value):
        if self.inputBox1.active:
            self.inputBox1.text += str(value)
            self.inputBox1.textProcess()

    def OpenPlayerCardEvent(self, player):
        print(player.holecards[0].rank, player.holecards[0].suit)

        for cardSprite in self.playerSprites:
            if cardSprite.__class__ == CardSprite and cardSprite.type == PLAYER_CARD:
                cardSprite.ChangeCardImage()  # 사용자 카드 뒤집기

    def InputBackspace(self):
        if self.inputBox1.active:
            self.inputBox1.text = self.inputBox1.text[:-1]
            self.inputBox1.textProcess()

    def DecideBettingAmount(self):
        if self.inputBox1.active and len(self.inputBox1.text) > 0:
            return self.inputBox1.text
        else:
            return ''

    # 베팅 금액 InputBox 활성화/비활성화 event
    def ClickInputBox(self, mouse):
        if self.isButtonsVisible:
            if self.inputBox1:
                if self.inputBox1.rect.collidepoint(mouse):
                    self.inputBox1.active = not self.inputBox1.active
                else:
                    self.inputBox1.active = False
                self.inputBox1.color = COLOR_ACTIVE if self.inputBox1.active else COLOR_INACTIVE
                self.inputBox1.draw()

    def NextRoundInitial(self, players, pot):
        for cardSprite in self.communitySprites:
            cardSprite.kill()

        for cardSprite in self.playerSprites:
            cardSprite.kill()

        for inputBoxSprite in self.inputBoxSprites:
            inputBoxSprite.kill()

        # 플레이어 이름 글씨 다시 써주기
        self.evManager.Post(DealPreFlops())

    def ShowInitGame(self):
        pass

    # ----------------------------------------------------------------------
    def Notify(self, event):
        for buttonSprite in self.buttonSprites:
            buttonSprite.isHover(pygame.mouse.get_pos())

        if isinstance(event, TickEvent):
            # Draw Everything
            self.backSprites.clear(self.window, self.background)
            self.playerSprites.clear(self.window, self.background)
            self.communitySprites.clear(self.window, self.background)
            self.staticSprites.clear(self.window, self.background)
            self.inputBoxSprites.clear(self.window, self.background)
            self.buttonSprites.clear(self.window, self.background)

            seconds = 50

            self.backSprites.update(seconds)
            self.playerSprites.update(seconds)
            self.communitySprites.update(seconds)
            self.staticSprites.update(seconds)
            self.inputBoxSprites.update(seconds)
            self.buttonSprites.update(seconds)

            dirtyRects1 = self.backSprites.draw(self.window)
            dirtyRects2 = self.playerSprites.draw(self.window)
            dirtyRects3 = self.communitySprites.draw(self.window)
            dirtyRects4 = self.staticSprites.draw(self.window)
            dirtyRects5 = self.inputBoxSprites.draw(self.window)
            dirtyRects6 = self.buttonSprites.draw(self.window)

            dirtyRects = dirtyRects1 + dirtyRects2 + dirtyRects3 + dirtyRects4 + dirtyRects5 + dirtyRects6
            pygame.display.update(dirtyRects)

        if isinstance(event, GameStartRequest):
            # self.ShowInitGame()
            self.ShowTable()

        # 베팅 금액 입력 후 엔터 눌렀을 때.
        if isinstance(event, ReturnKeyPress):
            amount = self.DecideBettingAmount()
            if amount != '':
                self.player_bet_amount = int(amount)
                self.ShowInputBox()  # inputBox visible false 처리
                self.HideButtons()
                self.evManager.Post(BetAmountKeyPress(amount))  # 여기서 Game 클래스로 입력값을 보낸다.

        # 백스페이스 입력 이벤트
        if isinstance(event, BackSpaceEvent):
            self.InputBackspace()

        # 숫자 입력 이벤트
        if isinstance(event, InputNumbers):
            self.InputBettingAmount(event.value)

        # 뒤집혀 있는 플레이어 카드 확인하기
        if isinstance(event, OpenPlayerCard):
            self.OpenPlayerCardEvent(event.player)

        # "BET" 버튼 클릭 이벤트.
        if isinstance(event, ClickBetButton):
            if self.isButtonsVisible:  # 버튼이 보이는 상태일때만 작동.
                self.ShowInputBox()

        # "Call" 버튼 클릭 이벤트.
        if isinstance(event, ClickCallButton):
            print("Call button")

        # "Fold" 버튼 클릭 이벤트.
        if isinstance(event, ClickFoldButton):
            print("Fold button")

        # InputBox 클릭(=>활성화/비활성화) 이벤트.
        if isinstance(event, ClickInputBox):
            if self.isButtonsVisible:
                self.ClickInputBox(event.mouse)

        if isinstance(event, PreFlopEvent):
            self.ShowPreFlopCards(event.players)
            self.ShowChips(event.players, event.pot)

        if isinstance(event, FlopEvent):
            self.ShowCommunityCards(event.card_list)

        if isinstance(event, ShowDownEvent):
            self.ShowShowDownResult(event.player, event.community_cards, event.card_list)

        if isinstance(event, InitializeRoundEvent):
            self.InitializeFrontSprites()

        if isinstance(event, NextRoundEvent):
            self.NextRoundInitial(event.players, event.pot)

        if isinstance(event, RefreshSprites):
            self.ShowChips(event.players, event.pot)


# ------------------------------------------------------
def main():
    evManager = EventManager()

    keybd = KeyboardController(evManager)
    spinner = CPUSpinnerController(evManager)
    pygameView = PygameView(evManager)

    texas_holdem = Game(evManager)

    spinner.Run()


if __name__ == "__main__":
    main()
